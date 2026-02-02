# Trading Dashboard - Architecture Overview

## System Architecture

The Trading Dashboard is built with a modular architecture that separates concerns and promotes maintainability.

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     User Interface Layer                     │
│                    (Streamlit Frontend)                      │
└───────────────────────┬─────────────────────────────────────┘
                        │
┌───────────────────────┴─────────────────────────────────────┐
│                   Application Layer                          │
│              (streamlit_app.py - Main App)                   │
└───────────┬─────────────┬──────────────┬────────────────────┘
            │             │              │
┌───────────┴───┐  ┌──────┴───────┐  ┌──┴──────────────┐
│  Data Layer   │  │ Logic Layer  │  │  Storage Layer  │
├───────────────┤  ├──────────────┤  ├─────────────────┤
│ DataFetcher   │  │ Indicators   │  │ Portfolio       │
│               │  │ Charts       │  │ Watchlist       │
│ (yfinance)    │  │ Utils        │  │ (JSON files)    │
└───────────────┘  └──────────────┘  └─────────────────┘
```

## Module Breakdown

### 1. User Interface Layer (`streamlit_app.py`)

**Responsibility**: Presentation and user interaction

**Components**:
- Page routing and navigation
- Form handling
- Data visualization
- User input validation

**Key Functions**:
- `render_market_overview()`: Display market indices
- `render_stock_analysis()`: Stock chart and technical analysis
- `render_portfolio()`: Portfolio management interface
- `render_watchlist()`: Watchlist management interface

### 2. Data Layer (`src/data_fetcher.py`)

**Responsibility**: External data acquisition and caching

**Key Class**: `DataFetcher`

**Methods**:
- `get_stock_data()`: Fetch historical OHLCV data
- `get_stock_info()`: Get current stock information
- `get_multiple_stocks()`: Batch fetch multiple tickers
- `get_market_indices()`: Fetch market index data
- `validate_ticker()`: Verify ticker exists

**Caching Strategy**:
- Historical data: 60 seconds TTL
- Stock info: 60 seconds TTL
- Multiple stocks: 5 minutes TTL
- Market indices: 1 hour TTL

### 3. Logic Layer

#### Technical Indicators (`src/indicators.py`)

**Responsibility**: Technical analysis calculations

**Key Class**: `TechnicalIndicators`

**Supported Indicators**:
- Moving Averages (SMA, EMA)
- Relative Strength Index (RSI)
- Moving Average Convergence Divergence (MACD)
- Bollinger Bands
- Average True Range (ATR)
- Stochastic Oscillator

**Design Pattern**: All calculations return pandas Series for seamless integration

#### Chart Generation (`src/charts.py`)

**Responsibility**: Interactive visualization

**Key Class**: `ChartGenerator`

**Chart Types**:
- Candlestick charts with volume
- Technical indicator overlays
- Separate indicator charts (RSI, MACD)
- Comparison charts for multiple stocks

**Technology**: Plotly for interactive, responsive charts

#### Utilities (`src/utils.py`)

**Responsibility**: Common helper functions

**Key Functions**:
- Configuration management
- Logging setup
- Data formatting (currency, percentages)
- Input validation
- Error handling

### 4. Storage Layer

#### Portfolio Management (`src/portfolio.py`)

**Responsibility**: User portfolio and watchlist persistence

**Key Classes**:
- `Portfolio`: Manage stock holdings
- `Watchlist`: Manage ticker watchlist

**Storage Format**: JSON files for simplicity and portability

**Operations**:
- CRUD operations for holdings
- Portfolio valuation and performance metrics
- Allocation calculations
- Persistent storage between sessions

## Data Flow

### Stock Analysis Flow

```
User Input (Ticker) 
    → Validation
    → DataFetcher.get_stock_data()
    → TechnicalIndicators.add_all_indicators()
    → ChartGenerator.create_candlestick_chart()
    → Display in UI
```

### Portfolio Update Flow

```
User Action (Add/Remove)
    → Portfolio.add_holding() / remove_holding()
    → Save to JSON
    → DataFetcher.get_stock_info() (for current prices)
    → Portfolio.calculate_portfolio_value()
    → Update UI with new values
```

## Configuration Management

Configuration is loaded from `config.yaml` with the following hierarchy:

1. Load `config.yaml` if exists
2. Fall back to `config.yaml.example`
3. Use sensible defaults in code

Configuration sections:
- `data`: Data fetching parameters
- `indicators`: Technical indicator settings
- `charts`: Visualization preferences
- `ui`: User interface settings
- `portfolio`: Portfolio defaults
- `watchlist`: Watchlist settings
- `market_indices`: List of indices to display

## Error Handling Strategy

### Levels of Error Handling

1. **Function Level**: Try-catch blocks in all functions that interact with external services
2. **User Level**: User-friendly error messages via Streamlit
3. **Logging Level**: Detailed error logs for debugging

### Error Types

- **Network Errors**: Graceful degradation, show cached data if available
- **Invalid Input**: Immediate validation feedback
- **Data Unavailable**: Clear messaging about what data is missing
- **API Rate Limits**: Inform user and suggest retry timing

## Testing Strategy

### Test Coverage

- **Unit Tests**: Individual functions and methods
- **Integration Tests**: Module interactions
- **Validation Tests**: End-to-end functionality checks

### Test Organization

```
tests/
├── test_utils.py          # Utility function tests
├── test_data_fetcher.py   # Data fetching tests
├── test_indicators.py     # Technical indicator tests
└── test_portfolio.py      # Portfolio management tests
```

### Mocking Strategy

- External API calls are mocked in unit tests
- Sample data generation for indicator testing
- Temporary files for storage testing

## Performance Considerations

### Optimization Techniques

1. **Caching**: Streamlit @st.cache_data decorator for expensive operations
2. **Lazy Loading**: Data fetched only when needed
3. **Batch Operations**: Multiple stocks fetched together
4. **Vectorized Calculations**: NumPy and pandas for efficient computation

### Scalability

The current architecture supports:
- Hundreds of portfolio holdings
- Dozens of concurrent ticker analyses
- Years of historical data

For larger scale, consider:
- Database backend (PostgreSQL, SQLite)
- Redis for caching
- Background job processing

## Security Considerations

### Input Validation

- Ticker symbol format validation
- Numeric input bounds checking
- File path sanitization

### Data Protection

- No sensitive credentials stored
- Portfolio data stored locally
- No transmission of personal data

### API Usage

- Respect rate limits
- Use public APIs appropriately
- Handle authentication if required

## Future Enhancements

### Potential Additions

1. **Authentication**: User accounts and cloud sync
2. **Real-time Data**: WebSocket connections for live updates
3. **Alerts**: Price alerts and notifications
4. **Backtesting**: Strategy testing framework
5. **Export**: PDF reports and CSV exports
6. **More Data Sources**: Multiple API integrations
7. **Advanced Analytics**: Machine learning predictions

### Architecture Evolution

For production scale:
```
Frontend (Streamlit/React) 
    ↓
API Gateway
    ↓
Microservices
    ├── Data Service (FastAPI)
    ├── Analysis Service (Python)
    ├── Portfolio Service (FastAPI)
    └── Notification Service
    ↓
Data Stores
    ├── PostgreSQL (Structured data)
    ├── Redis (Cache)
    └── S3 (File storage)
```

## Development Guidelines

### Adding New Features

1. Create module in `src/`
2. Add corresponding tests in `tests/`
3. Update configuration if needed
4. Document in README and code
5. Update validation script

### Code Organization Principles

- **Single Responsibility**: Each module has one clear purpose
- **Dependency Injection**: Pass dependencies explicitly
- **Configuration over Code**: Use config files for settings
- **Fail Fast**: Validate inputs early
- **Defensive Programming**: Handle all error cases

## Deployment

### Local Deployment

```bash
streamlit run streamlit_app.py
```

### Cloud Deployment Options

1. **Streamlit Cloud**: Native platform
2. **Heroku**: Container deployment
3. **AWS**: EC2 or ECS
4. **Docker**: Containerized deployment

### Environment Variables

- `STREAMLIT_SERVER_PORT`: Server port
- `STREAMLIT_SERVER_ADDRESS`: Bind address
- Custom configuration via environment

## Maintenance

### Regular Tasks

- Update dependencies monthly
- Monitor API changes
- Review logs for errors
- Update market indices list
- Backup user data

### Monitoring

- Application logs
- Error tracking
- Performance metrics
- User feedback

---

For more information, see the inline code documentation and README.md.
