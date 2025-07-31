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
        # Handle both direct invocation and API Gateway
        if 'body' in event and event['body']:
            # API Gateway format
            request_body = json.loads(event['body'])
            doctor_name = request_body.get('doctorName')
            procedure_code = request_body.get('procedureCode')
            procedure_name = request_body.get('procedureName')
            cost = request_body.get('cost')
            time_str = request_body.get('time')
        else:
            # Direct invocation (from Bedrock Agent)
            doctor_name = event.get('doctorName')
            procedure_code = event.get('procedureCode')
            procedure_name = event.get('procedureName')
            cost = event.get('cost')
            time_str = event.get('time')

        if not all([doctor_name, procedure_code, cost is not None]):
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'message': 'Missing required parameters: doctorName, procedureCode, and cost.'})
            }

        try:
            cost = Decimal(str(cost))
        except (ValueError, TypeError):
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'message': 'Cost must be a valid number.'})
            }

        # Handle time: use provided or current UTC
        if time_str:
            try:
                logged_time = datetime.fromisoformat(time_str.replace('Z', '+00:00')).astimezone(timezone.utc).isoformat().replace('+00:00', 'Z')
            except ValueError:
                return {
                    'statusCode': 400,
                    'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                    'body': json.dumps({'message': 'Invalid time format. Use ISO 8601 (e.g., YYYY-MM-DDTHH:MM:SSZ).'})
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

        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'message': f'Procedure "{procedure_name or procedure_code}" for Dr. {doctor_name} added successfully at {logged_time}.'})
        }

    except Exception as e:
        print(f"Error in addDoctorProcedureLambda: {e}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'message': f'Internal server error: {str(e)}'})
        }