# Quick Start Guide

## 🚀 Doctor Procedures Bedrock App - Development Setup Complete!

Your virtual environment and project structure are now ready for development and testing.

## ✅ What's Been Set Up

- ✅ Python virtual environment (`venv/`)
- ✅ AWS SAM CLI installed and configured
- ✅ All dependencies installed (boto3, pytest, black, flake8, etc.)
- ✅ Lambda functions for all three intents
- ✅ SAM template with DynamoDB table and API Gateway
- ✅ Test events and dummy data
- ✅ Local testing scripts

## 📁 Project Structure

```
doctor-procedures-bedrock-app/
├── 🐍 venv/                     # Virtual environment
├── 📋 template.yaml             # SAM infrastructure template
├── ⚙️ samconfig.yaml            # SAM configuration
├── 📦 requirements.txt          # Python dependencies
├── 🧪 test_local.py             # Local tests (no Docker needed)
├── 🏃 run_tests.sh             # Full test suite (requires Docker)
├── 🛠️ setup_env.sh             # Environment setup script
├── 📊 populate_dummy_data.py    # DynamoDB test data script
├── 🚮 .gitignore               # Git ignore file
└── functions/                   # Lambda functions
    ├── 🤖 bedrock_intent_mapper_lambda/
    ├── ➕ add_doctor_procedure/
    ├── 💰 get_quote_lambda/
    └── 📈 show_history_lambda/
```

## 🔧 Available Commands

### Activate Virtual Environment
```bash
source venv/bin/activate
```

### Run Local Tests (No Docker Required)
```bash
python3 test_local.py
```

### Build SAM Application
```bash
sam build
```

### Start Local API (Requires Docker)
```bash
sam local start-api --port 3000
```

### Run Full Tests (Requires Docker)
```bash
./run_tests.sh
```

## 🐳 Docker Setup (Optional for Full Local Testing)

If you want to run the full local testing with DynamoDB:

1. **Install Docker Desktop** from https://docker.com
2. **Start DynamoDB Local:**
   ```bash
   docker run -p 8000:8000 amazon/dynamodb-local
   ```
3. **Populate test data:**
   ```bash
   python3 populate_dummy_data.py
   ```

## 🌐 API Endpoints (When Running Locally)

- `POST http://localhost:3000/intent-mapper` - Bedrock intent mapping
- `POST http://localhost:3000/add-doctor-procedure` - Add procedure
- `GET http://localhost:3000/get-quote?procedureCode=CONSULT001` - Get quote
- `GET http://localhost:3000/show-history?doctorName=Dr.%20Alice%20Smith` - Show history

## 🧠 Bedrock Agent Setup

### Three Main Intents

1. **AddProcedureIntent**
   - Example: "Add a consultation for Dr. Smith with code CONSULT001 that costs $150"
   - Action Group: Uses `functions/add_doctor_procedure/`
   - OpenAPI Schema: `openapi_schemas/addDoctorProcedure.yaml`

2. **GetQuoteIntent**
   - Example: "What's the cost for procedure CONSULT001?"
   - Action Group: Uses `functions/get_quote_lambda/`
   - OpenAPI Schema: `openapi_schemas/getQuote.yaml`

3. **ShowHistoryIntent**
   - Example: "Show me Dr. Smith's recent procedures"
   - Action Group: Uses `functions/show_history_lambda/`
   - OpenAPI Schema: `openapi_schemas/showHistory.yaml`

4. **FallbackIntent**
   - Handles unrecognized requests with helpful guidance

### Configuration Steps

1. Create a new Bedrock Agent
2. Set up Action Groups for each intent using the OpenAPI schemas
3. Configure intent recognition with example phrases
4. Update `samconfig.yaml` with your Bedrock Agent ID and Alias ID
5. Deploy the application: `sam deploy --guided`

## 🧪 Testing Examples

### Test Add Procedure
```bash
curl -X POST http://localhost:3000/add-doctor-procedure \
  -H "Content-Type: application/json" \
  -d '{
    "doctorName": "Dr. Alice Smith",
    "procedureCode": "CONSULT001",
    "procedureName": "Initial Consultation",
    "cost": 150.00
  }'
```

### Test Get Quote
```bash
curl "http://localhost:3000/get-quote?procedureCode=CONSULT001"
```

### Test Show History
```bash
curl "http://localhost:3000/show-history?doctorName=Dr.%20Alice%20Smith&limit=5"
```

### Test Intent Mapper
```bash
curl -X POST http://localhost:3000/intent-mapper \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Add a consultation for Dr. Smith with code CONSULT001 that costs $150",
    "sessionId": "test-session-123"
  }'
```

## 🚀 Deploy to AWS

1. **Configure AWS credentials:**
   ```bash
   aws configure
   ```

2. **Deploy with guided setup:**
   ```bash
   sam deploy --guided
   ```

3. **Update Bedrock Agent** with the deployed Lambda function ARNs

## 📝 Development Workflow

1. **Activate environment:** `source venv/bin/activate`
2. **Make code changes** to Lambda functions
3. **Test locally:** `python3 test_local.py`
4. **Build:** `sam build`
5. **Test with Docker:** `sam local start-api --port 3000`
6. **Deploy:** `sam deploy`

## 🆘 Troubleshooting

- **Import errors:** Make sure virtual environment is activated
- **Docker issues:** Install Docker Desktop and make sure it's running
- **SAM build failures:** Try `sam build --use-container`
- **Permission errors:** Run `chmod +x *.sh *.py`

## 📚 Next Steps

1. Set up your Bedrock Agent in the AWS Console
2. Configure the three intents with your OpenAPI schemas
3. Test the intent mapping functionality
4. Deploy to production
5. Add monitoring and logging
6. Extend with additional intents as needed

Happy coding! 🎉
