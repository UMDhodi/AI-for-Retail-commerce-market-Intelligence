# 🛒 BharatSignal - AI-Powered Business Intelligence for Kirana Shops

> Empowering small retail shops in India with AI-driven decision support

[![Demo Video](https://img.shields.io/badge/▶️_Watch_Demo-YouTube-red?style=for-the-badge)](https://drive.google.com/file/d/1Ss6UzwRiRXGKljCWlon38Pc4MvUXgQXp/view?usp=sharing)
[![Live Demo](https://img.shields.io/badge/🚀_Try_Live_Demo-Click_Here-blue?style=for-the-badge)](http://bharatsignal-temp-env.eba-ze63igsz.us-east-1.elasticbeanstalk.com/)

---

## 📹 Demo Video

[**▶️ Watch the Full Demo**](https://drive.google.com/file/d/1Ss6UzwRiRXGKljCWlon38Pc4MvUXgQXp/view?usp=sharing)

*See BharatSignal in action - from CSV upload to AI-powered recommendations in under 2 minutes!*

---

## 🎯 Problem Statement

Small kirana shop owners in India face daily challenges:

- **Limited Data Analysis Skills** - No tools to understand sales patterns
- **Inventory Guesswork** - Uncertain about what to stock more or less
- **Seasonal Blindness** - Miss opportunities during festivals and events
- **Pricing Confusion** - Don't know when to adjust prices
- **No Expert Advice** - Can't afford business consultants

**Result**: Lost revenue, excess inventory, and missed opportunities.

---

## 💡 Our Solution

BharatSignal is an AI-powered decision-support system that:

✅ **Analyzes Sales Data** - Upload your CSV, get instant insights  
✅ **Provides Smart Recommendations** - AI tells you what to stock more/less  
✅ **Considers Local Context** - Factors in festivals, weather, and events  
✅ **Answers Your Questions** - Ask anything about your business  
✅ **Explains Reasoning** - Understand why each recommendation is made  

**Powered by Amazon Nova Pro AI** - Enterprise-grade intelligence for small businesses.

---

## 🚀 How It Works

### 1️⃣ Upload Your Sales Data
```
Upload "AI for Bharat test - Sheet1.csv" CSV file with: date, item, quantity, price
Example: 2024-01-15, Rice 1kg, 45, 45.00
```

### 2️⃣ You can use question
```
"Tell me about my stock"
"What about flour for festival season"
"What's my best-selling item this week"
"Should I stock more oil for diwali"
"Should I increase rice stock for cooking"
"Should I change price for any item"
```

### 3️⃣ Get AI Recommendations
```
✅ Stock 50% more Rice 1kg (festival demand)
✅ Reduce Oil 1L by 20% (slow sales)
✅ Increase Sweets Mix 500g by 75% (Diwali)
```

### 4️⃣ Ask Follow-Up Questions
```
Q: "What items are selling slowly?"
A: Oil 1L sales dropped 30% - consider reducing stock

Q: "Should I increase prices?"
A: Hold prices steady - demand is stable
```

---

## 🎬 Sample Questions You Can Ask

- "What should I stock more for the festival season?"
- "Which items are selling slowly?"
- "Should I increase my prices?"
- "Tell me about my Rice 1kg sales"
- "What should I reduce to save cash?"
- "How can I prepare for monsoon season?"
- "What are my top-selling items?"

---

## 🏗️ Architecture

```
┌─────────────────┐
│   Web Browser   │
│  (User Interface)│
└────────┬────────┘
         │ HTTPS
         ▼
┌─────────────────┐
│  Flask Backend  │
│   (Python 3.x)  │
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

---

## 🛠️ Technology Stack

### Frontend
- **HTML5/CSS3** - Responsive web interface
- **JavaScript** - Interactive features
- **Bootstrap-inspired** - Clean, modern design

### Backend
- **Python 3.x** - Core application logic
- **Flask** - Lightweight web framework
- **boto3** - AWS SDK for Python

### AWS Services
- **Amazon Bedrock** - AI model (Nova Pro)
- **Amazon S3** - File storage (30-day retention)
- **Amazon DynamoDB** - Sessions, cache, history
- **AWS IAM** - Authentication & authorization

### AI Model
- **Amazon Nova Pro** (`amazon.nova-pro-v1:0`)
  - Cost-effective (~$17-22/month for 100 users)
  - No marketplace subscription required
  - Excellent recommendation quality

---

## 📦 Installation & Setup

### Prerequisites
- Python 3.8+
- AWS Account
- AWS CLI configured

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/bharatsignal.git
cd bharatsignal
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure AWS Credentials
```bash
# Create .env file
cp .env.example .env

# Edit .env with your AWS credentials
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1
BEDROCK_MODEL_ID=amazon.nova-pro-v1:0
```

### 4. Set Up AWS Resources
```bash
# Create S3 buckets and DynamoDB tables
python aws_setup.py
```

### 5. Run Application
```bash
python run.py
```

### 6. Open Browser
```
http://localhost:5000
```

---

## 📊 Sample Data

Try the system with our sample datasets:

- **`sample_data/festival_season_sales.csv`** - Diwali festival data
- **`sample_data/monsoon_season_sales.csv`** - Monsoon season data
- **`sample_data/regular_daily_sales.csv`** - Regular daily sales
- **`sample_data/kirana_sales_sample.csv`** - General kirana shop data

---

## 🧪 Testing

### Test AWS Connection
```bash
python test_aws_connection.py
```

### Run Application Tests
```bash
pytest
```

### Manual Testing
1. Upload `sample_data/festival_season_sales.csv`
2. Add context: "Diwali festival coming in 2 weeks"
3. Click "Analyze"
4. Verify recommendations are generated
5. Ask follow-up questions

---

## 💰 Cost Breakdown

**Monthly Cost (100 users, 1000 requests)**:

| Service | Cost |
|---------|------|
| Amazon Bedrock (Nova Pro) | $15-20 |
| Amazon S3 | $0.23 |
| Amazon DynamoDB | $2 |
| CloudWatch Logs | $5 |
| **Total** | **~$22-27/month** |

**Per Request**: ~$0.02-0.03

---

## 🔒 Security

- ✅ AWS IAM authentication
- ✅ HTTPS encryption in transit
- ✅ S3 server-side encryption at rest
- ✅ No PII storage
- ✅ Session data cleared after 24 hours
- ✅ Automatic data expiration (30 days)

---

## 📈 Performance

- **CSV Processing**: < 1 second
- **AI Analysis**: 2-5 seconds
- **Cache Hit**: < 100ms
- **Total Response**: 3-6 seconds
- **Concurrent Users**: 100+
- **Max File Size**: 16MB

---

## 🎯 Key Features

### ✨ Core Features
- 📤 CSV file upload and validation
- 🤖 AI-powered recommendation generation
- 💬 Interactive Q&A system
- 🎭 Demo mode with sample data
- 📊 Sales pattern analysis
- 🌍 Local context integration
- 💾 Automatic caching (1-hour TTL)
- 📜 Analysis history (7 days)

### 🔮 Future Enhancements
- 📱 Mobile app
- 🌐 Multi-language support (Hindi, regional)
- 📧 Email notifications
- 📈 Historical trend charts
- 🏪 Multi-store support
- 👥 User authentication
- 📊 Advanced analytics dashboard

---

## 📚 Documentation

- **[Design Document](.kiro/specs/bharatsignal/design.md)** - Architecture and design decisions
- **[Requirements](.kiro/specs/bharatsignal/requirements.md)** - Functional and non-functional requirements
- **[Tasks](.kiro/specs/bharatsignal/tasks.md)** - Implementation tasks and progress
- **[AWS Architecture](AWS_ARCHITECTURE.md)** - Detailed AWS integration
- **[Deployment Guide](AWS_DEPLOYMENT_GUIDE.md)** - Production deployment steps
- **[Quick Reference](AWS_QUICK_REFERENCE.md)** - Common commands and tips

---

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👥 Team

- **Your Name** - Project Lead
- **Team Member 2** - Backend Developer
- **Team Member 3** - Frontend Developer

---

## 🙏 Acknowledgments

- **Amazon Web Services** - For Bedrock AI platform
- **Anthropic** - For Claude AI models
- **AI for Bharat** - For the hackathon opportunity
- **Kirana Shop Owners** - For inspiration and feedback

---

## 📞 Support

- **Email**: support@bharatsignal.com
- **Issues**: [GitHub Issues](https://github.com/yourusername/bharatsignal/issues)
- **Documentation**: [Wiki](https://github.com/yourusername/bharatsignal/wiki)

---

## 🌟 Star Us!

If you find BharatSignal useful, please ⭐ star this repository!

---

**Made with ❤️ for small businesses in India**
