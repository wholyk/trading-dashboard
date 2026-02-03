# YouTube Shorts Automation System - Technical Architecture

## System Overview

This is a fully automated GitHub-based system that produces, publishes, and optimizes profitable YouTube Shorts at scale.

## Architecture Diagram (Text)

```
┌─────────────────────────────────────────────────────────────────┐
│                        GITHUB (Control Center)                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                   DETECTION LAYER                         │  │
│  │                                                            │  │
│  │  ┌──────────────┐      ┌──────────────┐                 │  │
│  │  │ Viral Pattern│─────▶│ Idea Scoring │                 │  │
│  │  │   Detector   │      │  (0-100)     │                 │  │
│  │  └──────────────┘      └──────┬───────┘                 │  │
│  │         │                      │                          │  │
│  │         │                      ▼                          │  │
│  │         │              ┌──────────────┐                  │  │
│  │         │              │ Rejection    │ ◀─ Threshold=75  │  │
│  │         │              │ Gate         │                  │  │
│  │         │              └──────┬───────┘                  │  │
│  │         │                     │                          │  │
│  │         │          ┌──────────┴────────────┐            │  │
│  │         │          │   PASS (Score ≥ 75)   │            │  │
│  │         │          └──────────┬────────────┘            │  │
│  └─────────┼────────────────────┼─────────────────────────┘  │
│            │                     │                            │
│  ┌─────────┼────────────────────┼─────────────────────────┐  │
│  │         │     GENERATION LAYER│                         │  │
│  │         ▼                     ▼                         │  │
│  │  ┌──────────────┐      ┌──────────────┐               │  │
│  │  │ Script Gen   │◀─────│ Context      │               │  │
│  │  │ (GPT-4)      │      │ Builder      │               │  │
│  │  └──────┬───────┘      └──────────────┘               │  │
│  │         │                                               │  │
│  │         ▼                                               │  │
│  │  ┌──────────────┐                                      │  │
│  │  │ Visual Gen   │◀───── stock API / generation         │  │
│  │  │ (FFmpeg)     │                                      │  │
│  │  └──────┬───────┘                                      │  │
│  │         │                                               │  │
│  │         ▼                                               │  │
│  │  ┌──────────────┐                                      │  │
│  │  │ Caption +    │◀───── SEO optimizer                  │  │
│  │  │ Metadata Gen │                                      │  │
│  │  └──────┬───────┘                                      │  │
│  │         │                                               │  │
│  │         ▼                                               │  │
│  │  ┌──────────────┐                                      │  │
│  │  │ Quality      │◀───── validation rules               │  │
│  │  │ Validator    │                                      │  │
│  │  └──────┬───────┘                                      │  │
│  └─────────┼─────────────────────────────────────────────┘  │
│            │                                                 │
│  ┌─────────┼─────────────────────────────────────────────┐  │
│  │         │      PUBLICATION LAYER                       │  │
│  │         ▼                                               │  │
│  │  ┌──────────────┐                                      │  │
│  │  │ YouTube API  │◀───── OAuth credentials              │  │
│  │  │ Uploader     │                                      │  │
│  │  └──────┬───────┘                                      │  │
│  │         │                                               │  │
│  │         ▼                                               │  │
│  │  ┌──────────────┐                                      │  │
│  │  │ Published    │                                      │  │
│  │  │ Video        │                                      │  │
│  │  └──────┬───────┘                                      │  │
│  └─────────┼─────────────────────────────────────────────┘  │
│            │                                                 │
│  ┌─────────┼─────────────────────────────────────────────┐  │
│  │         │      LEARNING LAYER                          │  │
│  │         ▼                                               │  │
│  │  ┌──────────────┐      ┌──────────────┐              │  │
│  │  │ Performance  │─────▶│ Winner       │              │  │
│  │  │ Tracker      │      │ Identifier   │              │  │
│  │  └──────────────┘      └──────┬───────┘              │  │
│  │                               │                        │  │
│  │                               ▼                        │  │
│  │                        ┌──────────────┐               │  │
│  │                        │ Auto-Optimize│               │  │
│  │                        │ (Double Down)│               │  │
│  │                        └──────┬───────┘               │  │
│  │                               │                        │  │
│  │         ┌─────────────────────┘                        │  │
│  │         │    (Feedback Loop to Detection)              │  │
│  └─────────┼──────────────────────────────────────────────┘  │
│            │                                                 │
│  ┌─────────┼─────────────────────────────────────────────┐  │
│  │         │      SCALING LAYER                           │  │
│  │         ▼                                               │  │
│  │  ┌──────────────┐                                      │  │
│  │  │ Parallel     │◀───── Matrix strategy                │  │
│  │  │ Orchestrator │       (10 concurrent jobs)           │  │
│  │  └──────────────┘                                      │  │
│  │                                                         │  │
│  │  1x → 3x → 10x (no quality loss)                      │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

## Data Flow

### Phase 1: Detection (Every 6 hours)
```
Cron Trigger → Viral Pattern Detector → YouTube API → 
Analyze Top 100 Shorts in Niche → Extract Patterns →
Score Ideas (0-100) → Rejection Gate (threshold=75) →
Store Approved Ideas → Trigger Generation
```

### Phase 2: Generation (On approved idea)
```
Approved Idea → Context Builder → Script Generator (GPT-4) →
Visual Generator (FFmpeg + Stock API) → Caption Generator →
Metadata Generator → Quality Validator → Store Final Video
```

### Phase 3: Publication (On validated video)
```
Final Video → YouTube API Uploader → Publish →
Store Video ID → Schedule Performance Check
```

### Phase 4: Learning (24 hours after publish)
```
Published Video → Performance Tracker → Fetch Analytics →
Calculate Metrics (CTR, Retention, RPM) → Identify Winners →
Update Pattern Weights → Trigger More Similar Content
```

## Component Details

### 1. Viral Pattern Detector
**Location:** `src/detection/viral_detector.py`

**Function:** Scans YouTube Shorts in target niche, identifies patterns

**Inputs:**
- Niche keywords (config)
- Timeframe (last 7 days)
- Minimum view threshold

**Outputs:**
- Pattern dictionary with frequency scores
- Top performing topics
- Hook structures
- Visual styles

**API Calls:**
- YouTube Data API v3
- Rate limit: 10,000 units/day
- Caching: 6 hours

### 2. Idea Scoring Engine
**Location:** `src/detection/idea_scorer.py`

**Function:** Assigns confidence score 0-100 to each idea

**Scoring Algorithm:**
```python
score = (
    pattern_frequency * 0.30 +      # How often this pattern works
    recency_weight * 0.20 +          # How recent successful examples are
    engagement_rate * 0.25 +         # Average engagement of similar shorts
    competition_score * 0.15 +       # Market saturation (inverse)
    audience_fit * 0.10              # Match with channel's audience
)
```

**Rejection Logic:**
- Score < 75: Reject immediately
- Score 75-85: Queue (produce if queue empty)
- Score > 85: Priority queue (produce first)

### 3. Rejection Gate
**Location:** `src/detection/rejection_gate.py`

**Function:** Hard filter - no human override

**Rules:**
1. Score must be ≥ 75 (configurable)
2. No duplicate ideas in last 30 days
3. No blacklisted keywords
4. Must have successful reference examples (≥3)
5. Estimated production cost < budget threshold
6. Content fits platform guidelines (automated check)

**Failure Mode:** Rejected ideas logged to `data/rejected.json` with reason

### 4. Script Generator
**Location:** `src/generation/script_generator.py`

**Function:** Generates video script from approved idea

**Process:**
1. Load winning script templates
2. Inject idea-specific context
3. Call GPT-4 API with strict prompt
4. Validate output (length, structure, hooks)
5. Return script or fail

**Prompt Template:**
```
Role: Viral YouTube Shorts scriptwriter
Niche: {niche}
Pattern: {pattern}
Constraint: 45-60 seconds when spoken
Required: Hook in first 3 seconds
Required: Pattern interrupt every 12 seconds
Required: Clear CTA
Reference: {winning_examples}
Output: JSON with segments
```

### 5. Visual Generator
**Location:** `src/generation/visual_generator.py`

**Function:** Creates video file from script

**Process:**
1. Parse script segments
2. Source visuals (Pexels API / generated)
3. Add text overlays (FFmpeg)
4. Add background music (royalty-free)
5. Render 9:16 aspect ratio
6. Output MP4 (max 60 sec, <100MB)

**Dependencies:**
- FFmpeg (installed in runner)
- Pexels API (free tier: 200 requests/hour)
- Font files for captions

### 6. Quality Validator
**Location:** `src/generation/quality_validator.py`

**Function:** Checks video meets standards before upload

**Validation Rules:**
1. Duration: 15-60 seconds
2. Resolution: 1080x1920 (9:16)
3. File size: < 100MB
4. Audio levels: -14 LUFS ± 1
5. First frame: engaging (not black)
6. Caption readability: contrast ratio > 4.5:1
7. No copyright-flagged content (audio fingerprinting)

**Failure Mode:** Failed videos stored in `data/failed_qa/` with report

### 7. YouTube Uploader
**Location:** `src/publication/youtube_uploader.py`

**Function:** Uploads video to YouTube via API

**Process:**
1. Load OAuth credentials (GitHub Secrets)
2. Prepare metadata (title, description, tags)
3. Upload video (resumable upload)
4. Set privacy: Public
5. Store video ID
6. Log publish timestamp

**Rate Limits:**
- 6 uploads per day (API quota)
- Handled by GitHub Actions scheduling

### 8. Performance Tracker
**Location:** `src/learning/performance_tracker.py`

**Function:** Collects analytics for published videos

**Metrics:**
- Views (24h, 7d, 30d)
- CTR (click-through rate)
- Average view duration
- Likes/Comments ratio
- RPM (revenue per mille)
- Traffic sources

**Winner Threshold:**
- Top 20% of channel performance
- CTR > 5%
- Retention > 50%
- RPM > channel average

### 9. Auto-Optimizer
**Location:** `src/learning/auto_optimizer.py`

**Function:** Doubles down on winners

**Process:**
1. Identify winning videos (daily)
2. Extract common patterns
3. Increase pattern weights by 2x
4. Generate 3 variations of winner
5. Queue for production
6. Update niche keywords

**Feedback Loop:**
- Winner patterns → Detection layer weights
- Failing patterns → Penalty (weight * 0.5)

## GitHub Actions Workflows

### Workflow 1: Viral Detection
**File:** `.github/workflows/viral_detection.yml`

**Trigger:** Cron (every 6 hours: 0 */6 * * *)

**Steps:**
1. Checkout code
2. Install dependencies
3. Run viral detector
4. Run idea scorer
5. Run rejection gate
6. Store approved ideas (artifact)
7. Trigger generation (if ideas approved)

**Failure Conditions:**
- API rate limit exceeded → Wait and retry
- No ideas pass gate → Log warning (not error)
- Zero patterns detected → Alert (potential API issue)

### Workflow 2: Content Generation
**File:** `.github/workflows/content_generation.yml`

**Trigger:** 
- Workflow dispatch (from viral detection)
- Manual trigger (for testing)

**Strategy:** Matrix for parallel jobs (1x, 3x, 10x)

**Steps:**
1. Load approved idea from queue
2. Generate script
3. Generate visuals
4. Generate captions
5. Run quality validator
6. Store video (artifact)
7. Trigger upload

**Failure Conditions:**
- Script generation fails → Retry once, then skip
- Visual generation fails → Store error, move to next
- Quality validation fails → Log to failed_qa, reject

**Parallelization:**
- 10x mode: Run 10 jobs concurrently
- Each job processes different idea
- No shared state (fully isolated)

### Workflow 3: Upload Automation
**File:** `.github/workflows/upload_automation.yml`

**Trigger:** 
- On successful generation
- Manual trigger with video path

**Steps:**
1. Load video artifact
2. Load metadata
3. Authenticate YouTube API
4. Upload video (resumable)
5. Verify upload success
6. Store video ID
7. Schedule performance tracking (24h delay)

**Failure Conditions:**
- Auth failure → Alert (credentials issue)
- Upload failure → Retry up to 3 times with exponential backoff
- Quota exceeded → Queue for next day

### Workflow 4: Performance Analysis
**File:** `.github/workflows/performance_analysis.yml`

**Trigger:** 
- Cron (daily at 00:00 UTC)
- Manual trigger

**Steps:**
1. Fetch all published videos (last 30 days)
2. Collect analytics for each
3. Identify winners
4. Run auto-optimizer
5. Update pattern weights
6. Generate performance report (artifact)

**Failure Conditions:**
- Analytics API fails → Skip this run, alert
- No winners identified → Log info (not error)

### Workflow 5: Scaling Orchestrator
**File:** `.github/workflows/scaling_orchestrator.yml`

**Trigger:** Manual with input (scale_factor: 1, 3, or 10)

**Steps:**
1. Validate scale factor
2. Check resource availability (API quotas)
3. Trigger content generation workflow N times
4. Monitor parallel jobs
5. Aggregate results
6. Report success/failure counts

**Resource Management:**
- 1x: 1 video/run
- 3x: 3 videos/run (sequential)
- 10x: 10 videos/run (parallel matrix)

**Quota Protection:**
- Check YouTube API quota before scaling
- Fail fast if quota insufficient
- Automatically adjust scale factor if needed

## Enforcement Mechanisms

### 1. Rejection Gate Enforcement
- **Mechanism:** GitHub Action step must exit 0 to proceed
- **Bypass:** Impossible without code change and PR review
- **Logging:** All rejections logged to issues (auto-created)

### 2. Quality Gate Enforcement
- **Mechanism:** Quality validator returns pass/fail
- **Bypass:** Video must pass all checks (no overrides)
- **Audit:** Failed videos stored with detailed report

### 3. Rate Limiting
- **Mechanism:** GitHub Actions concurrency groups
- **Limits:**
  - Max 6 uploads per day (YouTube quota)
  - Max 10 concurrent generation jobs
  - Max 200 Pexels API calls per hour
- **Enforcement:** Workflow waits if limit reached

### 4. Cost Control
- **Mechanism:** Budget thresholds in config
- **Limits:**
  - Max $50/month for APIs
  - Alert at 80% budget
  - Hard stop at 100% budget
- **Tracking:** Cost tracking workflow (daily)

### 5. Content Policy
- **Mechanism:** Pre-upload content scan
- **Checks:**
  - Copyright detection (audio)
  - Profanity filter (script)
  - Brand safety (context)
- **Action:** Reject video if any check fails

## Failure Points and Prevention

### Failure Point 1: API Rate Limits
**Risk:** Exceeding YouTube/Pexels API quotas

**Prevention:**
- Quota tracking in workflow state
- Exponential backoff on rate limit errors
- Proactive quota monitoring
- Alert at 80% usage

**Recovery:**
- Queue excess requests for next day
- Automatic retry with delay

### Failure Point 2: Content Quality Degradation
**Risk:** System produces low-quality content at scale

**Prevention:**
- Strict quality validator (automated)
- Performance-based pattern weighting
- Regular audit reports (daily)
- Manual spot-check trigger

**Recovery:**
- Auto-disable failing patterns
- Revert to last known good config

### Failure Point 3: Monetization Drop
**Risk:** RPM decreases due to poor content

**Prevention:**
- RPM tracking per video
- Alert if RPM < 50% of average
- Auto-pause production if trend negative

**Recovery:**
- Roll back to previous winning patterns
- Increase quality threshold temporarily

### Failure Point 4: OAuth Token Expiration
**Risk:** YouTube upload fails due to expired credentials

**Prevention:**
- Token refresh in workflow
- Alert 7 days before expiration
- Fallback: Manual token rotation instructions

**Recovery:**
- Workflow pauses
- GitHub issue auto-created with instructions

### Failure Point 5: Storage Limits
**Risk:** GitHub Actions artifacts fill up

**Prevention:**
- Automatic cleanup of old artifacts (>30 days)
- Compress videos before storage
- Use external storage for finals

**Recovery:**
- Cleanup workflow runs on schedule

### Failure Point 6: Parallel Job Conflicts
**Risk:** 10x scaling causes race conditions

**Prevention:**
- Each job has unique workspace
- No shared mutable state
- Atomic file operations
- Job-level locking where needed

**Recovery:**
- Failed jobs don't affect others
- Automatic retry for transient failures

### Failure Point 7: Pattern Staleness
**Risk:** System keeps producing outdated content

**Prevention:**
- Weekly pattern refresh (forced)
- Performance decay function (older patterns lose weight)
- Trend detection (new patterns get bonus)

**Recovery:**
- Automatic pattern pruning (bottom 20%)

## System States

### State 1: Learning (Weeks 1-2)
- Scale: 1x (1 video per cycle)
- Quality threshold: 85
- Pattern count: Top 10 only
- Human review: Optional spot-check

### State 2: Stable (Weeks 3-8)
- Scale: 3x (3 videos per cycle)
- Quality threshold: 75
- Pattern count: Top 30
- Human review: Weekly performance review

### State 3: Scaled (Week 9+)
- Scale: 10x (10 videos per cycle)
- Quality threshold: 75
- Pattern count: Top 50
- Human review: Monthly audit only

## Configuration Management

All system parameters live in `config/system_config.yaml`:

```yaml
detection:
  niche: "personal_finance"  # or "fitness", "tech_tips", etc.
  scan_frequency_hours: 6
  top_patterns_count: 50
  min_pattern_frequency: 3
  
scoring:
  rejection_threshold: 75
  priority_threshold: 85
  max_queue_size: 100
  
generation:
  parallel_jobs: 1  # 1, 3, or 10
  script_model: "gpt-4"
  max_script_tokens: 500
  video_duration_sec: [45, 60]
  
publication:
  daily_upload_limit: 6
  privacy: "public"
  category_id: 22  # People & Blogs
  
learning:
  performance_check_delay_hours: 24
  winner_percentile: 0.8  # Top 20%
  min_views_for_analysis: 1000
  
monetization:
  target_rpm: 5.0
  alert_rpm_drop_percent: 50
  
scaling:
  scale_factor: 1  # Start at 1x
  max_scale_factor: 10
  scale_up_after_winners: 5
```

Changes to config trigger validation workflow before merge.

## Success Metrics

### Tier 1: Production Health
- Ideas generated per day
- Ideas passing gate (%)
- Videos produced per day
- Videos passing QA (%)
- Upload success rate (%)

### Tier 2: Content Performance
- Average CTR
- Average retention
- Average RPM
- Winner rate (top 20%)

### Tier 3: Business Impact
- Total views (monthly)
- Total revenue (monthly)
- Cost per video
- Profit margin (%)

All metrics tracked in `data/metrics.json` and visualized via GitHub Pages dashboard.

## Security and Compliance

### Secrets Management
- YouTube OAuth: GitHub Secrets (`YOUTUBE_CLIENT_ID`, `YOUTUBE_CLIENT_SECRET`, `YOUTUBE_REFRESH_TOKEN`)
- API Keys: GitHub Secrets (`PEXELS_API_KEY`, `OPENAI_API_KEY`)
- No secrets in code or artifacts

### Content Compliance
- Automated copyright check before upload
- Profanity filter on scripts
- Community guidelines check (keyword-based)
- COPPA compliance (no content targeting children)

### Data Privacy
- No personal data collected
- Analytics data anonymized
- Storage: GitHub (private repo) or S3 (encrypted)

## Deployment

1. Fork this repository
2. Set GitHub Secrets (see above)
3. Configure `config/system_config.yaml` for your niche
4. Enable GitHub Actions
5. Manually trigger viral_detection workflow to start
6. System runs autonomously thereafter

## Maintenance

### Weekly:
- Review performance report
- Check for failed workflows
- Verify API quota usage

### Monthly:
- Audit video quality (sample 10 videos)
- Review monetization metrics
- Update niche config if needed

### Quarterly:
- Update pattern templates
- Refresh API credentials
- Review and optimize costs

---

**This system is designed for zero human intervention once configured. Every decision point is automated and enforceable via GitHub Actions.**
