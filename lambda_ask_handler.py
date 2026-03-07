
import json
import logging
from models import LocalContext, SalesRecord
from interactive_qa import create_qa_system
from bedrock_client import create_bedrock_client
from aws_dynamodb_handler import create_dynamodb_handler
import hashlib

logger = logging.getLogger()
logger.setLevel(logging.INFO)

bedrock_client = None
qa_system = None
dynamodb_handler = None

def get_clients():
    global bedrock_client, qa_system, dynamodb_handler
    
    if bedrock_client is None:
        bedrock_client = create_bedrock_client()
        qa_system = create_qa_system(bedrock_client)
        dynamodb_handler = create_dynamodb_handler()
    
    return bedrock_client, qa_system, dynamodb_handler

def lambda_handler(event, context):
    try:
        _, qa_sys, dynamo = get_clients()
        
        # Parse request
        body = json.loads(event.get('body', '{}'))
        session_id = body.get('session_id')
        question = body.get('question')
        sales_data_raw = body.get('sales_data', [])
        context_text = body.get('context', '')
        
        # Check cache first
        cache_key = hashlib.md5(f"{session_id}:{question}".encode()).hexdigest()
        success, cached_data, _ = dynamo.get_cached_analysis(cache_key)
        
        if success and cached_data:
            logger.info("Cache hit")
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps(cached_data.get('answer', {}))
            }
        
        # Convert sales data
        sales_data = []
        for record in sales_data_raw:
            sales_data.append(SalesRecord(
                record['date'], record['item'], 
                record['quantity'], record['price']
            ))
        
        # Generate answer
        local_context = LocalContext(context_text)
        result = qa_sys.answer_question(question, sales_data, local_context)
        
        # Cache result
        dynamo.cache_analysis(cache_key, question, result.get('answer', {}))
        
        # Add to history
        items = list(set(r.item for r in sales_data))
        dynamo.add_to_history(session_id, question, result.get('answer', {}), items)
        
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
