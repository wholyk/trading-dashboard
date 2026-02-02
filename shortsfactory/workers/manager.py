"""
Worker manager - runs all workers.
"""

import signal
import sys
import threading
from typing import List

from shortsfactory.core.database import Database
from shortsfactory.core.logger import get_logger
from shortsfactory.workers.cutting import CuttingWorker
from shortsfactory.workers.formatting import FormattingWorker
from shortsfactory.workers.caption import CaptionWorker
from shortsfactory.workers.metadata import MetadataWorker
from shortsfactory.workers.rendering import RenderingWorker
from shortsfactory.workers.upload import UploadWorker


class WorkerManager:
    """Manages all worker threads"""
    
    def __init__(self, db: Database):
        self.db = db
        self.logger = get_logger("worker_manager")
        self.workers = []
        self.threads: List[threading.Thread] = []
        self.running = False
        
        # Initialize workers
        self.workers = [
            CuttingWorker(db),
            FormattingWorker(db),
            CaptionWorker(db),
            MetadataWorker(db),
            RenderingWorker(db),
            UploadWorker(db),
        ]
    
    def start(self):
        """Start all workers"""
        self.logger.info("Starting worker manager")
        self.running = True
        
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        # Start each worker in its own thread
        for worker in self.workers:
            thread = threading.Thread(
                target=worker.run,
                name=f"Worker-{worker.name}",
                daemon=False
            )
            thread.start()
            self.threads.append(thread)
            self.logger.info(f"Started worker: {worker.name}")
        
        self.logger.info(f"All {len(self.workers)} workers started")
        
        # Wait for all threads
        try:
            for thread in self.threads:
                thread.join()
        except KeyboardInterrupt:
            self.logger.info("Received interrupt signal")
            self.stop()
    
    def stop(self):
        """Stop all workers"""
        if not self.running:
            return
        
        self.logger.info("Stopping all workers")
        self.running = False
        
        # Stop each worker
        for worker in self.workers:
            worker.stop()
        
        # Wait for threads to finish (with timeout)
        for thread in self.threads:
            thread.join(timeout=5)
        
        self.logger.info("All workers stopped")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info(f"Received signal {signum}, shutting down gracefully")
        self.stop()
        sys.exit(0)


def main():
    """Main entry point for workers"""
    from shortsfactory.core.database import Database
    
    logger = get_logger("workers")
    logger.info("Initializing worker system")
    
    db = Database()
    manager = WorkerManager(db)
    
    try:
        manager.start()
    except KeyboardInterrupt:
        logger.info("Shutdown requested")
        manager.stop()


if __name__ == "__main__":
    main()
