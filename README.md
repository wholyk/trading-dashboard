# TradingView Chart Analyzer

A Python module for analyzing TradingView screenshots to detect liquidity sweeps and Break of Structure (BOS) patterns using computer vision techniques.

## Features

- **Screenshot Upload**: Accept TradingView screenshots in PNG, JPG, or JPEG format
- **Liquidity Sweep Detection**: Identifies wick patterns and price spike formations that indicate liquidity sweeps
- **Break of Structure (BOS) Detection**: Detects support/resistance breaks and directional momentum changes
- **Confidence Scoring**: Returns confidence scores (0-1) for detected patterns
- **Logging System**: Logs all analyses with screenshot hash, timestamp, and results
- **Interactive Dashboard**: Streamlit-based UI for easy use

## Installation

Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Streamlit Dashboard

Run the interactive dashboard:

```bash
streamlit run streamlit_app.py
```

Then upload a TradingView screenshot and click "Analyze Chart" to see the results.

### Python Module

Use the chart analyzer directly in your Python code:

```python
from chart_analyzer import ChartAnalyzer

# Create analyzer instance
analyzer = ChartAnalyzer()

# Read image file
with open('screenshot.png', 'rb') as f:
    image_data = f.read()

# Analyze the screenshot
results = analyzer.analyze_screenshot(image_data, filename='screenshot.png')

# Access results
print(f"Liquidity Sweep Confidence: {results['liquidity_sweep']['confidence']}")
print(f"BOS Confidence: {results['break_of_structure']['confidence']}")
print(f"Overall Confidence: {results['overall_confidence']}")
print(f"Image Hash: {results['image_hash']}")

# View analysis log
log = analyzer.get_analysis_log()
for entry in log:
    print(entry)
```

### Convenience Function

For one-off analysis without creating an analyzer instance:

```python
from chart_analyzer import analyze_chart

with open('screenshot.png', 'rb') as f:
    image_data = f.read()

results = analyze_chart(image_data, filename='screenshot.png')
```

## How It Works

### Liquidity Sweep Detection

The module detects liquidity sweeps by analyzing:
- **Wick Patterns**: Identifies thin, tall vertical structures that indicate price spikes
- **Edge Density**: Measures the concentration of edges in the image
- **Significant Wicks**: Counts larger wicks that suggest strong reversals

### Break of Structure Detection

BOS detection analyzes:
- **Horizontal Lines**: Identifies potential support/resistance levels
- **Gradient Analysis**: Measures directional strength using Sobel operators
- **Color Analysis**: Detects bullish (green) and bearish (red) regions to identify market sentiment

### Confidence Scoring

Confidence scores are calculated by combining multiple metrics:
- **Liquidity Sweep Confidence**: Weighted combination of wick score (40%), significant wick score (40%), and edge score (20%)
- **BOS Confidence**: Weighted combination of structure line score (30%), gradient score (40%), and color score (30%)
- **Overall Confidence**: Average of both pattern confidences

## Output Format

The `analyze_screenshot()` method returns a dictionary with:

```python
{
    'filename': str,              # Name of the analyzed file
    'image_hash': str,            # SHA-256 hash of the image
    'timestamp': str,             # ISO format timestamp
    'image_size': tuple,          # (width, height) in pixels
    'liquidity_sweep': {
        'confidence': float,      # 0-1 confidence score
        'metrics': dict          # Detailed detection metrics
    },
    'break_of_structure': {
        'confidence': float,      # 0-1 confidence score
        'metrics': dict          # Detailed detection metrics
    },
    'overall_confidence': float   # 0-1 combined confidence score
}
```

## Logging

All analyses are automatically logged with:
- Timestamp
- Image hash (SHA-256)
- Filename
- Confidence scores for each pattern
- Overall confidence

Access logs via:
```python
analyzer.get_analysis_log()  # Returns list of log entries
analyzer.clear_log()         # Clears the log
```

## Requirements

- Python 3.8+
- streamlit >= 1.28
- Pillow >= 10.2.0
- opencv-python >= 4.8.1.78
- numpy >= 1.25.0
- pandas >= 2.1.0

## Security

The module uses secure hashing (SHA-256) for screenshot identification and follows security best practices for image processing.

## License

This project is provided as-is for educational and analytical purposes.
