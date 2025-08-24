import boto3
import json
import uuid
import re  

# Initialize AWS Client for Bedrock Agent Runtime
bedrock_agent_runtime = boto3.client("bedrock-agent-runtime", region_name="us-east-1")

AGENT_ID = "<dummy-value>" 
AGENT_ALIAS_ID = "<dummy-value>"

def lambda_handler(event, context):
    try:
        # Parse API Gateway input safely
        if "body" not in event:
            return {
                "statusCode": 400,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type"
                },
                "body": json.dumps({"error": "Request body is missing."})
            }

        # Parse the request body
        request_body = json.loads(event["body"]) if event["body"] else {}

        # Check if inputText exists in the request body
        user_prompt = request_body.get("inputText", "").strip()
        if not user_prompt:
            return {
                "statusCode": 400,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type"
                },
                "body": json.dumps({"error": "Missing 'inputText' in request body."})
            }

        # Generate a unique session ID for tracking
        session_id = str(uuid.uuid4())

        # Call the Bedrock Agent
        response = bedrock_agent_runtime.invoke_agent(
            agentId=AGENT_ID,
            agentAliasId=AGENT_ALIAS_ID,
            sessionId=session_id,
            inputText=user_prompt
        )

        # Ensure 'completion' field exists in the response
        if "completion" not in response or not response["completion"]:
            return {
                "statusCode": 500,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type"
                },
                "body": json.dumps({"error": "Missing 'completion' field in response."})
            }

        # Read the streaming response
        generated_response = ""
        for event in response.get("completion", []):
            chunk = event.get("chunk", {})
            if chunk and "bytes" in chunk:
                generated_response += chunk["bytes"].decode("utf-8")

        # Handle empty responses
        if not generated_response.strip():
            return {
                "statusCode": 500,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "POST, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type"
                },
                "body": json.dumps({"error": "Bedrock response is empty."})
            }
=
        try:
            response_data = json.loads(generated_response)
            result = response_data.get("result", generated_response)  # Fallback to raw text if 'result' key is missing
        except json.JSONDecodeError:
            result = generated_response.strip()

        # Remove placeholders like %[...]% using regex
        result = re.sub(r"%\[[^\]]*\]%", "", result).strip()

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type"
            },
            "body": json.dumps({"response": result})
        }

    except Exception as e:
        print("Error:", str(e))
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type"
            },
            "body": json.dumps({"error": str(e)})
        }
