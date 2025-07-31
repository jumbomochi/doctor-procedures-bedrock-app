import json
import boto3
import os
import time
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

# Get agent details from environment variables
AGENT_ID = os.environ.get('BEDROCK_AGENT_ID')
AGENT_ALIAS_ID = os.environ.get('BEDROCK_AGENT_ALIAS_ID')

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

        if not user_text:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'message': 'Text input is required in the request body.'})
            }

        print(f"Invoking Bedrock Agent with text: '{user_text}' for session: '{session_id}'")

        # 2. Invoke the Bedrock Agent with retry logic for rate limiting
        max_retries = 3
        base_delay = 1  # Start with 1 second delay
        
        for attempt in range(max_retries):
            try:
                response = bedrock_agent_runtime.invoke_agent(
                    agentId=AGENT_ID,
                    agentAliasId=AGENT_ALIAS_ID,
                    sessionId=session_id,
                    inputText=user_text
                )
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
                        return {
                            'statusCode': 429,
                            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                            'body': json.dumps({
                                'message': 'Bedrock Agent rate limit exceeded. Please try again in a few minutes.',
                                'error': 'RATE_LIMIT_EXCEEDED'
                            })
                        }
                else:
                    # Re-raise non-rate-limit errors
                    raise e

        # 3. Process the streaming response from invoke_agent
        # Bedrock Agent responses come as a stream of chunks.
        completion = ""
        if 'completion' in response:
            for chunk in response['completion']:
                if 'chunk' in chunk:
                    completion += chunk['chunk']['bytes'].decode('utf-8')

        print(f"Bedrock Agent Response: {completion}")

        # 4. Format the response for API Gateway
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*' # Required for CORS if your frontend is on a different domain
            },
            'body': json.dumps({
                'response': completion,
                'sessionId': session_id
            })
        }

    except Exception as e:
        print(f"Error in IntentMapper (proxy) Lambda: {e}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'message': f'Internal server error: {str(e)}'})
        }