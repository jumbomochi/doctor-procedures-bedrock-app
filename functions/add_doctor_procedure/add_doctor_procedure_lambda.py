# filename: add_doctor_procedure_lambda.py
import json
import boto3
import os
from datetime import datetime, timezone
from decimal import Decimal
import difflib

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

        # Find the best matching doctor name using fuzzy matching
        print(f"Original doctor name input: {doctor_name}")
        matched_doctor_name, confidence = find_best_doctor_match(doctor_name)
        original_input = doctor_name
        
        # For adding procedures, we're more cautious with fuzzy matching
        if matched_doctor_name and confidence >= 0.8:
            # High confidence match - use it
            doctor_name = matched_doctor_name
            print(f"Using matched doctor name: {doctor_name} (confidence: {confidence:.2f})")
        elif matched_doctor_name and confidence >= 0.5:
            # Medium confidence - ask for confirmation or provide suggestion
            suggestion_message = f'Did you mean "{matched_doctor_name}"? The name "{original_input}" was not found exactly. Please confirm the doctor name or use the exact name "{matched_doctor_name}".'
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
                                'body': json.dumps({
                                    'message': suggestion_message,
                                    'suggestion': matched_doctor_name,
                                    'confidence': confidence
                                })
                            }
                        }
                    }
                }
            else:
                return {
                    'statusCode': 400,
                    'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                    'body': json.dumps({
                        'message': suggestion_message,
                        'suggestion': matched_doctor_name,
                        'confidence': confidence
                    })
                }
        else:
            # Low confidence or no match - use the original name (create new doctor)
            print(f"Using original doctor name (new doctor): {doctor_name}")
            confidence = 1.0  # Set confidence to 1.0 for new doctor

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

        success_message = f'Procedure "{procedure_name or procedure_code}" for {doctor_name} added successfully at {logged_time}.'
        
        # Add fuzzy match note if confidence is less than perfect and we used matching
        if confidence < 1.0 and matched_doctor_name:
            success_message += f' (Note: Matched "{doctor_name}" from your input "{original_input}")'
        
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
                                'timeLogged': logged_time,
                                'matchConfidence': confidence
                            })
                        }
                    }
                }
            }
        else:
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({
                    'message': success_message,
                    'doctorName': doctor_name,
                    'procedureCode': procedure_code,
                    'procedureName': procedure_name,
                    'cost': float(cost),
                    'timeLogged': logged_time,
                    'matchConfidence': confidence
                })
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