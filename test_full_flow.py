#!/usr/bin/env python3
"""
Test the full flow from CSV upload to Q&A analysis
"""

import io
from csv_processor import parse_csv
from interactive_qa import InteractiveQASystem
from models import LocalContext

# Create sample CSV content similar to what user would upload
csv_content = """date,item,quantity,price
2024-01-15,Rice 1kg,10,45.00
2024-01-15,Oil 1L,3,150.00
2024-01-15,Tea 250g,8,85.00
2024-01-16,Rice 1kg,8,45.00
2024-01-16,Oil 1L,4,150.00
2024-01-17,Tea 250g,6,85.00
2024-01-18,Oil 1L,2,150.00
2024-01-19,Rice 1kg,12,45.00"""

print("=== TESTING FULL FLOW ===")

# Step 1: Parse CSV (simulating file upload)
print("\n1. Parsing CSV...")
csv_file = io.StringIO(csv_content)
csv_result = parse_csv(csv_file)

if csv_result.success:
    print(f"✅ CSV parsed successfully: {len(csv_result.valid_records)} records")
    print("Items found:", list(set(record.item for record in csv_result.valid_records)))
else:
    print(f"❌ CSV parsing failed: {csv_result.errors}")
    exit(1)

# Step 2: Create Q&A system
print("\n2. Creating Q&A system...")
class MockBedrockClient:
    pass

qa_system = InteractiveQASystem(MockBedrockClient())

# Step 3: Test oil question
print("\n3. Testing oil question...")
question = "There's been heavy rainfall in 3 days should i restock oil"
context = LocalContext("Heavy rainfall for 3 days, people cooking more at home")

result = qa_system.answer_question(question, csv_result.valid_records, context)

if result['success']:
    answer = result['answer']
    print(f"✅ Question answered successfully")
    print(f"Question: {answer['answer_to']}")
    print(f"Item analyzed: {answer['primary_decision']['item']}")
    print(f"Decision: {answer['primary_decision']['decision']}")
    print(f"Action: {answer['primary_decision']['action']}")
    print(f"Sales summary: {answer['primary_decision']['recent_sales_summary']}")
else:
    print(f"❌ Question failed: {result.get('error', 'Unknown error')}")

# Step 4: Test rice question for comparison
print("\n4. Testing rice question...")
rice_question = "Should I restock rice for the festival?"
rice_result = qa_system.answer_question(rice_question, csv_result.valid_records, context)

if rice_result['success']:
    rice_answer = rice_result['answer']
    print(f"✅ Rice question answered")
    print(f"Item analyzed: {rice_answer['primary_decision']['item']}")
    print(f"Decision: {rice_answer['primary_decision']['decision']}")
else:
    print(f"❌ Rice question failed")

print("\n=== TEST COMPLETE ===")