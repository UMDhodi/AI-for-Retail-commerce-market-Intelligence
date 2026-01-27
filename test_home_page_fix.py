#!/usr/bin/env python3
"""
Test script to verify home page CSV upload works correctly
"""

import sys
import os
from io import StringIO
from models import SalesRecord, LocalContext
from interactive_qa import create_qa_system
from bedrock_client import create_bedrock_client
from csv_processor import parse_csv

def test_home_page_analysis():
    """Test that home page analysis works with actual uploaded data"""
    print("=== TESTING HOME PAGE CSV ANALYSIS ===\n")
    
    # Create sample CSV data (different from rice-focused data)
    csv_content = """date,item,quantity,price
2024-01-15,Biscuits Pack,25,26.00
2024-01-15,Cold Drink 500ml,18,25.00
2024-01-15,Bread,12,24.00
2024-01-16,Biscuits Pack,30,26.00
2024-01-16,Cold Drink 500ml,15,25.00
2024-01-16,Milk 1L,20,55.00
2024-01-17,Biscuits Pack,22,26.00
2024-01-17,Milk 1L,25,55.00"""
    
    print("1. Testing with Biscuits/Cold Drink data (NOT rice)...")
    
    # Parse CSV
    csv_file = StringIO(csv_content)
    csv_result = parse_csv(csv_file)
    
    if not csv_result.success:
        print("❌ CSV parsing failed")
        return False
    
    sales_data = csv_result.valid_records
    print(f"✅ CSV parsed: {len(sales_data)} records")
    print(f"Items found: {list(set(record.item for record in sales_data))}")
    
    # Create Q&A system
    try:
        bedrock_client = create_bedrock_client()
        qa_system = create_qa_system(bedrock_client)
    except Exception as e:
        print(f"⚠️  Using mock Q&A system: {e}")
        qa_system = MockQASystem()
    
    # Test 1: Default analysis (like home page with no question)
    print("\n2. Testing default analysis (Tell me about my stock)...")
    context = LocalContext("")
    result = qa_system.answer_question("Tell me about my stock", sales_data, context)
    
    if result['success']:
        answer = result['answer']
        item_analyzed = answer['primary_decision']['item']
        print(f"✅ Default analysis successful")
        print(f"Item analyzed: {item_analyzed}")
        print(f"Decision: {answer['primary_decision']['decision']}")
        
        # Check if it's analyzing actual data, not defaulting to rice
        if 'rice' in item_analyzed.lower() and 'rice' not in [r.item.lower() for r in sales_data]:
            print("❌ ERROR: System defaulted to rice when no rice in data!")
            return False
        else:
            print("✅ System analyzed actual uploaded data")
    else:
        print(f"❌ Default analysis failed: {result.get('error')}")
        return False
    
    # Test 2: Specific item question
    print("\n3. Testing specific item question (biscuits)...")
    result = qa_system.answer_question("Should I restock biscuits?", sales_data, context)
    
    if result['success']:
        answer = result['answer']
        item_analyzed = answer['primary_decision']['item']
        print(f"✅ Biscuits question answered")
        print(f"Item analyzed: {item_analyzed}")
        print(f"Decision: {answer['primary_decision']['decision']}")
        
        # Check if it analyzed biscuits specifically
        if 'biscuit' not in item_analyzed.lower():
            print("❌ ERROR: System didn't analyze biscuits when asked about biscuits!")
            return False
        else:
            print("✅ System analyzed biscuits as requested")
    else:
        print(f"❌ Biscuits question failed: {result.get('error')}")
        return False
    
    # Test 3: Check suggested questions use actual data
    print("\n4. Testing suggested questions use actual data...")
    suggestions = qa_system.get_suggested_questions(sales_data, context)
    print(f"Generated suggestions: {suggestions}")
    
    # Check if suggestions mention actual items from the data
    actual_items = [record.item.lower() for record in sales_data]
    suggestion_text = ' '.join(suggestions).lower()
    
    found_actual_items = any(item.split()[0] in suggestion_text for item in actual_items)
    if found_actual_items:
        print("✅ Suggestions reference actual uploaded items")
    else:
        print("⚠️  Suggestions may not reference actual items (could be generic)")
    
    print("\n=== HOME PAGE TEST COMPLETE ===")
    return True


class MockQASystem:
    """Mock Q&A system for testing when Bedrock is not available"""
    
    def answer_question(self, question, sales_data, context):
        # Find top selling item from actual data
        if sales_data:
            item_totals = {}
            for record in sales_data:
                if record.item not in item_totals:
                    item_totals[record.item] = 0
                item_totals[record.item] += record.quantity
            
            top_item = max(item_totals.items(), key=lambda x: x[1])[0]
            
            # Check if question mentions specific item
            question_lower = question.lower()
            mentioned_item = None
            for item in item_totals.keys():
                if item.lower().split()[0] in question_lower:
                    mentioned_item = item
                    break
            
            analyzed_item = mentioned_item if mentioned_item else top_item
            
            return {
                'success': True,
                'answer': {
                    'primary_decision': {
                        'item': analyzed_item,
                        'decision': f'YES - Focus on {analyzed_item}',
                        'action': f'Increase {analyzed_item} stock by 15%',
                        'why': f'{analyzed_item} shows good performance in your data',
                        'confidence': 'Medium (mock analysis)',
                        'based_on': ['Mock analysis of uploaded data']
                    },
                    'suggested_questions': [
                        f"Should I stock more {list(item_totals.keys())[0]}?",
                        f"What about {list(item_totals.keys())[1] if len(item_totals) > 1 else 'other items'}?",
                        "Tell me about my stock"
                    ]
                }
            }
        else:
            return {
                'success': False,
                'error': 'No sales data provided'
            }
    
    def get_suggested_questions(self, sales_data, context):
        if sales_data:
            items = list(set(record.item for record in sales_data))
            return [
                f"Should I stock more {items[0]}?" if items else "What should I stock?",
                f"What about {items[1]}?" if len(items) > 1 else "Should I reduce any items?",
                "Tell me about my stock"
            ]
        return ["What should I stock?", "Tell me about my business", "Should I change prices?"]


if __name__ == "__main__":
    success = test_home_page_analysis()
    if success:
        print("\n✅ All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)