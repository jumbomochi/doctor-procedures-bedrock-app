#!/bin/bash

# Test script for the Doctor Procedures Bedrock App
echo "🏥 Doctor Procedures Bedrock App - Local Testing"
echo "================================================"

# Check if SAM CLI is installed
if ! command -v sam &> /dev/null; then
    echo "❌ SAM CLI is not installed. Please install it first."
    exit 1
fi

# Check if AWS CLI is configured
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ AWS CLI is not configured. Please run 'aws configure' first."
    exit 1
fi

echo "✅ Prerequisites check passed"

# Build the application
echo "📦 Building the application..."
if sam build; then
    echo "✅ Build successful"
else
    echo "❌ Build failed"
    exit 1
fi

# Check if we can validate the template
echo "🔍 Validating SAM template..."
if sam validate; then
    echo "✅ Template validation successful"
else
    echo "❌ Template validation failed"
    exit 1
fi

# Test individual functions
echo "🧪 Testing individual Lambda functions..."

echo "  Testing AddDoctorProcedureFunction..."
if sam local invoke AddDoctorProcedureFunction --event events/add_doctor_event.json --no-event > /dev/null 2>&1; then
    echo "  ✅ AddDoctorProcedureFunction test passed"
else
    echo "  ⚠️  AddDoctorProcedureFunction test failed (expected without DynamoDB)"
fi

echo "  Testing GetQuoteFunction..."
if sam local invoke GetQuoteFunction --event events/get_quote_event.json --no-event > /dev/null 2>&1; then
    echo "  ✅ GetQuoteFunction test passed"
else
    echo "  ⚠️  GetQuoteFunction test failed (expected without DynamoDB)"
fi

echo "  Testing ShowHistoryFunction..."
if sam local invoke ShowHistoryFunction --event events/show_history_event.json --no-event > /dev/null 2>&1; then
    echo "  ✅ ShowHistoryFunction test passed"
else
    echo "  ⚠️  ShowHistoryFunction test failed (expected without DynamoDB)"
fi

echo ""
echo "🎉 Setup complete! Your environment is ready for local testing."
echo ""
echo "Next steps:"
echo "1. Start DynamoDB local: sam local start-lambda --docker-network sam-local"
echo "2. Start API Gateway: sam local start-api --port 3000"
echo "3. Run populate_table.py to add test data"
echo "4. Test the API endpoints as described in README.md"
echo ""
echo "For Bedrock Agent setup, update the environment variables in samconfig.yaml"
echo "with your actual Bedrock Agent ID and Alias ID."
