from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import models, schemas, auth
from database import get_db
from datetime import datetime

router = APIRouter(prefix="/api/candidates", tags=["candidates"])

def check_recruiter(current_user: models.User):
    if current_user.role != models.RoleEnum.recruiter:
        raise HTTPException(status_code=403, detail="Not authorized")

@router.get("", response_model=List[schemas.FullCandidateResponse])
def get_candidates(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    check_recruiter(current_user)
    
    candidates = db.query(models.User).filter(models.User.role == models.RoleEnum.candidate).all()
    result = []
    for cand in candidates:
        app = db.query(models.Application).filter(models.Application.candidate_id == cand.id).first()
        status = app.status.value if app else "Applied"
        applied_date = app.updated_at.strftime("%b %d") if app and app.updated_at else cand.created_at.strftime("%b %d")
        
        result.append({
            "id": cand.id,
            "name": cand.name,
            "email": cand.email,
            "role": cand.role.value,
            "status": status,
            "applied_date": applied_date,
            "profile": cand.profile
        })
    return result

@router.get("/{candidate_id}", response_model=schemas.FullCandidateResponse)
def get_candidate(candidate_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    check_recruiter(current_user)
    
    cand = db.query(models.User).filter(models.User.id == candidate_id, models.User.role == models.RoleEnum.candidate).first()
    if not cand:
        raise HTTPException(status_code=404, detail="Candidate not found")
        
    app = db.query(models.Application).filter(models.Application.candidate_id == cand.id).first()
    status = app.status.value if app else "Applied"
    applied_date = app.updated_at.strftime("%b %d") if app and app.updated_at else cand.created_at.strftime("%b %d")
    
    return {
        "id": cand.id,
        "name": cand.name,
        "email": cand.email,
        "role": cand.role.value,
        "status": status,
        "applied_date": applied_date,
        "profile": cand.profile
    }

@router.patch("/{candidate_id}/status")
def update_status(candidate_id: int, status_update: schemas.CandidateStatusUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    check_recruiter(current_user)
    
    app = db.query(models.Application).filter(models.Application.candidate_id == candidate_id).first()
    if not app:
        app = models.Application(candidate_id=candidate_id)
        db.add(app)
        
    try:
        app.status = models.StatusEnum(status_update.status)
        app.updated_at = datetime.utcnow()
        db.commit()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid status")
        
    return {"message": "Status updated successfully", "status": app.status.value}

@router.get("/search", response_model=List[schemas.FullCandidateResponse])
def search_candidates(q: str = None, skill: str = None, stage: str = None, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    check_recruiter(current_user)
    
    query = db.query(models.User).filter(models.User.role == models.RoleEnum.candidate)
    
    if q:
        query = query.filter(models.User.name.ilike(f"%{q}%"))
        
    if skill:
        query = query.filter(models.User.profile.has(models.Profile.skills.any(models.Skill.name.ilike(f"%{skill}%"))))
        
    if stage:
        try:
            status_enum = models.StatusEnum(stage)
            query = query.join(models.Application).filter(models.Application.status == status_enum)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid stage")
            
    candidates = query.all()
    result = []
    for cand in candidates:
        app = db.query(models.Application).filter(models.Application.candidate_id == cand.id).first()
        status = app.status.value if app else "Applied"
        applied_date = app.updated_at.strftime("%b %d") if app and app.updated_at else cand.created_at.strftime("%b %d")
        
        result.append({
            "id": cand.id,
            "name": cand.name,
            "email": cand.email,
            "role": cand.role.value,
            "status": status,
            "applied_date": applied_date,
            "profile": cand.profile
        })
    return result

@router.get("/pipeline/stages")
def get_stages_count(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    check_recruiter(current_user)
    
    results = {}
    for stage in models.StatusEnum:
        count = db.query(models.Application).filter(models.Application.status == stage).count()
        results[stage.value] = count
        
    return results
