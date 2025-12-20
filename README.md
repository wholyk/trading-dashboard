# Automated Day Trading System

An automated day trading system that connects to Alpaca's API, implements trading strategies, manages risk, and can be deployed to Google Cloud Functions for scheduled execution.

## Features

- **Alpaca API Integration**: Connect to Alpaca's commission-free trading platform
- **Risk Management**: Comprehensive position sizing, stop-loss management, and drawdown controls
- **Trading Strategies**: Configurable strategies including moving average crossover
- **Backtesting**: Test strategies on historical data before live trading
- **Cloud Deployment**: Ready for Google Cloud Functions deployment
- **Monitoring & Alerts**: Email notifications for trade execution and alerts
- **Paper Trading**: Test safely with paper trading before going live

## Installation

1. Clone the repository:
```bash
git clone https://github.com/wholyk/trading-dashboard.git
cd trading-dashboard
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your API credentials
```

## Configuration

### Alpaca API Setup

1. Create an account at [Alpaca](https://alpaca.markets/)
2. Get your API key and secret from the dashboard
3. Add credentials to `.env`:
   ```
   APCA_API_KEY_ID=your_api_key
   APCA_API_SECRET_KEY=your_api_secret
   ```

### Email Notifications (Optional)

For Gmail, you'll need to:
1. Enable 2-factor authentication
2. Create an [App Password](https://support.google.com/accounts/answer/185833)
3. Add to `.env`:
   ```
   SENDER_EMAIL=your_email@gmail.com
   SENDER_PASSWORD=your_app_password
   RECIPIENT_EMAIL=recipient@example.com
   ```

## Usage

### Local Testing

Run the trading bot locally:
```bash
python trading_bot.py
```

### Backtesting

Run backtests on historical data:
```bash
python backtesting.py
```

### Test Notifications

Verify email notification setup:
```bash
python notifications.py
```

## Risk Management

The system implements several risk management strategies:

1. **Position Sizing**: Limits risk to 1-2% of portfolio per trade
2. **Stop-Loss Management**: Automatic stop-loss orders (2% default)
3. **Maximum Drawdown**: Halts trading if portfolio drops 10% from peak
4. **Maximum Position Size**: Limits single position to 20% of portfolio
5. **Volatility Adjustments**: Scales positions based on market conditions

Configure risk parameters in `.env`:
```
MAX_RISK_PER_TRADE=0.02
MAX_DRAWDOWN=0.10
MAX_POSITION_SIZE=0.20
```

## Trading Strategies

### Moving Average Crossover (Default)

- Uses 10-day and 30-day moving averages
- Buy signal: Short MA crosses above Long MA
- Sell signal: Short MA crosses below Long MA
- Stop-loss: 2% below entry price

You can implement additional strategies by extending the `TradingStrategy` class.

## Cloud Deployment

### Google Cloud Functions

1. Install Google Cloud SDK:
```bash
curl https://sdk.cloud.google.com | bash
gcloud init
```

2. Deploy the function:
```bash
gcloud functions deploy trading_function \
  --runtime python311 \
  --trigger-http \
  --entry-point trading_function \
  --allow-unauthenticated \
  --set-env-vars APCA_API_KEY_ID=your_key,APCA_API_SECRET_KEY=your_secret
```

3. Create a Cloud Scheduler job:
```bash
gcloud scheduler jobs create http trading-bot-daily \
  --schedule="0 9 * * 1-5" \
  --uri="https://YOUR_REGION-YOUR_PROJECT.cloudfunctions.net/trading_function" \
  --http-method=GET
```

The example schedule runs at 9 AM on weekdays (Monday-Friday).

### Environment Variables in Cloud

Set environment variables during deployment:
```bash
gcloud functions deploy trading_function \
  --set-env-vars APCA_API_KEY_ID=your_key,APCA_API_SECRET_KEY=your_secret,TRADING_SYMBOLS=AAPL,MSFT,GOOGL
```

## Project Structure

```
trading-dashboard/
├── trading_bot.py        # Main trading bot implementation
├── main.py              # Cloud Function entry point
├── backtesting.py       # Backtesting engine
├── notifications.py     # Email notifications and alerts
├── requirements.txt     # Python dependencies
├── .env.example        # Example environment configuration
└── README.md           # This file
```

## Security Best Practices

- **Never commit API keys**: Always use environment variables
- **Use paper trading**: Test thoroughly before live trading
- **Start small**: Begin with small position sizes
- **Monitor closely**: Watch the bot's behavior especially in the beginning
- **Set alerts**: Configure notifications for errors and drawdowns

## Monitoring

The system provides:
- **Execution summaries**: Email reports after each trading session
- **Error alerts**: Immediate notification of issues
- **Drawdown warnings**: Alerts when portfolio value drops
- **Trading logs**: Detailed logging for debugging

## Disclaimer

**This software is for educational purposes only. Trading involves substantial risk of loss. Past performance does not guarantee future results. The authors are not responsible for any financial losses incurred through use of this software. Always consult with financial professionals before trading with real money.**

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is provided as-is for educational purposes.

## Support

For issues and questions, please open an issue on GitHub.

## Resources

- [Alpaca API Documentation](https://alpaca.markets/docs/)
- [Alpaca Algorithmic Trading Guide](https://alpaca.markets/learn/algorithmic-trading-bot-7-steps)
- [Risk Management Strategies](https://nurp.com/wisdom/7-risk-management-strategies-for-algorithmic-trading/)
- [Google Cloud Functions Documentation](https://cloud.google.com/functions/docs)
