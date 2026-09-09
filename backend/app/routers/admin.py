from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.dependencies.auth import admin_user
from app.models.models import Exam, Question, User
from app.schemas.schemas import ExamCreate, QuestionCreate

router = APIRouter(prefix="/api/admin", tags=["Admin"])

@router.get("/dashboard")
def dashboard(db: Session = Depends(get_db), user=Depends(admin_user)):
    return {
        "exams": db.query(Exam).count(),
        "questions": db.query(Question).count()
    }

@router.post("/exams")
def create_exam(data: ExamCreate, db: Session = Depends(get_db), user=Depends(admin_user)):
    exam = Exam(**data.model_dump())
    db.add(exam); db.commit(); db.refresh(exam)
    return exam

@router.get("/exams")
def exams(db: Session = Depends(get_db), user=Depends(admin_user)):
    return db.query(Exam).order_by(Exam.id.desc()).all()

@router.delete("/exams/{exam_id}")
def delete_exam(exam_id: int, db: Session = Depends(get_db), user=Depends(admin_user)):
    exam = db.get(Exam, exam_id)
    if not exam: raise HTTPException(404, "Exam not found")
    db.delete(exam); db.commit()
    return {"message": "Exam deleted"}

@router.post("/questions")
def create_question(data: QuestionCreate, db: Session = Depends(get_db), user=Depends(admin_user)):
    if data.correct_answer.upper() not in ["A","B","C","D"]:
        raise HTTPException(400, "Correct answer must be A, B, C or D")
    if not db.get(Exam, data.exam_id):
        raise HTTPException(404, "Exam not found")

    payload = data.model_dump()
    payload["correct_answer"] = payload["correct_answer"].upper()
    q = Question(**payload)

    db.add(q); db.commit(); db.refresh(q)
    exam = db.get(Exam, data.exam_id)
    exam.total_marks = sum(x.marks for x in exam.questions)
    db.commit()
    return q

@router.get("/questions/{exam_id}")
def questions(exam_id: int, db: Session = Depends(get_db), user=Depends(admin_user)):
    return db.query(Question).filter(Question.exam_id == exam_id).all()

@router.delete("/questions/{question_id}")
def delete_question(question_id: int, db: Session = Depends(get_db), user=Depends(admin_user)):
    q = db.get(Question, question_id)
    if not q: raise HTTPException(404, "Question not found")
    exam = db.get(Exam, q.exam_id)
    db.delete(q); db.commit()
    exam.total_marks = sum(x.marks for x in exam.questions)
    db.commit()
    return {"message": "Question deleted"}
