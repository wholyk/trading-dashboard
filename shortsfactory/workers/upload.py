"""
Upload worker - uploads approved videos to YouTube.
"""

import os
import time
import random
from datetime import datetime, timedelta
from typing import Optional

from shortsfactory.core.database import Job, JobState
from shortsfactory.workers.base import Worker


class UploadWorker(Worker):
    """Worker that uploads approved videos to YouTube"""
    
    def __init__(self, db):
        super().__init__("upload", db)
        self.last_upload_time = None
        self.uploads_today = 0
        self.today_date = datetime.now().date()
    
    def get_source_state(self) -> JobState:
        return JobState.APPROVED
    
    def get_target_state(self) -> JobState:
        return JobState.UPLOADING
    
    def get_next_state(self) -> JobState:
        return JobState.PUBLISHED
    
    def can_upload_now(self) -> bool:
        """Check if we can upload now based on rate limits"""
        # Reset daily counter if it's a new day
        current_date = datetime.now().date()
        if current_date != self.today_date:
            self.uploads_today = 0
            self.today_date = current_date
        
        # Check daily limit
        if self.uploads_today >= self.config.upload.max_per_day:
            self.logger.warning("Daily upload limit reached")
            return False
        
        # Check minimum delay between uploads
        if self.last_upload_time is not None:
            min_delay = timedelta(minutes=self.config.upload.min_delay_minutes)
            if datetime.now() - self.last_upload_time < min_delay:
                self.logger.debug("Minimum delay between uploads not met")
                return False
        
        return True
    
    def process_job(self, job: Job) -> bool:
        """Upload video to YouTube"""
        try:
            if not self.config.upload.enabled:
                self.logger.warning(
                    f"Job {job.id}: Upload is disabled in config. "
                    "Set upload.enabled=true to enable uploads."
                )
                # Move back to approved state
                self.db.update_job_state(job.id, JobState.APPROVED)
                return False
            
            if not self.can_upload_now():
                # Move back to approved state and wait
                self.db.update_job_state(job.id, JobState.APPROVED)
                time.sleep(60)  # Wait a minute before checking again
                return False
            
            source_path = job.final_path
            if not source_path or not os.path.exists(source_path):
                self.logger.error(f"Job {job.id}: Final file not found")
                return False
            
            self.logger.info(f"Job {job.id}: Starting upload")
            
            # Add randomized delay for natural behavior
            delay_minutes = random.randint(
                self.config.upload.min_delay_minutes,
                self.config.upload.max_delay_minutes
            )
            
            if self.last_upload_time is not None:
                time_since_last = (datetime.now() - self.last_upload_time).total_seconds() / 60
                if time_since_last < delay_minutes:
                    wait_time = (delay_minutes - time_since_last) * 60
                    self.logger.info(f"Job {job.id}: Waiting {wait_time:.0f}s before upload")
                    time.sleep(wait_time)
            
            # Perform upload
            # NOTE: This is a stub - real implementation would use YouTube API
            video_id, video_url = self.upload_to_youtube(job, source_path)
            
            # Update tracking
            self.last_upload_time = datetime.now()
            self.uploads_today += 1
            
            # Update job
            self.db.update_job_state(
                job.id,
                self.get_target_state(),
                uploaded_at=datetime.utcnow(),
                video_id=video_id,
                video_url=video_url
            )
            
            self.logger.info(
                f"Job {job.id}: Upload completed",
                video_id=video_id,
                url=video_url
            )
            
            return True
            
        except Exception as e:
            self.logger.error(
                f"Job {job.id}: Upload failed: {str(e)}",
                exc_info=True
            )
            return False
    
    def upload_to_youtube(self, job: Job, video_path: str) -> tuple[str, str]:
        """
        Upload video to YouTube.
        
        NOTE: This is a STUB implementation for safety.
        To enable real uploads, you need to:
        1. Set up YouTube API credentials
        2. Implement OAuth2 authentication
        3. Use google-api-python-client to upload
        
        Returns: (video_id, video_url)
        """
        self.logger.warning(
            f"Job {job.id}: STUB UPLOAD - Not actually uploading to YouTube. "
            "Configure YouTube API credentials to enable real uploads."
        )
        
        # Generate fake video ID for testing
        fake_video_id = f"STUB_{job.id}_{int(time.time())}"
        fake_video_url = f"https://youtube.com/watch?v={fake_video_id}"
        
        # Simulate upload time
        time.sleep(5)
        
        return fake_video_id, fake_video_url
        
        # Real implementation would look like:
        """
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload
        
        youtube = build('youtube', 'v3', credentials=credentials)
        
        body = {
            'snippet': {
                'title': job.title,
                'description': job.description,
                'tags': job.hashtags.split() if job.hashtags else [],
                'categoryId': self.config.upload.category_id
            },
            'status': {
                'privacyStatus': self.config.upload.privacy_status,
                'madeForKids': self.config.upload.made_for_kids,
                'selfDeclaredMadeForKids': self.config.upload.made_for_kids
            }
        }
        
        media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
        
        request = youtube.videos().insert(
            part='snippet,status',
            body=body,
            media_body=media
        )
        
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                self.logger.info(f"Upload progress: {int(status.progress() * 100)}%")
        
        video_id = response['id']
        video_url = f"https://youtube.com/watch?v={video_id}"
        
        return video_id, video_url
        """
