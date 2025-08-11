"""
Fuzzy matching utilities for doctor names
"""
import boto3
import os
import difflib

def find_best_doctor_match(input_name, threshold=0.4):
    """
    Find the best matching doctor name using fuzzy matching.
    Returns (matched_name, confidence_score) or (None, 0) if no good match found.
    """
    try:
        # Get DynamoDB table
        dynamodb = boto3.resource('dynamodb')
        TABLE_NAME = os.environ.get('DYNAMODB_TABLE_NAME', 'DoctorProcedures')
        table = dynamodb.Table(TABLE_NAME)
        
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


def get_original_input_name(event, is_bedrock_agent):
    """
    Extract the original input doctor name from the event for display purposes.
    """
    try:
        if is_bedrock_agent:
            parameters = event.get('parameters', [])
            for param in parameters:
                if param.get('name') == 'doctorName':
                    return param.get('value', '')
        else:
            query_params = event.get('queryStringParameters', {})
            if query_params:
                return query_params.get('doctorName', '')
            # Try body for POST requests
            if 'body' in event and event['body']:
                import json
                body = json.loads(event['body'])
                return body.get('doctorName', '')
    except Exception as e:
        print(f"Error getting original input name: {e}")
    
    return ""
