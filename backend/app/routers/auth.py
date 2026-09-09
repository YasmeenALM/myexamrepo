from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import hash_password, verify_password, create_access_token
from app.models.models import User
from app.schemas.schemas import RegisterRequest, LoginRequest

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/register")
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(400, "Email already registered")
    user = User(
        name=data.name,
        email=data.email,
        password_hash=hash_password(data.password),
        role="STUDENT",
    )
    db.add(user); db.commit(); db.refresh(user)
    return {"message": "Registration successful"}

@router.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(401, "Invalid email or password")
    token = create_access_token({"sub": str(user.id), "role": user.role})
    return {"access_token": token, "token_type": "bearer",
            "user": {"id": user.id, "name": user.name, "email": user.email, "role": user.role}}

@router.get("/me")
def me(user=Depends(__import__("app.dependencies.auth", fromlist=["current_user"]).current_user)):
    return {"id": user.id, "name": user.name, "email": user.email, "role": user.role}
