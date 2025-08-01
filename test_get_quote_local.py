#!/usr/bin/env python3

import os
import sys
import json

# Add the lambda function path to sys.path
sys.path.insert(0, '/Users/huilianglui/Documents/GitHub/doctor-procedures-bedrock-app/functions/get_quote_lambda')

# Set environment variable
os.environ['DYNAMODB_TABLE_NAME'] = 'DoctorProcedures'

# Import the lambda function
from get_quote_lambda import lambda_handler

# Test with API Gateway style event
api_gateway_event = {
    'queryStringParameters': {
        'doctorName': 'Dr. Sarah Johnson',
        'procedureCode': 'CONS001'
    }
}

print("Testing with API Gateway style event:")
print(json.dumps(api_gateway_event, indent=2))
print("\nResult:")

try:
    result = lambda_handler(api_gateway_event, {})
    print(json.dumps(result, indent=2))
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*50 + "\n")

# Test with Bedrock Agent style event
bedrock_event = {
    'agent': {
        'name': 'DoctorProceduresBedrockAgent',
        'version': '1.0.0',
        'id': 'EBGEJR3FWL'
    },
    'actionGroup': 'GetQuoteGroup',
    'apiPath': '/getQuote',
    'httpMethod': 'GET',
    'messageVersion': '1.0',
    'parameters': [
        {
            'name': 'doctorName',
            'type': 'string',
            'value': 'Dr. Sarah Johnson'
        },
        {
            'name': 'procedureCode',
            'type': 'string',
            'value': 'CONS001'
        }
    ]
}

print("Testing with Bedrock Agent style event:")
print(json.dumps(bedrock_event, indent=2))
print("\nResult:")

try:
    result = lambda_handler(bedrock_event, {})
    print(json.dumps(result, indent=2))
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
