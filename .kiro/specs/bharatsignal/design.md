# Design Document: BharatSignal

## Overview

BharatSignal is an AI-powered decision-support system for small kirana shops in India. It analyzes sales data using Amazon Nova Pro AI to provide actionable business recommendations.

## Final Architecture

```
┌─────────────────┐
│   Web Browser   │
│  (User Interface)│
└────────┬────────┘
         │ HTTP
         ▼
┌─────────────────┐
│  Flask Backend  │
│   (Python)      │
└────────┬────────┘
         │
    ┌────┴────┬──────────┬──────────┐
    │         │          │          │
    ▼         ▼          ▼          ▼
┌──────┐ ┌──────┐ ┌──────────┐ ┌──────────┐
│  S3  │ │DynamoDB│ │ Bedrock  │ │  CSV     │
│Bucket│ │ Tables │ │Nova Pro  │ │Processor │
└──────┘ └──────┘ └──────────┘ └──────────┘
```

## Technology Stack

### Frontend
- HTML5/CSS3 - Simple, responsive interface
- JavaScript - Interactive Q&A and file upload
- Bootstrap-inspired styling

### Backend
- Python 3.x - Core application logic
- Flask - Web framework
- boto3 - AWS SDK

### AWS Services
- **Amazon Bedrock** - AI model (Nova Pro)
- **Amazon S3** - CSV file storage (30-day retention)
- **Amazon DynamoDB** - Session data (24h), cache (1h), history (7d)
- **AWS IAM** - Authentication and authorization

### AI Model
- **Amazon Nova Pro** (`amazon.nova-pro-v1:0`)
  - Cost-effective (~$17-22/month for 100 users)
  - No marketplace subscription required
  - Excellent recommendation quality

## Core Components

### 1. Data Models (`models.py`)
```python
@dataclass
class SalesRecord:
    date: str
    item: str
    quantity: int
    price: float

@dataclass
class LocalContext:
    text: str  # Festival, weather, events

@dataclass
class Recommendation:
    item: str
    action: str
    explanation: str
    confidence: str
```

### 2. CSV Processor (`csv_processor.py`)
- Validates CSV format
- Handles errors gracefully
- Supports date, item, quantity, price columns

### 3. Bedrock Client (`bedrock_client.py`)
- Connects to Amazon Nova Pro
- Formats prompts for AI analysis
- Parses AI responses into recommendations

### 4. Interactive Q&A (`interactive_qa.py`)
- Answers specific business questions
- Analyzes sales patterns
- Provides contextual recommendations

### 5. AWS Handlers
- `aws_s3_handler.py` - File storage
- `aws_dynamodb_handler.py` - Session/cache management

## Data Flow

1. **Upload** → User uploads CSV file
2. **Store** → File saved to S3 bucket
3. **Process** → CSV parsed into SalesRecord objects
4. **Analyze** → Amazon Nova Pro analyzes data + context
5. **Recommend** → AI generates actionable recommendations
6. **Display** → Results shown to user
7. **Cache** → Results cached in DynamoDB (1 hour)

## Security

- AWS IAM authentication
- HTTPS encryption in transit
- S3 server-side encryption
- No PII storage
- Session data cleared after 24 hours

## Performance

- CSV processing: < 1 second
- AI analysis: 2-5 seconds
- Cache hit: < 100ms
- Total response: 3-6 seconds

## Scalability

Current design supports:
- 100 concurrent users
- 1000 requests/month
- 16MB max file size
- 30-day data retention
