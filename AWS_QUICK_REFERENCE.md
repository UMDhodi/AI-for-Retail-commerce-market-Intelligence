# BharatSignal AWS Quick Reference

## 🚀 Quick Start Commands

### Initial Setup
```bash
# 1. Configure environment
cp .env.example .env
# Edit .env with your AWS credentials

# 2. Create AWS resources
python aws_setup.py

# 3. Test integration
python test_aws_integration.py

# 4. Run application
python run.py
```

## 📊 GenAI Model Information

**Model**: Claude 3 Sonnet by Anthropic  
**Model ID**: `anthropic.claude-3-sonnet-20240229-v1:0`  
**Provider**: Amazon Bedrock  
**Region**: us-east-1  
**Cost**: ~$0.02 per recommendation

## 🗄️ Data Strategy

| Data Type | Storage | Retention | Purpose |
|-----------|---------|-----------|---------|
| CSV Files | S3 | 30 days | Sales data storage |
| Sessions | DynamoDB | 24 hours | User session tracking |
| Cache | DynamoDB | 1 hour | Fast response times |
| History | DynamoDB | 7 days | Query history |

## 💰 Cost Breakdown (100 users)

| Service | Monthly Cost |
|---------|--------------|
| Bedrock (Claude 3 Sonnet) | ~$60 |
| Lambda | ~$0.60 |
| S3 | ~$0.23 |
| DynamoDB | ~$2 |
| API Gateway | ~$0.10 |
| CloudWatch | ~$5 |
| **Total** | **~$68** |

## 🔧 AWS Resources

### S3 Buckets
- `bharatsignal-csv-uploads` - CSV file storage
- `bharatsignal-static` - Static assets

### DynamoDB Tables
- `BharatSignal_UserSessions` - Session data
- `BharatSignal_AnalysisCache` - Cached results
- `BharatSignal_AnalysisHistory` - Query history

### Lambda Functions
- `bharatsignal-analyze` - CSV analysis
- `bharatsignal-ask` - Q&A handling

## 📝 Environment Variables

```bash
# AWS Credentials
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_REGION=us-east-1

# S3
S3_BUCKET_NAME=bharatsignal-csv-uploads
S3_STATIC_BUCKET=bharatsignal-static

# DynamoDB
DYNAMODB_SESSIONS_TABLE=BharatSignal_UserSessions
DYNAMODB_CACHE_TABLE=BharatSignal_AnalysisCache
DYNAMODB_HISTORY_TABLE=BharatSignal_AnalysisHistory

# Bedrock
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
BEDROCK_MAX_TOKENS=1000
BEDROCK_TEMPERATURE=0.7
```

## 🧪 Testing Commands

```bash
# Test S3 integration
python -c "from aws_s3_handler import create_s3_handler; print(create_s3_handler().create_bucket_if_not_exists())"

# Test DynamoDB integration
python -c "from aws_dynamodb_handler import create_dynamodb_handler; print(create_dynamodb_handler().create_tables_if_not_exist())"

# Test Bedrock integration
python -c "from bedrock_client import test_bedrock_connection; print(test_bedrock_connection())"

# Run all tests
python test_aws_integration.py
```

## 📦 Lambda Deployment

```bash
# Create Lambda packages
python lambda_package.py

# Packages created in:
# lambda_packages/bharatsignal-analyze/bharatsignal-analyze.zip
# lambda_packages/bharatsignal-ask/bharatsignal-ask.zip
```

## 🔍 Monitoring Commands

```bash
# View Lambda logs
aws logs tail /aws/lambda/bharatsignal-analyze --follow

# Check S3 bucket
aws s3 ls s3://bharatsignal-csv-uploads/

# List DynamoDB tables
aws dynamodb list-tables

# View costs
aws ce get-cost-and-usage \
  --time-period Start=2024-01-01,End=2024-01-31 \
  --granularity MONTHLY \
  --metrics BlendedCost
```

## 🐛 Troubleshooting

### Issue: AWS credentials not found
```bash
# Solution: Configure AWS CLI
aws configure
```

### Issue: S3 bucket already exists
```bash
# Solution: Use unique bucket name
# Edit .env: S3_BUCKET_NAME=bharatsignal-csv-YOUR_UNIQUE_ID
```

### Issue: Bedrock access denied
```bash
# Solution: Enable Bedrock in AWS Console
# 1. Go to AWS Console → Bedrock
# 2. Enable model access
# 3. Select Claude 3 Sonnet
```

### Issue: Lambda timeout
```bash
# Solution: Increase timeout
aws lambda update-function-configuration \
  --function-name bharatsignal-analyze \
  --timeout 60
```

## 📚 Documentation Files

- `AWS_INTEGRATION_SUMMARY.md` - Complete overview
- `AWS_DEPLOYMENT_GUIDE.md` - Step-by-step deployment
- `AWS_ARCHITECTURE.md` - Architecture details
- `AWS_QUICK_REFERENCE.md` - This file

## ✅ Deployment Checklist

- [ ] AWS credentials configured
- [ ] .env file created and configured
- [ ] S3 buckets created (`python aws_setup.py`)
- [ ] DynamoDB tables created
- [ ] Bedrock access verified
- [ ] Integration tests passed (`python test_aws_integration.py`)
- [ ] Lambda functions packaged (`python lambda_package.py`)
- [ ] Lambda functions deployed (see deployment guide)
- [ ] API Gateway configured
- [ ] Frontend updated with API endpoints
- [ ] Monitoring set up
- [ ] Cost alerts configured

## 🎯 24-Hour Goal Timeline

| Time | Phase | Tasks |
|------|-------|-------|
| 0-4h | Setup | AWS credentials, S3, DynamoDB, Bedrock |
| 4-8h | Testing | Integration tests, local testing |
| 8-12h | Lambda | Package and deploy functions |
| 12-20h | API Gateway | Configure endpoints, CORS |
| 20-24h | Production | End-to-end testing, monitoring |

## 🔗 Useful Links

- [AWS Console](https://console.aws.amazon.com/)
- [Bedrock Console](https://console.aws.amazon.com/bedrock/)
- [S3 Console](https://console.aws.amazon.com/s3/)
- [DynamoDB Console](https://console.aws.amazon.com/dynamodb/)
- [Lambda Console](https://console.aws.amazon.com/lambda/)
- [CloudWatch Console](https://console.aws.amazon.com/cloudwatch/)

## 📞 Support

**Documentation**: See `AWS_DEPLOYMENT_GUIDE.md`  
**Issues**: Check CloudWatch Logs  
**Costs**: AWS Cost Explorer  
**Security**: IAM Console

---

**Quick Status Check**:
```bash
# Run this to verify everything is working
python test_aws_integration.py && echo "✅ All systems operational!"
```
