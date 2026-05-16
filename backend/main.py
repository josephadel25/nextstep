from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
import models
from database import engine, get_db
from routers import auth, profile, candidates, resume
from sqlalchemy.orm import Session

# Create all tables in the database
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="NextStep API", version="1.0.0")

# Setup CORS to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://13.53.39.78:8080", "http://13.53.39.78"], # Support both origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(candidates.router)
app.include_router(resume.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the NextStep API"}

@app.get("/api/stats")
def get_stats(db: Session = Depends(get_db)):
    try:
        db.expire_all()  # Ensure fresh data, not cached session state
        candidates_count = db.query(models.User).filter(models.User.role == models.RoleEnum.candidate).count()
        recruiters_count = db.query(models.User).filter(models.User.role == models.RoleEnum.recruiter).count()
        resumes_count = db.query(models.Profile).filter(models.Profile.resume_path != None).count()
        
        return {
            "candidates": candidates_count,
            "recruiters": recruiters_count,
            "resumes_parsed": resumes_count
        }
    except Exception as e:
        print(f"Database Error in stats: {e}")
        return {
            "candidates": 0,
            "recruiters": 0,
            "resumes_parsed": 0
        }
