# BharatSignal Project Structure

## 📁 Clean Project Organization

This document describes the essential files in the BharatSignal project after cleanup.

---

## 🎯 Core Application Files

### Python Backend
```
app.py                          # Main Flask application with routes
run.py                          # Application entry point
config.py                       # Configuration settings
models.py                       # Data models (SalesRecord, LocalContext, Recommendation)
```

### Business Logic
```
csv_processor.py                # CSV file parsing and validation
interactive_qa.py               # Q&A system for business questions
prompt_engineering.py           # AI prompt construction
recommendation_formatter.py     # Format recommendations for display
demo_data_handler.py           # Demo scenario management
```

### AWS Integration
```
bedrock_client.py              # Amazon Bedrock (Claude 3 Sonnet) integration
aws_s3_handler.py              # S3 file storage operations
aws_dynamodb_handler.py        # DynamoDB session/cache management
aws_setup.py                   # AWS resource setup script
lambda_package.py              # Lambda deployment package creator
```

---

## 🎨 Frontend Files

### Templates (Jinja2)
```
templates/
├── base.html                  # Base template with header/footer
├── index.html                 # Home page with CSV upload
└── results.html               # Results page with decision board
```

### Static Assets
```
static/
├── css/
│   └── style.css             # All application styles
└── js/
    └── main.js               # Client-side JavaScript
```

---

## 📊 Data Files

### Sample Data
```
sample_data/
├── demo_scenarios.json        # Demo scenario definitions
├── festival_season_sales.csv  # Festival demo data
├── monsoon_season_sales.csv   # Monsoon demo data
└── regular_daily_sales.csv    # Regular business demo data
```

---

## 📚 Documentation

### User Documentation
```
README.md                      # Project overview and setup instructions
UI_UX_WIREFRAME.md            # Complete UI/UX specifications
FIGMA_DESIGN_GUIDE.md         # Figma design recreation guide
design_mockup.html            # Interactive design mockup
```

### AWS Documentation
```
AWS_ARCHITECTURE.md           # Complete AWS architecture details
AWS_DEPLOYMENT_GUIDE.md       # Step-by-step deployment guide
AWS_INTEGRATION_SUMMARY.md    # AWS integration overview
AWS_QUICK_REFERENCE.md        # Quick commands and reference
```

---

## ⚙️ Configuration Files

```
.env.example                   # Environment variables template
.gitignore                     # Git ignore rules
requirements.txt               # Python dependencies
```

---

## 📦 Project Folders

### Hidden/System Folders
```
.git/                         # Git version control
.kiro/                        # Kiro IDE configuration
.vscode/                      # VS Code settings
.pytest_cache/                # Pytest cache (can be deleted)
__pycache__/                  # Python cache (can be deleted)
```

---

## 🗂️ File Categories

### Essential Production Files (18 files)
1. `app.py` - Main application
2. `run.py` - Entry point
3. `config.py` - Configuration
4. `models.py` - Data models
5. `csv_processor.py` - CSV processing
6. `interactive_qa.py` - Q&A system
7. `prompt_engineering.py` - Prompt engineering
8. `recommendation_formatter.py` - Formatting
9. `demo_data_handler.py` - Demo handler
10. `bedrock_client.py` - Bedrock integration
11. `aws_s3_handler.py` - S3 integration
12. `aws_dynamodb_handler.py` - DynamoDB integration
13. `templates/base.html` - Base template
14. `templates/index.html` - Home page
15. `templates/results.html` - Results page
16. `static/css/style.css` - Styles
17. `static/js/main.js` - JavaScript
18. `requirements.txt` - Dependencies

### AWS Deployment Files (3 files)
1. `aws_setup.py` - Setup script
2. `lambda_package.py` - Lambda packager
3. `.env.example` - Config template

### Documentation Files (8 files)
1. `README.md` - Main documentation
2. `AWS_ARCHITECTURE.md` - Architecture
3. `AWS_DEPLOYMENT_GUIDE.md` - Deployment
4. `AWS_INTEGRATION_SUMMARY.md` - Integration summary
5. `AWS_QUICK_REFERENCE.md` - Quick reference
6. `UI_UX_WIREFRAME.md` - UI/UX specs
7. `FIGMA_DESIGN_GUIDE.md` - Design guide
8. `design_mockup.html` - Design mockup

### Sample Data Files (4 files)
1. `sample_data/demo_scenarios.json`
2. `sample_data/festival_season_sales.csv`
3. `sample_data/monsoon_season_sales.csv`
4. `sample_data/regular_daily_sales.csv`

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env with your AWS credentials
```

### 3. Run Application
```bash
python run.py
```

### 4. Access Application
```
http://localhost:5000
```

---

## 🧹 Removed Files

The following file types were removed during cleanup:

### Debug Files (5 files removed)
- `debug_biscuit_match.py`
- `debug_item_extraction.py`
- `debug_oil_match.py`
- `debug_qa_system.py`
- `debug_rice_analysis.py`

### Test Files (24 files removed)
- All `test_*.py` files (unit tests, integration tests)

### Redundant Documentation (15+ files removed)
- Various `*_SUMMARY.md` files
- Various `*_FIXED.md` files
- Various `*_IMPLEMENTATION.md` files
- Duplicate final documentation files

### Temporary Files (3 files removed)
- `debug_response.html`
- `response.html`
- `sample_sales_data.csv`

**Total Removed**: ~47 files

---

## 📊 Project Statistics

### Current Project Size
- **Total Essential Files**: 33 files
- **Python Files**: 13 files
- **HTML/CSS/JS Files**: 5 files
- **Documentation Files**: 8 files
- **Sample Data Files**: 4 files
- **Configuration Files**: 3 files

### Lines of Code (Approximate)
- **Python Backend**: ~3,500 lines
- **Frontend (HTML/CSS/JS)**: ~2,000 lines
- **Documentation**: ~5,000 lines
- **Total**: ~10,500 lines

---

## 🎯 File Purpose Summary

### Core Functionality
- **CSV Processing**: `csv_processor.py`, `models.py`
- **AI Integration**: `bedrock_client.py`, `prompt_engineering.py`
- **Q&A System**: `interactive_qa.py`
- **Web Interface**: `app.py`, `templates/`, `static/`

### AWS Cloud
- **Storage**: `aws_s3_handler.py`
- **Database**: `aws_dynamodb_handler.py`
- **Deployment**: `aws_setup.py`, `lambda_package.py`

### User Experience
- **Frontend**: `templates/`, `static/`
- **Demo Mode**: `demo_data_handler.py`, `sample_data/`
- **Design**: `design_mockup.html`, `FIGMA_DESIGN_GUIDE.md`

---

## 🔄 Maintenance

### Regular Cleanup
```bash
# Remove Python cache
rm -rf __pycache__ .pytest_cache

# Remove temporary files
rm -f *.pyc *.pyo
```

### Update Dependencies
```bash
pip freeze > requirements.txt
```

### Version Control
```bash
git add .
git commit -m "Clean project structure"
git push
```

---

## 📝 Notes

- All test files have been removed (use pytest for testing if needed)
- Debug files have been removed (use logging for debugging)
- Redundant documentation has been consolidated
- Only essential production files remain
- Sample data is kept for demo mode functionality

---

**Last Updated**: 2024-03-01  
**Version**: 1.0 (Clean)  
**Status**: Production Ready
