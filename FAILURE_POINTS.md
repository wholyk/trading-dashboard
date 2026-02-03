# Failure Points and Prevention Mechanisms

This document catalogs every way the system can fail and how GitHub enforces prevention automatically.

## Critical Failures (System Cannot Proceed)

### Failure 1: YouTube API Authentication Failure

**Description:** OAuth credentials expired or invalid

**Impact:** Cannot upload videos, system dead in water

**Detection:**
```python
# In youtube_uploader.py
def authenticate():
    try:
        credentials = load_credentials()
        youtube = build('youtube', 'v3', credentials=credentials)
        # Test authentication
        youtube.channels().list(part='id', mine=True).execute()
        return youtube
    except HttpError as e:
        if e.resp.status == 401:
            raise AuthenticationError("OAuth token invalid or expired")
```

**GitHub Enforcement:**
- Workflow fails immediately on auth error
- GitHub Issue auto-created with title: "CRITICAL: YouTube Auth Failure"
- Issue includes instructions to refresh token
- Email notification sent to repo owner
- All subsequent workflows blocked until resolved

**Prevention:**
- Token refresh in workflow (before expiration)
- Alert 7 days before token expiry
- Automated token refresh (if refresh token valid)

**Manual Recovery:**
```bash
# Run OAuth setup script locally
python src/utils/oauth_setup.py

# Copy new tokens to GitHub Secrets
# Settings → Secrets → YOUTUBE_REFRESH_TOKEN
```

**SLA:** Manual intervention required within 24 hours to resume

---

### Failure 2: API Quota Exceeded

**Description:** YouTube API quota exhausted (10,000 units/day)

**Impact:** Cannot upload or fetch analytics until quota resets

**Detection:**
```python
# In youtube_api.py
def check_quota():
    used = get_quota_usage()
    limit = 10000
    
    if used > limit * 0.8:  # 80% threshold
        log_warning(f"Quota at {used/limit*100}%")
    
    if used >= limit:
        raise QuotaExceededError(f"Daily quota exhausted: {used}/{limit}")
```

**GitHub Enforcement:**
- Workflow exits with specific error code
- Remaining workflows for the day are cancelled
- GitHub Issue created: "Quota Exceeded - Uploads Paused"
- Cron-based auto-resume next day (00:00 UTC)

**Prevention:**
- Pre-flight quota check before each upload
- Scale factor auto-adjustment based on available quota
- Daily quota tracker in workflow state

**Quota Allocation Strategy:**
```yaml
# At start of day (quota reset)
total_quota: 10000
reserve_analytics: 1000  # For performance tracking
reserve_buffer: 500      # For errors/retries
available_for_uploads: 8500

# Per upload: 1850 units
max_uploads_today: 8500 / 1850 = 4.59 ≈ 4 uploads
```

**Auto-Recovery:**
- Workflow automatically resumes at 00:00 UTC next day
- Queued videos processed in order

**SLA:** 0-24 hour delay (automatic)

---

### Failure 3: Storage Limits Exceeded

**Description:** GitHub Actions artifacts exceed storage limits

**Impact:** Cannot store generated videos

**Detection:**
```python
# In workflow
- name: Check Storage
  run: |
    USED=$(du -sb data/ | cut -f1)
    LIMIT=1073741824  # 1GB
    
    if [ $USED -gt $LIMIT ]; then
      echo "Storage limit exceeded: ${USED} bytes"
      exit 1
    fi
```

**GitHub Enforcement:**
- Workflow fails before video generation
- GitHub Issue created: "Storage Cleanup Required"
- Cleanup workflow automatically triggered

**Prevention:**
- Auto-delete artifacts older than 7 days
- Compress videos before storage (FFmpeg)
- Upload to external storage (S3/GCS) for finals
- Keep only metadata locally

**Cleanup Workflow:**
```yaml
# .github/workflows/cleanup.yml
name: Storage Cleanup
on:
  schedule:
    - cron: '0 0 * * 0'  # Weekly on Sunday
  workflow_dispatch:

jobs:
  cleanup:
    runs-on: ubuntu-latest
    steps:
      - name: Delete Old Artifacts
        run: |
          # Delete artifacts older than 7 days
          gh api repos/$REPO/actions/artifacts \
            --jq '.artifacts[] | select(.created_at < now - 7*86400) | .id' \
            | xargs -I {} gh api -X DELETE repos/$REPO/actions/artifacts/{}
```

**Auto-Recovery:** Runs weekly, no manual intervention

**SLA:** Preventative (runs before failure occurs)

---

## Quality Failures (Content Rejected)

### Failure 4: Idea Rejection (Score < Threshold)

**Description:** Idea scores below 75, rejected by gate

**Impact:** No video produced for this idea

**Detection:**
```python
# In rejection_gate.py
def evaluate_idea(idea, score):
    threshold = config['scoring']['rejection_threshold']
    
    if score < threshold:
        log_rejection(idea, score, reason="Score below threshold")
        return False
    return True
```

**GitHub Enforcement:**
- Logged to `data/rejected/rejected_ideas.json`
- GitHub Issue created weekly with rejection summary
- No bypass mechanism (code change + PR required)

**Prevention:**
- This IS the prevention (filtering bad ideas)
- Threshold configurable but requires PR approval

**Expected Frequency:** 40-60% of ideas rejected (by design)

**Manual Override:** Not allowed (defeats purpose)

---

### Failure 5: Quality Validation Failure

**Description:** Generated video fails quality checks

**Impact:** Video not uploaded, production cost wasted

**Detection:**
```python
# In quality_validator.py
def validate_video(video_path):
    checks = [
        check_duration(video_path, min=15, max=60),
        check_resolution(video_path, width=1080, height=1920),
        check_file_size(video_path, max_mb=100),
        check_audio_levels(video_path, target_lufs=-14),
        check_first_frame(video_path),  # Not black
        check_caption_contrast(video_path),
        check_copyright(video_path)
    ]
    
    failed = [c for c in checks if not c['passed']]
    
    if failed:
        save_failed_video(video_path, failed)
        return False
    return True
```

**GitHub Enforcement:**
- Failed videos moved to `data/failed_qa/` with report
- Workflow continues (doesn't block other videos)
- Daily summary issue created with failure patterns

**Prevention:**
- Strict validation before upload
- Template-based generation (reduces variability)
- Automated fixes where possible (e.g., audio normalization)

**Automated Fixes:**
```python
def auto_fix_video(video_path, failures):
    for failure in failures:
        if failure['type'] == 'audio_levels':
            normalize_audio(video_path)
        elif failure['type'] == 'resolution':
            resize_video(video_path, 1080, 1920)
        elif failure['type'] == 'duration':
            trim_video(video_path, max_duration=60)
    
    # Re-validate
    return validate_video(video_path)
```

**Expected Frequency:** 5-10% of videos fail initial validation, 2-3% fail after auto-fix

**Manual Override:** Not allowed

---

### Failure 6: Copyright Detection

**Description:** Audio or visual content flagged as copyrighted

**Impact:** Video rejected, potential channel strike

**Detection:**
```python
# In quality_validator.py
def check_copyright(video_path):
    # Audio fingerprinting
    audio_hash = extract_audio_fingerprint(video_path)
    matches = copyright_db.search(audio_hash, threshold=0.95)
    
    if matches:
        return {
            'passed': False,
            'reason': f"Copyrighted audio detected: {matches}"
        }
    
    # Visual content check (less reliable, keyword-based)
    # Check for brand logos, trademarked content in overlays
    
    return {'passed': True}
```

**GitHub Enforcement:**
- Hard block, no upload
- Video quarantined in `data/copyright_flagged/`
- GitHub Issue created immediately
- Pattern that generated this video deprioritized

**Prevention:**
- Use only royalty-free music library
- Pre-screened stock footage (Pexels, Pixabay)
- No user-generated content
- Automated audio fingerprint check

**Manual Review:** Required if false positive suspected

---

## Operational Failures (Degraded Performance)

### Failure 7: Script Generation Failure

**Description:** GPT-4 API error or produces invalid script

**Impact:** Single video generation fails

**Detection:**
```python
# In script_generator.py
def generate_script(idea):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            timeout=30
        )
        
        script = parse_script(response['choices'][0]['message']['content'])
        
        if not validate_script_structure(script):
            raise InvalidScriptError("Script structure invalid")
        
        return script
        
    except (OpenAIError, Timeout, InvalidScriptError) as e:
        log_error(f"Script generation failed: {e}")
        return None
```

**GitHub Enforcement:**
- Retry once (exponential backoff: 5 seconds)
- If retry fails, skip this idea, move to next
- Error logged, aggregated in daily report
- If failure rate >20%, alert

**Prevention:**
- Robust prompt engineering
- Script validation before proceeding
- Fallback templates for common patterns

**Expected Frequency:** <5% of attempts fail

**Auto-Recovery:** Automatic retry + skip

---

### Failure 8: Visual Generation Failure

**Description:** Pexels API failure or FFmpeg error

**Impact:** Single video generation fails

**Detection:**
```python
# In visual_generator.py
def generate_visuals(script):
    try:
        # Fetch images from Pexels
        images = []
        for segment in script.segments:
            img = pexels_api.search(segment.keywords, per_page=1)
            if not img:
                raise VisualFetchError(f"No image for: {segment.keywords}")
            images.append(img[0])
        
        # Render video with FFmpeg
        video_path = render_video(images, script)
        
        if not os.path.exists(video_path):
            raise RenderError("FFmpeg failed to produce output")
        
        return video_path
        
    except (PexelsAPIError, VisualFetchError, RenderError) as e:
        log_error(f"Visual generation failed: {e}")
        return None
```

**GitHub Enforcement:**
- Retry once (different keywords)
- If retry fails, skip this video
- Error logged with specific failure reason
- If Pexels API consistently fails, alert (API key issue)

**Prevention:**
- Keyword fallbacks (generic → specific)
- Local cache of popular images
- FFmpeg command validation before execution

**Expected Frequency:** <10% of attempts fail

**Auto-Recovery:** Automatic retry with fallback keywords

---

### Failure 9: Upload Failure

**Description:** YouTube API upload fails mid-upload

**Impact:** Video not published

**Detection:**
```python
# In youtube_uploader.py
def upload_video(video_path, metadata):
    try:
        # Resumable upload
        request = youtube.videos().insert(
            part="snippet,status",
            body=metadata,
            media_body=MediaFileUpload(video_path, resumable=True)
        )
        
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                log_progress(f"Upload {int(status.progress() * 100)}%")
        
        return response['id']
        
    except HttpError as e:
        if e.resp.status in [500, 502, 503, 504]:
            # Server error, retryable
            raise RetryableUploadError(e)
        else:
            # Client error, not retryable
            raise FatalUploadError(e)
```

**GitHub Enforcement:**
- Automatic retry (up to 3 attempts, exponential backoff: 10s, 30s, 90s)
- If all retries fail, queue for next day
- Error logged with HTTP status code
- If pattern of failures, alert (API issue suspected)

**Prevention:**
- Resumable upload (handles interruptions)
- Pre-upload validation (file size, format)
- Exponential backoff on errors

**Expected Frequency:** <5% of uploads fail, <1% after retries

**Auto-Recovery:** Automatic retry, then queue

---

### Failure 10: Performance Tracking Failure

**Description:** YouTube Analytics API fails to return data

**Impact:** Cannot optimize based on performance

**Detection:**
```python
# In performance_tracker.py
def fetch_video_analytics(video_id):
    try:
        response = youtube_analytics.reports().query(
            ids=f'channel=={CHANNEL_ID}',
            filters=f'video=={video_id}',
            metrics='views,estimatedMinutesWatched,averageViewDuration',
            dimensions='day',
            startDate='7daysAgo',
            endDate='today'
        ).execute()
        
        if not response.get('rows'):
            raise NoDataError(f"No analytics for video {video_id}")
        
        return parse_analytics(response)
        
    except HttpError as e:
        log_error(f"Analytics fetch failed: {e}")
        return None
```

**GitHub Enforcement:**
- Retry later (6 hours)
- If 24 hours pass with no data, skip this video
- Warning logged (not error)
- System continues without this data point

**Prevention:**
- Delayed analytics fetch (24h after upload, when data available)
- Graceful degradation (system works without some data)
- Manual analytics review option

**Expected Frequency:** 10-20% of new videos have delayed analytics

**Auto-Recovery:** Automatic retry with delay

---

## Scaling Failures

### Failure 11: Parallel Job Conflicts

**Description:** Multiple jobs try to access same resource simultaneously

**Impact:** Race condition, corrupted data, or duplicate uploads

**Detection:**
```python
# In workflow state management
def acquire_lock(resource_id, job_id):
    lock_file = f"/tmp/lock_{resource_id}.lock"
    
    try:
        # Atomic file creation
        fd = os.open(lock_file, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        os.write(fd, job_id.encode())
        os.close(fd)
        return True
    except FileExistsError:
        # Another job has the lock
        return False
```

**GitHub Enforcement:**
- File-based locks for critical sections
- Each job has isolated workspace
- Atomic operations only (no shared mutable state)
- Job IDs prevent duplicate processing

**Prevention:**
- Fully isolated job execution
- Read-only shared resources
- Atomic queue operations
- Concurrency limits in workflow

**Workflow Configuration:**
```yaml
jobs:
  generate:
    strategy:
      matrix:
        job_id: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
      fail-fast: false  # Independent jobs
    
    # Prevent conflicts on upload
    concurrency:
      group: upload-slot-${{ matrix.job_id }}
      cancel-in-progress: false
```

**Expected Frequency:** Rare (<1% with proper isolation)

**Auto-Recovery:** Job-level isolation prevents cascading failures

---

### Failure 12: Idea Queue Exhaustion

**Description:** Not enough approved ideas for parallel jobs

**Impact:** Some parallel jobs have nothing to process

**Detection:**
```python
# In content_generation workflow
def get_next_idea(job_id):
    ideas = load_approved_ideas()
    
    if len(ideas) < job_id:
        log_info(f"Job {job_id}: No idea available, skipping")
        return None
    
    return ideas[job_id - 1]
```

**GitHub Enforcement:**
- Jobs gracefully skip if no idea available
- Warning logged (not error)
- Increases detection frequency temporarily

**Prevention:**
- Buffer of ideas (always maintain queue depth >10)
- Increase detection frequency if queue low
- Lower rejection threshold temporarily (85 → 75)

**Auto-Recovery:**
```yaml
# In viral_detection workflow
- name: Check Queue Depth
  run: |
    QUEUE_SIZE=$(jq 'length' data/idea_queue.json)
    if [ $QUEUE_SIZE -lt 5 ]; then
      echo "Queue low, triggering extra detection"
      # Trigger workflow again
    fi
```

**Expected Frequency:** 10-20% of 10x runs have <10 ideas

**Impact:** Reduced output (e.g., 7 videos instead of 10), but not failure

---

## Cost Control Failures

### Failure 13: Budget Overrun

**Description:** API costs exceed monthly budget threshold

**Impact:** Financial loss, need to pause system

**Detection:**
```python
# In cost_tracker.py
def check_budget():
    month_start = datetime.now().replace(day=1)
    costs = get_costs_since(month_start)
    budget = config['cost_control']['monthly_budget']
    
    if costs > budget * 0.8:  # 80% warning
        alert_budget_warning(costs, budget)
    
    if costs >= budget:
        raise BudgetExceededError(f"Budget exhausted: ${costs}/${budget}")
```

**GitHub Enforcement:**
- Daily cost tracking workflow
- Alert at 80% budget usage
- Hard stop at 100% budget
- Workflow cannot proceed until budget increased or month resets

**Prevention:**
- Pre-flight cost estimation
- Scale factor auto-adjustment based on burn rate
- Cost per video tracking

**Budget Allocation:**
```yaml
# config/cost_control.yaml
monthly_budget: 100  # USD

allocation:
  openai: 60%    # $60
  pexels: 20%    # $20
  other: 20%     # $20

alerts:
  warning_threshold: 0.8   # 80%
  critical_threshold: 1.0  # 100%
```

**Auto-Recovery:**
- Pause production until month resets
- Option to increase budget (manual config change)

**Manual Override:** Requires PR to increase budget

---

### Failure 14: Pattern Staleness

**Description:** System keeps producing content based on outdated patterns

**Impact:** Declining performance, lower engagement

**Detection:**
```python
# In auto_optimizer.py
def detect_staleness():
    patterns = load_patterns()
    
    for pattern in patterns:
        last_updated = pattern['last_updated']
        age_days = (datetime.now() - last_updated).days
        
        if age_days > 30:
            pattern['weight'] *= 0.9  # 10% penalty per check
        
        if pattern['weight'] < 0.1:
            archive_pattern(pattern)
```

**GitHub Enforcement:**
- Weekly pattern audit
- Automatic weight decay for old patterns
- Forced refresh if no new patterns in 14 days

**Prevention:**
- Continuous pattern detection (every 6 hours)
- Bonus weight for recent patterns
- Diversity enforcement (top 50 patterns, not just top 10)

**Auto-Recovery:**
```yaml
# In viral_detection workflow
- name: Force Pattern Refresh
  if: github.event.schedule == '0 0 * * 0'  # Weekly
  run: |
    python src/detection/pattern_refresh.py --force
```

**Expected Frequency:** Gradual decline over weeks if not monitored

**Impact:** Reduced performance metrics (CTR, retention) over time

---

## System-Level Failures

### Failure 15: Workflow Definition Errors

**Description:** GitHub Actions YAML syntax error or invalid configuration

**Impact:** Workflow cannot run at all

**Detection:**
- GitHub automatically validates YAML on push
- Workflow run fails with syntax error message

**GitHub Enforcement:**
- Pull request checks must pass before merge
- Syntax validation in CI
- Test workflow runs on PR

**Prevention:**
```yaml
# .github/workflows/validate.yml
name: Validate Workflows
on: [pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Validate YAML
        run: |
          yamllint .github/workflows/*.yml
      
      - name: Test Workflow Syntax
        run: |
          # Dry-run workflow validation
          gh workflow view viral_detection.yml
```

**Manual Override:** Not applicable (syntax errors must be fixed)

---

### Failure 16: Dependency Issues

**Description:** Python package or system dependency missing/broken

**Impact:** Workflows fail at runtime

**Detection:**
```yaml
# In workflow
- name: Install Dependencies
  run: |
    pip install -r requirements.txt
  continue-on-error: false  # Fail immediately if dependencies broken
```

**GitHub Enforcement:**
- Explicit dependency installation in workflow
- Version pinning in requirements.txt
- Docker container option for full reproducibility

**Prevention:**
```txt
# requirements.txt with pinned versions
google-api-python-client==2.108.0
google-auth==2.25.0
openai==1.6.0
requests==2.31.0
pyyaml==6.0.1
```

**Auto-Recovery:** None (must fix requirements.txt)

---

## Enforcement Summary

| Failure Type | Detection Method | Enforcement Mechanism | Auto-Recovery | Manual Required |
|--------------|-----------------|----------------------|---------------|-----------------|
| Auth Failure | API call fails | Workflow fails, issue created | Token refresh | Yes (if refresh fails) |
| Quota Exceeded | Pre-flight check | Day's workflows cancelled | Next day auto-resume | No |
| Storage Limits | Disk usage check | Cleanup triggered | Weekly cleanup | No |
| Idea Rejection | Score check | Logged, no video produced | N/A (by design) | No |
| Quality Failure | Validation checks | Video rejected, logged | Auto-fix attempted | No |
| Copyright | Fingerprinting | Hard block, quarantine | None | Yes (manual review) |
| Script Gen Fail | API error | Retry once, then skip | Automatic | No |
| Visual Gen Fail | API/FFmpeg error | Retry with fallbacks | Automatic | No |
| Upload Failure | HTTP error | Retry 3x, then queue | Automatic | No (queued) |
| Analytics Fail | API error | Retry later | Automatic | No |
| Job Conflicts | Lock contention | Job waits or skips | Automatic | No |
| Queue Exhaustion | Queue depth check | Increase detection | Automatic | No |
| Budget Overrun | Cost tracking | Production paused | Month reset | Yes (budget increase) |
| Pattern Stale | Age tracking | Weight decay | Automatic | No |
| Workflow Error | YAML validation | PR check fails | None | Yes (fix YAML) |
| Dependencies | Install step | Workflow fails | None | Yes (fix requirements) |

**Key Takeaway:** 80% of failures auto-recover, 15% gracefully degrade, 5% require manual intervention.

## Alert Escalation

### Level 1: Info (Logged Only)
- Idea rejected
- Job skipped (no idea available)
- Analytics delayed

**Action:** None

### Level 2: Warning (GitHub Issue Created)
- Quality validation failure
- Upload retry
- Queue depth low
- Budget at 80%

**Action:** Weekly review

### Level 3: Alert (Email + Issue)
- Quota at 90%
- Budget at 100%
- Auth token expiring (7 days)
- Failure rate >20%

**Action:** Check within 24 hours

### Level 4: Critical (Email + SMS + Issue)
- Auth failure
- Copyright strike
- Repeated critical errors
- System completely down

**Action:** Immediate response required

## Testing Failure Scenarios

```yaml
# .github/workflows/failure_testing.yml
name: Test Failure Scenarios
on: workflow_dispatch

jobs:
  test-failures:
    runs-on: ubuntu-latest
    steps:
      - name: Test Auth Failure
        run: python tests/test_auth_failure.py
      
      - name: Test Quota Exhaustion
        run: python tests/test_quota_limit.py
      
      - name: Test Quality Validation
        run: python tests/test_quality_checks.py
      
      # etc.
```

**Run monthly to verify enforcement mechanisms work correctly.**

---

**This system is designed to fail gracefully. Most failures are expected, handled automatically, and don't require human intervention. The remaining failures alert appropriately and block progress until resolved.**
