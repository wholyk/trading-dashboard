# Quick Start Guide

Get up and running with Trading Dashboard in 5 minutes.

## Prerequisites

- Python 3.8 or higher
- pip package manager
- Internet connection

## Installation

### Option 1: Automated Setup (Recommended)

```bash
# Clone the repository
git clone https://github.com/wholyk/trading-dashboard.git
cd trading-dashboard

# Run setup script
./setup.sh
```

### Option 2: Manual Setup

```bash
# Clone the repository
git clone https://github.com/wholyk/trading-dashboard.git
cd trading-dashboard

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create configuration
cp config.yaml.example config.yaml
```

## Running the Dashboard

```bash
# Make sure virtual environment is activated
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Start the dashboard
streamlit run streamlit_app.py
```

The dashboard will open in your browser at `http://localhost:8501`

## First Steps

### 1. Explore Market Overview

- View major market indices (S&P 500, Dow Jones, NASDAQ)
- See current market status

### 2. Analyze a Stock

1. Navigate to "Stock Analysis"
2. Enter a ticker symbol (e.g., AAPL, GOOGL, MSFT)
3. Select timeframe and interval
4. Choose technical indicators to display
5. Explore the interactive chart

### 3. Build Your Portfolio

1. Navigate to "Portfolio"
2. Add your first holding:
   - Enter ticker symbol
   - Number of shares
   - Purchase price
   - Purchase date
3. View your portfolio performance

### 4. Create a Watchlist

1. Navigate to "Watchlist"
2. Add tickers you want to monitor
3. View real-time prices and changes

## Common Ticker Symbols

### Tech Giants
- AAPL - Apple Inc.
- GOOGL - Alphabet Inc.
- MSFT - Microsoft Corporation
- AMZN - Amazon.com Inc.
- META - Meta Platforms Inc.

### Market Indices
- ^GSPC - S&P 500
- ^DJI - Dow Jones Industrial Average
- ^IXIC - NASDAQ Composite

### Popular Stocks
- TSLA - Tesla Inc.
- NVDA - NVIDIA Corporation
- JPM - JPMorgan Chase & Co.
- V - Visa Inc.
- WMT - Walmart Inc.

## Keyboard Shortcuts

- `Ctrl+C` - Stop the server
- `R` - Refresh the page (in browser)

## Configuration

Edit `config.yaml` to customize:
- Default ticker symbols
- Technical indicator parameters
- Chart appearance
- UI preferences

## Troubleshooting

### Dashboard won't start

```bash
# Verify installation
python validate.py

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Data not loading

- Check internet connection
- Verify ticker symbol is correct
- Wait a moment and refresh if rate limited

### Port already in use

```bash
# Use a different port
streamlit run streamlit_app.py --server.port 8502
```

## Next Steps

- Read the full [README.md](README.md) for detailed information
- Check [ARCHITECTURE.md](ARCHITECTURE.md) to understand the system
- Review [CONTRIBUTING.md](CONTRIBUTING.md) to contribute
- Run tests: `python -m pytest tests/ -v`

## Getting Help

- Check existing issues on GitHub
- Review documentation
- Open a new issue with:
  - Clear description of the problem
  - Steps to reproduce
  - Expected vs actual behavior
  - System information

## Resources

- [Streamlit Documentation](https://docs.streamlit.io/)
- [Yahoo Finance API](https://finance.yahoo.com/)
- [Plotly Documentation](https://plotly.com/python/)
- [Technical Analysis Indicators](https://www.investopedia.com/technical-analysis-4689657)

---

**Disclaimer**: This dashboard is for educational and informational purposes only. It is not financial advice. Always consult with a qualified financial advisor before making investment decisions.
