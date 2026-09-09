import time
from sqlalchemy import inspect, text
from sqlalchemy.exc import OperationalError
from app.core.database import Base, engine, SessionLocal
from app.models.models import User
from app.core.security import hash_password

for _ in range(30):
    try:
        Base.metadata.create_all(bind=engine)
        break
    except OperationalError:
        time.sleep(2)

db = SessionLocal()
inspector = inspect(db.bind)
if "users" in inspector.get_table_names():
    columns = {col["name"] for col in inspector.get_columns("users")}
    # payment-related columns removed

admin = db.query(User).filter(User.email == "admin@example.com").first()
if not admin:
    db.add(User(
        name="Administrator",
        email="admin@example.com",
        password_hash=hash_password("admin123"),
        role="ADMIN",
    ))
else:
    pass

db.commit()
db.close()
