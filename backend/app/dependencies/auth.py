from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import get_db
from app.models.models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("sub")
        if not user_id:
            raise Exception()
    except (JWTError, Exception):
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user = db.get(User, int(user_id))
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

def admin_user(user: User = Depends(current_user)):
    if user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user
