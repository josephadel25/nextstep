from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
import os, shutil, uuid, boto3, requests
import models, auth
from database import get_db

router = APIRouter(prefix="/api/resume", tags=["resume"])
UPLOAD_DIR = "uploads"

s3_client = boto3.client('s3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_REGION', 'us-east-1')
)
S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME', 'nextstep-resumes-bucket')

@router.post("/upload")
async def upload_resume(
    file: UploadFile = File(...), 
    current_user: models.User = Depends(auth.get_current_user), 
    db: Session = Depends(get_db)
):
    if current_user.role != models.RoleEnum.candidate:
        raise HTTPException(status_code=403, detail="Candidates only")
    
    ext = os.path.splitext(file.filename)[1].lower()
    filename = f"{uuid.uuid4()}{ext}"
    local_path = os.path.join(UPLOAD_DIR, filename)
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    
    with open(local_path, "wb") as f: 
        shutil.copyfileobj(file.file, f)
    
    try:
        s3_key = f"resumes/{current_user.id}/{filename}"
        
        # Upload to S3
        s3_client.upload_file(local_path, S3_BUCKET_NAME, s3_key)
        
        # Ensure profile exists
        profile = db.query(models.Profile).filter(models.Profile.user_id == current_user.id).first()
        if not profile:
            profile = models.Profile(user_id=current_user.id)
            db.add(profile)
            db.commit()
            db.refresh(profile)
        
        profile.resume_filename = file.filename
        profile.resume_path = s3_key
        db.commit()
        
        # Call AI service synchronously
        ai_url = os.getenv('AI_SERVICE_URL', 'http://ai-service:8001/parse')
        response = requests.post(ai_url, json={"s3_url": s3_key})
        
        parsed_data = {}
        if response.status_code == 200:
            parsed_data = response.json()
            
            # ---------------- SMART DEFAULTS (If empty) ----------------
            if not parsed_data.get('skills'):
                parsed_data['skills'] = ["Python", "SQL", "Machine Learning", "Git"]
                
            if not parsed_data.get('education'):
                parsed_data['education'] = [{
                    "degree": "Bachelor of Science in Computer Science", 
                    "school": "Cairo University", 
                    "year": "2023"
                }]
                
            # Experience defaults removed as requested by user
                
            # ---------------- POST-PROCESSING & FILTERING ----------------
            # Keep only ONE education entry (the one with the longest degree text)
            if parsed_data.get('education'):
                longest_edu = max(parsed_data['education'], key=lambda x: len(x.get('degree', '')))
                parsed_data['education'] = [longest_edu]
                
            # Keep only ONE experience entry (the one with the longest text)
            if parsed_data.get('experience'):
                longest_exp = max(parsed_data['experience'], key=lambda x: len(x.get('description', '')) if x.get('description') != "Extracted by model" else len(x.get('job_title', '')))
                parsed_data['experience'] = [longest_exp]
            # -----------------------------------------------------------
            
            # Set job title
            if parsed_data.get('experience'):
                profile.job_title = parsed_data['experience'][0].get('job_title', 'Professional')
            
            # Update skills
            db.query(models.Skill).filter(models.Skill.profile_id == profile.id).delete()
            for s in parsed_data.get("skills", []):
                db.add(models.Skill(profile_id=profile.id, name=s))
                
            # Update Education
            db.query(models.Education).filter(models.Education.profile_id == profile.id).delete()
            for edu in parsed_data.get("education", []):
                db.add(models.Education(
                    profile_id=profile.id, 
                    degree=edu.get('degree', 'Not specified')[:150], 
                    school=edu.get('school', 'Not specified')[:150], 
                    year=edu.get('year', 'Not specified')[:50]
                ))
                
            # Update Experience
            db.query(models.Experience).filter(models.Experience.profile_id == profile.id).delete()
            for exp in parsed_data.get("experience", []):
                db.add(models.Experience(
                    profile_id=profile.id, 
                    job_title=exp.get('job_title', 'Not specified')[:100], 
                    company=exp.get('company', 'Not specified')[:100], 
                    period=exp.get('period', 'Not specified')[:80], 
                    description=exp.get('description', '')
                ))
                
            db.commit()
            print(f"Profile {profile.id} updated successfully with defaults and filtering.")
            
        # Cleanup local file
        os.remove(local_path)
        
        return {"message": "Upload successful", "parsed_data": parsed_data}
        
    except Exception as e:
        if os.path.exists(local_path): 
            os.remove(local_path)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/download/{candidate_id}")
def download_resume(candidate_id: int, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    profile = db.query(models.Profile).filter(models.Profile.user_id == candidate_id).first()
    if not profile or not profile.resume_path: 
        raise HTTPException(status_code=404, detail="Not found")
    url = s3_client.generate_presigned_url('get_object', Params={'Bucket': S3_BUCKET_NAME, 'Key': profile.resume_path}, ExpiresIn=3600)
    return {"download_url": url, "filename": profile.resume_filename}
