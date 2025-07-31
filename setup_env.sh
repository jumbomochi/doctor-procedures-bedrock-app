#!/bin/bash

# setup_env.sh - Set up the development environment for the Doctor Procedures Bedrock App

set -e

echo "🚀 Setting up Doctor Procedures Bedrock App Development Environment"

# Check if Python 3.11+ is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✅ Found Python $PYTHON_VERSION"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Check if AWS SAM CLI is available
if ! command -v sam &> /dev/null; then
    echo "⚠️ AWS SAM CLI not found. Installing via pip..."
    pip install aws-sam-cli
else
    echo "✅ AWS SAM CLI found"
fi

# Create local test directories
echo "📁 Creating test directories..."
mkdir -p tests
mkdir -p .aws-sam

echo "✅ Environment setup complete!"
echo ""
echo "To activate the virtual environment in the future, run:"
echo "  source venv/bin/activate"
echo ""
echo "To test the setup, run:"
echo "  ./run_tests.sh"
echo ""
echo "To start local development, run:"
echo "  sam local start-api --port 3000"
