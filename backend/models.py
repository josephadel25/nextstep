from sqlalchemy import Column, Integer, String, Enum, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from database import Base

class RoleEnum(str, enum.Enum):
    candidate = "candidate"
    recruiter = "recruiter"

class StatusEnum(str, enum.Enum):
    Applied = "Applied"
    Interview = "Interview"
    Offer = "Offer"
    Rejected = "Rejected"
    Hired = "Hired"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(RoleEnum), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    profile = relationship("Profile", back_populates="user", uselist=False)
    application = relationship("Application", back_populates="candidate", uselist=False)

class Profile(Base):
    __tablename__ = "profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    job_title = Column(String(100))
    phone = Column(String(30))
    contact_email = Column(String(150))
    summary = Column(Text)
    resume_filename = Column(String(255))
    resume_path = Column(String(500))
    location = Column(String(150))

    user = relationship("User", back_populates="profile")
    skills = relationship("Skill", back_populates="profile", cascade="all, delete-orphan")
    education = relationship("Education", back_populates="profile", cascade="all, delete-orphan")
    experience = relationship("Experience", back_populates="profile", cascade="all, delete-orphan")
    courses = relationship("Course", back_populates="profile", cascade="all, delete-orphan")
    projects = relationship("Project", back_populates="profile", cascade="all, delete-orphan")

class Skill(Base):
    __tablename__ = "skills"
    
    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("profiles.id"))
    name = Column(String(100), nullable=False)

    profile = relationship("Profile", back_populates="skills")

class Education(Base):
    __tablename__ = "education"
    
    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("profiles.id"))
    degree = Column(String(150), nullable=False)
    school = Column(String(150), nullable=False)
    year = Column(String(50), nullable=False)

    profile = relationship("Profile", back_populates="education")

class Experience(Base):
    __tablename__ = "experience"
    
    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("profiles.id"))
    job_title = Column(String(100), nullable=False)
    company = Column(String(100), nullable=False)
    period = Column(String(80), nullable=False)
    description = Column(Text)

    profile = relationship("Profile", back_populates="experience")

class Course(Base):
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("profiles.id"))
    name = Column(String(150), nullable=False)
    institution = Column(String(150))
    year = Column(String(50))
    profile = relationship("Profile", back_populates="courses")

class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("profiles.id"))
    name = Column(String(150), nullable=False)
    description = Column(Text)
    link = Column(String(255))
    profile = relationship("Profile", back_populates="projects")

class Application(Base):
    __tablename__ = "applications"
    
    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("users.id"), unique=True)
    status = Column(Enum(StatusEnum), default=StatusEnum.Applied)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    candidate = relationship("User", back_populates="application")
