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
            procedure_code = parameters.get('procedureCode')
        else:
            # Handle API Gateway query parameters
            query_params = event.get('queryStringParameters') or {}
            doctor_name = query_params.get('doctorName')
            procedure_code = query_params.get('procedureCode')

        # Validate required parameters
        if not doctor_name or not procedure_code:
            missing_params = []
            if not doctor_name:
                missing_params.append('doctorName')
            if not procedure_code:
                missing_params.append('procedureCode')
            
            error_message = f'Missing required parameters: {", ".join(missing_params)}. Please provide both doctor name and procedure code.'
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

        # Query DynamoDB for specific doctor's procedures
        print(f"Querying for doctor: {doctor_name}, procedure: {procedure_code}")
        
        response = table.query(
            KeyConditionExpression=Key('DoctorName').eq(doctor_name),
            FilterExpression=Attr('procedure_code').eq(procedure_code)
        )

        items = response.get('Items', [])
        print(f"Found {len(items)} items for doctor {doctor_name} with procedure {procedure_code}")

        if items:
            # Extract costs and calculate median
            costs = [float(item['cost']) for item in items]
            median_cost = statistics.median(costs)
            procedure_name = items[0].get('procedure_name', procedure_code)
            
            print(f"Costs found: {costs}")
            print(f"Median cost: {median_cost}")
            
            message = f'The median cost for procedure "{procedure_name}" ({procedure_code}) by Dr. {doctor_name} is ${median_cost:.2f}.'

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
                                'body': json.dumps({
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
                                })
                            }
                        }
                    }
                }
            else:
                return {
                    'statusCode': 200,
                    'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                    'body': json.dumps({'message': message})
                }
        else:
            error_message = f'No procedures found for Dr. {doctor_name} with procedure code "{procedure_code}".'
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