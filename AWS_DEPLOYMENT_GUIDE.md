# BharatSignal AWS Deployment Guide

Complete step-by-step guide to deploy BharatSignal on AWS infrastructure.

## 🎯 Overview

This guide will help you deploy BharatSignal using:
- **Amazon Bedrock** (Claude 3 Sonnet) - Already integrated ✅
- **AWS Lambda** - Serverless compute
- **Amazon S3** - CSV file storage
- **Amazon DynamoDB** - Session and cache management
- **API Gateway** - RESTful API endpoints

## 📋 Prerequisites

### 1. AWS Account Setup
- AWS account with billing enabled
- IAM user with programmatic access
- Required IAM permissions:
  - AmazonBedrockFullAccess
  - AWSLambda_FullAccess
  - AmazonS3FullAccess
  - AmazonDynamoDBFullAccess
  - AmazonAPIGatewayAdministrator
  - CloudWatchFullAccess

### 2. Local Development Environment
- Python 3.11 or higher
- AWS CLI installed and configured
- Git (for version control)
- Virtual environment (recommended)

### 3. AWS CLI Configuration
```bash
aws configure
# Enter your AWS Access Key ID
# Enter your AWS Secret Access Key
# Default region: us-east-1
# Default output format: json
```

## 🚀 Phase 1: Initial Setup (0-4 hours)

### Step 1.1: Clone and Setup Project
```bash
# Clone repository (if not already done)
cd bharatsignal

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 1.2: Configure Environment Variables
```bash
# Copy example environment file
cp .env.example .env

# Edit .env file with your AWS credentials
# Required variables:
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_REGION=us-east-1

# S3 Configuration
S3_BUCKET_NAME=bharatsignal-csv-uploads-YOUR_UNIQUE_ID
S3_STATIC_BUCKET=bharatsignal-static-YOUR_UNIQUE_ID

# DynamoDB Configuration
DYNAMODB_SESSIONS_TABLE=BharatSignal_UserSessions
DYNAMODB_CACHE_TABLE=BharatSignal_AnalysisCache
DYNAMODB_HISTORY_TABLE=BharatSignal_AnalysisHistory
```

**Important**: Replace `YOUR_UNIQUE_ID` with a unique identifier (e.g., your company name or random string) to ensure bucket names are globally unique.

### Step 1.3: Verify Bedrock Access
```bash
# Test Bedrock connection
python -c "from bedrock_client import test_bedrock_connection; print(test_bedrock_connection())"
```

Expected output:
```
(True, 'Bedrock connection successful')
```

If you see an error:
- Verify AWS credentials are correct
- Ensure Bedrock is enabled in your AWS region (us-east-1)
- Check IAM permissions include Bedrock access

## 📦 Phase 2: S3 Setup (4-8 hours)

### Step 2.1: Run AWS Setup Script
```bash
# This script creates S3 buckets and DynamoDB tables
python aws_setup.py
```

The script will:
1. ✓ Verify AWS credentials
2. ✓ Create S3 bucket for CSV uploads
3. ✓ Create S3 bucket for static assets
4. ✓ Enable versioning on buckets
5. ✓ Set lifecycle policies (30-day expiration)
6. ✓ Enable server-side encryption

### Step 2.2: Verify S3 Buckets
```bash
# List your S3 buckets
aws s3 ls

# You should see:
# bharatsignal-csv-uploads-YOUR_UNIQUE_ID
# bharatsignal-static-YOUR_UNIQUE_ID
```

### Step 2.3: Test S3 Upload
```python
# Test S3 integration
from aws_s3_handler import create_s3_handler
import uuid

s3_handler = create_s3_handler()
session_id = str(uuid.uuid4())
test_content = b"date,item,quantity,price\n2024-01-15,Rice,10,50.00"

success, message, s3_key = s3_handler.upload_csv(test_content, session_id, "test.csv")
print(f"Upload: {success} - {message}")
print(f"S3 Key: {s3_key}")
```

## 🗄️ Phase 3: DynamoDB Setup (8-12 hours)

### Step 3.1: Verify DynamoDB Tables
The `aws_setup.py` script already created the tables. Verify:

```bash
# List DynamoDB tables
aws dynamodb list-tables

# You should see:
# - BharatSignal_UserSessions
# - BharatSignal_AnalysisCache
# - BharatSignal_AnalysisHistory
```

### Step 3.2: Check Table Details
```bash
# Describe sessions table
aws dynamodb describe-table --table-name BharatSignal_UserSessions

# Verify:
# - BillingMode: PAY_PER_REQUEST
# - TimeToLiveStatus: ENABLED
# - TimeToLiveAttributeName: expires_at
```

### Step 3.3: Test DynamoDB Operations
```python
# Test DynamoDB integration
from aws_dynamodb_handler import create_dynamodb_handler
import uuid

dynamo = create_dynamodb_handler()
session_id = str(uuid.uuid4())

# Create session
success, message = dynamo.create_session(
    session_id, 
    "test/file.csv",
    {"total_records": 10, "items": ["Rice", "Oil"]}
)
print(f"Create session: {success} - {message}")

# Retrieve session
success, data, message = dynamo.get_session(session_id)
print(f"Get session: {success} - {message}")
print(f"Data: {data}")
```

## ⚡ Phase 4: Lambda Deployment (12-20 hours)

### Step 4.1: Create Lambda Packages
```bash
# Generate Lambda deployment packages
python lambda_package.py
```

This creates:
- `lambda_packages/bharatsignal-analyze/bharatsignal-analyze.zip`
- `lambda_packages/bharatsignal-ask/bharatsignal-ask.zip`

### Step 4.2: Create IAM Role for Lambda
```bash
# Create trust policy file
cat > lambda-trust-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

# Create IAM role
aws iam create-role \
  --role-name BharatSignalLambdaRole \
  --assume-role-policy-document file://lambda-trust-policy.json

# Attach policies
aws iam attach-role-policy \
  --role-name BharatSignalLambdaRole \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

aws iam attach-role-policy \
  --role-name BharatSignalLambdaRole \
  --policy-arn arn:aws:iam::aws:policy/AmazonBedrockFullAccess

aws iam attach-role-policy \
  --role-name BharatSignalLambdaRole \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess

aws iam attach-role-policy \
  --role-name BharatSignalLambdaRole \
  --policy-arn arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess
```

### Step 4.3: Deploy Lambda Functions

#### Deploy Analyze Function
```bash
# Get IAM role ARN
ROLE_ARN=$(aws iam get-role --role-name BharatSignalLambdaRole --query 'Role.Arn' --output text)

# Create Lambda function
aws lambda create-function \
  --function-name bharatsignal-analyze \
  --runtime python3.11 \
  --role $ROLE_ARN \
  --handler lambda_analyze_handler.lambda_handler \
  --zip-file fileb://lambda_packages/bharatsignal-analyze/bharatsignal-analyze.zip \
  --timeout 30 \
  --memory-size 512 \
  --environment Variables="{
    AWS_REGION=us-east-1,
    S3_BUCKET_NAME=bharatsignal-csv-uploads-YOUR_UNIQUE_ID,
    DYNAMODB_SESSIONS_TABLE=BharatSignal_UserSessions,
    DYNAMODB_CACHE_TABLE=BharatSignal_AnalysisCache,
    DYNAMODB_HISTORY_TABLE=BharatSignal_AnalysisHistory
  }"
```

#### Deploy Ask Function
```bash
aws lambda create-function \
  --function-name bharatsignal-ask \
  --runtime python3.11 \
  --role $ROLE_ARN \
  --handler lambda_ask_handler.lambda_handler \
  --zip-file fileb://lambda_packages/bharatsignal-ask/bharatsignal-ask.zip \
  --timeout 30 \
  --memory-size 512 \
  --environment Variables="{
    AWS_REGION=us-east-1,
    DYNAMODB_SESSIONS_TABLE=BharatSignal_UserSessions,
    DYNAMODB_CACHE_TABLE=BharatSignal_AnalysisCache,
    DYNAMODB_HISTORY_TABLE=BharatSignal_AnalysisHistory
  }"
```

### Step 4.4: Test Lambda Functions
```bash
# Test analyze function
aws lambda invoke \
  --function-name bharatsignal-analyze \
  --payload '{"body": "{\"session_id\": \"test123\", \"csv_content\": \"ZGF0ZSxpdGVtLHF1YW50aXR5LHByaWNlCjIwMjQtMDEtMTUsUmljZSwxMCw1MC4wMA==\", \"question\": \"Tell me about my stock\"}"}' \
  response.json

# Check response
cat response.json
```

## 🌐 Phase 5: API Gateway Setup (20-24 hours)

### Step 5.1: Create REST API
```bash
# Create API
API_ID=$(aws apigateway create-rest-api \
  --name "BharatSignal API" \
  --description "API for BharatSignal kirana shop assistant" \
  --endpoint-configuration types=REGIONAL \
  --query 'id' --output text)

echo "API ID: $API_ID"

# Get root resource ID
ROOT_ID=$(aws apigateway get-resources \
  --rest-api-id $API_ID \
  --query 'items[0].id' --output text)
```

### Step 5.2: Create API Resources
```bash
# Create /analyze resource
ANALYZE_ID=$(aws apigateway create-resource \
  --rest-api-id $API_ID \
  --parent-id $ROOT_ID \
  --path-part analyze \
  --query 'id' --output text)

# Create /ask resource
ASK_ID=$(aws apigateway create-resource \
  --rest-api-id $API_ID \
  --parent-id $ROOT_ID \
  --path-part ask \
  --query 'id' --output text)
```

### Step 5.3: Create POST Methods
```bash
# Create POST method for /analyze
aws apigateway put-method \
  --rest-api-id $API_ID \
  --resource-id $ANALYZE_ID \
  --http-method POST \
  --authorization-type NONE

# Create POST method for /ask
aws apigateway put-method \
  --rest-api-id $API_ID \
  --resource-id $ASK_ID \
  --http-method POST \
  --authorization-type NONE
```

### Step 5.4: Integrate with Lambda
```bash
# Get AWS account ID
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
REGION=us-east-1

# Integrate /analyze with Lambda
aws apigateway put-integration \
  --rest-api-id $API_ID \
  --resource-id $ANALYZE_ID \
  --http-method POST \
  --type AWS_PROXY \
  --integration-http-method POST \
  --uri "arn:aws:apigateway:$REGION:lambda:path/2015-03-31/functions/arn:aws:lambda:$REGION:$ACCOUNT_ID:function:bharatsignal-analyze/invocations"

# Integrate /ask with Lambda
aws apigateway put-integration \
  --rest-api-id $API_ID \
  --resource-id $ASK_ID \
  --http-method POST \
  --type AWS_PROXY \
  --integration-http-method POST \
  --uri "arn:aws:apigateway:$REGION:lambda:path/2015-03-31/functions/arn:aws:lambda:$REGION:$ACCOUNT_ID:function:bharatsignal-ask/invocations"
```

### Step 5.5: Grant API Gateway Permissions
```bash
# Allow API Gateway to invoke analyze function
aws lambda add-permission \
  --function-name bharatsignal-analyze \
  --statement-id apigateway-invoke \
  --action lambda:InvokeFunction \
  --principal apigateway.amazonaws.com \
  --source-arn "arn:aws:execute-api:$REGION:$ACCOUNT_ID:$API_ID/*/*/analyze"

# Allow API Gateway to invoke ask function
aws lambda add-permission \
  --function-name bharatsignal-ask \
  --statement-id apigateway-invoke \
  --action lambda:InvokeFunction \
  --principal apigateway.amazonaws.com \
  --source-arn "arn:aws:execute-api:$REGION:$ACCOUNT_ID:$API_ID/*/*/ask"
```

### Step 5.6: Enable CORS
```bash
# Enable CORS for /analyze
aws apigateway put-method \
  --rest-api-id $API_ID \
  --resource-id $ANALYZE_ID \
  --http-method OPTIONS \
  --authorization-type NONE

aws apigateway put-integration \
  --rest-api-id $API_ID \
  --resource-id $ANALYZE_ID \
  --http-method OPTIONS \
  --type MOCK \
  --request-templates '{"application/json": "{\"statusCode\": 200}"}'

# Similar for /ask
aws apigateway put-method \
  --rest-api-id $API_ID \
  --resource-id $ASK_ID \
  --http-method OPTIONS \
  --authorization-type NONE

aws apigateway put-integration \
  --rest-api-id $API_ID \
  --resource-id $ASK_ID \
  --http-method OPTIONS \
  --type MOCK \
  --request-templates '{"application/json": "{\"statusCode\": 200}"}'
```

### Step 5.7: Deploy API
```bash
# Create deployment
aws apigateway create-deployment \
  --rest-api-id $API_ID \
  --stage-name prod

# Get API endpoint
echo "API Endpoint: https://$API_ID.execute-api.$REGION.amazonaws.com/prod"
```

### Step 5.8: Test API
```bash
# Test /analyze endpoint
curl -X POST \
  https://$API_ID.execute-api.$REGION.amazonaws.com/prod/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test123",
    "csv_content": "ZGF0ZSxpdGVtLHF1YW50aXR5LHByaWNlCjIwMjQtMDEtMTUsUmljZSwxMCw1MC4wMA==",
    "question": "Tell me about my stock"
  }'
```

## 📊 Monitoring and Maintenance

### CloudWatch Logs
```bash
# View Lambda logs
aws logs tail /aws/lambda/bharatsignal-analyze --follow

# View API Gateway logs
aws logs tail API-Gateway-Execution-Logs_$API_ID/prod --follow
```

### Cost Monitoring
```bash
# Check current month costs
aws ce get-cost-and-usage \
  --time-period Start=$(date -d "1 month ago" +%Y-%m-01),End=$(date +%Y-%m-%d) \
  --granularity MONTHLY \
  --metrics BlendedCost \
  --group-by Type=SERVICE
```

### Performance Metrics
- Lambda invocations: CloudWatch → Lambda → Metrics
- API Gateway requests: CloudWatch → API Gateway → Metrics
- DynamoDB operations: CloudWatch → DynamoDB → Metrics
- Bedrock API calls: CloudWatch → Bedrock → Metrics

## 🔒 Security Best Practices

1. **IAM Roles**: Use least privilege principle
2. **API Keys**: Enable API keys for production
3. **Rate Limiting**: Configure throttling on API Gateway
4. **Encryption**: Enable at rest and in transit
5. **Secrets**: Use AWS Secrets Manager for sensitive data
6. **VPC**: Consider VPC for Lambda functions
7. **WAF**: Add AWS WAF for API protection

## 💰 Cost Optimization

### Expected Monthly Costs (100 users, 10 requests/day)
- Bedrock (Claude 3 Sonnet): ~$60
- Lambda: ~$0.60
- S3: ~$0.23
- DynamoDB: ~$2
- API Gateway: ~$0.10
- CloudWatch: ~$5
- **Total**: ~$68/month

### Cost Reduction Tips
1. Use DynamoDB on-demand pricing
2. Enable S3 lifecycle policies
3. Set Lambda memory to minimum required
4. Use CloudWatch Logs retention policies
5. Enable API Gateway caching
6. Monitor and optimize Bedrock token usage

## 🐛 Troubleshooting

### Common Issues

**Issue**: Lambda timeout
- **Solution**: Increase timeout to 60 seconds
- **Command**: `aws lambda update-function-configuration --function-name bharatsignal-analyze --timeout 60`

**Issue**: S3 access denied
- **Solution**: Check IAM role has S3 permissions
- **Command**: `aws iam list-attached-role-policies --role-name BharatSignalLambdaRole`

**Issue**: DynamoDB throttling
- **Solution**: Switch to on-demand capacity or increase provisioned capacity

**Issue**: Bedrock access denied
- **Solution**: Verify Bedrock is enabled in your region and IAM has permissions

## 📞 Support

For issues or questions:
1. Check CloudWatch Logs for error details
2. Review AWS documentation
3. Contact AWS Support (if you have a support plan)

## ✅ Deployment Checklist

- [ ] AWS credentials configured
- [ ] Bedrock access verified
- [ ] S3 buckets created
- [ ] DynamoDB tables created
- [ ] Lambda functions deployed
- [ ] API Gateway configured
- [ ] CORS enabled
- [ ] API tested end-to-end
- [ ] CloudWatch monitoring set up
- [ ] Cost alerts configured
- [ ] Security best practices applied

## 🎉 Success!

Your BharatSignal application is now deployed on AWS! 

**API Endpoint**: `https://$API_ID.execute-api.us-east-1.amazonaws.com/prod`

Next steps:
1. Update frontend to use API Gateway endpoints
2. Set up custom domain (optional)
3. Configure CloudFront CDN (optional)
4. Enable API authentication
5. Set up CI/CD pipeline
