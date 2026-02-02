# Quick Start Guide

Get the YouTube Shorts automation system running in 30 minutes.

## Prerequisites Checklist

Before starting, ensure you have:

- [ ] GitHub account with Actions enabled
- [ ] YouTube channel with API access
- [ ] Google Cloud Platform account
- [ ] OpenAI API account (GPT-4 access)
- [ ] Pexels API account (free)

## Step 1: YouTube API Setup (10 minutes)

### 1.1 Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create new project: "YouTube Shorts Automation"
3. Enable YouTube Data API v3:
   - Navigate to "APIs & Services" → "Library"
   - Search for "YouTube Data API v3"
   - Click "Enable"

### 1.2 Create OAuth 2.0 Credentials

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth client ID"
3. Configure consent screen (if first time):
   - User type: External
   - App name: "YouTube Shorts Automation"
   - Scopes: Add `youtube.upload` and `youtube.readonly`
4. Application type: Desktop app
5. Save Client ID and Client Secret

### 1.3 Get Refresh Token

```bash
# Clone this repository
git clone https://github.com/YOUR_USERNAME/trading-dashboard.git
cd trading-dashboard

# Install dependencies
pip install -r requirements.txt

# Run OAuth setup helper (creates this if needed)
python -c "
from google_auth_oauthlib.flow import InstalledAppFlow

flow = InstalledAppFlow.from_client_config(
    {
        'installed': {
            'client_id': 'YOUR_CLIENT_ID',
            'client_secret': 'YOUR_CLIENT_SECRET',
            'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
            'token_uri': 'https://oauth2.googleapis.com/token',
        }
    },
    scopes=['https://www.googleapis.com/auth/youtube.upload',
            'https://www.googleapis.com/auth/youtube.readonly',
            'https://www.googleapis.com/auth/yt-analytics.readonly']
)

credentials = flow.run_local_server(port=0)
print(f'Refresh Token: {credentials.refresh_token}')
"
```

Save the refresh token securely.

## Step 2: API Keys (5 minutes)

### 2.1 OpenAI API Key

1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Navigate to API Keys
3. Create new secret key
4. Save key (starts with `sk-`)

### 2.2 Pexels API Key

1. Go to [Pexels API](https://www.pexels.com/api/)
2. Create account or sign in
3. Generate API key
4. Save key

## Step 3: Repository Setup (5 minutes)

### 3.1 Fork Repository

1. Go to https://github.com/wholyk/trading-dashboard
2. Click "Fork" button
3. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/trading-dashboard.git
   cd trading-dashboard
   ```

### 3.2 Configure GitHub Secrets

1. Go to your repo: Settings → Secrets and Variables → Actions
2. Click "New repository secret" for each:

| Secret Name | Value | Source |
|------------|-------|--------|
| `YOUTUBE_CLIENT_ID` | Your OAuth Client ID | Step 1.2 |
| `YOUTUBE_CLIENT_SECRET` | Your OAuth Client Secret | Step 1.2 |
| `YOUTUBE_REFRESH_TOKEN` | Your refresh token | Step 1.3 |
| `OPENAI_API_KEY` | Your OpenAI API key | Step 2.1 |
| `PEXELS_API_KEY` | Your Pexels API key | Step 2.2 |

## Step 4: Configuration (5 minutes)

### 4.1 Edit System Config

Edit `config/system_config.yaml`:

```yaml
# Choose your niche
detection:
  niche: "personal_finance"  # or "tech_tips", "productivity", "fitness"
  
  # Add your niche keywords
  keywords:
    - "money tips"
    - "save money"
    - "investing"
    - "passive income"

# Start at 1x scale (1 video every 6 hours)
scaling:
  scale_factor: 1

# Set your monthly budget
cost_control:
  monthly_budget: 100  # USD
```

### 4.2 Commit Configuration

```bash
git add config/system_config.yaml
git commit -m "Configure niche and settings"
git push
```

## Step 5: Activate System (5 minutes)

### 5.1 Enable GitHub Actions

1. Go to your repo's "Actions" tab
2. Click "I understand my workflows, go ahead and enable them"

### 5.2 Trigger First Run

1. Click on "Viral Pattern Detection" workflow
2. Click "Run workflow" → "Run workflow"
3. Wait for workflow to complete (5-10 minutes)

### 5.3 Verify Success

Check workflow run for:
- ✅ Patterns detected
- ✅ Ideas scored
- ✅ Ideas approved (at least 1)

If no ideas approved on first run, that's OK! The system will try again in 6 hours.

## Step 6: Monitor (Ongoing)

### 6.1 Check Dashboard

Go to Actions tab to see:
- Workflow runs (success/failure)
- Generated artifacts (videos, reports)
- System logs

### 6.2 View Published Videos

1. Wait for first video to upload (~30 minutes from first run)
2. Check your YouTube Studio
3. Review video in YouTube Shorts

## Troubleshooting

### No Ideas Approved

**Symptom:** Rejection gate blocks all ideas

**Solutions:**
1. Lower threshold temporarily:
   ```yaml
   scoring:
     rejection_threshold: 70  # From 75
   ```
2. Add more keywords for your niche
3. Choose less competitive niche

### Upload Fails

**Symptom:** Video generates but doesn't upload

**Check:**
1. YouTube API credentials are correct
2. OAuth scopes include `youtube.upload`
3. API quota not exceeded (10,000 units/day)

### Workflow Fails

**Symptom:** Red X on workflow run

**Check:**
1. Workflow logs for specific error
2. All required secrets are set
3. Python dependencies installed correctly

## Next Steps

### Week 1-2: Learning Mode (1x)

- System runs automatically every 6 hours
- ~4 videos per day
- Monitor performance
- Adjust niche/keywords as needed

### Week 3-8: Scale to 3x

When you have 3+ winning videos:

```yaml
scaling:
  scale_factor: 3  # Increase to 3x
```

Commit and push. System now produces ~12 videos per day.

### Week 9+: Scale to 10x

When you have consistent winners (20%+ winner rate):

```yaml
scaling:
  scale_factor: 10  # Increase to 10x
```

System now produces ~40 videos per day.

## Cost Expectations

### At 1x Scale (First Month)

- OpenAI API: $6/month
- Pexels API: Free
- YouTube API: Free
- GitHub Actions: Free
- **Total: $6/month**

### At 10x Scale

- OpenAI API: $60/month
- Pexels API: $20/month (paid tier)
- YouTube API: Free
- GitHub Actions: $8/month
- **Total: $88/month**

## Expected Timeline to Monetization

- **Month 1-2:** Build audience (1x scale)
- **Month 3-4:** Grow rapidly (3x scale)
- **Month 5-6:** Hit monetization threshold (1K subs, 10M views)
- **Month 7+:** Revenue (10x scale)

## Getting Help

1. **Check documentation:**
   - README.md - General overview
   - ARCHITECTURE.md - Technical details
   - FAILURE_POINTS.md - Troubleshooting

2. **Review workflow logs:**
   - Actions tab → Click on failed workflow
   - Expand failed step
   - Read error message

3. **Common issues:**
   - See FAILURE_POINTS.md for detailed solutions

4. **Open GitHub issue:**
   - Describe problem
   - Include workflow run ID
   - Attach relevant logs

## Security Reminders

- ✅ Never commit secrets to git
- ✅ Use GitHub Secrets only
- ✅ Rotate API keys periodically (every 90 days)
- ✅ Review published content regularly
- ✅ Monitor costs weekly

## Success Checklist

After 24 hours, you should have:

- [ ] First viral detection completed
- [ ] At least 1 idea approved
- [ ] First video generated
- [ ] First video uploaded to YouTube
- [ ] No critical errors in workflows
- [ ] Costs tracked and within budget

**Congratulations! Your automated YouTube Shorts system is now running.** 🎉

---

**Remember:** This system is fully automated. After setup, it runs without human intervention. Check weekly for monitoring, adjust monthly for optimization.
