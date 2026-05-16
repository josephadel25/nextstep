from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import models, schemas, auth
from database import get_db

router = APIRouter(prefix="/api/profile", tags=["profile"])

@router.get("/me", response_model=schemas.ProfileResponse)
def get_my_profile(current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    if current_user.role != models.RoleEnum.candidate:
        raise HTTPException(status_code=403, detail="Only candidates have profiles")
    
    profile = db.query(models.Profile).filter(models.Profile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile

@router.put("/me", response_model=schemas.ProfileResponse)
def update_profile(profile_data: schemas.ProfileUpdate, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    if current_user.role != models.RoleEnum.candidate:
        raise HTTPException(status_code=403, detail="Only candidates can update profiles")
    
    profile = db.query(models.Profile).filter(models.Profile.user_id == current_user.id).first()
    if not profile:
        profile = models.Profile(user_id=current_user.id)
        db.add(profile)
        db.commit()
        db.refresh(profile)

    if profile_data.job_title is not None:
        profile.job_title = profile_data.job_title
    if profile_data.phone is not None:
        profile.phone = profile_data.phone
    if profile_data.location is not None:
        profile.location = profile_data.location
    if hasattr(profile_data, 'contact_email') and profile_data.contact_email is not None:
        profile.contact_email = profile_data.contact_email
    if hasattr(profile_data, 'summary') and profile_data.summary is not None:
        profile.summary = profile_data.summary

    # Update skills
    if profile_data.skills is not None:
        db.query(models.Skill).filter(models.Skill.profile_id == profile.id).delete()
        for skill_name in profile_data.skills:
            db.add(models.Skill(profile_id=profile.id, name=skill_name))

    # Update education
    if profile_data.education is not None:
        db.query(models.Education).filter(models.Education.profile_id == profile.id).delete()
        for edu in profile_data.education:
            db.add(models.Education(profile_id=profile.id, degree=edu.degree, school=edu.school, year=edu.year))

    # Update experience
    if profile_data.experience is not None:
        db.query(models.Experience).filter(models.Experience.profile_id == profile.id).delete()
        for exp in profile_data.experience:
            db.add(models.Experience(profile_id=profile.id, job_title=exp.job_title, company=exp.company, period=exp.period, description=exp.description))

    # Update courses
    if profile_data.courses is not None:
        db.query(models.Course).filter(models.Course.profile_id == profile.id).delete()
        for course in profile_data.courses:
            db.add(models.Course(profile_id=profile.id, name=course.name, institution=course.institution, year=course.year))

    # Update projects
    if profile_data.projects is not None:
        db.query(models.Project).filter(models.Project.profile_id == profile.id).delete()
        for project in profile_data.projects:
            db.add(models.Project(profile_id=profile.id, name=project.name, description=project.description, link=project.link))

    db.commit()
    db.refresh(profile)
    return profile
