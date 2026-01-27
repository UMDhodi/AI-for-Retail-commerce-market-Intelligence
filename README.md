# BharatSignal 🇮🇳

AI-powered decision-support system for Indian kirana shops (small general stores). BharatSignal analyzes sales data and local context to provide actionable business recommendations using Amazon Bedrock's AI capabilities.

## Features

- 📊 **CSV Sales Data Upload**: Simple file upload for sales records
- 🏪 **Local Context Integration**: Account for festivals, weather, and local events
- 🤖 **AI-Powered Recommendations**: Get specific stocking and pricing advice
- 💬 **Explainable AI**: Understand why recommendations are made
- 🎯 **Demo Mode**: Try with sample data before using your own
- 📱 **Simple Interface**: One-page design optimized for ease of use

## Quick Start

### Prerequisites

- Python 3.8 or higher
- AWS account with Bedrock access
- AWS credentials configured

### Installation

1. **Clone and setup**:
   ```bash
   git clone <repository-url>
   cd bharatsignal
   pip install -r requirements.txt
   ```

2. **Configure AWS credentials**:
   ```bash
   cp .env.example .env
   # Edit .env with your AWS credentials
   ```

3. **Run the application**:
   ```bash
   python app.py
   ```

4. **Open in browser**:
   ```
   http://localhost:5000
   ```

## AWS Setup

### Required AWS Services

- **Amazon Bedrock**: For AI recommendations
- **IAM**: For secure authentication

### AWS Credentials

Create a `.env` file with your AWS credentials:

```env
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_REGION=us-east-1
```

### IAM Permissions

Your AWS user needs the following permissions:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel"
            ],
            "Resource": [
                "arn:aws:bedrock:*:*:foundation-model/anthropic.claude-3-sonnet-20240229-v1:0"
            ]
        }
    ]
}
```

## Usage

### 1. Prepare Your Sales Data

Create a CSV file with the following columns:

```csv
date,item,quantity,price
2024-01-15,Rice 1kg,10,45.00
2024-01-15,Dal Toor 1kg,5,120.00
2024-01-16,Tea 250g,8,85.00
```

**Required columns**:
- `date`: Transaction date (YYYY-MM-DD format)
- `item`: Product name or description
- `quantity`: Number of units sold (integer)
- `price`: Price per unit in INR (decimal)

### 2. Add Local Context

Provide information about:
- Upcoming festivals (Diwali, Holi, etc.)
- Weather conditions (monsoon, heat wave)
- Local events (weddings, celebrations)
- Market changes or competition

### 3. Get AI Recommendations

The system will analyze your data and provide:
- **Stocking recommendations**: Which items to stock more/less
- **Pricing guidance**: Suggested price adjustments
- **Clear explanations**: Why each recommendation is made

## Demo Mode

Try the system without your own data:

1. Click "Load Sample Data" on the main page
2. Download the sample CSV file
3. Upload it along with the pre-filled context
4. Generate recommendations to see how it works

## Project Structure

```
bharatsignal/
├── app.py                 # Main Flask application
├── config.py             # Configuration settings
├── requirements.txt      # Python dependencies
├── .env.example         # Environment variables template
├── templates/           # HTML templates
│   ├── base.html       # Base template
│   ├── index.html      # Main page
│   └── results.html    # Results page
└── static/             # Static assets
    ├── css/
    │   └── style.css   # Styles
    └── js/
        └── main.js     # JavaScript functionality
```

## Security Features

- **AWS IAM Authentication**: Secure access to Bedrock
- **Encrypted Transit**: HTTPS communication with AWS
- **Session-based Processing**: No persistent data storage
- **Input Validation**: CSV and context data validation
- **Error Handling**: Graceful error messages

## Troubleshooting

### Common Issues

1. **AWS Credentials Error**:
   - Verify your `.env` file has correct credentials
   - Check IAM permissions for Bedrock access

2. **CSV Upload Error**:
   - Ensure CSV has required columns: date, item, quantity, price
   - Check file size (max 16MB)
   - Verify date format is YYYY-MM-DD

3. **No Recommendations Generated**:
   - Check AWS Bedrock service availability
   - Verify internet connection
   - Try with demo data first

### Getting Help

- Check the browser console for JavaScript errors
- Review the Flask application logs
- Verify AWS service status

## Development

### Running in Development Mode

```bash
export FLASK_ENV=development
export FLASK_DEBUG=True
python app.py
```

### Testing

The application includes manual testing scenarios:

1. **Valid CSV Upload**: Test with properly formatted sales data
2. **Invalid CSV Handling**: Test error messages with malformed files
3. **Context Integration**: Verify local context influences recommendations
4. **Demo Mode**: Ensure sample data generates meaningful results

## Requirements Traceability

This implementation addresses the following requirements:

- **Requirement 7.1**: AWS IAM authentication for Bedrock access
- **Requirement 8.1**: Reliable processing during demo conditions
- **Data Security**: Session-based processing with no persistent storage
- **User Interface**: Simple one-page design with clear feedback
- **AI Integration**: Amazon Bedrock for recommendation generation

## License

This project is developed as a prototype for demonstration purposes.

## Support

For questions or issues, please refer to the troubleshooting section or contact the development team.