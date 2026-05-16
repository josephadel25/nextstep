from pydantic import BaseModel, EmailStr, field_validator
from typing import List, Optional, Any
from datetime import datetime

# --- Auth Schemas ---
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str

    class Config:
        from_attributes = True

# --- Profile Schemas ---
class SkillSchema(BaseModel):
    name: str

    class Config:
        from_attributes = True

class EducationSchema(BaseModel):
    degree: str
    school: str
    year: str

    class Config:
        from_attributes = True

class ExperienceSchema(BaseModel):
    job_title: str
    company: str
    period: str
    description: Optional[str] = None

    class Config:
        from_attributes = True

class CourseSchema(BaseModel):
    name: str
    institution: Optional[str] = None
    year: Optional[str] = None
    class Config:
        from_attributes = True

class ProjectSchema(BaseModel):
    name: str
    description: Optional[str] = None
    link: Optional[str] = None
    class Config:
        from_attributes = True

class ProfileUpdate(BaseModel):
    job_title: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    contact_email: Optional[str] = None
    summary: Optional[str] = None
    skills: Optional[Any] = None
    education: Optional[List[EducationSchema]] = None
    experience: Optional[List[ExperienceSchema]] = None
    courses: Optional[List[CourseSchema]] = None
    projects: Optional[List[ProjectSchema]] = None

    @field_validator('skills', mode='before')
    @classmethod
    def validate_skills(cls, v: Any) -> Optional[List[str]]:
        if v is None:
            return None
        if isinstance(v, str):
            return [s.strip() for s in v.split(',') if s.strip()]
        if isinstance(v, list):
            return [str(s) for s in v]
        return []

class ProfileResponse(BaseModel):
    id: int
    job_title: Optional[str] = None
    phone: Optional[str] = None
    contact_email: Optional[str] = None
    summary: Optional[str] = None
    resume_filename: Optional[str] = None
    skills: List[SkillSchema] = []
    education: List[EducationSchema] = []
    experience: List[ExperienceSchema] = []
    courses: List[CourseSchema] = []
    projects: List[ProjectSchema] = []

    class Config:
        from_attributes = True

class FullCandidateResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str
    status: str
    applied_date: str
    profile: Optional[ProfileResponse] = None

class CandidateStatusUpdate(BaseModel):
    status: str

class CandidateSummary(BaseModel):
    id: int
    user_id: int
    name: str
    email: str
    status: str
    location: Optional[str] = None
    skills: Optional[str] = None
    created_at: int

class CandidateDetail(BaseModel):
    id: int
    user_id: int
    name: str
    email: str
    phone: Optional[str] = None
    location: Optional[str] = None
    title: Optional[str] = None
    status: str
    skills: Optional[str] = None
    summary: Optional[str] = None
    education: List[EducationSchema] = []
    experience: List[ExperienceSchema] = []
    courses: List[CourseSchema] = []
    projects: List[ProjectSchema] = []
