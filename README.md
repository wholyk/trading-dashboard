# ShortsFactory

A business-grade, local, permissioned automation system for YouTube Shorts production.

## Overview

ShortsFactory is an end-to-end YouTube Shorts production system that automatically ingests content, processes it, enforces quality control, and publishes approved Shorts — reliably, safely, and repeatably.

## Features

- **Automated Ingestion**: Watched folders for videos, clips, and ideas
- **Job Queue Management**: SQLite-based state machine with full lifecycle tracking
- **Worker Pipeline**: Modular workers for cutting, formatting, captioning, metadata, and rendering
- **Quality Control**: Local review interface with approval gates
- **Safe Publishing**: Rate-limited uploads with retry logic and duplicate protection
- **Full Observability**: Dashboard showing queue status, jobs, and history
- **Crash-Safe**: All jobs are resumable after crashes or restarts
- **Audit Trail**: Complete logging of all actions with timestamps

## Architecture

```
ShortsFactory/
├── INBOX/                  # Input folders (watched)
│   ├── long_videos/
│   ├── clips/
│   └── ideas.txt
├── storage/                # Persistent storage
│   ├── originals/
│   ├── intermediate/
│   ├── finals/
│   └── captions/
├── logs/                   # Audit trail
├── database/               # SQLite database
├── workers/                # Processing workers
├── dashboard/              # Web UI
└── config/                 # Configuration
```

## Job Lifecycle States

- `NEW` - Job created, pending processing
- `CUTTING` - Clip selection in progress
- `FORMATTING` - Converting to 9:16 format
- `CAPTIONING` - Adding captions
- `METADATA` - Generating title/description/hashtags
- `RENDERING` - Final export
- `READY_FOR_REVIEW` - Awaiting human approval
- `APPROVED` - Approved for upload
- `REJECTED` - Rejected by reviewer
- `UPLOADING` - Upload in progress
- `PUBLISHED` - Successfully published
- `FAILED` - Processing failed (with reason)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd trading-dashboard
```

2. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Initialize the system:
```bash
python -m shortsfactory.init
```

## Usage

### Starting the System

1. Start the ingestion watcher:
```bash
python -m shortsfactory.watcher
```

2. Start the worker processes:
```bash
python -m shortsfactory.workers
```

3. Start the dashboard:
```bash
python -m shortsfactory.dashboard
```

4. Access the dashboard at `http://localhost:8501`

### Adding Content

1. Place video files in `INBOX/long_videos/` or `INBOX/clips/`
2. Add text ideas to `INBOX/ideas.txt`
3. The system will automatically create jobs and begin processing

### Reviewing Content

1. Open the dashboard at `http://localhost:8501`
2. Navigate to "Review Queue"
3. Preview videos, approve or reject
4. Approved videos will be queued for upload

### Monitoring

- View queue status in the dashboard
- Check logs in the `logs/` directory
- Review job details in the database

## Configuration

Edit `config/settings.yaml` to customize:
- Upload schedule and throttling
- Worker behavior
- Video processing parameters
- Channel settings

## Safety Features

- **Explicit Permission**: All operations require user authorization
- **Review Gate**: Nothing uploads without manual approval
- **Rate Limiting**: Respects platform limits with randomized timing
- **Graceful Shutdown**: Clean shutdown on CTRL+C
- **Full Audit Trail**: Every action is logged
- **Crash Recovery**: Jobs resume from last known state

## Extending the System

### Adding a New Worker

1. Create a new worker in `workers/`
2. Implement the `Worker` base class
3. Register it in the worker manager
4. Add corresponding state to the state machine

### Adding Channel Support

1. Add channel configuration in `config/settings.yaml`
2. Create channel-specific templates
3. Configure upload credentials per channel

### Analytics Integration

The system is designed to support analytics feedback loops:
- Add analytics data collection in the upload module
- Create analytics workers for processing feedback
- Adjust metadata generation based on performance

## Uninstalling

1. Stop all running processes (CTRL+C)
2. Remove the virtual environment: `rm -rf .venv`
3. Remove the project directory
4. No system-wide changes are made

## Safety and Compliance

This system:
- Runs locally with explicit user permission
- Does NOT bypass any security measures
- Does NOT hide or obfuscate its operation
- Does NOT self-persist without consent
- Respects platform terms of service
- Includes safety throttles and randomization

## License

See LICENSE file for details.

## Support

For issues, questions, or feature requests, please open an issue on GitHub.
