# Bedrock Agent Configuration Guide

## 🎯 Overview
This guide will walk you through creating a Bedrock Agent in the AWS Console to complete your Doctor Procedures Intent Mapper.

## 📋 Prerequisites
- AWS Console access with Bedrock permissions
- Deployed Lambda functions (✅ Already done)
- OpenAPI schemas (✅ Already created)

## 🚀 Step-by-Step Setup

### Step 1: Navigate to Amazon Bedrock
1. Open AWS Console
2. Navigate to **Amazon Bedrock** service
3. Go to **Agents** in the left sidebar
4. Click **Create Agent**

### Step 2: Agent Basic Configuration
```
Agent Name: DoctorProceduresAgent
Description: AI agent for managing doctor procedures, cost estimates, and procedure history
Foundation Model: Claude 3 Haiku (recommended for cost-efficiency)
```

### Step 3: Agent Instructions
Copy and paste this instruction set:

```
You are a helpful assistant for managing doctor procedures and cost estimates. You can:

1. Add new medical procedures for doctors with procedure codes and costs
2. Provide cost estimates for specific procedure codes
3. Show procedure history for doctors with optional date filtering

When users ask about adding procedures, use the AddDoctorProcedure action.
When users ask about costs or quotes, use the GetQuote action.
When users ask about history or past procedures, use the ShowHistory action.

Always be helpful and provide clear, concise responses about medical procedure management.
```

### Step 4: Create Action Groups

#### Action Group 1: AddDoctorProcedure
- **Action Group Name**: `AddDoctorProcedureGroup`
- **Description**: `Add new medical procedures to the database`
- **Lambda Function**: `doctor-procedures-bedrock-AddDoctorProcedureFuncti-iew26y2xQ11H`
- **API Schema**: Upload `openapi_schemas/addDoctorProcedure.yaml`

#### Action Group 2: GetQuote  
- **Action Group Name**: `GetQuoteGroup`
- **Description**: `Get cost estimates for procedure codes`
- **Lambda Function**: `doctor-procedures-bedrock-app-GetQuoteFunction-weEztYJpLinp`
- **API Schema**: Upload `openapi_schemas/getQuote.yaml`

#### Action Group 3: ShowHistory
- **Action Group Name**: `ShowHistoryGroup`  
- **Description**: `Show procedure history for doctors`
- **Lambda Function**: `doctor-procedures-bedrock-app-ShowHistoryFunction-6ri533GOJGz3`
- **API Schema**: Upload `openapi_schemas/showHistory.yaml`

### Step 5: Test the Agent
After creating the agent, use the test interface to try these queries:

1. **Add Procedure Test**:
   ```
   "Add a consultation procedure for Dr. Smith with code CONSULT001 that costs $150"
   ```

2. **Get Quote Test**:
   ```
   "What is the average cost for procedure code CONSULT001?"
   ```

3. **Show History Test**:
   ```
   "Show me the procedure history for Dr. Smith"
   ```

### Step 6: Get Agent Details
After creation, note down:
- **Agent ID** (e.g., `ABCD123456`)
- **Agent Alias ID** (usually `TSTALIASID` for test alias)

## 🔧 Update Your Application

After creating the Bedrock Agent, update the environment variables:

### Option 1: Update samconfig.toml
Edit the parameter overrides in samconfig.toml:

```toml
parameter_overrides = "BedrockAgentId=\"YOUR_AGENT_ID\" BedrockAgentAliasId=\"YOUR_ALIAS_ID\""
```

### Option 2: Deploy with Parameters
```bash
sam deploy --parameter-overrides BedrockAgentId=YOUR_AGENT_ID BedrockAgentAliasId=YOUR_ALIAS_ID --profile vsc-sso --region us-east-1
```

## 🧪 Final Testing
Once updated, test the intent mapper:

```bash
curl -X POST https://jj6skt98b3.execute-api.us-east-1.amazonaws.com/dev/intent-mapper \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Add a consultation for Dr. Johnson with code CONSULT002 that costs $175",
    "sessionId": "test-session-456"
  }'
```

## 📝 Notes
- The agent will take a few minutes to become available after creation
- Test thoroughly in the Bedrock console before updating your Lambda
- Keep your Agent ID and Alias ID secure
- The test alias is automatically created and sufficient for development

## 🔍 Troubleshooting
- **Permission errors**: Ensure Lambda functions have proper IAM roles. If you get "Access denied while invoking Lambda function" error, make sure the latest deployment includes Bedrock permissions (✅ Already included in template.yaml)
- **Schema validation**: Double-check OpenAPI schemas match your Lambda inputs and include description fields
- **Agent not responding**: Wait 5-10 minutes after creation for full activation
- **Lambda permissions**: The SAM template automatically creates the required Lambda permissions for Bedrock Agent access
