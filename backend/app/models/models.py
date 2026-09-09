from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.core.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="STUDENT")
    # payment fields removed
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class Exam(Base):
    __tablename__ = "exams"
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, default="")
    duration_minutes = Column(Integer, default=45)
    total_marks = Column(Integer, default=0)
    passing_marks = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    questions = relationship("Question", back_populates="exam", cascade="all, delete-orphan")

class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True)
    exam_id = Column(Integer, ForeignKey("exams.id", ondelete="CASCADE"), nullable=False)
    question_text = Column(Text, nullable=False)
    option_a = Column(Text, nullable=False)
    option_b = Column(Text, nullable=False)
    option_c = Column(Text, nullable=False)
    option_d = Column(Text, nullable=False)
    correct_answer = Column(String(1), nullable=False)
    marks = Column(Integer, default=1)
    exam = relationship("Exam", back_populates="questions")

class ExamAttempt(Base):
    __tablename__ = "exam_attempts"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    exam_id = Column(Integer, ForeignKey("exams.id"), nullable=False)
    started_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    submitted_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=False)
    score = Column(Integer, default=0)
    status = Column(String(20), default="STARTED")

class StudentAnswer(Base):
    __tablename__ = "student_answers"
    id = Column(Integer, primary_key=True)
    attempt_id = Column(Integer, ForeignKey("exam_attempts.id", ondelete="CASCADE"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    selected_answer = Column(String(1), nullable=True)
    is_correct = Column(Boolean, default=False)
    marks_obtained = Column(Integer, default=0)
