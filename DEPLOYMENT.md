# Google Cloud Deployment Guide

This guide walks you through deploying the automated trading bot to Google Cloud Platform.

## Prerequisites

- Google Cloud Platform account ([Sign up for free trial](https://cloud.google.com/free))
- Alpaca API credentials
- Google Cloud SDK installed locally

## Step 1: Set Up Google Cloud Project

1. Create a new project in [Google Cloud Console](https://console.cloud.google.com/)
2. Enable billing for the project
3. Enable the following APIs:
   - Cloud Functions API
   - Cloud Scheduler API
   - Cloud Build API

```bash
gcloud services enable cloudfunctions.googleapis.com
gcloud services enable cloudscheduler.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

## Step 2: Prepare Your Code

Ensure your project structure looks like this:

```
trading-dashboard/
├── main.py              # Cloud Function entry point
├── trading_bot.py       # Main bot logic
├── backtesting.py       # Backtesting module
├── notifications.py     # Notifications module
└── requirements.txt     # Dependencies
```

## Step 3: Deploy Cloud Function

### Option A: Deploy via Command Line

```bash
# Navigate to project directory
cd trading-dashboard

# Deploy function
gcloud functions deploy trading_function \
  --gen2 \
  --runtime=python311 \
  --region=us-central1 \
  --source=. \
  --entry-point=trading_function \
  --trigger-http \
  --allow-unauthenticated \
  --timeout=540s \
  --memory=512MB \
  --set-env-vars \
APCA_API_KEY_ID="your_alpaca_key",\
APCA_API_SECRET_KEY="your_alpaca_secret",\
TRADING_SYMBOLS="AAPL,MSFT,GOOGL,AMZN",\
PAPER_TRADING="true"
```

### Option B: Deploy via Console

1. Go to [Cloud Functions](https://console.cloud.google.com/functions)
2. Click "Create Function"
3. Configure:
   - **Name**: trading_function
   - **Region**: us-central1 (or your preferred region)
   - **Trigger**: HTTP
   - **Authentication**: Allow unauthenticated invocations
4. Click "Next"
5. Configure runtime:
   - **Runtime**: Python 3.11
   - **Entry point**: trading_function
   - **Source code**: Inline editor or ZIP upload
6. Copy contents of `main.py` to the inline editor
7. Add other files (trading_bot.py, etc.) as additional files
8. Copy contents of `requirements.txt` to requirements.txt
9. Add environment variables:
   - `APCA_API_KEY_ID`: Your Alpaca API key
   - `APCA_API_SECRET_KEY`: Your Alpaca secret
   - `TRADING_SYMBOLS`: AAPL,MSFT,GOOGL,AMZN
   - `PAPER_TRADING`: true
10. Click "Deploy"

## Step 4: Set Up Cloud Scheduler

### Create Scheduler Job via Command Line

```bash
# Create a job that runs every weekday at 9:30 AM ET (14:30 UTC)
gcloud scheduler jobs create http trading-bot-daily \
  --location=us-central1 \
  --schedule="30 14 * * 1-5" \
  --time-zone="UTC" \
  --uri="https://us-central1-YOUR_PROJECT_ID.cloudfunctions.net/trading_function" \
  --http-method=GET \
  --attempt-deadline=540s
```

### Create Scheduler Job via Console

1. Go to [Cloud Scheduler](https://console.cloud.google.com/cloudscheduler)
2. Click "Create Job"
3. Configure:
   - **Name**: trading-bot-daily
   - **Region**: us-central1 (match your function region)
   - **Frequency**: `30 14 * * 1-5` (9:30 AM ET, weekdays)
   - **Timezone**: UTC
   - **Target**: HTTP
   - **URL**: Your Cloud Function URL
   - **HTTP method**: GET
4. Click "Create"

### Common Schedules

```bash
# Every weekday at market open (9:30 AM ET = 14:30 UTC)
30 14 * * 1-5

# Every weekday at 10 AM ET = 15:00 UTC
0 15 * * 1-5

# Every weekday at market close (4:00 PM ET = 21:00 UTC)
0 21 * * 1-5

# Multiple times per day (10 AM, 12 PM, 2 PM ET)
0 15,17,19 * * 1-5
```

## Step 5: Configure Email Notifications (Optional)

Add email configuration to your Cloud Function environment variables:

```bash
gcloud functions deploy trading_function \
  --update-env-vars \
SENDER_EMAIL="your_email@gmail.com",\
SENDER_PASSWORD="your_app_password",\
RECIPIENT_EMAIL="recipient@example.com",\
SMTP_SERVER="smtp.gmail.com",\
SMTP_PORT="587"
```

## Step 6: Test the Deployment

### Test the Function Manually

```bash
# Get your function URL
gcloud functions describe trading_function --region=us-central1 --format="value(url)"

# Test with curl
curl "YOUR_FUNCTION_URL"
```

### View Logs

```bash
# View recent logs
gcloud functions logs read trading_function --region=us-central1 --limit=50

# Stream logs in real-time
gcloud functions logs read trading_function --region=us-central1 --follow
```

### Test Scheduler Job

```bash
# Manually trigger the job
gcloud scheduler jobs run trading-bot-daily --location=us-central1

# View job status
gcloud scheduler jobs describe trading-bot-daily --location=us-central1
```

## Step 7: Monitor and Maintain

### View Function Metrics

1. Go to [Cloud Functions](https://console.cloud.google.com/functions)
2. Click on your function
3. View metrics:
   - Invocations
   - Execution time
   - Memory usage
   - Errors

### Set Up Alerts

1. Go to [Monitoring](https://console.cloud.google.com/monitoring)
2. Create alert policies for:
   - Function errors
   - Execution timeouts
   - High memory usage

### Budget Alerts

1. Go to [Billing](https://console.cloud.google.com/billing)
2. Set up budget alerts to monitor costs
3. Recommended: Set alert at $10-20 for development

## Estimated Costs

With Google Cloud free tier:
- **Cloud Functions**: 2M invocations free per month
- **Cloud Scheduler**: 3 jobs free per month
- **Typical monthly cost**: $0-5 for basic usage

## Troubleshooting

### Function Timeout

If execution takes too long:
```bash
gcloud functions deploy trading_function --timeout=540s
```

### Memory Issues

Increase memory:
```bash
gcloud functions deploy trading_function --memory=1GB
```

### Authentication Errors

Check API credentials:
```bash
gcloud functions describe trading_function --region=us-central1 --format="value(environmentVariables)"
```

### Scheduler Not Running

Check scheduler status:
```bash
gcloud scheduler jobs describe trading-bot-daily --location=us-central1
```

View scheduler logs:
```bash
gcloud logging read "resource.type=cloud_scheduler_job AND resource.labels.job_id=trading-bot-daily" --limit=10
```

## Security Best Practices

1. **Secret Manager**: Use Google Secret Manager for sensitive data:
```bash
echo -n "your_api_key" | gcloud secrets create alpaca-api-key --data-file=-
```

2. **Service Account**: Create a dedicated service account with minimal permissions

3. **VPC**: Deploy function in VPC for enhanced security

4. **Audit Logs**: Enable Cloud Audit Logs for compliance

## Clean Up

To remove all resources:

```bash
# Delete Cloud Function
gcloud functions delete trading_function --region=us-central1

# Delete Cloud Scheduler job
gcloud scheduler jobs delete trading-bot-daily --location=us-central1
```

## Next Steps

- Monitor the bot's performance for a few days
- Adjust risk parameters based on results
- Implement additional strategies
- Scale to more symbols gradually
- Consider implementing a web dashboard for monitoring

## Support

- [Google Cloud Functions Documentation](https://cloud.google.com/functions/docs)
- [Cloud Scheduler Documentation](https://cloud.google.com/scheduler/docs)
- [Alpaca API Support](https://alpaca.markets/support)
