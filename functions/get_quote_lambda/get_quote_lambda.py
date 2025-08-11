# filename: get_quote_lambda.py
import json
import boto3
import os
from boto3.dynamodb.conditions import Key, Attr
from decimal import Decimal
import statistics
import difflib
import re

dynamodb = boto3.resource('dynamodb')
TABLE_NAME = os.environ.get('DYNAMODB_TABLE_NAME', 'DoctorProcedures')
table = dynamodb.Table(TABLE_NAME)

def find_best_doctor_match(input_name, threshold=0.4):
    """
    Find the best matching doctor name using fuzzy matching.
    Returns (matched_name, confidence_score) or (None, 0) if no good match found.
    """
    try:
        # Get all unique doctor names from the table
        response = table.scan(
            ProjectionExpression='DoctorName'
        )
        
        all_doctors = list(set(item['DoctorName'] for item in response.get('Items', [])))
        print(f"Available doctors: {all_doctors}")
        
        if not all_doctors:
            return None, 0
        
        # Normalize input name for comparison
        input_normalized = input_name.lower().strip()
        
        # Try exact case-insensitive match first
        for doctor in all_doctors:
            if doctor.lower() == input_normalized:
                print(f"Exact match found: {doctor}")
                return doctor, 1.0
        
        # Try partial matching (if input is contained in doctor name or vice versa)
        for doctor in all_doctors:
            doctor_normalized = doctor.lower()
            if input_normalized in doctor_normalized or doctor_normalized in input_normalized:
                # Calculate confidence based on length similarity
                confidence = min(len(input_normalized), len(doctor_normalized)) / max(len(input_normalized), len(doctor_normalized))
                if confidence >= threshold:
                    print(f"Partial match found: {doctor} (confidence: {confidence:.2f})")
                    return doctor, confidence
        
        # Use fuzzy matching for typos and spelling mistakes
        matches = difflib.get_close_matches(
            input_normalized, 
            [doctor.lower() for doctor in all_doctors], 
            n=1, 
            cutoff=threshold
        )
        
        if matches:
            # Find the original doctor name corresponding to the matched normalized name
            matched_normalized = matches[0]
            for doctor in all_doctors:
                if doctor.lower() == matched_normalized:
                    confidence = difflib.SequenceMatcher(None, input_normalized, matched_normalized).ratio()
                    print(f"Fuzzy match found: {doctor} (confidence: {confidence:.2f})")
                    return doctor, confidence
        
        print(f"No good match found for: {input_name}")
        return None, 0
        
    except Exception as e:
        print(f"Error in find_best_doctor_match: {e}")
        return None, 0

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
        
        # Additional debugging for Bedrock Agent events
        if is_bedrock_agent:
            print(f"Bedrock Agent ID: {event.get('agent', {}).get('id', 'Unknown')}")
            print(f"Action Group: {event.get('actionGroup', 'Unknown')}")
            print(f"API Path: {event.get('apiPath', 'Unknown')}")
            print(f"Raw parameters: {event.get('parameters', [])}")
        
        # Handle Bedrock Agent parameters vs API Gateway parameters
        if is_bedrock_agent:
            # Extract parameters from Bedrock Agent event
            parameters = {param['name']: param['value'] for param in event.get('parameters', [])}
            doctor_name = parameters.get('doctorName')
            procedure_code = parameters.get('procedureCode')  # Optional
            
            # Debug: Print extracted parameters
            print(f"Bedrock Agent parameters extracted: {parameters}")
            print(f"Doctor name from parameters: {doctor_name}")
        else:
            # Handle API Gateway query parameters
            query_params = event.get('queryStringParameters') or {}
            doctor_name = query_params.get('doctorName')
            procedure_code = query_params.get('procedureCode')  # Optional

        # Validate required parameters - only doctorName is required
        if not doctor_name:
            if is_bedrock_agent:
                error_message = 'Missing required parameter: doctorName. Please specify which doctor you want to get a quote for.'
            else:
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

        # Find the best matching doctor name using fuzzy matching
        print(f"Original doctor name input: {doctor_name}")
        matched_doctor_name, confidence = find_best_doctor_match(doctor_name)
        
        if not matched_doctor_name:
            error_message = f'No doctor found matching "{doctor_name}". Please check the spelling and try again.'
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
        
        # Use the matched doctor name for the query
        doctor_name = matched_doctor_name
        print(f"Using matched doctor name: {doctor_name} (confidence: {confidence:.2f})")

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
                base_message = f'The median cost for procedure "{procedure_name}" ({procedure_code}) by {doctor_name} is ${median_cost:.2f}.'
                
                # Add fuzzy match note if confidence is less than perfect
                if confidence < 1.0:
                    base_message += f' (Note: Matched "{doctor_name}" from your input "{event.get("queryStringParameters", {}).get("doctorName") if not is_bedrock_agent else [p["value"] for p in event.get("parameters", []) if p["name"] == "doctorName"][0]}")'
                
                result_data = {
                    'message': base_message,
                    'doctorName': doctor_name,
                    'procedureCode': procedure_code,
                    'procedureName': procedure_name,
                    'medianCost': median_cost,
                    'sampleCount': len(items),
                    'matchConfidence': confidence,
                    'costRange': {
                        'min': min(costs),
                        'max': max(costs)
                    }
                }
            else:
                # Overall median for all procedures by this doctor
                unique_procedures = list(set(item.get('procedure_name', 'Unknown') for item in items))
                base_message = f'The median cost for all procedures by {doctor_name} is ${median_cost:.2f}. This includes {len(unique_procedures)} different procedure types.'
                
                # Add fuzzy match note if confidence is less than perfect
                if confidence < 1.0:
                    base_message += f' (Note: Matched "{doctor_name}" from your input "{event.get("queryStringParameters", {}).get("doctorName") if not is_bedrock_agent else [p["value"] for p in event.get("parameters", []) if p["name"] == "doctorName"][0]}")'
                
                result_data = {
                    'message': base_message,
                    'doctorName': doctor_name,
                    'allProcedures': True,
                    'medianCost': median_cost,
                    'sampleCount': len(items),
                    'procedureTypes': unique_procedures,
                    'matchConfidence': confidence,
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
                error_message = f'No procedures found for {doctor_name} with procedure code "{procedure_code}".'
            else:
                error_message = f'No procedures found for {doctor_name}.'
                
            # Add fuzzy match note if confidence is less than perfect
            if confidence < 1.0:
                original_input = event.get("queryStringParameters", {}).get("doctorName") if not is_bedrock_agent else [p["value"] for p in event.get("parameters", []) if p["name"] == "doctorName"][0]
                error_message += f' (Note: Matched "{doctor_name}" from your input "{original_input}")'
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