# Contributing to Trading Dashboard

Thank you for your interest in contributing to the Trading Dashboard project!

## Development Setup

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/trading-dashboard.git
   cd trading-dashboard
   ```

3. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Create your feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Code Standards

### Python Code Style

- Follow PEP 8 guidelines
- Use type hints for function parameters and return values
- Maximum line length: 120 characters
- Use meaningful variable and function names
- Add docstrings for all public functions and classes

### Example:

```python
def calculate_return(initial_value: float, final_value: float) -> float:
    """
    Calculate percentage return on investment.
    
    Args:
        initial_value: Initial investment value
        final_value: Final investment value
        
    Returns:
        Percentage return as decimal (0.10 = 10%)
    """
    if initial_value == 0:
        return 0.0
    return (final_value - initial_value) / initial_value
```

## Testing

All new features must include tests.

### Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run tests with coverage
python -m pytest tests/ --cov=src --cov-report=html

# Run specific test file
python -m pytest tests/test_indicators.py -v
```

### Writing Tests

- Place tests in the `tests/` directory
- Name test files with `test_` prefix
- Name test functions with `test_` prefix
- Use fixtures for common setup
- Test both success and failure cases
- Include edge cases

## Pull Request Process

1. **Update tests**: Ensure all tests pass and add new tests for new features
2. **Update documentation**: Update README.md and code comments as needed
3. **Commit messages**: Write clear, concise commit messages
   - Use present tense: "Add feature" not "Added feature"
   - Reference issues: "Fix #123: Resolve portfolio calculation bug"
4. **Pull request description**: Clearly describe:
   - What changes were made
   - Why the changes were made
   - How to test the changes
   - Any breaking changes

## Feature Requests

Open an issue with:
- Clear description of the feature
- Use case and benefits
- Any implementation considerations

## Bug Reports

Open an issue with:
- Clear description of the bug
- Steps to reproduce
- Expected vs actual behavior
- Screenshots if applicable
- Environment details (OS, Python version, etc.)

## Code Review Process

All submissions require review. We use GitHub pull requests for this purpose. The maintainers will:

1. Review code for quality and style
2. Test functionality
3. Provide feedback or approve
4. Merge approved changes

## Areas for Contribution

- **New indicators**: Additional technical indicators
- **Data sources**: Integration with other data providers
- **UI improvements**: Enhanced visualizations and user experience
- **Performance**: Optimization of data fetching and calculations
- **Documentation**: Improved guides and examples
- **Tests**: Increased test coverage

## Questions?

Feel free to open an issue for any questions about contributing.

Thank you for contributing to Trading Dashboard!
