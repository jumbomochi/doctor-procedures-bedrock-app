# filename: get_quote_lambda.py
import json
import boto3
import os
from boto3.dynamodb.conditions import Key, Attr
from decimal import Decimal
import statistics

dynamodb = boto3.resource('dynamodb')
TABLE_NAME = os.environ.get('DYNAMODB_TABLE_NAME', 'DoctorProcedures')
table = dynamodb.Table(TABLE_NAME)

def lambda_handler(event, context):
    try:
        # Debug: print the event to understand Bedrock Agent invocation format
        print(f"Event received: {json.dumps(event)}")
        
        # Detect Bedrock Agent by checking for agent and parameters structure
        is_bedrock_agent = (
            'agent' in event and 
            'actionGroup' in event and 
            'parameters' in event and
            'messageVersion' in event
        )
        
        print(f"Detected Bedrock Agent: {is_bedrock_agent}")
        
        # Handle Bedrock Agent parameters vs API Gateway parameters
        if is_bedrock_agent:
            # Extract parameters from Bedrock Agent event
            parameters = {param['name']: param['value'] for param in event.get('parameters', [])}
            doctor_name = parameters.get('doctorName')
            procedure_code = parameters.get('procedureCode')  # Optional
        else:
            # Handle API Gateway query parameters
            query_params = event.get('queryStringParameters') or {}
            doctor_name = query_params.get('doctorName')
            procedure_code = query_params.get('procedureCode')  # Optional

        # Validate required parameters - only doctorName is required
        if not doctor_name:
            error_message = 'Missing required parameter: doctorName. Please provide the doctor name.'
            if is_bedrock_agent:
                return {
                    'messageVersion': '1.0',
                    'response': {
                        'actionGroup': event.get('actionGroup', 'GetQuoteGroup'),
                        'apiPath': event.get('apiPath', '/getQuote'),
                        'httpMethod': event.get('httpMethod', 'GET'),
                        'httpStatusCode': 400,
                        'responseBody': {
                            'application/json': {
                                'body': json.dumps({'message': error_message})
                            }
                        }
                    }
                }
            else:
                return {
                    'statusCode': 400,
                    'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                    'body': json.dumps({'message': error_message})
                }

        # Query DynamoDB for doctor's procedures
        print(f"Querying for doctor: {doctor_name}")
        if procedure_code:
            print(f"Filtering for specific procedure: {procedure_code}")
        
        # Base query for the doctor
        response = table.query(
            KeyConditionExpression=Key('DoctorName').eq(doctor_name)
        )

        items = response.get('Items', [])
        print(f"Found {len(items)} total items for doctor {doctor_name}")

        # Filter by procedure code if provided
        if procedure_code:
            items = [item for item in items if item.get('procedure_code') == procedure_code]
            print(f"Filtered to {len(items)} items for procedure {procedure_code}")

        if items:
            # Extract costs and calculate median
            costs = [float(item['cost']) for item in items]
            median_cost = statistics.median(costs)
            
            print(f"Costs found: {costs}")
            print(f"Median cost: {median_cost}")
            
            if procedure_code:
                # Specific procedure median
                procedure_name = items[0].get('procedure_name', procedure_code)
                message = f'The median cost for procedure "{procedure_name}" ({procedure_code}) by Dr. {doctor_name} is ${median_cost:.2f}.'
                result_data = {
                    'message': message,
                    'doctorName': doctor_name,
                    'procedureCode': procedure_code,
                    'procedureName': procedure_name,
                    'medianCost': median_cost,
                    'sampleCount': len(items),
                    'costRange': {
                        'min': min(costs),
                        'max': max(costs)
                    }
                }
            else:
                # Overall median for all procedures by this doctor
                unique_procedures = list(set(item.get('procedure_name', 'Unknown') for item in items))
                message = f'The median cost for all procedures by Dr. {doctor_name} is ${median_cost:.2f}. This includes {len(unique_procedures)} different procedure types.'
                result_data = {
                    'message': message,
                    'doctorName': doctor_name,
                    'allProcedures': True,
                    'medianCost': median_cost,
                    'sampleCount': len(items),
                    'procedureTypes': unique_procedures,
                    'costRange': {
                        'min': min(costs),
                        'max': max(costs)
                    }
                }

            if is_bedrock_agent:
                return {
                    'messageVersion': '1.0',
                    'response': {
                        'actionGroup': event.get('actionGroup', 'GetQuoteGroup'),
                        'apiPath': event.get('apiPath', '/getQuote'),
                        'httpMethod': event.get('httpMethod', 'GET'),
                        'httpStatusCode': 200,
                        'responseBody': {
                            'application/json': {
                                'body': json.dumps(result_data)
                            }
                        }
                    }
                }
            else:
                return {
                    'statusCode': 200,
                    'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                    'body': json.dumps(result_data)
                }
        else:
            if procedure_code:
                error_message = f'No procedures found for Dr. {doctor_name} with procedure code "{procedure_code}".'
            else:
                error_message = f'No procedures found for Dr. {doctor_name}.'
            if is_bedrock_agent:
                return {
                    'messageVersion': '1.0',
                    'response': {
                        'actionGroup': event.get('actionGroup', 'GetQuoteGroup'),
                        'apiPath': event.get('apiPath', '/getQuote'),
                        'httpMethod': event.get('httpMethod', 'GET'),
                        'httpStatusCode': 404,
                        'responseBody': {
                            'application/json': {
                                'body': json.dumps({'message': error_message})
                            }
                        }
                    }
                }
            else:
                return {
                    'statusCode': 404,
                    'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                    'body': json.dumps({'message': error_message})
                }

    except Exception as e:
        print(f"Error in getQuoteLambda: {e}")
        error_message = f'Internal server error: {str(e)}'
        
        if 'is_bedrock_agent' in locals() and is_bedrock_agent:
            return {
                'messageVersion': '1.0',
                'response': {
                    'actionGroup': event.get('actionGroup', 'GetQuoteGroup'),
                    'apiPath': event.get('apiPath', '/getQuote'),
                    'httpMethod': event.get('httpMethod', 'GET'),
                    'httpStatusCode': 500,
                    'responseBody': {
                        'application/json': {
                            'body': json.dumps({'message': error_message})
                        }
                    }
                }
            }
        else:
            return {
                'statusCode': 500,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'message': error_message})
            }