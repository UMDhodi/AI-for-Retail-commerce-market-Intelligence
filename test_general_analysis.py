#!/usr/bin/env python3
"""
Test the general analysis that happens when user uploads CSV from home page
"""

import io
from csv_processor import parse_csv
from interactive_qa import InteractiveQASystem
from models import LocalContext

# Create sample CSV content with Oil as top seller
csv_content = """date,item,quantity,price
2024-01-15,Rice 1kg,5,45.00
2024-01-15,Oil 1L,15,150.00
2024-01-15,Tea 250g,3,85.00
2024-01-16,Rice 1kg,4,45.00
2024-01-16,Oil 1L,18,150.00
2024-01-17,Tea 250g,2,85.00
2024-01-17,Oil 1L,20,150.00
2024-01-18,Rice 1kg,6,45.00
2024-01-19,Oil 1L,22,150.00"""

print("=== TESTING GENERAL ANALYSIS (HOME PAGE UPLOAD) ===")

# Step 1: Parse CSV
print("\n1. Parsing CSV...")
csv_file = io.StringIO(csv_content)
csv_result = parse_csv(csv_file)

if csv_result.success:
    print(f"✅ CSV parsed successfully: {len(csv_result.valid_records)} records")
    
    # Show item quantities
    item_totals = {}
    for record in csv_result.valid_records:
        if record.item not in item_totals:
            item_totals[record.item] = 0
        item_totals[record.item] += record.quantity
    
    print("Item totals:", item_totals)
    top_item = max(item_totals.items(), key=lambda x: x[1])
    print(f"Top seller: {top_item[0]} ({top_item[1]} units)")
else:
    print(f"❌ CSV parsing failed: {csv_result.errors}")
    exit(1)

# Step 2: Test general analysis (what happens on home page)
print("\n2. Testing general analysis...")
class MockBedrockClient:
    pass

qa_system = InteractiveQASystem(MockBedrockClient())

# This is the default question used when user uploads CSV
question = "What should I do today for my shop?"
context = LocalContext("Local business context")

result = qa_system.answer_question(question, csv_result.valid_records, context)

if result['success']:
    answer = result['answer']
    print(f"✅ General analysis successful")
    print(f"Question: {answer['answer_to']}")
    print(f"Item analyzed: {answer['primary_decision']['item']}")
    print(f"Decision: {answer['primary_decision']['decision']}")
    print(f"Action: {answer['primary_decision']['action']}")
    print(f"Why: {answer['primary_decision']['why']}")
else:
    print(f"❌ General analysis failed: {result.get('error', 'Unknown error')}")

print("\n=== TEST COMPLETE ===")