#!/bin/bash

# Launch script for Doctor Procedures React App
# This script sets up the environment and starts the development server

set -e

echo "🚀 Starting Doctor Procedures React App..."

# Check if we're in the frontend directory
if [ ! -f "package.json" ]; then
    echo "Error: Please run this script from the frontend directory"
    echo "Usage: cd frontend && ./launch.sh"
    exit 1
fi

# Create environment file if it doesn't exist
if [ ! -f ".env.local" ]; then
    echo "📝 Creating .env.local from template..."
    cp .env.example .env.local
    echo "✅ Environment file created. You can edit .env.local to customize settings."
fi

# Check if dependencies are installed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Start the development server
echo "🌐 Starting development server..."
echo "The app will open in your browser at http://localhost:3000"
echo "Press Ctrl+C to stop the server"

npm start
