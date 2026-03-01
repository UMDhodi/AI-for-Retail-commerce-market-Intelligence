"""
Lambda Deployment Package Creator for BharatSignal

Creates deployment packages for AWS Lambda functions with all dependencies.
"""

import os
import sys
import shutil
import subprocess
import logging
from pathlib import Path
import zipfile

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_lambda_package(function_name: str, handler_file: str, output_dir: str = 'lambda_packages'):
    """
    Create a Lambda deployment package
    
    Args:
        function_name: Name of the Lambda function
        handler_file: Python file containing the Lambda handler
        output_dir: Directory to store the package
    """
    logger.info(f"Creating Lambda package for: {function_name}")
    
    # Create output directory
    package_dir = Path(output_dir) / function_name
    package_dir.mkdir(parents=True, exist_ok=True)
    
    # Create temporary build directory
    build_dir = package_dir / 'build'
    if build_dir.exists():
        shutil.rmtree(build_dir)
    build_dir.mkdir()
    
    logger.info(f"Installing dependencies to: {build_dir}")
    
    # Install dependencies
    try:
        subprocess.run([
            sys.executable, '-m', 'pip', 'install',
            '-r', 'requirements.txt',
            '-t', str(build_dir),
            '--upgrade'
        ], check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install dependencies: {e}")
        return False
    
    # Copy application files
    logger.info("Copying application files...")
    
    app_files = [
        'models.py',
        'csv_processor.py',
        'bedrock_client.py',
        'prompt_engineering.py',
        'recommendation_formatter.py',
        'interactive_qa.py',
        'config.py',
        'aws_s3_handler.py',
        'aws_dynamodb_handler.py',
        handler_file
    ]
    
    for file in app_files:
        if os.path.exists(file):
            shutil.copy(file, build_dir / file)
            logger.info(f"  Copied: {file}")
        else:
            logger.warning(f"  File not found: {file}")
    
    # Create ZIP package
    zip_path = package_dir / f'{function_name}.zip'
    logger.info(f"Creating ZIP package: {zip_path}")
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(build_dir):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(build_dir)
                zipf.write(file_path, arcname)
    
    # Clean up build directory
    shutil.rmtree(build_dir)
    
    zip_size_mb = zip_path.stat().st_size / (1024 * 1024)
    logger.info(f"✓ Package created: {zip_path} ({zip_size_mb:.2f} MB)")
    
    return True


def create_lambda_handlers():
    """Create Lambda handler files"""
    logger.info("Creating Lambda handler files...")
    
    # Handler for CSV analysis
    analyze_handler = """
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
"""
    
    with open('lambda_analyze_handler.py', 'w') as f:
        f.write(analyze_handler)
    logger.info("✓ Created: lambda_analyze_handler.py")
    
    # Handler for Q&A
    ask_handler = """
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
"""
    
    with open('lambda_ask_handler.py', 'w') as f:
        f.write(ask_handler)
    logger.info("✓ Created: lambda_ask_handler.py")


def main():
    """Main packaging function"""
    logger.info("="*60)
    logger.info("BharatSignal Lambda Package Creator")
    logger.info("="*60)
    
    # Create handler files
    create_lambda_handlers()
    
    # Create packages
    packages = [
        ('bharatsignal-analyze', 'lambda_analyze_handler.py'),
        ('bharatsignal-ask', 'lambda_ask_handler.py')
    ]
    
    for function_name, handler_file in packages:
        success = create_lambda_package(function_name, handler_file)
        if not success:
            logger.error(f"Failed to create package: {function_name}")
            sys.exit(1)
    
    logger.info("\n" + "="*60)
    logger.info("✓ All Lambda packages created successfully!")
    logger.info("="*60)
    logger.info("\nPackages location: lambda_packages/")
    logger.info("\nNext steps:")
    logger.info("1. Upload packages to AWS Lambda")
    logger.info("2. Configure Lambda environment variables")
    logger.info("3. Set up API Gateway endpoints")
    logger.info("4. Test Lambda functions")


if __name__ == '__main__':
    main()
