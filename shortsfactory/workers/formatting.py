"""
Formatting worker - converts videos to 9:16 vertical format.
"""

import os
from moviepy.editor import VideoFileClip, CompositeVideoClip, ColorClip

from shortsfactory.core.database import Job, JobState
from shortsfactory.workers.base import Worker


class FormattingWorker(Worker):
    """Worker that formats videos to 9:16 vertical aspect ratio"""
    
    def __init__(self, db):
        super().__init__("formatting", db)
    
    def get_source_state(self) -> JobState:
        return JobState.CUTTING
    
    def get_target_state(self) -> JobState:
        return JobState.FORMATTING
    
    def get_next_state(self) -> JobState:
        return JobState.CAPTIONING
    
    def process_job(self, job: Job) -> bool:
        """Format video to 9:16 aspect ratio"""
        try:
            source_path = job.cut_path
            if not source_path or not os.path.exists(source_path):
                self.logger.error(f"Job {job.id}: Cut file not found")
                return False
            
            self.logger.info(f"Job {job.id}: Loading cut video {source_path}")
            
            # Load video
            video = VideoFileClip(source_path)
            
            # Target dimensions (9:16 aspect ratio)
            target_width = self.config.video.target_width
            target_height = self.config.video.target_height
            
            # Calculate scaling
            video_aspect = video.w / video.h
            target_aspect = target_width / target_height
            
            if video_aspect > target_aspect:
                # Video is wider - scale to height and crop width
                scale_factor = target_height / video.h
            else:
                # Video is taller - scale to width and crop height
                scale_factor = target_width / video.w
            
            # Resize video
            resized = video.resize(scale_factor)
            
            # Center crop to target dimensions
            if resized.w > target_width:
                x_center = resized.w / 2
                x1 = int(x_center - target_width / 2)
                resized = resized.crop(x1=x1, width=target_width)
            
            if resized.h > target_height:
                y_center = resized.h / 2
                y1 = int(y_center - target_height / 2)
                resized = resized.crop(y1=y1, height=target_height)
            
            # If needed, pad to exact dimensions with black bars
            if resized.w < target_width or resized.h < target_height:
                background = ColorClip(
                    size=(target_width, target_height),
                    color=(0, 0, 0),
                    duration=resized.duration
                )
                
                x_pos = (target_width - resized.w) // 2
                y_pos = (target_height - resized.h) // 2
                
                final = CompositeVideoClip([
                    background,
                    resized.set_position((x_pos, y_pos))
                ])
            else:
                final = resized
            
            # Save formatted version
            filename = f"job_{job.id}_formatted.mp4"
            output_path = os.path.join(self.config.storage.intermediate, filename)
            
            self.logger.info(f"Job {job.id}: Writing formatted video to {output_path}")
            
            final.write_videofile(
                output_path,
                codec=self.config.video.video_codec,
                audio_codec=self.config.video.audio_codec,
                fps=self.config.video.fps,
                bitrate=self.config.video.bitrate,
                logger=None
            )
            
            # Clean up
            final.close()
            if resized != final:
                resized.close()
            video.close()
            
            # Update job
            self.db.update_job_state(
                job.id,
                self.get_target_state(),
                formatted_path=output_path
            )
            
            self.logger.info(f"Job {job.id}: Formatting completed")
            
            return True
            
        except Exception as e:
            self.logger.error(
                f"Job {job.id}: Formatting failed: {str(e)}",
                exc_info=True
            )
            return False
