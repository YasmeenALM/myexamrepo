from pydantic import BaseModel, EmailStr
from typing import Optional

class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    # payment fields removed

# PaymentDetailsUpdate removed

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class QuestionCreate(BaseModel):
    exam_id: int
    question_text: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    correct_answer: str
    marks: int = 1

class ExamCreate(BaseModel):
    title: str
    description: str = ""
    duration_minutes: int = 45
    passing_marks: int = 0
    is_active: bool = True

class AnswerRequest(BaseModel):
    question_id: int
    selected_answer: Optional[str] = None
