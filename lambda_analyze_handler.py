
import json
import logging
from models import LocalContext
from csv_processor import parse_csv
from interactive_qa import create_qa_system
from bedrock_client import create_bedrock_client
from aws_s3_handler import create_s3_handler
from aws_dynamodb_handler import create_dynamodb_handler
import io

logger = logging.getLogger()
logger.setLevel(logging.INFO)

bedrock_client = None
qa_system = None
s3_handler = None
dynamodb_handler = None

def get_clients():
    global bedrock_client, qa_system, s3_handler, dynamodb_handler
    
    if bedrock_client is None:
        bedrock_client = create_bedrock_client()
        qa_system = create_qa_system(bedrock_client)
        s3_handler = create_s3_handler()
        dynamodb_handler = create_dynamodb_handler()
    
    return bedrock_client, qa_system, s3_handler, dynamodb_handler

def lambda_handler(event, context):
    try:
        _, qa_sys, s3, dynamo = get_clients()
        
        # Parse request
        body = json.loads(event.get('body', '{}'))
        session_id = body.get('session_id')
        csv_content = body.get('csv_content')  # Base64 encoded
        question = body.get('question', 'Tell me about my stock')
        context_text = body.get('context', '')
        
        # Decode and parse CSV
        import base64
        csv_bytes = base64.b64decode(csv_content)
        csv_file = io.BytesIO(csv_bytes)
        
        # Process CSV
        csv_result = parse_csv(csv_file)
        if not csv_result.success:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'CSV validation failed'})
            }
        
        sales_data = csv_result.valid_records
        
        # Upload to S3
        success, message, s3_key = s3.upload_csv(csv_bytes, session_id, 'sales_data.csv')
        if not success:
            logger.error(f"S3 upload failed: {message}")
        
        # Create session in DynamoDB
        sales_summary = {
            'total_records': len(sales_data),
            'items': list(set(r.item for r in sales_data))
        }
        dynamo.create_session(session_id, s3_key or '', sales_summary)
        
        # Generate answer
        local_context = LocalContext(context_text)
        result = qa_sys.answer_question(question, sales_data, local_context)
        
        # Cache result
        import hashlib
        cache_key = hashlib.md5(f"{session_id}:{question}".encode()).hexdigest()
        dynamo.cache_analysis(cache_key, question, result.get('answer', {}))
        
        # Add to history
        dynamo.add_to_history(session_id, question, result.get('answer', {}), 
                             sales_summary['items'])
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps(result)
        }
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
