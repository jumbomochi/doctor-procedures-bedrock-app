#!/bin/bash

# run_tests.sh - Test script for Doctor Procedures Bedrock App

set -e

echo "🧪 Running Doctor Procedures Bedrock App Tests"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "🔌 Activating virtual environment..."
    source venv/bin/activate
else
    echo "⚠️ Virtual environment not found. Run ./setup_env.sh first"
    exit 1
fi

# Check if SAM is available
if ! command -v sam &> /dev/null; then
    echo "❌ AWS SAM CLI not found. Please install it first."
    exit 1
fi

echo "✅ AWS SAM CLI found"

# Build the application
echo "🔨 Building SAM application..."
sam build

# Validate the template
echo "✅ Validating SAM template..."
sam validate

# Test individual Lambda functions
echo "🔍 Testing Lambda functions locally..."

echo "📝 Testing Add Doctor Procedure Lambda..."
sam local invoke AddDoctorProcedureFunction --event events/add_doctor_event.json

echo "💰 Testing Get Quote Lambda..."
sam local invoke GetQuoteFunction --event events/get_quote_event.json

echo "📊 Testing Show History Lambda..."
sam local invoke ShowHistoryFunction --event events/show_history_event.json

echo "✅ All tests completed successfully!"
echo ""
echo "To start the local API server, run:"
echo "  sam local start-api --port 3000"
echo ""
echo "To test with DynamoDB Local, first start DynamoDB:"
echo "  docker run -p 8000:8000 amazon/dynamodb-local"
echo "Then populate dummy data:"
echo "  python3 populate_dummy_data.py"
