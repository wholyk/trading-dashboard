"""
Base worker class for job processing.
"""

import time
from abc import ABC, abstractmethod
from typing import Optional
from datetime import datetime

from shortsfactory.core.database import Database, Job, JobState
from shortsfactory.core.config import get_config
from shortsfactory.core.logger import get_logger


class Worker(ABC):
    """Base class for all workers"""
    
    def __init__(self, name: str, db: Database):
        self.name = name
        self.db = db
        self.config = get_config()
        self.logger = get_logger(f"worker.{name}")
        self.running = False
    
    @abstractmethod
    def get_source_state(self) -> JobState:
        """Get the state this worker looks for"""
        pass
    
    @abstractmethod
    def get_target_state(self) -> JobState:
        """Get the state this worker transitions to on success"""
        pass
    
    @abstractmethod
    def process_job(self, job: Job) -> bool:
        """
        Process a single job.
        Returns True on success, False on failure.
        """
        pass
    
    def run(self):
        """Main worker loop"""
        self.running = True
        self.logger.info(f"Worker {self.name} started")
        
        while self.running:
            try:
                # Get next job
                jobs = self.db.get_jobs_by_state(self.get_source_state(), limit=1)
                
                if not jobs:
                    time.sleep(5)
                    continue
                
                job = jobs[0]
                self.logger.job_event(job.id, f"Processing started by {self.name}")
                
                # Update state to indicate processing
                processing_state = f"{self.get_target_state()}"
                self.db.update_job_state(
                    job.id,
                    processing_state,
                    error_message=None
                )
                
                # Process the job
                try:
                    success = self.process_job(job)
                    
                    if success:
                        # Move to next state
                        next_state = self.get_next_state()
                        self.db.update_job_state(job.id, next_state)
                        self.logger.job_event(
                            job.id,
                            f"Processing completed by {self.name}"
                        )
                    else:
                        # Handle failure
                        self.handle_failure(job)
                
                except Exception as e:
                    self.logger.error(
                        f"Error processing job {job.id}: {str(e)}",
                        exc_info=True
                    )
                    self.handle_failure(job, str(e))
            
            except KeyboardInterrupt:
                self.logger.info("Worker interrupted by user")
                break
            except Exception as e:
                self.logger.error(f"Worker error: {str(e)}", exc_info=True)
                time.sleep(10)
        
        self.logger.info(f"Worker {self.name} stopped")
    
    def get_next_state(self) -> JobState:
        """Get the next state after successful processing"""
        # Default implementation - can be overridden
        return self.get_target_state()
    
    def handle_failure(self, job: Job, error_message: Optional[str] = None):
        """Handle job failure"""
        retry_count = job.retry_count + 1
        
        if retry_count >= self.config.worker.max_retries:
            # Max retries reached - mark as failed
            self.db.update_job_state(
                job.id,
                JobState.FAILED,
                error_message=error_message or "Max retries reached",
                retry_count=retry_count
            )
            self.logger.error(f"Job {job.id} failed after {retry_count} retries")
        else:
            # Retry - move back to source state
            self.db.update_job_state(
                job.id,
                self.get_source_state(),
                error_message=error_message,
                retry_count=retry_count
            )
            self.logger.warning(
                f"Job {job.id} retry {retry_count}/{self.config.worker.max_retries}"
            )
            time.sleep(self.config.worker.retry_delay)
    
    def stop(self):
        """Stop the worker"""
        self.running = False
