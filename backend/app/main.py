from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import Base, engine
from app.models.models import User, Exam, Question, ExamAttempt, StudentAnswer
from app.routers import auth, admin, student
from app.core.config import settings

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Group B Mock Exam API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[x.strip() for x in settings.CORS_ORIGINS.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(student.router)

@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/api/health")
def api_health():
    return {"status": "ok"}
