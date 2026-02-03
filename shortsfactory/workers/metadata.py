"""
Metadata worker - generates titles, descriptions, and hashtags.
"""

import os
import json
import random
from datetime import datetime

from shortsfactory.core.database import Job, JobState
from shortsfactory.workers.base import Worker


class MetadataWorker(Worker):
    """Worker that generates metadata for videos"""
    
    def __init__(self, db):
        super().__init__("metadata", db)
    
    def get_source_state(self) -> JobState:
        return JobState.CAPTIONING
    
    def get_target_state(self) -> JobState:
        return JobState.METADATA
    
    def get_next_state(self) -> JobState:
        return JobState.RENDERING
    
    def process_job(self, job: Job) -> bool:
        """Generate metadata for the video"""
        try:
            self.logger.info(f"Job {job.id}: Generating metadata")
            
            # Generate title
            title = self.generate_title(job)
            
            # Generate description
            description = self.generate_description(job)
            
            # Generate hashtags
            hashtags = self.generate_hashtags(job)
            
            # Save metadata
            metadata_filename = f"job_{job.id}_metadata.json"
            metadata_path = os.path.join(self.config.storage.metadata, metadata_filename)
            
            metadata = {
                'job_id': job.id,
                'title': title,
                'description': description,
                'hashtags': hashtags,
                'generated_at': datetime.utcnow().isoformat()
            }
            
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2)
            
            # Update job
            self.db.update_job_state(
                job.id,
                self.get_target_state(),
                title=title,
                description=description,
                hashtags=" ".join(hashtags),
                metadata_file=metadata_path
            )
            
            self.logger.info(f"Job {job.id}: Metadata generated")
            
            return True
            
        except Exception as e:
            self.logger.error(
                f"Job {job.id}: Metadata generation failed: {str(e)}",
                exc_info=True
            )
            return False
    
    def generate_title(self, job: Job) -> str:
        """Generate a title for the video"""
        # In a real system, this would use AI
        # For now, generate a simple title
        
        if job.source_idea:
            # Use the idea as basis for title
            words = job.source_idea.split()[:10]
            title = " ".join(words)
            if len(title) > 90:
                title = title[:87] + "..."
            return title
        else:
            templates = [
                "Must Watch! Amazing Content",
                "You Won't Believe This!",
                "Incredible Moment Caught on Camera",
                "This Changed Everything",
                "The Best Thing You'll See Today"
            ]
            return random.choice(templates)
    
    def generate_description(self, job: Job) -> str:
        """Generate a description for the video"""
        base_description = ""
        
        if job.source_idea:
            base_description = f"{job.source_idea}\n\n"
        
        base_description += (
            "Thanks for watching! Don't forget to like and subscribe for more content.\n\n"
            f"#Shorts #Viral #Trending\n"
            f"\nGenerated: {datetime.now().strftime('%Y-%m-%d')}"
        )
        
        return base_description
    
    def generate_hashtags(self, job: Job) -> list:
        """Generate hashtags for the video"""
        # In a real system, this would be smarter and vary more
        base_tags = ["#Shorts", "#Viral", "#Trending"]
        
        # Add some random variation
        optional_tags = [
            "#Amazing", "#MustWatch", "#Incredible",
            "#Awesome", "#Epic", "#Unbelievable",
            "#Content", "#Video", "#Entertainment"
        ]
        
        # Select 2-3 random optional tags
        selected = random.sample(optional_tags, random.randint(2, 3))
        
        return base_tags + selected
