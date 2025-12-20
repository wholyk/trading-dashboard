# Quick Start Guide

Get your automated trading bot up and running in 5 minutes.

## Prerequisites

- Python 3.11 or higher
- Alpaca account (free at [alpaca.markets](https://alpaca.markets/))

## Step 1: Get Your API Credentials

1. Sign up at [Alpaca](https://alpaca.markets/)
2. Go to your dashboard
3. Navigate to "API Keys" section
4. Create a new API key (or use existing one)
5. Copy your API Key ID and Secret Key

## Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 3: Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your credentials
nano .env  # or use your favorite editor
```

Add your Alpaca credentials:
```
APCA_API_KEY_ID=your_actual_api_key
APCA_API_SECRET_KEY=your_actual_secret_key
TRADING_SYMBOLS=AAPL,MSFT,GOOGL,AMZN
PAPER_TRADING=true
```

## Step 4: Run Your First Test

```bash
# Test the bot locally
python examples.py
```

This will show you example outputs without making real trades.

## Step 5: Run the Bot

```bash
# Run the trading bot
python trading_bot.py
```

The bot will:
- Connect to Alpaca's paper trading API
- Analyze the configured symbols
- Execute trades based on the strategy
- Log all actions

## What's Happening?

The bot implements a Moving Average Crossover strategy:
- **Buy Signal**: When the 10-day moving average crosses above the 30-day moving average
- **Sell Signal**: When the 10-day moving average crosses below the 30-day moving average
- **Stop Loss**: Automatically set at 2% below entry price

## Risk Management

The bot includes automatic risk management:
- Maximum 2% risk per trade
- Maximum 20% position size
- Stops trading if portfolio drops 10% from peak

## Next Steps

### Test with Paper Trading

Keep `PAPER_TRADING=true` in your `.env` file and run the bot multiple times to see how it performs.

### Set Up Automation

Follow the [DEPLOYMENT.md](DEPLOYMENT.md) guide to deploy to Google Cloud and run automatically on a schedule.

### Monitor Performance

Check the logs to see:
- Which trades were made
- Why they were made
- Any errors or issues

### Customize

Edit the configuration in `.env`:
- Change `TRADING_SYMBOLS` to trade different stocks
- Adjust risk parameters
- Configure email notifications

## Testing

Run the test suite to verify everything works:

```bash
python test_trading_bot.py
```

## Safety First

⚠️ **Important Safety Notes:**

1. **Start with Paper Trading**: Always test with paper trading first
2. **Small Positions**: Start with small position sizes when going live
3. **Monitor Closely**: Watch the bot's behavior for the first few weeks
4. **Have a Kill Switch**: Know how to stop the bot if needed
5. **Never Risk More Than You Can Afford to Lose**: Trading is risky

## Getting Help

If you encounter issues:

1. Check the logs in the console output
2. Review the [README.md](README.md) for detailed documentation
3. Make sure your API credentials are correct
4. Ensure you have sufficient buying power in your account

## Troubleshooting

### "No module named 'alpaca_trade_api'"
```bash
pip install alpaca-trade-api
```

### "API credentials not provided"
Make sure you've created a `.env` file with your credentials.

### "Connection error"
Check your internet connection and verify your API credentials are correct.

## Example Output

When running successfully, you should see output like:

```
INFO - TradingBot initialized (paper_trading=True)
INFO - Starting trading execution for symbols: ['AAPL', 'MSFT', 'GOOGL']
INFO - Account info: equity=$100000.00, cash=$100000.00
INFO - Retrieved 100 bars for AAPL
INFO - Order placed: buy 50 AAPL - Order ID: abc123
INFO - Trading execution completed. Orders placed: 1
```

## Going Live

When you're ready to trade with real money:

1. Test thoroughly with paper trading (at least 2-4 weeks)
2. Review all trades and ensure the logic is sound
3. Set `PAPER_TRADING=false` in `.env`
4. Start with very small position sizes
5. Monitor closely for the first few weeks

**Remember**: This is your money at risk. Proceed carefully and responsibly.

## Additional Resources

- [Full Documentation](README.md)
- [Deployment Guide](DEPLOYMENT.md)
- [Example Code](examples.py)
- [Alpaca Documentation](https://alpaca.markets/docs/)
