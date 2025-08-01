# Test Suite Organization

This directory contains all test files for the Doctor Procedures Bedrock App, organized by test type and purpose.

## 📁 Directory Structure

```
tests/
├── unit/                    # Unit tests (no external dependencies)
│   ├── test_local.py       # Local Lambda function tests
│   └── test_get_quote_local.py  # Local quote functionality tests
├── integration/             # Integration tests (require deployed services)
│   └── test_get_quote_api.py    # API endpoint integration tests
├── events/                  # Test event JSON files
│   ├── simple_test.json    # Simple test payload
│   ├── test_clean.json     # Clean test event
│   ├── test_get_quote_median.json  # Quote median test event
│   ├── test_payload.json   # Standard test payload
│   └── test_payload_simple.json   # Simplified test payload
├── scripts/                 # Setup and utility scripts
│   └── test_setup.sh       # Environment setup script
└── README.md               # This file
```

## 🧪 Test Categories

### Unit Tests (`tests/unit/`)
Tests that run independently without requiring AWS services or external dependencies:
- **test_local.py**: Tests Lambda function logic locally
- **test_get_quote_local.py**: Tests quote calculation logic

**Run individually:**
```bash
python3 tests/unit/test_local.py
python3 tests/unit/test_get_quote_local.py
```

### Integration Tests (`tests/integration/`)
Tests that require deployed AWS services and test end-to-end functionality:
- **test_get_quote_api.py**: Tests the deployed API Gateway endpoints

**Run individually:**
```bash
python3 tests/integration/test_get_quote_api.py
```

### Test Events (`tests/events/`)
JSON files containing test payloads for various scenarios:
- **simple_test.json**: Basic test event
- **test_clean.json**: Clean/reset test event
- **test_get_quote_median.json**: Quote calculation test
- **test_payload.json**: Standard API test payload
- **test_payload_simple.json**: Simplified API test payload

### Setup Scripts (`tests/scripts/`)
Utility scripts for test environment setup:
- **test_setup.sh**: Validates environment and prerequisites

## 🚀 Running Tests

### Run All Tests
```bash
./run_tests.sh
```

### Run Specific Test Categories
```bash
# Unit tests only
python3 tests/unit/test_local.py

# Integration tests only
python3 tests/integration/test_get_quote_api.py

# Setup validation
bash tests/scripts/test_setup.sh
```

### Run SAM Local Tests
```bash
# Build and test with SAM
sam build
sam validate

# Test specific Lambda functions
sam local invoke AddDoctorProcedureFunction --event events/add_doctor_event.json
sam local invoke GetQuoteFunction --event events/get_quote_event.json
sam local invoke ShowHistoryFunction --event events/show_history_event.json
```

## 📋 Test Requirements

### Prerequisites
- Python 3.7+
- AWS CLI configured
- AWS SAM CLI (for Lambda tests)
- Virtual environment activated (`source venv/bin/activate`)

### Environment Variables
Some tests may require:
- `DYNAMODB_TABLE_NAME`: DynamoDB table name
- `AWS_REGION`: AWS region (default: us-east-1)

### Dependencies
Install test dependencies:
```bash
pip install requests boto3
```

## 🔧 Adding New Tests

### Unit Tests
Add new unit tests to `tests/unit/`:
1. Create `test_<feature>.py`
2. Import required modules
3. Add test functions with descriptive names
4. Update this README

### Integration Tests
Add new integration tests to `tests/integration/`:
1. Create `test_<feature>_api.py`
2. Test deployed endpoints
3. Include error handling scenarios
4. Update this README

### Test Events
Add new test events to `tests/events/`:
1. Create `<scenario>_test.json`
2. Include realistic test data
3. Document the test scenario
4. Update this README

## 🐛 Troubleshooting

### Common Issues
1. **Permission errors**: Ensure AWS credentials are configured
2. **Import errors**: Activate virtual environment and install dependencies
3. **Timeout errors**: Check AWS services are deployed and accessible
4. **Rate limiting**: Wait between Bedrock API calls (see RATE_LIMITING_GUIDE.md)

### Debug Commands
```bash
# Check AWS configuration
aws sts get-caller-identity

# Validate SAM template
sam validate

# Check Python imports
python3 -c "import boto3; print('boto3 available')"
```

## 📊 Test Coverage

Current test coverage includes:
- ✅ Lambda function basic validation
- ✅ API endpoint integration
- ✅ DynamoDB operations (mocked)
- ✅ Error handling scenarios
- ✅ Bedrock Agent integration
- ⚠️ Frontend testing (manual)
- ❌ Load testing (not implemented)

## 🎯 Future Improvements

Planned test enhancements:
- [ ] Automated frontend testing
- [ ] Load testing scenarios
- [ ] Continuous integration setup
- [ ] Test data management
- [ ] Performance benchmarking
