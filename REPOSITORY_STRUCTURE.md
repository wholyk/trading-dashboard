# Repository Structure

This document explains the purpose of each directory and file in the repository.

## Root Directory

```
.
├── .github/              # GitHub-specific files
├── config/               # Configuration files
├── data/                 # Runtime data (gitignored)
├── src/                  # Source code
├── templates/            # Content templates
├── ARCHITECTURE.md       # Technical system design
├── FAILURE_POINTS.md     # Failure modes and prevention
├── MONETIZATION.md       # Revenue strategy
├── README.md             # Main documentation
├── SCALING.md            # Scaling strategy (1x → 10x)
├── requirements.txt      # Python dependencies
└── streamlit_app.py      # Legacy file (unused)
```

## .github/

GitHub Actions workflows and configuration.

```
.github/
└── workflows/
    ├── viral_detection.yml       # Scans YouTube for viral patterns (every 6h)
    ├── content_generation.yml    # Generates videos from approved ideas
    ├── upload_automation.yml     # Uploads videos to YouTube
    └── performance_analysis.yml  # Tracks performance and optimizes
```

### Workflow Triggers

| Workflow | Trigger | Frequency |
|----------|---------|-----------|
| viral_detection | Cron | Every 6 hours |
| content_generation | Dispatch | On approved ideas |
| upload_automation | Dispatch | After generation |
| performance_analysis | Cron | Daily at midnight |

## config/

System configuration files.

```
config/
├── system_config.yaml       # Main system configuration
├── blacklist.yaml          # Blacklisted patterns/keywords
└── secrets.example.yaml    # Example secrets file (NOT for actual secrets)
```

### Configuration Files

**system_config.yaml** - Controls all system behavior:
- Detection settings (niche, keywords, thresholds)
- Scoring weights and rejection threshold
- Generation parameters (models, quality settings)
- Monetization configuration
- Scaling factor (1x, 3x, or 10x)
- Cost controls and limits

**blacklist.yaml** - Rejection rules:
- Patterns to avoid
- Keywords to filter out
- Compliance rules

**secrets.example.yaml** - Template for secrets:
- Shows required API keys
- Not used in production (GitHub Secrets used instead)

## data/

Runtime data storage (all files gitignored).

```
data/
├── rejected/              # Rejected ideas with reasons
├── failed_qa/             # Videos that failed quality checks
├── videos/                # Generated videos (temporary)
├── metrics/               # Performance metrics
├── logs/                  # System logs
├── patterns_detected.json # Detected viral patterns
├── ideas_generated.json   # Raw ideas before scoring
├── ideas_scored.json      # Scored ideas
├── idea_queue.json        # Approved ideas ready for production
├── idea_history.json      # Historical ideas (for duplicate detection)
├── quota_state.json       # YouTube API quota tracking
└── published_videos.json  # Published video metadata
```

### Data Flow Through Files

1. **viral_detector.py** → `patterns_detected.json`, `ideas_generated.json`
2. **idea_scorer.py** → `ideas_scored.json`
3. **rejection_gate.py** → `idea_queue.json`, `rejected/rejected_ideas.json`
4. **content_generation** → `videos/*.mp4`, `failed_qa/` (if validation fails)
5. **youtube_uploader.py** → `published_videos.json`
6. **performance_tracker.py** → `metrics/video_performance.json`

## src/

Source code organized by function.

```
src/
├── detection/           # Viral pattern detection and scoring
│   ├── viral_detector.py
│   ├── idea_scorer.py
│   └── rejection_gate.py
├── generation/          # Content creation pipeline
│   ├── script_generator.py
│   ├── visual_generator.py
│   ├── caption_generator.py
│   └── quality_validator.py
├── publication/         # YouTube upload automation
│   └── youtube_uploader.py
├── learning/            # Performance tracking and optimization
│   ├── performance_tracker.py
│   ├── winner_identifier.py
│   └── auto_optimizer.py
└── utils/               # Shared utilities
    ├── check_quota.py
    └── cost_tracker.py
```

### Module Descriptions

#### Detection Modules

**viral_detector.py**
- Scans YouTube for top Shorts in niche
- Extracts patterns (hooks, topics, styles)
- Generates content ideas
- **Input:** YouTube API, system config
- **Output:** `patterns_detected.json`, `ideas_generated.json`

**idea_scorer.py**
- Scores ideas 0-100 using weighted algorithm
- Considers: frequency, recency, engagement, competition, audience fit
- **Input:** `ideas_generated.json`, system config
- **Output:** `ideas_scored.json`

**rejection_gate.py**
- Applies strict filtering rules
- Rejects ideas below threshold (no override)
- Checks for duplicates, blacklist, minimum requirements
- **Input:** `ideas_scored.json`, blacklist config
- **Output:** `idea_queue.json`, `rejected/rejected_ideas.json`

#### Generation Modules

**script_generator.py**
- Generates video script from idea using GPT-4
- Includes hooks, main content, CTA
- Validates script structure
- **Input:** Idea from queue
- **Output:** Script JSON

**visual_generator.py**
- Creates video from script
- Sources images/clips from Pexels
- Adds text overlays with FFmpeg
- Renders 9:16 video
- **Input:** Script JSON
- **Output:** MP4 video file

**caption_generator.py**
- Generates title, description, tags
- SEO optimization
- Hashtag selection
- **Input:** Script, video file
- **Output:** Metadata JSON

**quality_validator.py**
- Validates video meets standards
- Checks: duration, resolution, audio, copyright
- Auto-fixes when possible
- **Input:** Video file, metadata
- **Output:** Pass/fail status, quality report

#### Publication Modules

**youtube_uploader.py**
- Uploads video to YouTube via API
- Resumable upload (handles interruptions)
- Sets metadata (title, description, privacy)
- **Input:** Video file, metadata JSON
- **Output:** Video ID, upload status

#### Learning Modules

**performance_tracker.py**
- Fetches analytics for published videos
- Tracks views, CTR, retention, RPM
- **Input:** Published video IDs
- **Output:** `metrics/video_performance.json`

**winner_identifier.py**
- Identifies top-performing videos (top 20%)
- Compares against channel baselines
- **Input:** Performance metrics
- **Output:** `metrics/winners.json`

**auto_optimizer.py**
- Adjusts pattern weights based on performance
- Doubles down on winners (weight × 2)
- Penalizes losers (weight × 0.5)
- **Input:** Winners, losers
- **Output:** Updated pattern weights

#### Utility Modules

**check_quota.py**
- Checks YouTube API quota availability
- Prevents quota exhaustion
- **Input:** Operation type, count
- **Output:** Pass/fail (exit code)

**cost_tracker.py**
- Tracks API costs per operation
- Monitors against budget
- **Input:** Operation type, count
- **Output:** Updated cost state

## templates/

Content templates for consistency.

```
templates/
├── scripts/            # Winning script templates
│   └── (template files)
└── prompts/            # GPT-4 prompt templates
    └── (prompt files)
```

### Template Usage

- **Script templates:** Pre-proven structures that work
- **Prompt templates:** Optimized prompts for GPT-4
- Templates ensure consistency and quality

## Documentation Files

### ARCHITECTURE.md (24KB)
Complete technical architecture:
- System diagram
- Data flow
- Component details
- API integration
- Enforcement mechanisms
- Configuration management

### README.md (9KB)
User-facing documentation:
- What the system does
- Setup instructions
- How to configure
- Monitoring and troubleshooting
- Cost estimation

### SCALING.md (11KB)
Scaling strategy:
- Phases: 1x → 3x → 10x
- Parallelization architecture
- Resource management
- Performance maintenance
- Decision tree for scaling

### MONETIZATION.md (13KB)
Revenue optimization:
- Revenue streams (ads, affiliates, funnel, sponsors)
- RPM optimization
- Niche selection
- Cost vs revenue analysis
- Automated reporting

### FAILURE_POINTS.md (23KB)
Failure modes and prevention:
- 16 identified failure points
- Detection methods
- Enforcement mechanisms
- Auto-recovery procedures
- Alert escalation

## Dependencies (requirements.txt)

### API Clients
- `google-api-python-client` - YouTube API
- `google-auth` - OAuth authentication
- `openai` - GPT-4 for script generation

### Video Processing
- `ffmpeg-python` - Video rendering (requires FFmpeg binary)

### Data Handling
- `pandas` - Data analysis
- `numpy` - Numerical operations
- `pyyaml` - Configuration parsing

### Utilities
- `requests` - HTTP requests (Pexels API)
- `tenacity` - Retry logic

## System Initialization

### First-Time Setup

1. **Configure secrets in GitHub:**
   - `YOUTUBE_CLIENT_ID`
   - `YOUTUBE_CLIENT_SECRET`
   - `YOUTUBE_REFRESH_TOKEN`
   - `OPENAI_API_KEY`
   - `PEXELS_API_KEY`

2. **Configure system:**
   - Edit `config/system_config.yaml`
   - Set niche, keywords, thresholds

3. **Enable workflows:**
   - Go to Actions tab
   - Enable workflows

4. **Manual trigger first run:**
   - Trigger `viral_detection.yml`
   - System runs autonomously thereafter

### Daily Operations

**Automated (no human intervention):**
- Viral pattern detection (every 6 hours)
- Content generation (on approved ideas)
- Video upload (after generation)
- Performance analysis (daily)
- Auto-optimization (based on performance)

**Human monitoring (weekly):**
- Review GitHub Actions runs
- Check performance metrics
- Review rejected ideas (optional)
- Spot-check video quality (optional)

**Human intervention (as needed):**
- Update niche configuration
- Adjust thresholds
- Handle critical alerts (auth failures, etc.)
- Scale factor changes (1x → 3x → 10x)

## File Permissions

All Python files are executable (`chmod +x`):
- Allows direct execution: `./src/detection/viral_detector.py`
- Used by GitHub Actions runners

## Gitignore

**Ignored directories:**
- `data/` (all runtime data)
- `.venv/` (Python virtual environment)
- `__pycache__/` (Python cache)
- `/tmp/` (temporary files)

**Ignored files:**
- `*.pyc`, `*.pyo` (Python bytecode)
- `secrets.yaml` (actual secrets)
- `*.log` (log files)
- `.env` (environment variables)

**Tracked:**
- All source code
- Configuration templates
- Documentation
- Workflow definitions
- `data/.gitkeep` (ensures directory exists)

## Version Control

**Branch strategy:**
- `main` - Production system
- `copilot/*` - Development branches
- Pull requests required for changes

**Commit messages:**
- Descriptive and actionable
- Reference issue numbers when applicable

## Security

**Secrets management:**
- Never commit secrets to repository
- Use GitHub Secrets exclusively
- `secrets.example.yaml` is template only

**API credentials:**
- OAuth refresh tokens (auto-renewing)
- API keys rotated periodically
- Least-privilege access

**Content safety:**
- Blacklist enforcement
- Copyright detection
- Community guidelines compliance

---

**This repository structure enables fully automated, scalable, and maintainable YouTube Shorts production with minimal human intervention.**
