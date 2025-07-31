#!/bin/bash

# Bedrock Agent Deployment Script
# Usage: ./update_bedrock_agent.sh AGENT_ID ALIAS_ID

set -e

if [ $# -ne 2 ]; then
    echo "Usage: $0 <AGENT_ID> <ALIAS_ID>"
    echo "Example: $0 ABCD123456 TSTALIASID"
    exit 1
fi

AGENT_ID=$1
ALIAS_ID=$2

echo "🚀 Updating Bedrock Agent configuration..."
echo "Agent ID: $AGENT_ID"
echo "Alias ID: $ALIAS_ID"

# Build the application
echo "📦 Building SAM application..."
sam build

# Deploy with new parameters
echo "🔄 Deploying with Bedrock Agent configuration..."
sam deploy \
    --parameter-overrides "BedrockAgentId=$AGENT_ID BedrockAgentAliasId=$ALIAS_ID" \
    --profile vsc-sso \
    --region us-east-1

echo "✅ Deployment complete!"
echo ""
echo "🧪 Test your intent mapper with:"
echo "curl -X POST https://jj6skt98b3.execute-api.us-east-1.amazonaws.com/dev/intent-mapper \\"
echo "  -H \"Content-Type: application/json\" \\"
echo "  -d '{\"text\":\"Add a consultation for Dr. Test\",\"sessionId\":\"test-123\"}'"
