"""
File watcher for INBOX folders - automatically creates jobs from new content.
"""

import os
import time
import shutil
from pathlib import Path
from typing import Set
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent

from shortsfactory.core.database import Database, JobState
from shortsfactory.core.config import get_config
from shortsfactory.core.logger import get_logger


class InboxHandler(FileSystemEventHandler):
    """Handler for file system events in INBOX folders"""
    
    def __init__(self, db: Database, logger):
        self.db = db
        self.logger = logger
        self.config = get_config()
        self.processed_files: Set[str] = set()
        
        # Ensure storage directories exist
        os.makedirs(self.config.storage.originals, exist_ok=True)
    
    def on_created(self, event: FileSystemEvent):
        """Handle file creation events"""
        if event.is_directory:
            return
        
        # Ignore temporary files
        if event.src_path.endswith(('.tmp', '.part', '.crdownload')):
            return
        
        # Avoid processing the same file twice
        if event.src_path in self.processed_files:
            return
        
        self.process_new_file(event.src_path)
    
    def on_modified(self, event: FileSystemEvent):
        """Handle file modification events (for ideas.txt)"""
        if event.is_directory:
            return
        
        # Only process ideas.txt modifications
        if event.src_path.endswith('ideas.txt'):
            self.process_ideas_file(event.src_path)
    
    def process_new_file(self, file_path: str):
        """Process a newly added file"""
        try:
            # Wait a bit to ensure file is fully written
            time.sleep(1)
            
            # Determine source type
            source_type = None
            if 'long_videos' in file_path:
                source_type = 'long_video'
            elif 'clips' in file_path:
                source_type = 'clip'
            else:
                return
            
            # Check if it's a video file
            valid_extensions = ['.mp4', '.mov', '.avi', '.mkv', '.wmv', '.flv', '.webm']
            if not any(file_path.lower().endswith(ext) for ext in valid_extensions):
                self.logger.warning(f"Skipping non-video file: {file_path}")
                return
            
            # Copy to storage
            filename = os.path.basename(file_path)
            dest_path = os.path.join(self.config.storage.originals, filename)
            
            # Ensure unique filename
            counter = 1
            base_name, ext = os.path.splitext(filename)
            while os.path.exists(dest_path):
                filename = f"{base_name}_{counter}{ext}"
                dest_path = os.path.join(self.config.storage.originals, filename)
                counter += 1
            
            shutil.copy2(file_path, dest_path)
            
            # Create job
            job = self.db.create_job(
                source_type=source_type,
                source_path=file_path
            )
            
            # Update with storage path
            self.db.update_job_state(
                job.id,
                JobState.NEW,
                original_path=dest_path
            )
            
            self.logger.info(
                f"Created job {job.id} from {source_type}",
                file=filename
            )
            
            self.processed_files.add(file_path)
            
        except Exception as e:
            self.logger.error(
                f"Error processing file {file_path}: {str(e)}",
                exc_info=True
            )
    
    def process_ideas_file(self, file_path: str):
        """Process ideas.txt file for new ideas"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Track which ideas we've already processed
            processed_ideas_file = os.path.join(
                self.config.storage.metadata,
                'processed_ideas.txt'
            )
            
            processed_ideas = set()
            if os.path.exists(processed_ideas_file):
                with open(processed_ideas_file, 'r', encoding='utf-8') as f:
                    processed_ideas = set(line.strip() for line in f if line.strip())
            
            # Process new ideas
            new_ideas = []
            for line in lines:
                idea = line.strip()
                if idea and idea not in processed_ideas and not idea.startswith('#'):
                    # Create job for this idea
                    job = self.db.create_job(
                        source_type='idea',
                        source_idea=idea
                    )
                    
                    self.logger.info(
                        f"Created job {job.id} from idea",
                        idea=idea[:50]
                    )
                    
                    new_ideas.append(idea)
            
            # Update processed ideas file
            if new_ideas:
                with open(processed_ideas_file, 'a', encoding='utf-8') as f:
                    for idea in new_ideas:
                        f.write(idea + '\n')
        
        except Exception as e:
            self.logger.error(
                f"Error processing ideas file: {str(e)}",
                exc_info=True
            )


class InboxWatcher:
    """Watches INBOX folders for new content"""
    
    def __init__(self, db: Database):
        self.db = db
        self.logger = get_logger("watcher")
        self.config = get_config()
        self.observer = Observer()
        
        # Ensure INBOX directories exist
        os.makedirs(self.config.inbox.long_videos, exist_ok=True)
        os.makedirs(self.config.inbox.clips, exist_ok=True)
        
        # Create ideas.txt if it doesn't exist
        if not os.path.exists(self.config.inbox.ideas):
            with open(self.config.inbox.ideas, 'w') as f:
                f.write("# Add your video ideas here, one per line\n")
    
    def start(self):
        """Start watching INBOX folders"""
        self.logger.info("Starting inbox watcher")
        
        handler = InboxHandler(self.db, self.logger)
        
        # Watch long_videos folder
        self.observer.schedule(
            handler,
            self.config.inbox.long_videos,
            recursive=False
        )
        self.logger.info(f"Watching: {self.config.inbox.long_videos}")
        
        # Watch clips folder
        self.observer.schedule(
            handler,
            self.config.inbox.clips,
            recursive=False
        )
        self.logger.info(f"Watching: {self.config.inbox.clips}")
        
        # Watch ideas.txt
        ideas_dir = os.path.dirname(self.config.inbox.ideas)
        self.observer.schedule(
            handler,
            ideas_dir,
            recursive=False
        )
        self.logger.info(f"Watching: {self.config.inbox.ideas}")
        
        self.observer.start()
        self.logger.info("Inbox watcher started successfully")
        
        try:
            while True:
                time.sleep(self.config.inbox.watch_interval)
        except KeyboardInterrupt:
            self.stop()
    
    def stop(self):
        """Stop watching"""
        self.logger.info("Stopping inbox watcher")
        self.observer.stop()
        self.observer.join()
        self.logger.info("Inbox watcher stopped")


def main():
    """Main entry point for watcher"""
    from shortsfactory.core.database import Database
    
    db = Database()
    watcher = InboxWatcher(db)
    
    try:
        watcher.start()
    except KeyboardInterrupt:
        print("\nShutting down gracefully...")


if __name__ == "__main__":
    main()
