from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.dependencies.auth import current_user
from app.models.models import Exam, Question, ExamAttempt, StudentAnswer
from app.schemas.schemas import AnswerRequest

router = APIRouter(prefix="/api/student", tags=["Student"])

def as_utc(dt):
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)

def public_question(q):
    return {
        "id": q.id, "question_text": q.question_text,
        "options": {"A": q.option_a, "B": q.option_b, "C": q.option_c, "D": q.option_d},
        "marks": q.marks
    }

@router.get("/exams")
def available_exams(db: Session = Depends(get_db), user=Depends(current_user)):
    return db.query(Exam).filter(Exam.is_active == True).all()

@router.post("/exams/{exam_id}/start")
def start_exam(exam_id: int, db: Session = Depends(get_db), user=Depends(current_user)):
    exam = db.get(Exam, exam_id)
    if not exam or not exam.is_active: raise HTTPException(404, "Exam unavailable")
    active = db.query(ExamAttempt).filter(
        ExamAttempt.user_id == user.id, ExamAttempt.exam_id == exam_id,
        ExamAttempt.status == "STARTED"
    ).first()
    now = datetime.now(timezone.utc)
    if active:
        expires_at = as_utc(active.expires_at)
        if expires_at > now:
            return {"attempt_id": active.id, "expires_at": expires_at, "questions": [public_question(q) for q in exam.questions]}
        active.status = "TIME_EXPIRED"
        active.submitted_at = now
        db.commit()
    attempt = ExamAttempt(
        user_id=user.id, exam_id=exam.id, started_at=now,
        expires_at=now + timedelta(minutes=exam.duration_minutes), status="STARTED"
    )
    db.add(attempt); db.commit(); db.refresh(attempt)
    return {"attempt_id": attempt.id, "expires_at": as_utc(attempt.expires_at),
            "questions": [public_question(q) for q in exam.questions]}

@router.post("/attempts/{attempt_id}/answer")
def answer(attempt_id: int, data: AnswerRequest, db: Session = Depends(get_db), user=Depends(current_user)):
    attempt = db.get(ExamAttempt, attempt_id)
    if not attempt or attempt.user_id != user.id: raise HTTPException(404, "Attempt not found")
    now = datetime.now(timezone.utc)
    if attempt.status != "STARTED": raise HTTPException(400, "Attempt is not active")
    if now >= as_utc(attempt.expires_at):
        attempt.status = "TIME_EXPIRED"; attempt.submitted_at = now; db.commit()
        raise HTTPException(400, "Time expired")
    q = db.get(Question, data.question_id)
    if not q or q.exam_id != attempt.exam_id: raise HTTPException(400, "Invalid question")
    selected = data.selected_answer.upper() if data.selected_answer else None
    existing = db.query(StudentAnswer).filter_by(attempt_id=attempt.id, question_id=q.id).first()
    if not existing:
        existing = StudentAnswer(attempt_id=attempt.id, question_id=q.id)
        db.add(existing)
    existing.selected_answer = selected
    existing.is_correct = selected == q.correct_answer
    existing.marks_obtained = q.marks if existing.is_correct else 0
    db.commit()
    return {"message": "Answer saved"}

@router.post("/attempts/{attempt_id}/submit")
def submit(attempt_id: int, db: Session = Depends(get_db), user=Depends(current_user)):
    attempt = db.get(ExamAttempt, attempt_id)
    if not attempt or attempt.user_id != user.id: raise HTTPException(404, "Attempt not found")
    if attempt.status != "STARTED":
        return {"message": "Already submitted", "score": attempt.score}
    now = datetime.now(timezone.utc)
    attempt.status = "TIME_EXPIRED" if now >= as_utc(attempt.expires_at) else "SUBMITTED"
    attempt.submitted_at = now
    answers = db.query(StudentAnswer).filter_by(attempt_id=attempt.id).all()
    attempt.score = sum(a.marks_obtained for a in answers)
    db.commit()
    return {"message": "Exam submitted", "score": attempt.score, "status": attempt.status}

@router.get("/results")
def results(db: Session = Depends(get_db), user=Depends(current_user)):
    rows = db.query(ExamAttempt, Exam).join(Exam, Exam.id == ExamAttempt.exam_id).filter(
        ExamAttempt.user_id == user.id, ExamAttempt.status != "STARTED"
    ).order_by(ExamAttempt.id.desc()).all()
    return [{"attempt_id": a.id, "exam_id": e.id, "exam_title": e.title,
             "score": a.score, "total_marks": e.total_marks, "status": a.status,
             "submitted_at": a.submitted_at} for a,e in rows]
