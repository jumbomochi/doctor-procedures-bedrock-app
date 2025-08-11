import json
import boto3
import os
import time
import re
from botocore.exceptions import ClientError

# Configure boto3 with retry configuration
bedrock_agent_runtime = boto3.client(
    service_name='bedrock-agent-runtime',
    region_name=os.environ.get('AWS_REGION', 'us-east-1'),
    config=boto3.session.Config(
        retries={
            'max_attempts': 3,
            'mode': 'adaptive'
        }
    )
)

# Configure Lambda client for direct function invocation
lambda_client = boto3.client('lambda', region_name=os.environ.get('AWS_REGION', 'us-east-1'))

# Get agent details from environment variables
AGENT_ID = os.environ.get('BEDROCK_AGENT_ID')
AGENT_ALIAS_ID = os.environ.get('BEDROCK_AGENT_ALIAS_ID')

# Common doctor names for enhanced matching
COMMON_DOCTORS = [
    "Sarah Johnson", "Robert Brown", "Michael Smith", "Emily Davis", 
    "David Wilson", "Lisa Anderson", "John Thompson", "Maria Garcia", 
    "James Martinez", "Jennifer Lee"
]

# Common procedure codes for enhanced matching
PROCEDURE_CODES = [
    "ENDO001", "LAB001", "RAD001", "SURG001", "CONS001", 
    "PHYS001", "CARD001", "DERM001", "ORTH001", "NEUR001"
]

def extract_parameters_from_text(text, conversation_history=None):
    """
    Enhanced parameter extraction from natural language text with conversation context.
    Returns dict with extracted parameters for better Bedrock Agent results.
    """
    text_lower = text.lower()
    extracted = {
        'intent': None,
        'doctorName': None,
        'procedureCode': None,
        'enhanced_prompt': text
    }
    
    # Extract context from conversation history
    context_doctors = []
    context_procedures = []
    last_intent = None
    
    if conversation_history:
        for msg in conversation_history[-6:]:  # Look at last 6 messages
            if msg.get('extractedParams'):
                params = msg['extractedParams']
                if params.get('doctorName'):
                    context_doctors.append(params['doctorName'])
                if params.get('procedureCode'):
                    context_procedures.append(params['procedureCode'])
                if params.get('intent'):
                    last_intent = params['intent']
            
            # Also scan message content for doctor names and procedure codes
            content = msg.get('content', '').lower()
            for doctor in COMMON_DOCTORS:
                if doctor.lower() in content:
                    context_doctors.append(doctor)
            
            for code in PROCEDURE_CODES:
                if code.lower() in content:
                    context_procedures.append(code)
    
    # Remove duplicates while preserving order (most recent first)
    context_doctors = list(dict.fromkeys(reversed(context_doctors)))
    context_procedures = list(dict.fromkeys(reversed(context_procedures)))
    
    # Intent detection with context awareness
    if any(phrase in text_lower for phrase in ['show history', 'history for', 'procedures for', 'show procedures']):
        extracted['intent'] = 'showHistory'
    elif any(phrase in text_lower for phrase in ['get quote', 'cost for', 'quote for', 'price for', 'cost of', 'costs']):
        extracted['intent'] = 'getQuote'
    elif any(phrase in text_lower for phrase in ['add procedure', 'new procedure', 'create procedure']):
        extracted['intent'] = 'addProcedure'
    elif any(phrase in text_lower for phrase in ['what about', 'how about', 'and', 'also']) and last_intent:
        # Context-dependent queries inherit the last intent
        extracted['intent'] = last_intent
    
    # Pronoun and reference resolution
    pronouns_references = ['her', 'his', 'their', 'that doctor', 'this doctor', 'the doctor', 'same doctor']
    has_pronoun = any(pronoun in text_lower for pronoun in pronouns_references)
    
    # Doctor name extraction - improved fuzzy matching with context resolution
    for doctor in COMMON_DOCTORS:
        # Full name match
        if doctor.lower() in text_lower:
            extracted['doctorName'] = doctor
            break
        
        # First name only
        first_name = doctor.split()[0].lower()
        if f" {first_name}" in f" {text_lower}" or text_lower.startswith(first_name):
            extracted['doctorName'] = doctor
            break
            
        # Last name only
        last_name = doctor.split()[-1].lower()
        if last_name in text_lower:
            extracted['doctorName'] = doctor
            break
    
    # If no explicit doctor found but we have pronouns/references, use context
    if not extracted['doctorName'] and has_pronoun and context_doctors:
        extracted['doctorName'] = context_doctors[0]  # Most recent doctor
    
    # If no exact match, try partial matching
    if not extracted['doctorName']:
        for doctor in COMMON_DOCTORS:
            doctor_words = doctor.lower().split()
            if any(word in text_lower for word in doctor_words if len(word) > 2):
                extracted['doctorName'] = doctor
                break
    
    # Procedure code extraction
    for code in PROCEDURE_CODES:
        if code.lower() in text_lower:
            extracted['procedureCode'] = code
            break
    
    # Pattern matching for codes like "ENDO001" or "endo001"
    code_pattern = r'\b([A-Z]{3,4}\d{3})\b'
    code_match = re.search(code_pattern, text.upper())
    if code_match and not extracted['procedureCode']:
        extracted['procedureCode'] = code_match.group(1)
    
    # Context-based procedure code resolution
    procedure_references = ['that procedure', 'this procedure', 'the procedure', 'same procedure']
    has_procedure_reference = any(ref in text_lower for ref in procedure_references)
    if not extracted['procedureCode'] and has_procedure_reference and context_procedures:
        extracted['procedureCode'] = context_procedures[0]  # Most recent procedure
    
    # Enhanced prompt generation with context resolution
    if extracted['intent'] == 'getQuote' and extracted['doctorName']:
        if extracted['procedureCode']:
            extracted['enhanced_prompt'] = f"Get a cost quote for doctor {extracted['doctorName']} for procedure {extracted['procedureCode']}"
        else:
            extracted['enhanced_prompt'] = f"Get overall cost quote for doctor {extracted['doctorName']} for all procedures"
    elif extracted['intent'] == 'showHistory' and extracted['doctorName']:
        extracted['enhanced_prompt'] = f"Show procedure history for doctor {extracted['doctorName']}"
    elif extracted['intent'] and extracted['doctorName']:
        extracted['enhanced_prompt'] = f"{extracted['intent']} for doctor {extracted['doctorName']}"
    
    return extracted

def try_direct_lambda_invocation(intent, doctor_name, procedure_code=None):
    """
    Try to invoke Lambda functions directly when Bedrock Agent fails.
    This provides a fallback mechanism for better user experience.
    """
    try:
        if intent == 'getQuote' and doctor_name:
            # Direct invocation of get-quote function
            function_name = "doctor-procedures-bedrock-app-GetQuoteFunction-weEztYJpLinp"
            
            # Construct event for direct Lambda invocation
            event = {
                'queryStringParameters': {
                    'doctorName': doctor_name
                }
            }
            
            if procedure_code:
                event['queryStringParameters']['procedureCode'] = procedure_code
            
            response = lambda_client.invoke(
                FunctionName=function_name,
                InvocationType='RequestResponse',
                Payload=json.dumps(event)
            )
            
            payload = json.loads(response['Payload'].read())
            if payload.get('statusCode') == 200:
                body = json.loads(payload.get('body', '{}'))
                return format_direct_response(body, 'getQuote')
                
        elif intent == 'showHistory' and doctor_name:
            # Direct invocation of show-history function
            function_name = "doctor-procedures-bedrock-app-ShowHistoryFunction-6ri533GOJGz3"
            
            event = {
                'queryStringParameters': {
                    'doctorName': doctor_name
                }
            }
            
            response = lambda_client.invoke(
                FunctionName=function_name,
                InvocationType='RequestResponse',
                Payload=json.dumps(event)
            )
            
            payload = json.loads(response['Payload'].read())
            if payload.get('statusCode') == 200:
                body = json.loads(payload.get('body', '{}'))
                return format_direct_response(body, 'showHistory')
    
    except Exception as e:
        print(f"Direct Lambda invocation failed: {e}")
        return None
    
    return None

def format_direct_response(lambda_response, intent):
    """
    Format direct Lambda responses to match Bedrock Agent style.
    """
    if intent == 'getQuote':
        if 'medianCost' in lambda_response:
            return lambda_response.get('message', 'Quote retrieved successfully.')
        else:
            return lambda_response.get('message', 'Unable to get quote.')
    
    elif intent == 'showHistory':
        if 'history' in lambda_response:
            return lambda_response.get('message', 'History retrieved successfully.')
        else:
            return lambda_response.get('message', 'No history found.')
    
    return str(lambda_response)

def lambda_handler(event, context):
    if not AGENT_ID or not AGENT_ALIAS_ID:
        print("Error: BEDROCK_AGENT_ID or BEDROCK_AGENT_ALIAS_ID not set as environment variables.")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'message': 'Internal configuration error: Bedrock Agent details missing.'})
        }

    try:
        # 1. Parse the incoming request from API Gateway
        if 'body' not in event:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'message': 'Request body is missing.'})
            }

        request_body = json.loads(event['body'])
        user_text = request_body.get('text')
        session_id = request_body.get('sessionId', context.aws_request_id) # Use AWS request ID as a default session ID
        conversation_history = request_body.get('conversationHistory', [])

        if not user_text:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'message': 'Text input is required in the request body.'})
            }

        # Enhanced parameter extraction with conversation context
        extracted_params = extract_parameters_from_text(user_text, conversation_history)
        print(f"Extracted parameters: {extracted_params}")

        # Build context-aware prompt if we have conversation history
        enhanced_prompt = extracted_params['enhanced_prompt']
        if conversation_history:
            # Create a summary of recent context
            recent_context = conversation_history[-6:]  # Last 3 exchanges (6 messages)
            context_summary = "Previous conversation context:\n"
            for msg in recent_context:
                role = "User" if msg.get('role') == 'user' else "Assistant"
                content = msg.get('content', '')[:200]  # Limit to 200 chars per message
                context_summary += f"{role}: {content}\n"
            
            enhanced_prompt = f"{context_summary}\nCurrent question: {enhanced_prompt}"
            print(f"Enhanced prompt with context: {enhanced_prompt[:500]}...")  # Log first 500 chars

        print(f"Invoking Bedrock Agent with text: '{enhanced_prompt}' for session: '{session_id}' with {len(conversation_history)} context messages")

        # 2. Try Bedrock Agent first with enhanced prompt
        agent_response = None
        max_retries = 3
        base_delay = 1  # Start with 1 second delay
        
        for attempt in range(max_retries):
            try:
                response = bedrock_agent_runtime.invoke_agent(
                    agentId=AGENT_ID,
                    agentAliasId=AGENT_ALIAS_ID,
                    sessionId=session_id,
                    inputText=enhanced_prompt
                )
                
                # Process the streaming response from invoke_agent
                completion = ""
                if 'completion' in response:
                    for chunk in response['completion']:
                        if 'chunk' in chunk:
                            completion += chunk['chunk']['bytes'].decode('utf-8')

                print(f"Bedrock Agent Response: {completion}")
                agent_response = completion
                break  # Success, exit retry loop
                
            except ClientError as e:
                error_code = e.response.get('Error', {}).get('Code', '')
                
                if error_code in ['ThrottlingException', 'TooManyRequestsException']:
                    if attempt < max_retries - 1:  # Don't wait on the last attempt
                        delay = base_delay * (2 ** attempt)  # Exponential backoff
                        print(f"Rate limit hit, retrying in {delay} seconds... (attempt {attempt + 1}/{max_retries})")
                        time.sleep(delay)
                        continue
                    else:
                        agent_response = None
                        break
                else:
                    print(f"Bedrock Agent error: {e}")
                    agent_response = None
                    break

        # 3. Fallback to direct Lambda invocation if Bedrock Agent fails or gives poor response
        fallback_used = False
        final_response = agent_response
        
        # Check if Bedrock Agent response indicates parameter extraction failure or generic responses
        poor_response_indicators = [
            "please specify which doctor", "please provide the doctor's name", 
            "i don't understand", "i'm not sure", "could you clarify",
            "i found that you want to get a quote, but i need",
            "try: 'get quote for [doctor name]'",
            "available doctors include:",
            "but i need both a doctor name"
        ]
        
        # Additional logic: If we have good extracted parameters but Bedrock Agent gives generic response, use fallback
        has_good_params = (extracted_params['intent'] and extracted_params['doctorName'])
        agent_gave_generic_response = agent_response and any(indicator in agent_response.lower() for indicator in poor_response_indicators)
        
        # Force fallback when we have extracted parameters but agent gives boilerplate response
        should_use_fallback = (
            agent_gave_generic_response or 
            not agent_response or 
            (has_good_params and "try:" in (agent_response or '').lower() and "[doctor name]" in (agent_response or '').lower())
        )
            
        if should_use_fallback:
            
            print("Bedrock Agent failed or gave poor response, trying direct Lambda invocation...")
            print(f"Reason: agent_gave_generic_response={agent_gave_generic_response}, no_response={not agent_response}, has_good_params={has_good_params}")
            
            direct_response = try_direct_lambda_invocation(
                extracted_params['intent'], 
                extracted_params['doctorName'], 
                extracted_params['procedureCode']
            )
            
            if direct_response:
                final_response = direct_response
                fallback_used = True
                print(f"Direct Lambda response: {direct_response}")

        # 4. If still no good response, provide helpful guidance
        if not final_response or any(phrase in final_response.lower() for phrase in [
            "please specify which doctor", "please provide the doctor's name"
        ]):
            if extracted_params['intent'] == 'getQuote':
                final_response = f"I found that you want to get a quote, but I need both a doctor name and optionally a procedure code. " \
                               f"Try: 'Get quote for [Doctor Name]' or 'Get quote for [Doctor Name] procedure [Code]'. " \
                               f"Available doctors include: {', '.join(COMMON_DOCTORS[:5])}..."
            elif extracted_params['intent'] == 'showHistory':
                final_response = f"I found that you want to see history, but I need a doctor name. " \
                               f"Try: 'Show history for [Doctor Name]'. " \
                               f"Available doctors include: {', '.join(COMMON_DOCTORS[:5])}..."
            else:
                final_response = f"I didn't quite understand your request. You can ask me to:\n" \
                               f"• 'Show history for [Doctor Name]'\n" \
                               f"• 'Get quote for [Doctor Name]'\n" \
                               f"• 'Get quote for [Doctor Name] procedure [Code]'\n" \
                               f"Available doctors: {', '.join(COMMON_DOCTORS[:3])}..."

        # Determine if this was a successful intent mapping
        intent_mapped = bool(final_response and not any(phrase in final_response.lower() for phrase in [
            "i don't understand", "i'm not sure", "could you clarify", 
            "i don't have enough information", "i'm not able to", 
            "sorry, i don't", "i can't", "that's not something i can"
        ]))
        
        # 5. Format the response for API Gateway
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*' # Required for CORS if your frontend is on a different domain
            },
            'body': json.dumps({
                'response': final_response,
                'sessionId': session_id,
                'intentMapped': intent_mapped,
                'contextUsed': len(conversation_history) > 0,
                'originalMessage': user_text,
                'extractedParams': extracted_params,
                'fallbackUsed': fallback_used
            })
        }

    except Exception as e:
        print(f"Error in IntentMapper (proxy) Lambda: {e}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'message': f'Internal server error: {str(e)}'})
        }