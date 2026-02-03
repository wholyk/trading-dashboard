"""
Cutting worker - extracts clips from long videos.
"""

import os
from moviepy.editor import VideoFileClip

from shortsfactory.core.database import Job, JobState
from shortsfactory.workers.base import Worker


class CuttingWorker(Worker):
    """Worker that cuts/selects clips from source videos"""
    
    def __init__(self, db):
        super().__init__("cutting", db)
    
    def get_source_state(self) -> JobState:
        return JobState.NEW
    
    def get_target_state(self) -> JobState:
        return JobState.CUTTING
    
    def get_next_state(self) -> JobState:
        return JobState.FORMATTING
    
    def process_job(self, job: Job) -> bool:
        """Cut/select clip from source video"""
        try:
            if not job.original_path or not os.path.exists(job.original_path):
                self.logger.error(f"Job {job.id}: Source file not found")
                return False
            
            self.logger.info(f"Job {job.id}: Loading video {job.original_path}")
            
            # Load video
            video = VideoFileClip(job.original_path)
            duration = video.duration
            
            self.logger.info(f"Job {job.id}: Video duration: {duration:.2f}s")
            
            # Determine clip duration
            target_duration = min(
                self.config.video.max_duration,
                max(self.config.video.min_duration, duration)
            )
            
            if job.source_type == 'clip':
                # For clips, use the entire video if within limits
                if duration <= self.config.video.max_duration:
                    start_time = 0
                    end_time = duration
                else:
                    # Extract middle section
                    start_time = (duration - target_duration) / 2
                    end_time = start_time + target_duration
            else:
                # For long videos, extract from the middle
                # In a real system, this would use AI to find best moment
                start_time = max(0, (duration - target_duration) / 2)
                end_time = min(duration, start_time + target_duration)
            
            self.logger.info(
                f"Job {job.id}: Cutting from {start_time:.2f}s to {end_time:.2f}s"
            )
            
            # Cut the clip
            clip = video.subclip(start_time, end_time)
            
            # Save cut version
            filename = f"job_{job.id}_cut.mp4"
            output_path = os.path.join(self.config.storage.intermediate, filename)
            
            clip.write_videofile(
                output_path,
                codec=self.config.video.video_codec,
                audio_codec=self.config.video.audio_codec,
                fps=self.config.video.fps,
                logger=None  # Suppress moviepy's output
            )
            
            # Clean up
            clip.close()
            video.close()
            
            # Update job
            self.db.update_job_state(
                job.id,
                self.get_target_state(),
                cut_path=output_path,
                duration_seconds=end_time - start_time
            )
            
            self.logger.info(f"Job {job.id}: Cutting completed, saved to {output_path}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Job {job.id}: Cutting failed: {str(e)}", exc_info=True)
            return False
