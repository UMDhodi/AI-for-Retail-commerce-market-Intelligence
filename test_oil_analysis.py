#!/usr/bin/env python3
"""
Test script to verify oil analysis is working correctly
"""

from interactive_qa import InteractiveQASystem
from models import SalesRecord, LocalContext

# Create sample data similar to the CSV
sample_sales = [
    SalesRecord("2024-01-15", "Rice 1kg", 10, 45.00),
    SalesRecord("2024-01-15", "Oil 1L", 3, 150.00),
    SalesRecord("2024-01-16", "Rice 1kg", 8, 45.00),
    SalesRecord("2024-01-18", "Oil 1L", 4, 150.00),
    SalesRecord("2024-01-19", "Tea 250g", 5, 85.00),
]

# Create context
context = LocalContext("There's been heavy rainfall for 3 days")

# Create Q&A system (without bedrock client for testing)
class MockBedrockClient:
    pass

qa_system = InteractiveQASystem(MockBedrockClient())

# Test item extraction
question = "There's been heavy rainfall in 3 days should i restock oil"
items = qa_system._extract_items_from_question(question)
print(f"Question: {question}")
print(f"Extracted items: {items}")

# Test item filtering
filtered_sales = qa_system._filter_sales_by_items(sample_sales, items)
print(f"Filtered sales records: {[(r.item, r.quantity) for r in filtered_sales]}")

# Test full analysis
try:
    result = qa_system.answer_question(question, sample_sales, context)
    if result['success']:
        answer = result['answer']
        print(f"\nAnalysis Result:")
        print(f"Item analyzed: {answer['primary_decision']['item']}")
        print(f"Decision: {answer['primary_decision']['decision']}")
        print(f"Action: {answer['primary_decision']['action']}")
    else:
        print(f"Error: {result['error']}")
except Exception as e:
    print(f"Exception: {e}")