# YouTube Shorts Automation System

A fully automated GitHub-based system that detects viral patterns, generates content, publishes to YouTube, and optimizes based on performance—all without human intervention.

## What This System Does

1. **Detects Viral Patterns:** Scans YouTube Shorts every 6 hours to identify what's working in your niche
2. **Scores Ideas:** Assigns confidence scores (0-100) to content ideas
3. **Rejects Bad Ideas:** Only produces content scoring ≥75 (no human override)
4. **Generates Content:** Creates script → visuals → captions → metadata automatically
5. **Publishes:** Uploads to YouTube via API (6 videos/day)
6. **Learns:** Tracks performance, doubles down on winners, penalizes losers
7. **Scales:** Goes from 1x to 10x output via parallelization without quality loss

## Repository Structure

```
.
├── .github/
│   └── workflows/              # GitHub Actions automation
│       ├── viral_detection.yml
│       ├── content_generation.yml
│       ├── upload_automation.yml
│       ├── performance_analysis.yml
│       └── scaling_orchestrator.yml
├── src/
│   ├── detection/              # Viral pattern detection & scoring
│   │   ├── viral_detector.py
│   │   ├── idea_scorer.py
│   │   └── rejection_gate.py
│   ├── generation/             # Content creation pipeline
│   │   ├── script_generator.py
│   │   ├── visual_generator.py
│   │   ├── caption_generator.py
│   │   └── quality_validator.py
│   ├── publication/            # YouTube upload automation
│   │   └── youtube_uploader.py
│   ├── learning/               # Performance tracking & optimization
│   │   ├── performance_tracker.py
│   │   └── auto_optimizer.py
│   └── utils/                  # Shared utilities
│       ├── youtube_api.py
│       ├── cost_tracker.py
│       └── logger.py
├── config/
│   ├── system_config.yaml      # Main system configuration
│   ├── niche_config.yaml       # Niche-specific settings
│   └── secrets.example.yaml    # Example secrets file
├── templates/
│   ├── scripts/                # Winning script templates
│   └── prompts/                # GPT-4 prompt templates
├── data/                       # Gitignored data storage
│   ├── rejected/               # Rejected ideas with reasons
│   ├── failed_qa/              # Videos that failed quality checks
│   ├── videos/                 # Generated videos (temporary)
│   └── metrics/                # Performance metrics
├── ARCHITECTURE.md             # Technical system design
├── SCALING.md                  # How to scale 1x → 10x
├── MONETIZATION.md             # Revenue optimization strategy
└── FAILURE_POINTS.md           # Failure modes and prevention
```

## Prerequisites

1. **GitHub Account** with Actions enabled
2. **YouTube Channel** with API access enabled
3. **API Keys:**
   - YouTube Data API v3 (OAuth 2.0 credentials)
   - OpenAI API (GPT-4 access)
   - Pexels API (free tier)

## Setup Instructions

### Step 1: Fork and Clone

```bash
# Note: Repository name is "trading-dashboard" but contains YouTube Shorts automation system
git clone https://github.com/YOUR_USERNAME/trading-dashboard.git
cd trading-dashboard
```

### Step 2: Configure GitHub Secrets

Go to Settings → Secrets and Variables → Actions, add:

| Secret Name | Description | How to Get |
|------------|-------------|------------|
| `YOUTUBE_CLIENT_ID` | YouTube OAuth client ID | [Google Cloud Console](https://console.cloud.google.com/) |
| `YOUTUBE_CLIENT_SECRET` | YouTube OAuth client secret | Same as above |
| `YOUTUBE_REFRESH_TOKEN` | OAuth refresh token | Run `python src/utils/oauth_setup.py` |
| `OPENAI_API_KEY` | OpenAI API key | [OpenAI Platform](https://platform.openai.com/) |
| `PEXELS_API_KEY` | Pexels API key | [Pexels API](https://www.pexels.com/api/) |

### Step 3: Configure Your Niche

Edit `config/system_config.yaml`:

```yaml
detection:
  niche: "personal_finance"  # Change to your niche
  keywords:
    - "money tips"
    - "finance hacks"
    - "passive income"
```

See `config/niche_config.yaml` for niche-specific presets.

### Step 4: Enable GitHub Actions

1. Go to Actions tab in your repo
2. Click "I understand my workflows, go ahead and enable them"
3. Manually trigger "Viral Detection" workflow to start the system

### Step 5: Verify Setup

Check the Actions tab for workflow runs. First run should:
- ✅ Detect viral patterns
- ✅ Score at least one idea above threshold
- ✅ Generate a video
- ✅ Pass quality validation
- ✅ Upload to YouTube (if credentials correct)

## How It Works

### Automated Cycle (Every 6 Hours)

```
1. Viral Detection (6h)
   └─> Scans top YouTube Shorts
   └─> Identifies patterns
   └─> Scores ideas

2. Rejection Gate
   └─> Score < 75? REJECT
   └─> Score ≥ 75? PROCEED

3. Content Generation (parallel)
   └─> Script from GPT-4
   └─> Visuals from Pexels + FFmpeg
   └─> Captions with SEO

4. Quality Validation
   └─> Duration check
   └─> Resolution check
   └─> Audio check
   └─> Pass? UPLOAD

5. Publication
   └─> Upload to YouTube
   └─> Store video ID

6. Performance Learning (24h later)
   └─> Fetch analytics
   └─> Identify winners
   └─> Adjust pattern weights
```

### Scaling Strategy

Start at 1x, scale when ready:

```bash
# Scale to 3x (3 videos per cycle)
# Edit config/system_config.yaml
generation:
  parallel_jobs: 3

# Scale to 10x (10 videos per cycle)
generation:
  parallel_jobs: 10
```

System automatically parallelizes via GitHub Actions matrix strategy.

## Monitoring

### Dashboard
Visit Actions tab to see:
- Workflow runs (success/failure)
- Logs for each step
- Artifacts (videos, reports)

### Metrics
Performance metrics stored in `data/metrics/`:
- `daily_stats.json` - Daily production metrics
- `video_performance.json` - Per-video analytics
- `cost_tracking.json` - API costs

### Alerts
System creates GitHub Issues for:
- API quota warnings (80% usage)
- Quality validation failures
- OAuth token expiration (7 days notice)
- RPM drop (>50% decrease)

## Troubleshooting

### No Ideas Passing Gate
**Symptom:** Rejection gate blocks all ideas

**Solution:** 
- Lower threshold in `config/system_config.yaml` (try 70)
- Check if niche is too competitive
- Verify YouTube API is returning results

### Upload Failures
**Symptom:** Videos generate but don't upload

**Solution:**
- Check YouTube OAuth credentials
- Verify API quota not exceeded
- Check video meets YouTube requirements (duration, size)

### Quality Validation Fails
**Symptom:** Videos fail quality checks

**Solution:**
- Check FFmpeg installation in workflow
- Verify Pexels API returns valid images
- Review `data/failed_qa/` for specific errors

### High Costs
**Symptom:** API costs exceed budget

**Solution:**
- Reduce `parallel_jobs` to 1
- Increase detection frequency to 12 hours
- Use lower-cost GPT model (gpt-3.5-turbo)

## Cost Estimation

### At 1x Scale (1 video per 6 hours = 4 videos/day)

| Service | Usage | Cost/Month |
|---------|-------|-----------|
| OpenAI API | 120 scripts | $6 |
| Pexels API | Free | $0 |
| YouTube API | Free | $0 |
| GitHub Actions | ~500 min/month | Free (2000 min free) |
| **Total** | | **$6/month** |

### At 10x Scale (10 videos per 6 hours = 40 videos/day)

| Service | Usage | Cost/Month |
|---------|-------|-----------|
| OpenAI API | 1200 scripts | $60 |
| Pexels API | Need paid tier | $20 |
| YouTube API | Free (within quota) | $0 |
| GitHub Actions | ~5000 min/month | $8 (3000 min overage) |
| **Total** | | **$88/month** |

## Monetization (Once Eligible)

YouTube Shorts monetization requires:
- 1,000 subscribers
- 10 million Shorts views in 90 days

**Expected Timeline:**
- Month 1-2: Build audience (1x scale)
- Month 3-4: Grow rapidly (3x scale)
- Month 5-6: Hit monetization threshold
- Month 7+: Profit (10x scale)

**Revenue Projection:**
- Average Shorts RPM: $3-8
- At 1M views/month: $3,000-8,000
- Cost at 10x: $88
- Net profit: $2,912-7,912/month

See `MONETIZATION.md` for detailed strategy.

## Security

- ✅ All secrets in GitHub Secrets (never in code)
- ✅ Automatic copyright detection
- ✅ Content policy compliance checks
- ✅ No personal data collected
- ✅ Rate limiting enforced

## Compliance

- ✅ YouTube Terms of Service compliant
- ✅ API rate limits respected
- ✅ No spam or deceptive practices
- ✅ COPPA compliant (no targeting children)
- ✅ DMCA compliant (copyright checks)

## Support

- **Issues:** Open GitHub issue with logs
- **Docs:** See `ARCHITECTURE.md` for technical details
- **Scaling:** See `SCALING.md` for growth strategy
- **Failures:** See `FAILURE_POINTS.md` for debugging

## License

MIT License - See LICENSE file

## Disclaimer

This system automates content creation and publishing. You are responsible for:
- Ensuring content complies with YouTube policies
- Monitoring published content
- Responding to copyright claims
- Maintaining API credentials
- Staying within API quotas and budgets

Automation does not absolve you of responsibility for your channel.

---

**Built for execution, not experimentation. Deploy once, run forever.**
