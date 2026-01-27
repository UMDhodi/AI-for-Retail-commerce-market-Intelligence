#!/usr/bin/env python3
"""
Debug the Q&A system to see what it's actually returning
"""

from models import SalesRecord, LocalContext
from interactive_qa import create_qa_system
from bedrock_client import create_bedrock_client
import logging

# Set up detailed logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def debug_qa_system():
    """Debug what the Q&A system is actually returning"""
    
    print("=== DEBUGGING Q&A SYSTEM ===\n")
    
    # Create test data that matches what user uploaded
    sales_data = [
        SalesRecord("2024-01-15", "Chocolate Bar", 25, 45.00),
        SalesRecord("2024-01-15", "Potato Chips", 30, 20.00),
        SalesRecord("2024-01-15", "Orange Juice", 15, 85.00),
        SalesRecord("2024-01-16", "Chocolate Bar", 20, 45.00),
        SalesRecord("2024-01-16", "Potato Chips", 35, 20.00),
        SalesRecord("2024-01-16", "Cookies Pack", 18, 35.00),
        SalesRecord("2024-01-17", "Orange Juice", 12, 85.00),
        SalesRecord("2024-01-17", "Cookies Pack", 22, 35.00)
    ]
    
    print(f"Test data items: {list(set(record.item for record in sales_data))}")
    
    # Create Q&A system
    try:
        bedrock_client = create_bedrock_client()
        qa_system = create_qa_system(bedrock_client)
        print("✅ Q&A system created")
    except Exception as e:
        print(f"❌ Q&A system failed: {e}")
        return
    
    # Test the exact scenario
    question = "Tell me about my stock"
    context = LocalContext("")
    
    print(f"\n🔍 Testing question: '{question}'")
    print("📊 Calling qa_system.answer_question()...")
    
    try:
        result = qa_system.answer_question(question, sales_data, context)
        
        print(f"✅ Q&A system returned: success={result.get('success')}")
        
        if result.get('success'):
            answer = result['answer']
            print("\n📋 Full Q&A Response:")
            print(f"  answer_to: {answer.get('answer_to')}")
            
            primary_decision = answer.get('primary_decision', {})
            print(f"\n🎯 Primary Decision:")
            print(f"  item: {primary_decision.get('item')}")
            print(f"  decision: {primary_decision.get('decision')}")
            print(f"  action: {primary_decision.get('action')}")
            print(f"  why: {primary_decision.get('why')}")
            print(f"  confidence: {primary_decision.get('confidence')}")
            print(f"  based_on: {primary_decision.get('based_on')}")
            
            # Check if it mentions rice anywhere
            full_response_text = str(answer).lower()
            if 'rice' in full_response_text:
                print("\n❌ ERROR: Q&A response contains 'rice'!")
                print("🔍 Rice mentions:")
                for key, value in primary_decision.items():
                    if 'rice' in str(value).lower():
                        print(f"   {key}: {value}")
            else:
                print("\n✅ No rice mentions in Q&A response")
                
        else:
            print(f"❌ Q&A system failed: {result.get('error')}")
            fallback = result.get('fallback_answer')
            if fallback:
                print(f"📋 Fallback answer: {fallback}")
    
    except Exception as e:
        print(f"❌ Exception in Q&A system: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n=== DEBUG COMPLETE ===")

if __name__ == "__main__":
    debug_qa_system()