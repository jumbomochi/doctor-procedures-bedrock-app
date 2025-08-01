# filename: add_doctor_procedure_lambda.py
import json
import boto3
import os
from datetime import datetime, timezone
from decimal import Decimal

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
        
        # Handle Bedrock Agent parameters vs API Gateway body
        if is_bedrock_agent:
            # Extract parameters from Bedrock Agent event
            parameters = {param['name']: param['value'] for param in event.get('parameters', [])}
            doctor_name = parameters.get('doctorName')
            procedure_code = parameters.get('procedureCode')
            procedure_name = parameters.get('procedureName')
            cost = parameters.get('cost')
            time_str = parameters.get('time')
        elif 'body' in event and event['body']:
            # API Gateway format
            request_body = json.loads(event['body'])
            doctor_name = request_body.get('doctorName')
            procedure_code = request_body.get('procedureCode')
            procedure_name = request_body.get('procedureName')
            cost = request_body.get('cost')
            time_str = request_body.get('time')
        else:
            # Direct invocation fallback
            doctor_name = event.get('doctorName')
            procedure_code = event.get('procedureCode')
            procedure_name = event.get('procedureName')
            cost = event.get('cost')
            time_str = event.get('time')

        if not all([doctor_name, procedure_code, cost is not None]):
            error_message = 'Missing required parameters: doctorName, procedureCode, and cost.'
            if is_bedrock_agent:
                return {
                    'messageVersion': '1.0',
                    'response': {
                        'actionGroup': event.get('actionGroup', 'AddDoctorProcedureGroup'),
                        'apiPath': event.get('apiPath', '/addDoctorProcedure'),
                        'httpMethod': event.get('httpMethod', 'POST'),
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

        try:
            cost = Decimal(str(cost))
        except (ValueError, TypeError):
            error_message = 'Cost must be a valid number.'
            if is_bedrock_agent:
                return {
                    'messageVersion': '1.0',
                    'response': {
                        'actionGroup': event.get('actionGroup', 'AddDoctorProcedureGroup'),
                        'apiPath': event.get('apiPath', '/addDoctorProcedure'),
                        'httpMethod': event.get('httpMethod', 'POST'),
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

        # Handle time: use provided or current UTC
        if time_str:
            try:
                logged_time = datetime.fromisoformat(time_str.replace('Z', '+00:00')).astimezone(timezone.utc).isoformat().replace('+00:00', 'Z')
            except ValueError:
                error_message = 'Invalid time format. Use ISO 8601 (e.g., YYYY-MM-DDTHH:MM:SSZ).'
                if is_bedrock_agent:
                    return {
                        'messageVersion': '1.0',
                        'response': {
                            'actionGroup': event.get('actionGroup', 'AddDoctorProcedureGroup'),
                            'apiPath': event.get('apiPath', '/addDoctorProcedure'),
                            'httpMethod': event.get('httpMethod', 'POST'),
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
        else:
            logged_time = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

        item = {
            'DoctorName': doctor_name,
            'ProcedureTime': logged_time,
            'procedure_code': procedure_code,
            'procedure_name': procedure_name,
            'cost': cost,
            'time_logged': logged_time
        }

        table.put_item(Item=item)

        success_message = f'Procedure "{procedure_name or procedure_code}" for Dr. {doctor_name} added successfully at {logged_time}.'
        
        if is_bedrock_agent:
            return {
                'messageVersion': '1.0',
                'response': {
                    'actionGroup': event.get('actionGroup', 'AddDoctorProcedureGroup'),
                    'apiPath': event.get('apiPath', '/addDoctorProcedure'),
                    'httpMethod': event.get('httpMethod', 'POST'),
                    'httpStatusCode': 200,
                    'responseBody': {
                        'application/json': {
                            'body': json.dumps({
                                'message': success_message,
                                'doctorName': doctor_name,
                                'procedureCode': procedure_code,
                                'procedureName': procedure_name,
                                'cost': float(cost),
                                'timeLogged': logged_time
                            })
                        }
                    }
                }
            }
        else:
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'message': success_message})
            }

    except Exception as e:
        print(f"Error in addDoctorProcedureLambda: {e}")
        error_message = f'Internal server error: {str(e)}'
        
        if 'is_bedrock_agent' in locals() and is_bedrock_agent:
            return {
                'messageVersion': '1.0',
                'response': {
                    'actionGroup': event.get('actionGroup', 'AddDoctorProcedureGroup'),
                    'apiPath': event.get('apiPath', '/addDoctorProcedure'),
                    'httpMethod': event.get('httpMethod', 'POST'),
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