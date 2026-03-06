# 🚀 Getting Started with BharatSignal

## Quick Start (5 Minutes)

### 1. Verify Setup ✅
Your application is already configured and running!

```bash
# Check if application is running
# Open: http://localhost:5000
```

### 2. Try Demo Mode 🎭

1. Open http://localhost:5000
2. Click **"Try Demo"** button
3. Select **"Festival Season Sales"**
4. See AI recommendations instantly!

### 3. Upload Your Own Data 📤

**CSV Format Required:**
```csv
date,item,quantity,price
2024-01-15,Rice 1kg,45,45.00
2024-01-15,Tea 250g,20,85.00
2024-01-15,Sugar 1kg,30,42.00
```

**Steps:**
1. Click **"Choose File"**
2. Select your CSV file
3. (Optional) Add context: "Diwali festival in 2 weeks"
4. Click **"Analyze"**
5. Get AI recommendations!

### 4. Ask Questions 💬

After getting recommendations, ask:
- "What items are selling slowly?"
- "Should I increase prices?"
- "Tell me about Rice 1kg"
- "What should I stock for festivals?"

---

## 📊 Sample Data Files

Located in `sample_data/` folder:

1. **festival_season_sales.csv** - Diwali festival data
2. **monsoon_season_sales.csv** - Monsoon season data
3. **regular_daily_sales.csv** - Regular daily sales
4. **kirana_sales_sample.csv** - General kirana shop data

---

## 🎯 What You Can Do

### Get Recommendations
- Stock more/less of specific items
- Pricing strategies
- Festival preparation
- Seasonal adjustments

### Ask Questions
- Item-specific analysis
- Sales trends
- Inventory optimization
- Cash flow management

### Add Context
- Upcoming festivals
- Weather conditions
- Local events
- Market changes

---

## 🛠️ Troubleshooting

### Application Not Running?
```bash
# Start the application
python run.py

# Open browser
http://localhost:5000
```

### CSV Upload Fails?
- Check file format: date, item, quantity, price
- Ensure date format: YYYY-MM-DD
- Max file size: 16MB
- Remove special characters from item names

### No Recommendations?
- Verify CSV has valid data
- Check AWS connection: `python test_aws_connection.py`
- Ensure Bedrock model is accessible

### Slow Response?
- First request may take 5-10 seconds (AI initialization)
- Subsequent requests are faster (< 3 seconds)
- Check internet connection

---

## 📚 Documentation

- **[README.md](README.md)** - Complete project overview
- **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - What was accomplished
- **[AWS_ARCHITECTURE.md](AWS_ARCHITECTURE.md)** - AWS integration details
- **[AWS_QUICK_REFERENCE.md](AWS_QUICK_REFERENCE.md)** - Common commands

---

## 💡 Tips

1. **Start with Demo** - Try demo mode first to understand the system
2. **Add Context** - Local context improves recommendations
3. **Ask Follow-ups** - Use Q&A for specific questions
4. **Check History** - View past analyses (7-day retention)
5. **Use Cache** - Repeated queries are faster (1-hour cache)

---

## 🎊 You're Ready!

Your BharatSignal application is fully operational!

**Next Steps:**
1. Try demo mode
2. Upload your sales data
3. Get AI recommendations
4. Ask follow-up questions
5. Make better business decisions!

---

**Need Help?** Check the documentation or run `python test_aws_connection.py` to verify setup.

**Happy Analyzing! 🚀**
