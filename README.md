# Doctor Procedures Bedrock App

A serverless application built with AWS SAM for managing doctor procedures using AWS Bedrock for intent mapping and DynamoDB for data storage.

## 🚀 Quick Start

```bash
# 1. Set up the environment
./setup_env.sh

# 2. Activate virtual environment
source venv/bin/activate

# 3. Test locally (no Docker required)
make test-local

# 4. Build and validate
make build
make validate
```

For complete setup instructions, see [QUICKSTART.md](QUICKSTART.md)

## Architecture

The application consists of:

1. **Bedrock Intent Mapper Lambda** - Routes user intents to appropriate actions
2. **Add Doctor Procedure Lambda** - Adds new medical procedures to the database
3. **Get Quote Lambda** - Retrieves cost estimates for procedures
4. **Show History Lambda** - Shows procedure history for doctors
5. **DynamoDB Table** - Stores procedure data

## Prerequisites

- Python 3.11+
- AWS SAM CLI (installed via setup script)
- Docker (optional, for full local testing)
- AWS CLI configured (for deployment)

## Local Development Setup

### 1. Install Dependencies

```bash
# Install AWS CLI
curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"
sudo installer -pkg AWSCLIV2.pkg -target /

# Install AWS SAM CLI
brew install aws-sam-cli

# Verify installations
aws --version
sam --version
```

### 2. Configure AWS Credentials

```bash
aws configure
# Enter your AWS Access Key ID, Secret Access Key, Region, and Output format
```

### 3. Build the Application

```bash
# Build all Lambda functions
sam build
```

### 4. Start Local DynamoDB

```bash
# Start DynamoDB Local (in a separate terminal)
sam local start-lambda --docker-network sam-local
```

### 5. Start Local API

```bash
# Start the API Gateway locally
sam local start-api --port 3000
```

### 6. Populate Test Data (Optional)

```bash
# Install boto3 locally for the populate script
pip3 install boto3

# Run the populate script (make sure DynamoDB local is running)
python3 populate_table.py
```

## Testing the Application

### 1. Test Individual Lambda Functions

```bash
# Test Add Doctor Procedure
sam local invoke AddDoctorProcedureFunction --event events/add_doctor_event.json

# Test Get Quote
sam local invoke GetQuoteFunction --event events/get_quote_event.json

# Test Show History
sam local invoke ShowHistoryFunction --event events/show_history_event.json

# Test Bedrock Intent Mapper (requires valid Bedrock Agent)
sam local invoke BedrockIntentMapperFunction --event events/bedrock_intent_mapper.json
```

### 2. Test API Endpoints

```bash
# Add a new procedure
curl -X POST http://localhost:3000/add-doctor-procedure \
  -H "Content-Type: application/json" \
  -d '{
    "doctorName": "Dr. Alice Smith",
    "procedureCode": "CONSULT001",
    "procedureName": "Initial Consultation",
    "cost": 150.00
  }'

# Get a quote for a procedure
curl "http://localhost:3000/get-quote?procedureCode=CONSULT001"

# Show procedure history for a doctor
curl "http://localhost:3000/show-history?doctorName=Dr.%20Alice%20Smith&limit=5"

# Test intent mapper
curl -X POST http://localhost:3000/intent-mapper \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Add a consultation for Dr. Smith with code CONSULT001 that costs $150",
    "sessionId": "test-session-123"
  }'
```

## Bedrock Agent Configuration

To set up the Bedrock Agent for intent mapping:

### 1. Create Action Groups

1. **AddDoctorProcedureAction**
   - Lambda Function: `AddDoctorProcedureFunction`
   - OpenAPI Schema: `openapi_schemas/addDoctorProcedure.yaml`

2. **GetQuoteAction**
   - Lambda Function: `GetQuoteFunction`
   - OpenAPI Schema: `openapi_schemas/getQuote.yaml`

3. **ShowHistoryAction**
   - Lambda Function: `ShowHistoryFunction`
   - OpenAPI Schema: `openapi_schemas/showHistory.yaml`

### 2. Configure Intents

1. **AddProcedureIntent**
   - Trigger phrases: "add procedure", "log procedure", "record procedure"
   - Action Group: AddDoctorProcedureAction

2. **GetQuoteIntent**
   - Trigger phrases: "get quote", "cost estimate", "procedure cost"
   - Action Group: GetQuoteAction

3. **ShowHistoryIntent**
   - Trigger phrases: "show history", "procedure history", "recent procedures"
   - Action Group: ShowHistoryAction

4. **FallbackIntent**
   - Default intent for unrecognized inputs
   - Response: "I'm sorry, I didn't understand that. I can help you add procedures, get quotes, or show procedure history."

### 3. Update Environment Variables

Update the `samconfig.yaml` file with your actual Bedrock Agent details:

```yaml
parameter_overrides: 
  - BedrockAgentId=YOUR_ACTUAL_AGENT_ID
  - BedrockAgentAliasId=YOUR_ACTUAL_ALIAS_ID
```

## Deployment

### Deploy to AWS

```bash
# Deploy the stack
sam deploy --guided

# For subsequent deployments
sam deploy
```

### Environment Variables

The following environment variables are set automatically:

- `DYNAMODB_TABLE_NAME` - DynamoDB table name
- `BEDROCK_AGENT_ID` - Bedrock Agent ID
- `BEDROCK_AGENT_ALIAS_ID` - Bedrock Agent Alias ID
- `AWS_REGION` - AWS region

## API Endpoints

After deployment, you'll have the following endpoints:

- `POST /intent-mapper` - Bedrock intent mapping
- `POST /add-doctor-procedure` - Add a new procedure
- `GET /get-quote` - Get procedure cost estimate
- `GET /show-history` - Show doctor's procedure history

## Project Structure

```
.
├── template.yaml                 # SAM template
├── samconfig.yaml               # SAM configuration
├── events/                      # Test events
│   ├── add_doctor_event.json
│   ├── get_quote_event.json
│   ├── show_history_event.json
│   └── bedrock_intent_mapper.json
├── functions/                   # Lambda functions
│   ├── bedrock_intent_mapper_lambda/
│   ├── add_doctor_procedure/
│   ├── get_quote_lambda/
│   └── show_history_lambda/
├── openapi_schemas/            # OpenAPI schemas for Bedrock
│   ├── addDoctorProcedure.yaml
│   ├── getQuote.yaml
│   └── showHistory.yaml
├── doctor_procedures_table/    # Test data
│   └── dummy_data.json
└── populate_table.py           # Script to populate test data
```

## Troubleshooting

### Common Issues

1. **Docker not running**: Make sure Docker is running before using SAM local
2. **Port already in use**: Use different ports with `--port` flag
3. **DynamoDB connection**: Ensure DynamoDB local is running on port 8000
4. **Bedrock permissions**: Ensure your AWS credentials have Bedrock permissions

### Logs

```bash
# View Lambda function logs
sam logs --name FunctionName --tail

# View all logs
sam logs --tail
```

## Next Steps

1. Configure your Bedrock Agent with the provided OpenAPI schemas
2. Test the intent mapping functionality
3. Deploy to AWS for production use
4. Set up monitoring and alerting
5. Add additional intents as needed
