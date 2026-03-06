# Requirements Document: BharatSignal

## Project Overview

BharatSignal is an AI-powered decision-support system that helps small kirana shop owners in India make data-driven business decisions by analyzing sales data with Amazon Nova Pro AI.

## Functional Requirements

### FR1: Data Input
- System SHALL accept CSV files with columns: date, item, quantity, price
- System SHALL validate CSV format and provide clear error messages
- System SHALL accept local context (festivals, weather, events)
- System SHALL support files up to 16MB

### FR2: AI Analysis
- System SHALL use Amazon Nova Pro for data analysis
- System SHALL combine sales data with local context
- System SHALL identify sales trends and patterns
- System SHALL generate specific, actionable recommendations

### FR3: Recommendations
- System SHALL provide stock recommendations (what to buy more/less)
- System SHALL suggest pricing strategies
- System SHALL prioritize recommendations by impact
- System SHALL explain reasoning in simple language

### FR4: Interactive Q&A
- System SHALL answer specific business questions
- System SHALL analyze individual items on request
- System SHALL provide follow-up suggestions
- System SHALL maintain conversation context

### FR5: Data Management
- System SHALL store CSV files in S3 (30-day retention)
- System SHALL cache analysis results (1-hour TTL)
- System SHALL track session data (24-hour TTL)
- System SHALL maintain analysis history (7 days)

## Non-Functional Requirements

### NFR1: Performance
- CSV processing: < 1 second
- AI analysis: < 10 seconds
- Page load: < 2 seconds
- Cache response: < 100ms

### NFR2: Security
- AWS IAM authentication required
- HTTPS encryption in transit
- S3 server-side encryption at rest
- No PII storage

### NFR3: Usability
- Single-page interface
- Clear error messages
- Mobile-responsive design
- Simple English language

### NFR4: Reliability
- 99% uptime during business hours
- Graceful error handling
- Clear status indicators
- Automatic retry on failures

### NFR5: Scalability
- Support 100 concurrent users
- Handle 1000 requests/month
- Process files up to 16MB
- Store 30 days of data

## User Stories

### US1: Upload Sales Data
**As a** kirana shop owner  
**I want to** upload my sales CSV file  
**So that** the AI can analyze my business data

**Acceptance Criteria:**
- Can select and upload CSV file
- See upload progress indicator
- Receive confirmation or error message
- File is validated before processing

### US2: Get Recommendations
**As a** kirana shop owner  
**I want to** receive AI-powered recommendations  
**So that** I can make better stocking decisions

**Acceptance Criteria:**
- Recommendations are specific to my items
- Each recommendation has clear reasoning
- Actions are practical and actionable
- Confidence level is indicated

### US3: Ask Questions
**As a** kirana shop owner  
**I want to** ask specific questions about my business  
**So that** I can get targeted advice

**Acceptance Criteria:**
- Can type questions in natural language
- Receive relevant, data-driven answers
- Get follow-up question suggestions
- Answers reference my actual data

### US4: Add Context
**As a** kirana shop owner  
**I want to** provide local context (festivals, weather)  
**So that** recommendations consider my situation

**Acceptance Criteria:**
- Can enter context as free text
- Context influences recommendations
- AI explains how context was used
- Can update context anytime

### US5: Try Demo
**As a** potential user  
**I want to** try the system with sample data  
**So that** I can evaluate it before using my data

**Acceptance Criteria:**
- Can load pre-filled demo scenarios
- Demo data is realistic
- All features work in demo mode
- Clear indication it's demo mode

## Technical Requirements

### TR1: AWS Integration
- Amazon Bedrock (Nova Pro model)
- Amazon S3 (file storage)
- Amazon DynamoDB (sessions, cache, history)
- AWS IAM (authentication)

### TR2: Development Stack
- Python 3.x
- Flask web framework
- boto3 AWS SDK
- HTML/CSS/JavaScript frontend

### TR3: Data Format
- CSV with headers: date, item, quantity, price
- Date format: YYYY-MM-DD
- Quantity: positive integer
- Price: positive decimal

### TR4: Deployment
- Development: Local Flask server
- Production: AWS Lambda + API Gateway (future)
- Database: DynamoDB (serverless)
- Storage: S3 (serverless)

## Success Criteria

1. ✅ System processes CSV files correctly
2. ✅ AI generates relevant recommendations
3. ✅ Users understand recommendations
4. ✅ Response time < 10 seconds
5. ✅ No data loss or security issues
6. ✅ 90%+ user satisfaction
7. ✅ Cost < $25/month for 100 users

## Out of Scope

- Multi-language support (English only)
- Mobile app (web only)
- Inventory management
- Point of sale integration
- Multi-store support
- Historical trend charts
- Email notifications
- User authentication (single-user prototype)
