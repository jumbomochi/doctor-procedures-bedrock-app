# filename: get_quote_lambda.py
import json
import boto3
import os
from boto3.dynamodb.conditions import Attr
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
TABLE_NAME = os.environ.get('DYNAMODB_TABLE_NAME', 'DoctorProcedures')
table = dynamodb.Table(TABLE_NAME)

def lambda_handler(event, context):
    try:
        # Check if this is a Bedrock Agent invocation
        is_bedrock_agent = 'agent' in event or 'actionGroup' in event or ('httpMethod' not in event and 'queryStringParameters' not in event)
        
        # Handle API Gateway query parameters vs direct parameters
        if 'queryStringParameters' in event and event['queryStringParameters'] and not is_bedrock_agent:
            query_params = event.get('queryStringParameters') or {}
            procedure_code = query_params.get('procedureCode')
        else:
            procedure_code = event.get('procedureCode')

        if not procedure_code:
            error_message = 'Missing required parameter: procedureCode.'
            if is_bedrock_agent:
                return {'message': error_message}
            else:
                return {
                    'statusCode': 400,
                    'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                    'body': json.dumps({'message': error_message})
                }

        response = table.scan(
            FilterExpression=Attr('procedure_code').eq(procedure_code)
        )

        items = response.get('Items', [])

        if items:
            avg_cost = sum(float(item['cost']) for item in items) / len(items)
            procedure_name = items[0].get('procedure_name', procedure_code)
            message = f'The estimated cost for procedure "{procedure_name}" ({procedure_code}) is ${avg_cost:.2f}.'

            if is_bedrock_agent:
                return {
                    'message': message,
                    'procedureCode': procedure_code,
                    'procedureName': procedure_name,
                    'averageCost': avg_cost,
                    'sampleCount': len(items)
                }
            else:
                return {
                    'statusCode': 200,
                    'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                    'body': json.dumps({'message': message})
                }
        else:
            error_message = f'Procedure code "{procedure_code}" not found or no associated cost data.'
            if is_bedrock_agent:
                return {'message': error_message}
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
            return {'message': error_message}
        else:
            return {
                'statusCode': 500,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'message': error_message})
            }