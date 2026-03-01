# BharatSignal AWS Architecture & Implementation Plan

## 🎯 Current Status

### ✅ **Already Implemented**:
- **Amazon Bedrock Integration**: Using Claude 3 Sonnet model
- **Model ID**: `anthropic.claude-3-sonnet-20240229-v1:0`
- **Region**: `us-east-1` (US East - N. Virginia)
- **Authentication**: AWS credentials via environment variables

### 📊 **GenAI Model Details**:

**Model**: **Claude 3 Sonnet by Anthropic**
- **Version**: `anthropic.claude-3-sonnet-20240229-v1:0`
- **Provider**: Anthropic (via Amazon Bedrock)
- **Capabilities**:
  - 200K context window
  - Advanced reasoning and analysis
  - Structured output generation
  - Business intelligence and recommendations
  - Natural language understanding in English and Hindi

**Why Claude 3 Sonnet?**
- ✅ **Balanced Performance**: Best price-to-performance ratio
- ✅ **Business Intelligence**: Excellent at analyzing sales data and providing actionable insights
- ✅ **Structured Output**: Generates consistent, parseable recommendations
- ✅ **Cost-Effective**: ~$3 per million input tokens, $15 per million output tokens
- ✅ **Low Latency**: Fast response times for real-time recommendations

## 🏗️ Proposed AWS Architecture

### **Current Architecture** (Local Development):
```
User Browser
    ↓
Flask App (Local)
    ↓
Amazon Bedrock (Claude 3 Sonnet)
```

### **Target Production Architecture**:
```
User Browser
    ↓
CloudFront (CDN)
    ↓
API Gateway (REST API)
    ↓
AWS Lambda (Python 3.11)
    ├── CSV Processing
    ├── Q&A System
    └── Amazon Bedrock (Claude 3 Sonnet)
    ↓
├── Amazon S3 (CSV Storage)
├── DynamoDB (User Sessions & Cache)
└── CloudWatch (Logging & Monitoring)
```

## 📦 AWS Services Integration Plan

### 1. **Amazon Bedrock** ✅ (Already Integrated)
**Purpose**: AI-powered business recommendations

**Current Implementation**:
```python
# bedrock_client.py
model_id = 'anthropic.claude-3-sonnet-20240229-v1:0'
region = 'us-east-1'
max_tokens = 1000
temperature = 0.7
```

**Configuration**:
- Model: Claude 3 Sonnet
- Max tokens: 1000 (adjustable for longer responses)
- Temperature: 0.7 (balanced creativity/consistency)
- Region: us-east-1

**Cost Estimate**:
- Input: $3 per 1M tokens (~$0.003 per request)
- Output: $15 per 1M tokens (~$0.015 per request)
- **Average cost per recommendation**: ~$0.02

---

### 2. **AWS Lambda** 🔄 (To Implement)
**Purpose**: Serverless compute for API endpoints

**Functions to Create**:
1. **`analyze-csv`**: Process uploaded CSV and generate recommendations
2. **`ask-question`**: Handle Q&A queries
3. **`get-suggestions`**: Generate suggested questions

**Benefits**:
- ✅ Auto-scaling (0 to 1000s of concurrent users)
- ✅ Pay per request (no idle costs)
- ✅ Built-in high availability
- ✅ Integrated with API Gateway

**Configuration**:
```yaml
Runtime: Python 3.11
Memory: 512 MB (adjustable)
Timeout: 30 seconds
Environment Variables:
  - AWS_REGION: us-east-1
  - BEDROCK_MODEL_ID: anthropic.claude-3-sonnet-20240229-v1:0
```

**Cost Estimate**:
- Free tier: 1M requests/month
- After free tier: $0.20 per 1M requests
- **Average cost**: ~$0.0002 per request

---

### 3. **Amazon S3** 🔄 (To Implement)
**Purpose**: Store uploaded CSV files and static assets

**Buckets to Create**:
1. **`bharatsignal-csv-uploads`**: User-uploaded sales data
2. **`bharatsignal-static`**: Frontend assets (HTML, CSS, JS)

**Features**:
- ✅ Versioning enabled (track CSV changes)
- ✅ Lifecycle policies (auto-delete old files after 30 days)
- ✅ Server-side encryption (AES-256)
- ✅ Pre-signed URLs for secure uploads

**Data Strategy**:
```
bharatsignal-csv-uploads/
├── {user-session-id}/
│   ├── {timestamp}-sales-data.csv
│   └── metadata.json
└── temp/ (auto-delete after 24 hours)
```

**Cost Estimate**:
- Storage: $0.023 per GB/month
- Requests: $0.0004 per 1000 PUT requests
- **Average cost**: ~$0.50/month for 100 users

---

### 4. **Amazon DynamoDB** 🔄 (To Implement)
**Purpose**: Store user sessions, cache, and analysis history

**Tables to Create**:

**Table 1: `UserSessions`**
```json
{
  "session_id": "string (partition key)",
  "created_at": "timestamp",
  "expires_at": "timestamp (TTL)",
  "csv_s3_key": "string",
  "sales_data_summary": {
    "total_records": "number",
    "date_range": "string",
    "items": ["array"]
  }
}
```

**Table 2: `AnalysisCache`**
```json
{
  "cache_key": "string (partition key)",
  "question": "string",
  "answer": "object",
  "created_at": "timestamp",
  "expires_at": "timestamp (TTL: 1 hour)"
}
```

**Table 3: `AnalysisHistory`**
```json
{
  "session_id": "string (partition key)",
  "timestamp": "number (sort key)",
  "question": "string",
  "answer": "object",
  "items_analyzed": ["array"]
}
```

**Benefits**:
- ✅ Single-digit millisecond latency
- ✅ Auto-scaling capacity
- ✅ Built-in TTL for automatic cleanup
- ✅ Point-in-time recovery

**Cost Estimate**:
- On-demand pricing: $1.25 per million write requests
- Read requests: $0.25 per million
- Storage: $0.25 per GB/month
- **Average cost**: ~$1-2/month for 100 users

---

### 5. **Amazon API Gateway** 🔄 (To Implement)
**Purpose**: RESTful API for frontend-backend communication

**Endpoints to Create**:
```
POST /api/analyze
  - Upload CSV and get initial recommendations
  - Request: multipart/form-data (CSV file + context)
  - Response: Recommendations JSON

POST /api/ask
  - Ask specific business questions
  - Request: JSON (question, session_id)
  - Response: Answer JSON

GET /api/suggestions
  - Get suggested questions
  - Request: Query params (session_id)
  - Response: Array of questions

GET /api/session/{session_id}
  - Get session data
  - Response: Session info + sales summary
```

**Features**:
- ✅ Request validation
- ✅ Rate limiting (1000 requests/minute per IP)
- ✅ CORS configuration
- ✅ API keys for security
- ✅ CloudWatch logging

**Cost Estimate**:
- Free tier: 1M API calls/month
- After free tier: $3.50 per million requests
- **Average cost**: ~$0.0035 per request

---

### 6. **Amazon CloudWatch** 🔄 (To Implement)
**Purpose**: Monitoring, logging, and alerting

**Metrics to Track**:
- Lambda invocations and errors
- Bedrock API latency and costs
- DynamoDB read/write capacity
- API Gateway request counts
- S3 upload success rates

**Alarms to Set**:
- Lambda error rate > 5%
- Bedrock API latency > 5 seconds
- DynamoDB throttling events
- S3 upload failures

**Cost Estimate**:
- Logs: $0.50 per GB ingested
- Metrics: $0.30 per custom metric
- **Average cost**: ~$5-10/month

---

## 📊 Data Strategy

### **Data Flow**:
```
1. User uploads CSV
   ↓
2. Store in S3 (bharatsignal-csv-uploads/{session-id}/)
   ↓
3. Parse and validate CSV
   ↓
4. Store summary in DynamoDB (UserSessions)
   ↓
5. Generate recommendations via Bedrock
   ↓
6. Cache results in DynamoDB (AnalysisCache)
   ↓
7. Return to user
```

### **Data Retention**:
- **CSV Files**: 30 days (S3 lifecycle policy)
- **User Sessions**: 24 hours (DynamoDB TTL)
- **Analysis Cache**: 1 hour (DynamoDB TTL)
- **Analysis History**: 7 days (DynamoDB TTL)

### **Data Security**:
- ✅ **Encryption at Rest**: S3 (AES-256), DynamoDB (AWS managed keys)
- ✅ **Encryption in Transit**: TLS 1.2+ for all API calls
- ✅ **Access Control**: IAM roles with least privilege
- ✅ **Data Privacy**: No PII stored, session-based isolation

### **Data Processing**:
- **CSV Validation**: Check format, required columns, data types
- **Data Cleaning**: Remove duplicates, handle missing values
- **Data Aggregation**: Calculate totals, averages, trends
- **Data Analysis**: Identify top/slow sellers, trends, patterns

---

## 🎯 24-Hour Goal

### **Immediate Objectives** (Next 24 Hours):

#### ✅ **Phase 1: AWS Setup** (Hours 0-4)
1. **Create AWS Account** (if not exists)
2. **Set up IAM User** with permissions:
   - AmazonBedrockFullAccess
   - AWSLambda_FullAccess
   - AmazonS3FullAccess
   - AmazonDynamoDBFullAccess
   - CloudWatchFullAccess
3. **Configure AWS CLI** with credentials
4. **Test Bedrock Access** with current code

#### ✅ **Phase 2: S3 Setup** (Hours 4-8)
1. **Create S3 Buckets**:
   - `bharatsignal-csv-uploads-{unique-id}`
   - `bharatsignal-static-{unique-id}`
2. **Configure Bucket Policies**:
   - Enable versioning
   - Set lifecycle rules (30-day expiration)
   - Enable server-side encryption
3. **Update Code** to upload CSV to S3
4. **Test CSV Upload/Download**

#### ✅ **Phase 3: DynamoDB Setup** (Hours 8-12)
1. **Create DynamoDB Tables**:
   - UserSessions (on-demand capacity)
   - AnalysisCache (on-demand capacity)
   - AnalysisHistory (on-demand capacity)
2. **Configure TTL** on expires_at attribute
3. **Update Code** to store/retrieve from DynamoDB
4. **Test Session Management**

#### ✅ **Phase 4: Lambda Deployment** (Hours 12-20)
1. **Package Lambda Functions**:
   - Create deployment packages with dependencies
   - Configure environment variables
   - Set up IAM execution roles
2. **Deploy Functions**:
   - analyze-csv function
   - ask-question function
   - get-suggestions function
3. **Test Lambda Functions** locally with SAM
4. **Deploy to AWS**

#### ✅ **Phase 5: API Gateway Setup** (Hours 20-24)
1. **Create REST API**
2. **Configure Endpoints** (POST /analyze, POST /ask, GET /suggestions)
3. **Set up CORS**
4. **Enable API Keys** and rate limiting
5. **Deploy API** to production stage
6. **Update Frontend** to use API Gateway URLs
7. **End-to-End Testing**

---

## 💰 Cost Estimation (Monthly)

### **For 100 Active Users** (10 requests/user/day):

| Service | Usage | Cost |
|---------|-------|------|
| **Amazon Bedrock** | 30K requests | ~$60 |
| **AWS Lambda** | 30K invocations | ~$0.60 |
| **Amazon S3** | 10 GB storage | ~$0.23 |
| **DynamoDB** | 30K writes, 60K reads | ~$2 |
| **API Gateway** | 30K requests | ~$0.10 |
| **CloudWatch** | Logs + Metrics | ~$5 |
| **Data Transfer** | 5 GB out | ~$0.45 |
| **TOTAL** | | **~$68.38/month** |

### **For 1000 Active Users**:
- **Estimated Cost**: ~$650/month
- **Cost per User**: ~$0.65/month

### **Free Tier Benefits** (First 12 months):
- Lambda: 1M requests/month FREE
- S3: 5 GB storage FREE
- DynamoDB: 25 GB storage FREE
- API Gateway: 1M requests/month FREE
- **Estimated First Year Cost**: ~$40/month (mostly Bedrock)

---

## 🚀 Deployment Checklist

### **Prerequisites**:
- [ ] AWS Account created
- [ ] AWS CLI installed and configured
- [ ] Python 3.11 installed
- [ ] boto3 and dependencies installed
- [ ] AWS SAM CLI installed (for Lambda testing)

### **Configuration**:
- [ ] Create `.env` file with AWS credentials
- [ ] Update `AWS_REGION` in config
- [ ] Set `BEDROCK_MODEL_ID` (already set)
- [ ] Configure S3 bucket names
- [ ] Set DynamoDB table names

### **Testing**:
- [ ] Test Bedrock connection locally
- [ ] Test S3 upload/download
- [ ] Test DynamoDB read/write
- [ ] Test Lambda functions locally
- [ ] Test API Gateway endpoints
- [ ] End-to-end integration test

### **Monitoring**:
- [ ] Set up CloudWatch dashboards
- [ ] Configure alarms for errors
- [ ] Enable X-Ray tracing
- [ ] Set up cost alerts

---

## 📝 Next Steps

1. **Verify AWS Credentials**: Ensure your `.env` file has valid AWS credentials
2. **Test Current Bedrock Integration**: Run `python test_bedrock_integration.py`
3. **Create S3 Buckets**: Use AWS Console or CLI
4. **Set up DynamoDB Tables**: Use AWS Console or CloudFormation
5. **Package Lambda Functions**: Create deployment packages
6. **Deploy to AWS**: Use SAM or Serverless Framework

## ✅ Implementation Status

### Completed
- ✅ S3 integration code (`aws_s3_handler.py`)
- ✅ DynamoDB integration code (`aws_dynamodb_handler.py`)
- ✅ Lambda deployment scripts (`lambda_package.py`)
- ✅ AWS setup automation (`aws_setup.py`)
- ✅ Integration testing suite (`test_aws_integration.py`)
- ✅ Complete deployment guide (`AWS_DEPLOYMENT_GUIDE.md`)
- ✅ Quick reference card (`AWS_QUICK_REFERENCE.md`)
- ✅ Integration summary (`AWS_INTEGRATION_SUMMARY.md`)

### Ready to Deploy
All AWS integration code is complete and ready for deployment. Follow the deployment guide to:
1. Set up AWS resources: `python aws_setup.py`
2. Test integration: `python test_aws_integration.py`
3. Package Lambda functions: `python lambda_package.py`
4. Deploy to AWS: Follow `AWS_DEPLOYMENT_GUIDE.md`