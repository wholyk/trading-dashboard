#!/bin/bash

# Trading Dashboard - Setup Script
# This script automates the setup process for the Trading Dashboard

set -e  # Exit on error

echo "=========================================="
echo "Trading Dashboard - Setup Script"
echo "=========================================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python --version 2>&1 | grep -oP '\d+\.\d+')
min_version="3.8"

if [ "$(printf '%s\n' "$min_version" "$python_version" | sort -V | head -n1)" != "$min_version" ]; then
    echo "Error: Python $min_version or higher is required. Found: $python_version"
    exit 1
fi

echo "✓ Python $python_version detected"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
if [ -d ".venv" ]; then
    echo "⚠ Virtual environment already exists. Skipping creation."
else
    python -m venv .venv
    echo "✓ Virtual environment created"
fi
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
    echo "✓ Virtual environment activated"
elif [ -f ".venv/Scripts/activate" ]; then
    source .venv/Scripts/activate
    echo "✓ Virtual environment activated"
else
    echo "Error: Could not find activation script"
    exit 1
fi
echo ""

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt
echo "✓ Dependencies installed"
echo ""

# Create config file if not exists
echo "Setting up configuration..."
if [ -f "config.yaml" ]; then
    echo "⚠ config.yaml already exists. Skipping."
else
    cp config.yaml.example config.yaml
    echo "✓ config.yaml created from example"
fi
echo ""

# Run validation
echo "Running validation checks..."
python validate.py
echo ""

# Display completion message
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "To start the Trading Dashboard:"
echo "  1. Activate the virtual environment:"
echo "     source .venv/bin/activate"
echo ""
echo "  2. Run the dashboard:"
echo "     streamlit run streamlit_app.py"
echo ""
echo "The dashboard will open in your browser at http://localhost:8501"
echo ""
echo "For more information, see README.md"
echo ""
