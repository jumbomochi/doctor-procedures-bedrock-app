#!/bin/bash

# OpenAPI Schema Validation Script
# Checks if all required schemas exist and are valid

echo "🔍 Validating OpenAPI schemas for Bedrock Agent..."

SCHEMAS_DIR="openapi_schemas"
REQUIRED_SCHEMAS=("addDoctorProcedure.yaml" "getQuote.yaml" "showHistory.yaml")

# Check if schemas directory exists
if [ ! -d "$SCHEMAS_DIR" ]; then
    echo "❌ Schemas directory not found: $SCHEMAS_DIR"
    exit 1
fi

# Check each required schema
for schema in "${REQUIRED_SCHEMAS[@]}"; do
    schema_path="$SCHEMAS_DIR/$schema"
    if [ -f "$schema_path" ]; then
        echo "✅ Found: $schema"
        # Basic YAML validation
        if command -v yq &> /dev/null; then
            if yq eval '.' "$schema_path" > /dev/null 2>&1; then
                echo "   📋 Valid YAML syntax"
            else
                echo "   ⚠️  Invalid YAML syntax"
            fi
        fi
    else
        echo "❌ Missing: $schema"
        exit 1
    fi
done

echo ""
echo "🎯 Next steps:"
echo "1. Open AWS Console → Amazon Bedrock → Agents"
echo "2. Create new agent with the configuration from bedrock_agent_setup.md"
echo "3. Upload the OpenAPI schemas from the $SCHEMAS_DIR/ directory"
echo "4. Note down your Agent ID and Alias ID"
echo "5. Run: ./update_bedrock_agent.sh YOUR_AGENT_ID YOUR_ALIAS_ID"

echo ""
echo "📁 Lambda Functions to configure:"
echo "- AddDoctorProcedure: doctor-procedures-bedrock-AddDoctorProcedureFuncti-iew26y2xQ11H"
echo "- GetQuote: doctor-procedures-bedrock-app-GetQuoteFunction-weEztYJpLinp"  
echo "- ShowHistory: doctor-procedures-bedrock-app-ShowHistoryFunction-6ri533GOJGz3"
