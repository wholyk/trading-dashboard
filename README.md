# Trading Dashboard

A production-ready trading dashboard built with Streamlit for real-time market data visualization, technical analysis, and portfolio tracking.

## Features

- **Real-time Market Data**: Fetch and display live stock data using Yahoo Finance API
- **Technical Analysis**: Multiple technical indicators (SMA, EMA, RSI, MACD, Bollinger Bands)
- **Interactive Charts**: Candlestick charts with volume overlay and customizable timeframes
- **Portfolio Tracking**: Monitor multiple stocks with performance metrics
- **Watchlist Management**: Create and manage custom watchlists
- **Market Overview**: Key market indices and sector performance

## Prerequisites

- Python 3.8 or higher
- pip package manager
- Internet connection for real-time data

## Installation

1. Clone the repository:
```bash
git clone https://github.com/wholyk/trading-dashboard.git
cd trading-dashboard
```

2. Create a virtual environment (recommended):
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

The application uses `config.yaml` for configuration. Default settings are provided, but you can customize:

- Default ticker symbols
- Chart timeframes
- Technical indicator parameters
- UI theme preferences

Copy `config.yaml.example` to `config.yaml` and modify as needed:
```bash
cp config.yaml.example config.yaml
```

## Running the Application

Start the Streamlit server:
```bash
streamlit run streamlit_app.py
```

The dashboard will open in your default browser at `http://localhost:8501`

## Usage

### Market Overview
- View major market indices (S&P 500, Dow Jones, NASDAQ)
- Check sector performance
- Monitor market breadth indicators

### Stock Analysis
1. Enter a ticker symbol (e.g., AAPL, GOOGL, MSFT)
2. Select your preferred timeframe (1D, 5D, 1M, 3M, 6M, 1Y, 5Y)
3. Choose technical indicators to overlay
4. Analyze price patterns and volume

### Portfolio Tracking
1. Add stocks to your portfolio with purchase details
2. Monitor current values and performance
3. View allocation breakdown
4. Track gains/losses

### Watchlist
- Add/remove tickers to your watchlist
- Quick access to favorite stocks
- Real-time price updates

## Project Structure

```
trading-dashboard/
├── streamlit_app.py          # Main application entry point
├── config.yaml               # Configuration file
├── requirements.txt          # Python dependencies
├── src/
│   ├── __init__.py
│   ├── data_fetcher.py      # Yahoo Finance data retrieval
│   ├── indicators.py        # Technical indicator calculations
│   ├── charts.py            # Chart generation utilities
│   ├── portfolio.py         # Portfolio management
│   └── utils.py             # Helper functions
├── tests/
│   ├── __init__.py
│   ├── test_data_fetcher.py
│   ├── test_indicators.py
│   └── test_portfolio.py
└── .streamlit/
    └── config.toml          # Streamlit configuration
```

## Testing

Run the test suite:
```bash
python -m pytest tests/ -v
```

Run tests with coverage:
```bash
python -m pytest tests/ --cov=src --cov-report=html
```

## Error Handling

The application includes comprehensive error handling for:
- Network connectivity issues
- Invalid ticker symbols
- Missing or incomplete data
- API rate limits
- Invalid user inputs

Error messages are user-friendly and provide actionable guidance.

## Development

### Adding New Features

1. Create feature branch: `git checkout -b feature/your-feature`
2. Implement changes with tests
3. Run test suite: `pytest tests/`
4. Submit pull request

### Code Style

- Follow PEP 8 guidelines
- Use type hints for function signatures
- Add docstrings for all public functions
- Keep functions focused and modular

## Troubleshooting

### Data not loading
- Check internet connection
- Verify ticker symbol is valid
- Check if market is open (delayed data outside trading hours)
- Rate limits may apply; wait a moment and retry

### Installation issues
- Ensure Python 3.8+ is installed
- Update pip: `pip install --upgrade pip`
- Try installing dependencies one by one if batch install fails

### Performance issues
- Reduce number of indicators displayed simultaneously
- Use shorter timeframes for better performance
- Close other browser tabs if memory is constrained

## License

MIT License - see LICENSE file for details

## Contributing

Contributions are welcome! Please read CONTRIBUTING.md for guidelines.

## Disclaimer

This dashboard is for educational and informational purposes only. It is not financial advice. Always consult with a qualified financial advisor before making investment decisions. Historical performance does not guarantee future results.

## Support

For issues and questions:
- Open an issue on GitHub
- Check existing documentation
- Review troubleshooting section

## Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Market data from [Yahoo Finance](https://finance.yahoo.com/)
- Technical analysis indicators implemented directly with pandas and NumPy
