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
        # Handle API Gateway query parameters
        query_params = event.get('queryStringParameters') or {}
        procedure_code = query_params.get('procedureCode') or event.get('procedureCode')

        if not procedure_code:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'message': 'Missing required parameter: procedureCode.'})
            }

        response = table.scan(
            FilterExpression=Attr('procedure_code').eq(procedure_code)
        )

        items = response.get('Items', [])

        if items:
            avg_cost = sum(float(item['cost']) for item in items) / len(items)
            procedure_name = items[0].get('procedure_name', procedure_code)

            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'message': f'The estimated cost for procedure "{procedure_name}" ({procedure_code}) is ${avg_cost:.2f}.'})
            }
        else:
            return {
                'statusCode': 404,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'message': f'Procedure code "{procedure_code}" not found or no associated cost data.'})
            }

    except Exception as e:
        print(f"Error in getQuoteLambda: {e}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'message': f'Internal server error: {str(e)}'})
        }