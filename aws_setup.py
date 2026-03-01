"""
AWS Setup and Initialization Script for BharatSignal

This script sets up all required AWS resources:
- S3 buckets for CSV storage
- DynamoDB tables for sessions, cache, and history
- Verifies Bedrock access

Run this script once before deploying the application.
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def check_aws_credentials():
    """Verify AWS credentials are configured"""
    logger.info("Checking AWS credentials...")
    
    access_key = os.getenv('AWS_ACCESS_KEY_ID')
    secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    region = os.getenv('AWS_REGION', 'us-east-1')
    
    if not access_key or not secret_key:
        logger.error("AWS credentials not found in environment variables")
        logger.error("Please set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY in .env file")
        return False
    
    logger.info(f"✓ AWS credentials found")
    logger.info(f"✓ Region: {region}")
    return True


def setup_s3_buckets():
    """Create and configure S3 buckets"""
    logger.info("\n=== Setting up S3 Buckets ===")
    
    try:
        from aws_s3_handler import create_s3_handler
        
        # Create CSV uploads bucket
        csv_bucket = os.getenv('S3_BUCKET_NAME', 'bharatsignal-csv-uploads')
        logger.info(f"Creating S3 bucket: {csv_bucket}")
        
        s3_handler = create_s3_handler(bucket_name=csv_bucket)
        success, message = s3_handler.create_bucket_if_not_exists()
        
        if success:
            logger.info(f"✓ {message}")
        else:
            logger.error(f"✗ {message}")
            return False
        
        # Create static assets bucket (optional)
        static_bucket = os.getenv('S3_STATIC_BUCKET', 'bharatsignal-static')
        logger.info(f"Creating S3 bucket: {static_bucket}")
        
        static_handler = create_s3_handler(bucket_name=static_bucket)
        success, message = static_handler.create_bucket_if_not_exists()
        
        if success:
            logger.info(f"✓ {message}")
        else:
            logger.warning(f"⚠ Static bucket creation: {message}")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ S3 setup failed: {str(e)}")
        return False


def setup_dynamodb_tables():
    """Create and configure DynamoDB tables"""
    logger.info("\n=== Setting up DynamoDB Tables ===")
    
    try:
        from aws_dynamodb_handler import create_dynamodb_handler
        
        dynamodb_handler = create_dynamodb_handler()
        
        logger.info("Creating DynamoDB tables...")
        logger.info(f"  - {dynamodb_handler.sessions_table}")
        logger.info(f"  - {dynamodb_handler.cache_table}")
        logger.info(f"  - {dynamodb_handler.history_table}")
        
        success, message = dynamodb_handler.create_tables_if_not_exist()
        
        if success:
            logger.info(f"✓ {message}")
        else:
            logger.error(f"✗ {message}")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"✗ DynamoDB setup failed: {str(e)}")
        return False


def verify_bedrock_access():
    """Verify Amazon Bedrock access"""
    logger.info("\n=== Verifying Bedrock Access ===")
    
    try:
        from bedrock_client import test_bedrock_connection
        
        logger.info("Testing Bedrock connection...")
        success, message = test_bedrock_connection()
        
        if success:
            logger.info(f"✓ {message}")
            logger.info(f"✓ Model: anthropic.claude-3-sonnet-20240229-v1:0")
        else:
            logger.error(f"✗ {message}")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Bedrock verification failed: {str(e)}")
        return False


def print_summary(results):
    """Print setup summary"""
    logger.info("\n" + "="*60)
    logger.info("AWS SETUP SUMMARY")
    logger.info("="*60)
    
    all_success = all(results.values())
    
    for step, success in results.items():
        status = "✓ SUCCESS" if success else "✗ FAILED"
        logger.info(f"{step}: {status}")
    
    logger.info("="*60)
    
    if all_success:
        logger.info("\n🎉 AWS setup completed successfully!")
        logger.info("\nNext steps:")
        logger.info("1. Update your .env file with actual AWS credentials")
        logger.info("2. Run the Flask application: python run.py")
        logger.info("3. Upload CSV files to test S3 integration")
        logger.info("4. Monitor DynamoDB tables in AWS Console")
    else:
        logger.error("\n⚠ AWS setup completed with errors")
        logger.error("Please review the errors above and fix them before proceeding")
        logger.error("\nCommon issues:")
        logger.error("- Invalid AWS credentials")
        logger.error("- Insufficient IAM permissions")
        logger.error("- Bedrock not enabled in your region")
        logger.error("- Network connectivity issues")
    
    return all_success


def main():
    """Main setup function"""
    logger.info("="*60)
    logger.info("BharatSignal AWS Setup Script")
    logger.info("="*60)
    
    results = {}
    
    # Step 1: Check credentials
    if not check_aws_credentials():
        logger.error("\n❌ Setup aborted: AWS credentials not configured")
        sys.exit(1)
    
    # Step 2: Setup S3
    results['S3 Buckets'] = setup_s3_buckets()
    
    # Step 3: Setup DynamoDB
    results['DynamoDB Tables'] = setup_dynamodb_tables()
    
    # Step 4: Verify Bedrock
    results['Bedrock Access'] = verify_bedrock_access()
    
    # Print summary
    success = print_summary(results)
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
