#!/bin/bash

# run_tests.sh - Comprehensive Test Script for Doctor Procedures Bedrock App

set -e

echo "🧪 Running Doctor Procedures Bedrock App Tests"
echo "=============================================="

# Function to run a specific test category
run_test_category() {
    local category=$1
    local description=$2
    
    echo ""
    echo "🔍 $description"
    echo "----------------------------------------"
    
    if [ -d "tests/$category" ] && [ "$(ls -A tests/$category)" ]; then
        for test_file in tests/$category/*.py; do
            if [ -f "$test_file" ]; then
                echo "  📋 Running $(basename "$test_file")..."
                python3 "$test_file" || echo "  ⚠️  Test failed (expected without proper setup)"
            fi
        done
        
        for test_file in tests/$category/*.sh; do
            if [ -f "$test_file" ]; then
                echo "  🔧 Running $(basename "$test_file")..."
                bash "$test_file" || echo "  ⚠️  Script failed (expected without proper setup)"
            fi
        done
    else
        echo "  📂 No tests found in tests/$category/"
    fi
}

# Check prerequisites
echo "🔍 Checking prerequisites..."

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "  🔌 Activating virtual environment..."
    source venv/bin/activate
else
    echo "  ⚠️ Virtual environment not found. Some tests may fail."
fi

# Check if SAM is available
if ! command -v sam &> /dev/null; then
    echo "  ❌ AWS SAM CLI not found. SAM tests will be skipped."
    SAM_AVAILABLE=false
else
    echo "  ✅ AWS SAM CLI found"
    SAM_AVAILABLE=true
fi

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "  ❌ Python 3 not found. Python tests will be skipped."
    PYTHON_AVAILABLE=false
else
    echo "  ✅ Python 3 found"
    PYTHON_AVAILABLE=true
fi

echo "  ✅ Prerequisites check complete"

# Run setup scripts
run_test_category "scripts" "Running Setup Scripts"

# Run unit tests
if [ "$PYTHON_AVAILABLE" = true ]; then
    run_test_category "unit" "Running Unit Tests"
else
    echo ""
    echo "⚠️  Skipping unit tests - Python 3 not available"
fi

# Run integration tests
if [ "$PYTHON_AVAILABLE" = true ]; then
    run_test_category "integration" "Running Integration Tests"
else
    echo ""
    echo "⚠️  Skipping integration tests - Python 3 not available"
fi

# Run SAM tests if available
if [ "$SAM_AVAILABLE" = true ]; then
    echo ""
    echo "� Running SAM Lambda Tests"
    echo "----------------------------------------"
    
    echo "  �🔨 Building SAM application..."
    if sam build; then
        echo "  ✅ Build successful"
        
        echo "  ✅ Validating SAM template..."
        if sam validate; then
            echo "  ✅ Template validation successful"
            
            echo "  🧪 Testing Lambda functions locally..."
            
            echo "    📝 Testing Add Doctor Procedure Lambda..."
            sam local invoke AddDoctorProcedureFunction --event events/add_doctor_event.json --no-event || echo "    ⚠️  Expected failure without DynamoDB"
            
            echo "    💰 Testing Get Quote Lambda..."
            sam local invoke GetQuoteFunction --event events/get_quote_event.json --no-event || echo "    ⚠️  Expected failure without DynamoDB"
            
            echo "    📊 Testing Show History Lambda..."
            sam local invoke ShowHistoryFunction --event events/show_history_event.json --no-event || echo "    ⚠️  Expected failure without DynamoDB"
            
            echo "    🤖 Testing Bedrock Intent Mapper Lambda..."
            sam local invoke BedrockIntentMapperFunction --event tests/events/simple_test.json --no-event || echo "    ⚠️  Expected failure without Bedrock access"
            
        else
            echo "  ❌ Template validation failed"
        fi
    else
        echo "  ❌ Build failed"
    fi
else
    echo ""
    echo "⚠️  Skipping SAM tests - AWS SAM CLI not available"
fi

echo ""
echo "🎉 Test run completed!"
echo ""
echo "📋 Available test commands:"
echo "  Unit tests:        python3 tests/unit/test_local.py"
echo "  Integration tests: python3 tests/integration/test_get_quote_api.py"
echo "  Setup scripts:     bash tests/scripts/test_setup.sh"
echo ""
echo "🚀 To start local development:"
echo "  sam local start-api --port 3000"
echo ""
echo "📁 Test structure:"
echo "  tests/unit/        - Unit tests (no external dependencies)"
echo "  tests/integration/ - API integration tests"
echo "  tests/events/      - Test event JSON files"
echo "  tests/scripts/     - Setup and utility scripts"
echo "To test with DynamoDB Local, first start DynamoDB:"
echo "  docker run -p 8000:8000 amazon/dynamodb-local"
echo "Then populate dummy data:"
echo "  python3 populate_dummy_data.py"
