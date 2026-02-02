# ShortsFactory Architecture

## System Overview

ShortsFactory is a business-grade, local automation system for YouTube Shorts production. It runs entirely on a single PC with explicit user permission and can scale to support multiple channels.

## Architecture Principles

1. **Local First**: Everything runs locally with no cloud dependencies
2. **Explicit Permission**: No hidden operations, all actions are logged
3. **Crash Safe**: All jobs are resumable after crashes or restarts
4. **Observable**: Full audit trail with timestamps
5. **Scalable**: Designed to scale from single PC to distributed system
6. **Safe**: Multiple safety gates including human review

## System Components

### 1. Ingestion System (`shortsfactory/watcher.py`)

**Purpose**: Automatically detect and queue new content

**Watched Locations**:
- `INBOX/long_videos/` - Long-form videos to extract clips from
- `INBOX/clips/` - Pre-cut video clips
- `INBOX/ideas.txt` - Text-based video ideas

**Process**:
1. File system watcher monitors INBOX folders
2. New files trigger job creation
3. Files are copied to `storage/originals` for backup
4. Job record created in database with state=NEW

**Key Features**:
- Uses watchdog library for efficient file monitoring
- Avoids processing temporary/incomplete files
- Tracks processed ideas to prevent duplicates
- Validates file types before processing

### 2. Database Layer (`shortsfactory/core/database.py`)

**Purpose**: Persistent job queue and state management

**Technology**: SQLite with SQLAlchemy ORM

**Schema**:

```sql
-- jobs table
CREATE TABLE jobs (
    id INTEGER PRIMARY KEY,
    created_at DATETIME,
    updated_at DATETIME,
    source_type VARCHAR(50),  -- 'long_video', 'clip', 'idea'
    source_path VARCHAR(500),
    source_idea TEXT,
    state VARCHAR(50),  -- Job lifecycle state
    state_data TEXT,  -- JSON for state-specific data
    progress FLOAT,  -- 0-100%
    error_message TEXT,
    retry_count INTEGER,
    
    -- File paths
    original_path VARCHAR(500),
    cut_path VARCHAR(500),
    formatted_path VARCHAR(500),
    captioned_path VARCHAR(500),
    final_path VARCHAR(500),
    caption_file VARCHAR(500),
    metadata_file VARCHAR(500),
    
    -- Metadata
    title VARCHAR(100),
    description TEXT,
    hashtags TEXT,
    duration_seconds FLOAT,
    
    -- Review
    reviewed_at DATETIME,
    reviewed_by VARCHAR(100),
    review_notes TEXT,
    
    -- Publishing
    uploaded_at DATETIME,
    video_id VARCHAR(100),
    video_url VARCHAR(500)
);

-- activity_logs table
CREATE TABLE activity_logs (
    id INTEGER PRIMARY KEY,
    timestamp DATETIME,
    job_id INTEGER,
    action VARCHAR(100),
    details TEXT,
    success BOOLEAN
);
```

**Job States**:
- `NEW` - Initial state after ingestion
- `CUTTING` - Clip extraction in progress
- `FORMATTING` - Converting to 9:16 format
- `CAPTIONING` - Generating/burning captions
- `METADATA` - Creating title/description/hashtags
- `RENDERING` - Final export
- `READY_FOR_REVIEW` - Awaiting human approval
- `APPROVED` - Approved for upload
- `REJECTED` - Rejected by reviewer
- `UPLOADING` - Upload in progress
- `PUBLISHED` - Successfully published
- `FAILED` - Processing failed

### 3. Worker System

**Purpose**: Isolated, resumable processing units

**Base Class** (`shortsfactory/workers/base.py`):
- Defines worker interface
- Handles retry logic
- Manages state transitions
- Provides failure handling

**Worker Implementations**:

#### CuttingWorker (`shortsfactory/workers/cutting.py`)
- **Input State**: NEW
- **Output State**: CUTTING → FORMATTING
- **Purpose**: Extract clips from long videos
- **Process**:
  1. Load source video
  2. Determine optimal clip duration (15-60 seconds)
  3. Extract segment (currently from middle, could use AI)
  4. Save to `storage/intermediate`

#### FormattingWorker (`shortsfactory/workers/formatting.py`)
- **Input State**: CUTTING
- **Output State**: FORMATTING → CAPTIONING
- **Purpose**: Convert to 9:16 vertical format
- **Process**:
  1. Load cut video
  2. Scale to target resolution (1080x1920)
  3. Crop/pad to exact dimensions
  4. Maintain quality with proper bitrate
  5. Save formatted version

#### CaptionWorker (`shortsfactory/workers/caption.py`)
- **Input State**: FORMATTING
- **Output State**: CAPTIONING → METADATA
- **Purpose**: Generate and burn captions
- **Process**:
  1. Generate caption text (placeholder for Whisper integration)
  2. Save caption data as JSON
  3. In production: burn captions using TextClip
  4. Currently: passes through for MVP

#### MetadataWorker (`shortsfactory/workers/metadata.py`)
- **Input State**: CAPTIONING
- **Output State**: METADATA → RENDERING
- **Purpose**: Generate titles, descriptions, hashtags
- **Process**:
  1. Generate engaging title (max 100 chars)
  2. Create description with call-to-action
  3. Select relevant hashtags with randomization
  4. Save metadata as JSON
  5. Update job record

#### RenderingWorker (`shortsfactory/workers/rendering.py`)
- **Input State**: METADATA
- **Output State**: RENDERING → READY_FOR_REVIEW
- **Purpose**: Create final export
- **Process**:
  1. Finalize video file
  2. Copy to `storage/finals`
  3. Mark as ready for review
  4. Set progress to 100%

#### UploadWorker (`shortsfactory/workers/upload.py`)
- **Input State**: APPROVED
- **Output State**: UPLOADING → PUBLISHED
- **Purpose**: Upload to YouTube with safety limits
- **Features**:
  - Rate limiting (configurable max per day)
  - Minimum delay between uploads
  - Randomized timing for natural behavior
  - Retry logic for transient failures
  - Currently stub implementation (safety)

**Worker Manager** (`shortsfactory/workers/manager.py`):
- Starts all workers in separate threads
- Handles graceful shutdown on SIGINT/SIGTERM
- Ensures workers stop cleanly

### 4. Review System (`shortsfactory/dashboard/app.py`)

**Purpose**: Human-in-the-loop quality control

**Features**:
- Video preview in browser
- Display metadata (title, description, hashtags)
- Three actions:
  - ✅ **Approve** - Queue for upload
  - ❌ **Reject** - Mark as rejected
  - 🔄 **Reprocess** - Send back to start
- Review notes for documentation
- Enforces: **Nothing uploads without approval**

**Access**: http://localhost:8501 (Streamlit)

### 5. Dashboard (`shortsfactory/dashboard/app.py`)

**Purpose**: System observability and control

**Pages**:

1. **Overview**
   - Total jobs count
   - Jobs by state breakdown
   - Recent activity log
   - System metrics

2. **Job Queue**
   - Filter by state
   - View job details
   - Track progress
   - See errors

3. **Review Queue**
   - Preview videos
   - Approve/reject/reprocess
   - Add review notes
   - **Main quality control interface**

4. **Published**
   - View published videos
   - See video IDs and URLs
   - Track publish dates

5. **Failed Jobs**
   - View failure reasons
   - Retry failed jobs
   - Debug information

6. **Logs**
   - Activity log viewer
   - Filter by job
   - Audit trail

7. **Settings**
   - View current configuration
   - Configuration reference
   - Instructions to modify

### 6. Configuration System (`shortsfactory/core/config.py`)

**File**: `config/settings.yaml`

**Configuration Sections**:

```yaml
inbox:
  long_videos: "INBOX/long_videos"
  clips: "INBOX/clips"
  ideas: "INBOX/ideas.txt"
  watch_interval: 5  # seconds

storage:
  originals: "storage/originals"
  intermediate: "storage/intermediate"
  finals: "storage/finals"
  captions: "storage/captions"
  metadata: "storage/metadata"

video:
  target_width: 1080
  target_height: 1920
  fps: 30
  max_duration: 60
  min_duration: 15
  video_codec: "libx264"
  audio_codec: "aac"
  bitrate: "8M"

caption:
  font_size: 48
  font_color: "white"
  bg_color: "black"
  bg_opacity: 0.7
  position: "bottom"
  max_words_per_line: 6

upload:
  enabled: false  # Must be explicitly enabled
  min_delay_minutes: 60
  max_delay_minutes: 180
  max_per_day: 5
  privacy_status: "private"
  category_id: "22"
  made_for_kids: false

worker:
  max_retries: 3
  retry_delay: 60
  timeout: 600
  parallel_workers: 1

dashboard:
  host: "localhost"
  port: 8501
  title: "ShortsFactory Dashboard"
```

### 7. Logging System (`shortsfactory/core/logger.py`)

**Purpose**: Comprehensive audit trail

**Features**:
- Console output with colors
- File logging (main log + daily log)
- Structured logging with context
- Job-specific events
- Worker-specific events
- Exception tracking with stack traces

**Log Locations**:
- `logs/shortsfactory.log` - Main log file
- `logs/shortsfactory_YYYY-MM-DD.log` - Daily log files

### 8. Storage Organization

```
storage/
├── originals/       # Backup of uploaded files
├── intermediate/    # Work-in-progress files
│   ├── job_1_cut.mp4
│   └── job_1_formatted.mp4
├── finals/          # Final exported videos
│   └── job_1_final.mp4
├── captions/        # Caption data (JSON)
│   └── job_1_captions.json
└── metadata/        # Metadata (JSON)
    └── job_1_metadata.json
```

## Data Flow

```
[User drops file in INBOX]
           ↓
[InboxWatcher detects file]
           ↓
[Job created with state=NEW]
           ↓
[CuttingWorker] → state=FORMATTING
           ↓
[FormattingWorker] → state=CAPTIONING
           ↓
[CaptionWorker] → state=METADATA
           ↓
[MetadataWorker] → state=RENDERING
           ↓
[RenderingWorker] → state=READY_FOR_REVIEW
           ↓
[Human reviews in Dashboard]
           ↓
     [Approve/Reject/Reprocess]
           ↓
[If approved: state=APPROVED]
           ↓
[UploadWorker] → state=PUBLISHED
           ↓
[Video live on YouTube]
```

## Safety Features

1. **Review Gate**: Nothing uploads without explicit approval
2. **Rate Limiting**: Configurable upload limits per day
3. **Randomized Timing**: Natural posting patterns
4. **Retry Logic**: Graceful handling of transient failures
5. **Full Audit Trail**: Every action logged with timestamp
6. **Crash Recovery**: Jobs resume from last known state
7. **Graceful Shutdown**: Clean stop on CTRL+C
8. **No Hidden Operations**: Everything is observable

## Scalability Design

### Current (Single PC)
- All components run locally
- SQLite database
- Single worker threads
- File-based storage

### Future Scaling Options

1. **Multiple Channels**
   - Add channel ID to job records
   - Channel-specific templates
   - Separate upload credentials

2. **Distributed Workers**
   - Replace SQLite with PostgreSQL
   - Workers on separate machines
   - Shared network storage or S3

3. **Analytics Integration**
   - Collect performance metrics
   - Feed back into metadata generation
   - A/B testing support

4. **Advanced AI**
   - Better clip selection (hook detection)
   - Real caption generation (Whisper)
   - AI-powered metadata optimization

## Extension Points

### Adding a New Worker
1. Extend `Worker` base class
2. Implement required methods
3. Add to `WorkerManager`
4. Add new state to `JobState` enum

### Adding Analytics
1. Create analytics collector worker
2. Store metrics in database
3. Add dashboard page for metrics
4. Feed data back to metadata worker

### Multi-Channel Support
1. Add `channel_id` to Job model
2. Create channel configuration system
3. Update upload worker for multiple credentials
4. Add channel selector in dashboard

## Security Considerations

1. **Credentials**: Store YouTube API credentials securely
2. **Privacy**: All data stays local by default
3. **Permissions**: Explicit user consent required
4. **Transparency**: Open source, auditable code
5. **Compliance**: Respects platform terms of service

## Deployment

### Development Mode
```bash
python -m shortsfactory.main all
```

### Production Mode
Run components separately:
```bash
# Terminal 1: Watcher
python -m shortsfactory.watcher

# Terminal 2: Workers
python -m shortsfactory.workers.manager

# Terminal 3: Dashboard
python -m shortsfactory.dashboard.app
```

### System Service
Use systemd (Linux) or Task Scheduler (Windows) to run as background services.

## Maintenance

### Backup Strategy
- Database: Regular SQLite backups
- Storage: External backup of finals/
- Config: Version control settings.yaml

### Monitoring
- Check logs/ directory regularly
- Review failed jobs in dashboard
- Monitor upload success rate

### Cleanup
- Periodically archive old intermediate files
- Maintain finals/ as permanent archive
- Clean up logs older than 30 days

## License and Usage

This system is designed for:
- Personal content creation
- Small business automation
- Educational purposes
- Compliant commercial use

NOT designed for:
- Spam or abuse
- Terms of service violations
- Malicious activity
- Hidden/stealth operations

All operations must be transparent and authorized.
