"""
Quick test to verify the core system functionality.
"""

import sys
import time
from shortsfactory.core.database import Database, JobState
from shortsfactory.core.config import get_config
from shortsfactory.core.logger import get_logger

def test_database():
    """Test database operations"""
    print("Testing database operations...")
    
    db = Database()
    
    # Create a test job
    job = db.create_job(
        source_type="clip",
        source_path="test.mp4"
    )
    
    print(f"✓ Created job {job.id}")
    
    # Update job state
    db.update_job_state(job.id, JobState.CUTTING, progress=25.0)
    print(f"✓ Updated job state to {JobState.CUTTING}")
    
    # Get job
    retrieved = db.get_job(job.id)
    assert retrieved.id == job.id
    assert retrieved.state == JobState.CUTTING
    print(f"✓ Retrieved job {job.id}")
    
    # Get stats
    stats = db.get_stats()
    print(f"✓ Stats: {stats['total_jobs']} total jobs")
    
    # Get activity logs
    logs = db.get_activity_logs(limit=5)
    print(f"✓ Retrieved {len(logs)} activity logs")
    
    print("Database tests passed!\n")
    return True


def test_config():
    """Test configuration system"""
    print("Testing configuration system...")
    
    config = get_config()
    
    assert config.video.target_width == 1080
    assert config.video.target_height == 1920
    assert config.upload.enabled == False
    
    print(f"✓ Config loaded: {config.video.target_width}x{config.video.target_height}")
    print(f"✓ Upload enabled: {config.upload.enabled}")
    print("Configuration tests passed!\n")
    return True


def test_logger():
    """Test logging system"""
    print("Testing logging system...")
    
    logger = get_logger("test")
    
    logger.info("Test info message")
    logger.warning("Test warning message")
    logger.job_event(999, "TEST_EVENT", "Testing job event logging")
    
    print("✓ Logger working correctly")
    print("Logging tests passed!\n")
    return True


def main():
    """Run all tests"""
    print("=" * 60)
    print("ShortsFactory Core System Tests")
    print("=" * 60)
    print()
    
    try:
        all_passed = True
        
        all_passed &= test_database()
        all_passed &= test_config()
        all_passed &= test_logger()
        
        if all_passed:
            print("=" * 60)
            print("✓ ALL TESTS PASSED")
            print("=" * 60)
            return 0
        else:
            print("=" * 60)
            print("✗ SOME TESTS FAILED")
            print("=" * 60)
            return 1
            
    except Exception as e:
        print(f"\n✗ TEST FAILED WITH ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
