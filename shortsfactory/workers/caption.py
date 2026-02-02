"""
Caption worker - generates and burns captions into videos.
"""

import os
import json
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip

from shortsfactory.core.database import Job, JobState
from shortsfactory.workers.base import Worker


class CaptionWorker(Worker):
    """Worker that generates and burns captions into videos"""
    
    def __init__(self, db):
        super().__init__("caption", db)
    
    def get_source_state(self) -> JobState:
        return JobState.FORMATTING
    
    def get_target_state(self) -> JobState:
        return JobState.CAPTIONING
    
    def get_next_state(self) -> JobState:
        return JobState.METADATA
    
    def process_job(self, job: Job) -> bool:
        """Generate and burn captions into video"""
        try:
            source_path = job.formatted_path
            if not source_path or not os.path.exists(source_path):
                self.logger.error(f"Job {job.id}: Formatted file not found")
                return False
            
            self.logger.info(f"Job {job.id}: Loading formatted video {source_path}")
            
            # Load video
            video = VideoFileClip(source_path)
            
            # For now, generate simple placeholder captions
            # In a real system, this would use Whisper for speech-to-text
            caption_text = self.generate_caption_text(job, video)
            
            # Save caption text
            caption_filename = f"job_{job.id}_captions.json"
            caption_path = os.path.join(self.config.storage.captions, caption_filename)
            
            with open(caption_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'job_id': job.id,
                    'text': caption_text,
                    'duration': video.duration
                }, f, indent=2)
            
            # For MVP, we'll skip burning captions to keep it simple
            # In production, you'd use TextClip to overlay captions
            # For now, just use the formatted video as-is
            output_path = source_path
            
            # Update job
            self.db.update_job_state(
                job.id,
                self.get_target_state(),
                captioned_path=output_path,
                caption_file=caption_path
            )
            
            self.logger.info(f"Job {job.id}: Captioning completed")
            
            # Close video
            video.close()
            
            return True
            
        except Exception as e:
            self.logger.error(
                f"Job {job.id}: Captioning failed: {str(e)}",
                exc_info=True
            )
            return False
    
    def generate_caption_text(self, job: Job, video) -> str:
        """Generate caption text for the video"""
        # In a real implementation, this would use Whisper or similar
        # For now, return a placeholder based on source
        
        if job.source_idea:
            return f"Check out this amazing content! {job.source_idea[:50]}"
        else:
            return "Amazing content coming your way!"
