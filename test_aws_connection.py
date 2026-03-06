"""
Quick AWS Connection Test Script
Run this after granting IAM permissions to verify everything works
"""

import os
import sys
from dotenv import load_dotenv
import boto3
from botocore.exceptions import ClientError

# Load environment variables
load_dotenv()

def print_header(text):
    """Print formatted header"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def print_result(service, success, message):
    """Print test result"""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} | {service:20} | {message}")

def test_credentials():
    """Test if AWS credentials are configured"""
    print_header("1. Testing AWS Credentials")
    
    access_key = os.getenv('AWS_ACCESS_KEY_ID')
    secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    region = os.getenv('AWS_REGION', 'us-east-1')
    
    if not access_key or not secret_key:
        print_result("Credentials", False, "AWS credentials not found in .env file")
        return False
    
    print_result("Credentials", True, f"Found credentials for region: {region}")
    print(f"   Access Key: {access_key[:10]}...")
    return True

def test_iam_identity():
    """Test IAM identity and get user info"""
    print_header("2. Testing IAM Identity")
    
    try:
        sts = boto3.client('sts',
                          aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                          aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                          region_name=os.getenv('AWS_REGION', 'us-east-1'))
        
        identity = sts.get_caller_identity()
        user_arn = identity['Arn']
        account_id = identity['Account']
        
        print_result("IAM Identity", True, f"Authenticated as: {user_arn}")
        print(f"   Account ID: {account_id}")
        return True
        
    except ClientError as e:
        print_result("IAM Identity", False, f"Authentication failed: {e.response['Error']['Message']}")
        return False
    except Exception as e:
        print_result("IAM Identity", False, f"Error: {str(e)}")
        return False

def test_s3_permissions():
    """Test S3 permissions"""
    print_header("3. Testing S3 Permissions")
    
    try:
        s3 = boto3.client('s3',
                         aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                         aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                         region_name=os.getenv('AWS_REGION', 'us-east-1'))
        
        # Try to list buckets (basic permission test)
        response = s3.list_buckets()
        bucket_count = len(response['Buckets'])
        
        print_result("S3 List Buckets", True, f"Can list buckets ({bucket_count} found)")
        
        # Check if our buckets exist
        bucket_names = [b['Name'] for b in response['Buckets']]
        csv_bucket = os.getenv('S3_BUCKET_NAME', 'bharatsignal-csv-uploads')
        static_bucket = os.getenv('S3_STATIC_BUCKET', 'bharatsignal-static')
        
        if csv_bucket in bucket_names:
            print(f"   ✓ CSV bucket exists: {csv_bucket}")
        else:
            print(f"   ⚠ CSV bucket not found: {csv_bucket} (will be created)")
        
        if static_bucket in bucket_names:
            print(f"   ✓ Static bucket exists: {static_bucket}")
        else:
            print(f"   ⚠ Static bucket not found: {static_bucket} (will be created)")
        
        return True
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_msg = e.response['Error']['Message']
        print_result("S3 Permissions", False, f"{error_code}: {error_msg}")
        
        if error_code == 'AccessDenied':
            print("\n   💡 Solution: Grant S3 permissions to your IAM user")
            print("   See IAM_PERMISSIONS_GUIDE.md for instructions")
        
        return False
    except Exception as e:
        print_result("S3 Permissions", False, f"Error: {str(e)}")
        return False

def test_dynamodb_permissions():
    """Test DynamoDB permissions"""
    print_header("4. Testing DynamoDB Permissions")
    
    try:
        dynamodb = boto3.client('dynamodb',
                               aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                               aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                               region_name=os.getenv('AWS_REGION', 'us-east-1'))
        
        # Try to list tables (basic permission test)
        response = dynamodb.list_tables()
        table_count = len(response['TableNames'])
        
        print_result("DynamoDB List Tables", True, f"Can list tables ({table_count} found)")
        
        # Check if our tables exist
        table_names = response['TableNames']
        sessions_table = os.getenv('DYNAMODB_SESSIONS_TABLE', 'BharatSignal_UserSessions')
        cache_table = os.getenv('DYNAMODB_CACHE_TABLE', 'BharatSignal_AnalysisCache')
        history_table = os.getenv('DYNAMODB_HISTORY_TABLE', 'BharatSignal_AnalysisHistory')
        
        for table in [sessions_table, cache_table, history_table]:
            if table in table_names:
                print(f"   ✓ Table exists: {table}")
            else:
                print(f"   ⚠ Table not found: {table} (will be created)")
        
        return True
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_msg = e.response['Error']['Message']
        print_result("DynamoDB Permissions", False, f"{error_code}: {error_msg}")
        
        if error_code == 'AccessDeniedException':
            print("\n   💡 Solution: Grant DynamoDB permissions to your IAM user")
            print("   See IAM_PERMISSIONS_GUIDE.md for instructions")
        
        return False
    except Exception as e:
        print_result("DynamoDB Permissions", False, f"Error: {str(e)}")
        return False

def test_bedrock_permissions():
    """Test Bedrock permissions"""
    print_header("5. Testing Bedrock Permissions")
    
    try:
        bedrock = boto3.client('bedrock-runtime',
                              aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                              aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                              region_name=os.getenv('AWS_REGION', 'us-east-1'))
        
        # Try a simple test invocation
        model_id = os.getenv('BEDROCK_MODEL_ID', 'anthropic.claude-3-sonnet-20240229-v1:0')
        
        test_prompt = "Hello, respond with just 'OK'"
        
        response = bedrock.invoke_model(
            modelId=model_id,
            body='{"anthropic_version":"bedrock-2023-05-31","max_tokens":10,"messages":[{"role":"user","content":"' + test_prompt + '"}]}'
        )
        
        print_result("Bedrock Invoke Model", True, f"Successfully invoked {model_id}")
        print(f"   ✓ Model is accessible and responding")
        
        return True
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_msg = e.response['Error']['Message']
        print_result("Bedrock Permissions", False, f"{error_code}: {error_msg}")
        
        if error_code == 'AccessDeniedException':
            print("\n   💡 Solution: Grant Bedrock permissions AND enable model access")
            print("   1. Grant IAM permissions (see IAM_PERMISSIONS_GUIDE.md)")
            print("   2. Enable Claude 3 Sonnet in Bedrock Console")
            print("   3. Go to: https://console.aws.amazon.com/bedrock/")
        elif error_code == 'ResourceNotFoundException':
            print("\n   💡 Solution: Enable Claude 3 Sonnet model access")
            print("   Go to: https://console.aws.amazon.com/bedrock/")
            print("   Click 'Model access' → 'Manage model access'")
            print("   Enable 'Claude 3 Sonnet' by Anthropic")
        
        return False
    except Exception as e:
        print_result("Bedrock Permissions", False, f"Error: {str(e)}")
        return False

def print_summary(results):
    """Print test summary"""
    print_header("Test Summary")
    
    total = len(results)
    passed = sum(1 for r in results.values() if r)
    failed = total - passed
    
    print(f"\nTotal Tests: {total}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    
    if failed == 0:
        print("\n🎉 All tests passed! Your AWS integration is ready!")
        print("\nNext steps:")
        print("1. Run: python aws_setup.py")
        print("2. Run: python run.py")
        print("3. Open: http://localhost:5000")
        print("4. Upload a CSV file and get AI recommendations!")
    else:
        print("\n⚠️ Some tests failed. Please fix the issues above.")
        print("\n📖 For detailed help, see: IAM_PERMISSIONS_GUIDE.md")
        print("\nFailed services:")
        for service, passed in results.items():
            if not passed:
                print(f"  ❌ {service}")

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("  BharatSignal AWS Connection Test")
    print("="*60)
    print("\nThis script will test your AWS credentials and permissions.")
    print("Make sure you have granted IAM permissions before running this.")
    print("\n📖 See IAM_PERMISSIONS_GUIDE.md for setup instructions")
    
    results = {}
    
    # Test 1: Credentials
    if not test_credentials():
        print("\n❌ Cannot proceed without AWS credentials")
        print("Please configure your .env file first")
        sys.exit(1)
    results['Credentials'] = True
    
    # Test 2: IAM Identity
    results['IAM Identity'] = test_iam_identity()
    
    # Test 3: S3
    results['S3'] = test_s3_permissions()
    
    # Test 4: DynamoDB
    results['DynamoDB'] = test_dynamodb_permissions()
    
    # Test 5: Bedrock
    results['Bedrock'] = test_bedrock_permissions()
    
    # Print summary
    print_summary(results)
    
    # Exit with appropriate code
    sys.exit(0 if all(results.values()) else 1)

if __name__ == '__main__':
    main()
