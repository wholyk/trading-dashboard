# ShortsFactory Quick Start Guide

## Installation

1. **Clone and navigate to the repository:**
   ```bash
   cd trading-dashboard
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize the system:**
   ```bash
   python -m shortsfactory.init
   ```

## Quick Start (All-in-One)

Run all components together (best for testing):

```bash
python -m shortsfactory.main all
```

This starts:
- Inbox watcher (monitors for new files)
- Worker processes (processes videos)
- Dashboard (http://localhost:8501)

Press `CTRL+C` to stop all components.

## Running Components Separately

For production use, run each component in its own terminal:

### Terminal 1: Inbox Watcher
```bash
python -m shortsfactory.watcher
```
Monitors INBOX folders for new content.

### Terminal 2: Workers
```bash
python -m shortsfactory.workers.manager
```
Processes videos through the pipeline.

### Terminal 3: Dashboard
```bash
python -m shortsfactory.dashboard.app
# Or using streamlit directly:
streamlit run shortsfactory/dashboard/app.py
```
Open http://localhost:8501 in your browser.

## Adding Content

### Option 1: Video Files
1. Drop video files into:
   - `INBOX/long_videos/` - For full-length videos (clips will be extracted)
   - `INBOX/clips/` - For pre-cut video clips
2. System automatically creates jobs and begins processing

### Option 2: Text Ideas
1. Open `INBOX/ideas.txt`
2. Add your ideas, one per line:
   ```
   Amazing life hack for productivity
   Top 5 travel destinations in 2024
   Quick recipe for busy people
   ```
3. System detects changes and creates jobs

## Monitoring Progress

### Dashboard (Recommended)
1. Open http://localhost:8501
2. Navigate through pages:
   - **Overview**: System statistics and recent activity
   - **Job Queue**: View all jobs and their states
   - **Review Queue**: Approve/reject videos (required!)
   - **Published**: See published videos
   - **Failed Jobs**: Debug errors
   - **Logs**: Activity audit trail
   - **Settings**: View configuration

### Command Line
Check logs in real-time:
```bash
tail -f logs/shortsfactory.log
```

## Reviewing and Approving Content

**IMPORTANT**: Nothing uploads without your approval!

1. Go to **Review Queue** in dashboard
2. Watch video preview
3. Review metadata (title, description, hashtags)
4. Choose action:
   - **✅ Approve**: Queue for upload
   - **❌ Reject**: Mark as rejected
   - **🔄 Reprocess**: Send back to start

## Enabling Uploads

By default, uploads are **disabled** for safety.

To enable:
1. Edit `config/settings.yaml`
2. Set `upload.enabled: true`
3. Configure YouTube API credentials (see below)
4. Restart workers

### YouTube API Setup (Required for Real Uploads)

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project
3. Enable YouTube Data API v3
4. Create OAuth 2.0 credentials
5. Download credentials as `config/credentials.json`
6. First upload will open browser for authorization
7. Token saved to `config/token.json` for future use

## Configuration

Edit `config/settings.yaml` to customize:

```yaml
video:
  target_width: 1080      # 9:16 aspect ratio
  target_height: 1920
  max_duration: 60        # seconds
  min_duration: 15

upload:
  enabled: false          # SET TO true TO ENABLE
  max_per_day: 5          # Daily upload limit
  min_delay_minutes: 60   # Minimum time between uploads
  privacy_status: private # private/unlisted/public

worker:
  max_retries: 3          # Retry failed jobs
  retry_delay: 60         # Seconds between retries
```

## Troubleshooting

### "No module named 'shortsfactory'"
- Make sure you're in the project directory
- Virtual environment is activated
- Dependencies are installed: `pip install -r requirements.txt`

### Workers not processing jobs
- Check `logs/shortsfactory.log` for errors
- Verify video files are valid formats (.mp4, .mov, .avi, etc.)
- Check Dashboard → Failed Jobs for error details

### Dashboard not loading
- Check if port 8501 is available
- Try: `lsof -i :8501` (Linux/Mac) or `netstat -ano | findstr :8501` (Windows)
- Change port in `config/settings.yaml` if needed

### Videos stuck in Review Queue
- This is expected! Manual approval is required
- Go to Dashboard → Review Queue
- Approve videos to proceed with upload

### Upload not working
- Verify `upload.enabled: true` in config
- Check YouTube API credentials are configured
- Review upload worker logs for errors
- Ensure rate limits not exceeded

## Safety Features

✅ **Review Gate**: All videos require manual approval  
✅ **Rate Limiting**: Respects platform limits  
✅ **Audit Trail**: Every action logged with timestamp  
✅ **Crash Recovery**: Jobs resume after restart  
✅ **Graceful Shutdown**: Clean stop with CTRL+C  

## File Organization

```
INBOX/                      # Drop files here
├── long_videos/            # Full videos (auto-extract clips)
├── clips/                  # Pre-cut clips
└── ideas.txt               # Text ideas

storage/                    # Automated storage
├── originals/              # Backup of source files
├── intermediate/           # Work-in-progress
├── finals/                 # Ready for upload
├── captions/               # Caption data
└── metadata/               # Title/description/hashtags

logs/                       # System logs
├── shortsfactory.log       # Main log
└── shortsfactory_*.log     # Daily logs

database/                   # SQLite database
└── shortsfactory.db        # Job queue

config/                     # Configuration
├── settings.yaml           # User settings
├── credentials.json        # YouTube API (not included)
└── token.json              # OAuth token (auto-generated)
```

## Stopping the System

### If running with "all" command:
Press `CTRL+C` once - all components stop gracefully

### If running separately:
Press `CTRL+C` in each terminal window

### Force stop if needed:
```bash
# Find processes
ps aux | grep shortsfactory

# Kill by PID
kill <PID>
```

## Uninstalling

1. Stop all running processes
2. Deactivate virtual environment: `deactivate`
3. Remove the project directory
4. No system-wide changes were made

## Getting Help

- Check `README.md` for overview
- Read `ARCHITECTURE.md` for technical details
- Review logs in `logs/` directory
- Check Dashboard → Logs page for activity

## Next Steps

1. ✅ Initialize and test with sample videos
2. ✅ Review the processing pipeline in Dashboard
3. ✅ Configure settings to your preferences
4. ✅ Set up YouTube API credentials (if uploading)
5. ✅ Enable uploads when ready
6. ✅ Monitor and approve content regularly

## Tips

- Start small: Test with 1-2 videos first
- Review settings before enabling uploads
- Monitor the first few uploads closely
- Keep originals backed up separately
- Check logs regularly for issues
- Adjust rate limits based on your needs

---

**Remember**: This system gives you full control. Nothing happens without your knowledge and approval. All operations are logged and can be audited at any time.
