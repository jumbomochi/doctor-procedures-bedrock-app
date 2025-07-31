import json
import boto3
import os

bedrock_agent_runtime = boto3.client(
    service_name='bedrock-agent-runtime',
    region_name=os.environ.get('AWS_REGION', 'us-east-1') # Ensure your Bedrock Agent region
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

        # 2. Invoke the Bedrock Agent
        response = bedrock_agent_runtime.invoke_agent(
            agentId=AGENT_ID,
            agentAliasId=AGENT_ALIAS_ID,
            sessionId=session_id,
            inputText=user_text
        )

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