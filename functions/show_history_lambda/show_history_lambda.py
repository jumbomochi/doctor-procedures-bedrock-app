# filename: show_history_lambda.py
import json
import boto3
import os
from datetime import datetime, timezone
from boto3.dynamodb.conditions import Key, Attr
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
            doctor_name = query_params.get('doctorName')
            limit = query_params.get('limit', 5)
            start_date = query_params.get('startDate')
            end_date = query_params.get('endDate')
        else:
            doctor_name = event.get('doctorName')
            limit = event.get('limit', 5)
            start_date = event.get('startDate')
            end_date = event.get('endDate')

        if not doctor_name:
            error_message = 'Missing required parameter: doctorName.'
            if is_bedrock_agent:
                return {'message': error_message}
            else:
                return {
                    'statusCode': 400,
                    'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                    'body': json.dumps({'message': error_message})
                }

        try:
            limit = int(limit)
        except (ValueError, TypeError):
            limit = 5

        # Build filter expression
        filter_expression = Attr('DoctorName').eq(doctor_name)
        
        if start_date:
            try:
                start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                filter_expression = filter_expression & Attr('ProcedureTime').gte(start_dt.isoformat().replace('+00:00', 'Z'))
            except ValueError:
                error_message = 'Invalid startDate format. Use ISO 8601 (e.g., YYYY-MM-DDTHH:MM:SSZ).'
                if is_bedrock_agent:
                    return {'message': error_message}
                else:
                    return {
                        'statusCode': 400,
                        'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                        'body': json.dumps({'message': error_message})
                    }
        
        if end_date:
            try:
                end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                filter_expression = filter_expression & Attr('ProcedureTime').lte(end_dt.isoformat().replace('+00:00', 'Z'))
            except ValueError:
                error_message = 'Invalid endDate format. Use ISO 8601 (e.g., YYYY-MM-DDTHH:MM:SSZ).'
                if is_bedrock_agent:
                    return {'message': error_message}
                else:
                    return {
                        'statusCode': 400,
                        'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                        'body': json.dumps({'message': error_message})
                    }

        response = table.scan(
            FilterExpression=filter_expression
        )

        items = response.get('Items', [])

        if not items:
            error_message = f'No procedure history found for Dr. {doctor_name}.'
            if is_bedrock_agent:
                return {'message': error_message}
            else:
                return {
                    'statusCode': 404,
                    'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                    'body': json.dumps({'message': error_message})
                }

        # Sort by procedure time (most recent first) and limit
        items = sorted(items, key=lambda x: x['ProcedureTime'], reverse=True)[:limit]
        
        total_cost = sum(float(item['cost']) for item in items)
        
        history = []
        for item in items:
            history.append({
                'procedure': item.get('procedure_name', item.get('procedure_code', 'Unknown')),
                'time': item['ProcedureTime'],
                'cost': float(item['cost'])
            })

        message = f'Found {len(history)} procedures for Dr. {doctor_name}.'
        
        if is_bedrock_agent:
            return {
                'message': message,
                'doctorName': doctor_name,
                'procedureCount': len(history),
                'totalCost': total_cost,
                'history': history
            }
        else:
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({
                    'message': message,
                    'history': history,
                    'totalCost': total_cost
                })
            }

    except Exception as e:
        print(f"Error in showHistoryLambda: {e}")
        error_message = f'Internal server error: {str(e)}'
        
        if 'is_bedrock_agent' in locals() and is_bedrock_agent:
            return {'message': error_message}
        else:
            return {
                'statusCode': 500,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'message': error_message})
            }