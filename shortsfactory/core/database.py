"""
Database models and schema for ShortsFactory job queue.
"""

from datetime import datetime
from enum import Enum
from typing import Optional
from sqlalchemy import (
    create_engine, Column, Integer, String, DateTime, Text, Float, Boolean
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

Base = declarative_base()


class JobState(str, Enum):
    """Job lifecycle states"""
    NEW = "NEW"
    CUTTING = "CUTTING"
    FORMATTING = "FORMATTING"
    CAPTIONING = "CAPTIONING"
    METADATA = "METADATA"
    RENDERING = "RENDERING"
    READY_FOR_REVIEW = "READY_FOR_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    UPLOADING = "UPLOADING"
    PUBLISHED = "PUBLISHED"
    FAILED = "FAILED"


class Job(Base):
    """Job model representing a Short in the production pipeline"""
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Job identification
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Source information
    source_type = Column(String(50), nullable=False)  # 'long_video', 'clip', 'idea'
    source_path = Column(String(500), nullable=True)
    source_idea = Column(Text, nullable=True)
    
    # State tracking
    state = Column(String(50), default=JobState.NEW, nullable=False)
    state_data = Column(Text, nullable=True)  # JSON data for state-specific info
    
    # Processing tracking
    progress = Column(Float, default=0.0)  # 0-100%
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    
    # File paths
    original_path = Column(String(500), nullable=True)
    cut_path = Column(String(500), nullable=True)
    formatted_path = Column(String(500), nullable=True)
    captioned_path = Column(String(500), nullable=True)
    final_path = Column(String(500), nullable=True)
    caption_file = Column(String(500), nullable=True)
    metadata_file = Column(String(500), nullable=True)
    
    # Metadata
    title = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    hashtags = Column(Text, nullable=True)
    duration_seconds = Column(Float, nullable=True)
    
    # Review information
    reviewed_at = Column(DateTime, nullable=True)
    reviewed_by = Column(String(100), nullable=True)
    review_notes = Column(Text, nullable=True)
    
    # Publishing
    uploaded_at = Column(DateTime, nullable=True)
    video_id = Column(String(100), nullable=True)  # YouTube video ID
    video_url = Column(String(500), nullable=True)
    
    def __repr__(self):
        return f"<Job(id={self.id}, state={self.state}, created={self.created_at})>"


class ActivityLog(Base):
    """Activity log for audit trail"""
    __tablename__ = "activity_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    job_id = Column(Integer, nullable=True)
    action = Column(String(100), nullable=False)
    details = Column(Text, nullable=True)
    success = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<ActivityLog(id={self.id}, action={self.action}, job_id={self.job_id})>"


class Database:
    """Database manager for ShortsFactory"""
    
    def __init__(self, db_path: str = "database/shortsfactory.db"):
        """Initialize database connection"""
        self.engine = create_engine(f"sqlite:///{db_path}", echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine)
        Base.metadata.create_all(self.engine)
    
    def get_session(self) -> Session:
        """Get a new database session"""
        return self.SessionLocal()
    
    def create_job(self, source_type: str, source_path: Optional[str] = None,
                   source_idea: Optional[str] = None) -> Job:
        """Create a new job"""
        session = self.get_session()
        try:
            job = Job(
                source_type=source_type,
                source_path=source_path,
                source_idea=source_idea,
                state=JobState.NEW
            )
            session.add(job)
            session.commit()
            session.refresh(job)
            
            # Store job_id before closing session
            job_id = job.id
            
            # Log activity
            self.log_activity(
                session,
                job_id=job_id,
                action="JOB_CREATED",
                details=f"Created job from {source_type}"
            )
            session.commit()
            
            # Force load all attributes before expunging
            _ = (job.id, job.state, job.created_at, job.updated_at, 
                 job.source_type, job.source_path, job.progress)
            session.expunge(job)
            
            return job
        finally:
            session.close()
    
    def update_job_state(self, job_id: int, new_state: JobState,
                        error_message: Optional[str] = None,
                        **kwargs) -> Optional[Job]:
        """Update job state and related fields"""
        session = self.get_session()
        try:
            job = session.query(Job).filter(Job.id == job_id).first()
            if not job:
                return None
            
            old_state = job.state
            job.state = new_state
            job.updated_at = datetime.utcnow()
            
            if error_message:
                job.error_message = error_message
            
            # Update additional fields
            for key, value in kwargs.items():
                if hasattr(job, key):
                    setattr(job, key, value)
            
            session.commit()
            
            # Log state transition
            self.log_activity(
                session,
                job_id=job_id,
                action="STATE_CHANGE",
                details=f"State changed from {old_state} to {new_state}"
            )
            session.commit()
            session.refresh(job)
            
            # Make job object available outside session
            session.expunge(job)
            
            return job
        finally:
            session.close()
    
    def get_job(self, job_id: int) -> Optional[Job]:
        """Get a job by ID"""
        session = self.get_session()
        try:
            job = session.query(Job).filter(Job.id == job_id).first()
            if job:
                session.expunge(job)
            return job
        finally:
            session.close()
    
    def get_jobs_by_state(self, state: JobState, limit: int = 100):
        """Get all jobs in a specific state"""
        session = self.get_session()
        try:
            jobs = session.query(Job).filter(Job.state == state).limit(limit).all()
            for job in jobs:
                session.expunge(job)
            return jobs
        finally:
            session.close()
    
    def get_all_jobs(self, limit: int = 1000):
        """Get all jobs"""
        session = self.get_session()
        try:
            jobs = session.query(Job).order_by(Job.created_at.desc()).limit(limit).all()
            for job in jobs:
                session.expunge(job)
            return jobs
        finally:
            session.close()
    
    def log_activity(self, session: Session, job_id: Optional[int],
                    action: str, details: Optional[str] = None,
                    success: bool = True):
        """Log an activity"""
        log = ActivityLog(
            job_id=job_id,
            action=action,
            details=details,
            success=success
        )
        session.add(log)
    
    def get_activity_logs(self, job_id: Optional[int] = None, limit: int = 100):
        """Get activity logs"""
        session = self.get_session()
        try:
            query = session.query(ActivityLog).order_by(ActivityLog.timestamp.desc())
            if job_id is not None:
                query = query.filter(ActivityLog.job_id == job_id)
            logs = query.limit(limit).all()
            for log in logs:
                session.expunge(log)
            return logs
        finally:
            session.close()
    
    def get_stats(self):
        """Get overall statistics"""
        session = self.get_session()
        try:
            total = session.query(Job).count()
            by_state = {}
            for state in JobState:
                count = session.query(Job).filter(Job.state == state.value).count()
                by_state[state.value] = count
            
            return {
                "total_jobs": total,
                "by_state": by_state
            }
        finally:
            session.close()
