# Group B Mock Exam Application

Full-stack starter application for Group B mock exams.

## Stack
- Frontend: React + Vite
- Backend: FastAPI + SQLAlchemy
- Database: PostgreSQL
- Auth: JWT
- Local deployment: Docker Compose

## Run
1. Copy `.env.example` to `.env`
2. Run `docker compose up --build`
3. Open http://localhost:5173
4. API docs: http://localhost:8000/docs

Default seeded admin:
- Email: admin@example.com
- Password: admin123

The application includes student/admin authentication, exam creation, question management,
45-minute server-controlled attempts, submission, scoring, and result history.
