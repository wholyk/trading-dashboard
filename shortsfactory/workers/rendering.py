"""
Rendering worker - creates final export of the video.
"""

import os
import shutil

from shortsfactory.core.database import Job, JobState
from shortsfactory.workers.base import Worker


class RenderingWorker(Worker):
    """Worker that creates final rendered export"""
    
    def __init__(self, db):
        super().__init__("rendering", db)
    
    def get_source_state(self) -> JobState:
        return JobState.METADATA
    
    def get_target_state(self) -> JobState:
        return JobState.RENDERING
    
    def get_next_state(self) -> JobState:
        return JobState.READY_FOR_REVIEW
    
    def process_job(self, job: Job) -> bool:
        """Create final rendered video"""
        try:
            source_path = job.captioned_path
            if not source_path or not os.path.exists(source_path):
                self.logger.error(f"Job {job.id}: Captioned file not found")
                return False
            
            self.logger.info(f"Job {job.id}: Rendering final video")
            
            # For now, just copy the captioned version as the final
            # In a real system, this might do additional processing
            filename = f"job_{job.id}_final.mp4"
            output_path = os.path.join(self.config.storage.finals, filename)
            
            shutil.copy2(source_path, output_path)
            
            # Update job
            self.db.update_job_state(
                job.id,
                self.get_target_state(),
                final_path=output_path,
                progress=100.0
            )
            
            self.logger.info(f"Job {job.id}: Rendering completed, saved to {output_path}")
            
            return True
            
        except Exception as e:
            self.logger.error(
                f"Job {job.id}: Rendering failed: {str(e)}",
                exc_info=True
            )
            return False
