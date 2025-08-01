#!/bin/bash

# Frontend Setup Script
# Sets up and starts the React frontend for Doctor Procedures App

set -e

echo "🚀 Setting up Doctor Procedures Frontend..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed."
    echo "Please install Node.js from https://nodejs.org/"
    exit 1
fi

NODE_VERSION=$(node --version)
echo "✅ Found Node.js $NODE_VERSION"

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is required but not installed."
    exit 1
fi

NPM_VERSION=$(npm --version)
echo "✅ Found npm $NPM_VERSION"

# Navigate to frontend directory
cd "$(dirname "$0")"

# Install dependencies
echo "📦 Installing dependencies..."
npm install

# Check if installation was successful
if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo ""
echo "🎯 Setup complete! You can now:"
echo ""
echo "1. Start development server:"
echo "   npm start"
echo ""
echo "2. Build for production:"
echo "   npm run build"
echo ""
echo "3. Run tests:"
echo "   npm test"
echo ""
echo "The app will connect to: https://jj6skt98b3.execute-api.us-east-1.amazonaws.com/dev"
echo ""
echo "🌟 Ready to go! The frontend will be available at http://localhost:3000"
