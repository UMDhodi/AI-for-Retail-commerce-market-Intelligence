#!/usr/bin/env python3
"""
Debug the Rice analysis to see why it's showing inventory instead of Rice details
"""

from models import SalesRecord, LocalContext
from interactive_qa import create_qa_system
from bedrock_client import create_bedrock_client
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def debug_rice_analysis():
    """Debug why 'Tell me about Rice' shows inventory instead of Rice details"""
    
    print("=== DEBUGGING RICE ANALYSIS ===\n")
    
    # Create test data
    sales_data = [
        SalesRecord("2024-01-15", "Rice 1kg", 50, 45.00),
        SalesRecord("2024-01-15", "Oil 1L", 30, 150.00),
        SalesRecord("2024-01-15", "Tea 250g", 25, 85.00),
        SalesRecord("2024-01-15", "Biscuits", 8, 25.00),
        SalesRecord("2024-01-16", "Rice 1kg", 48, 45.00),
        SalesRecord("2024-01-16", "Oil 1L", 28, 150.00),
        SalesRecord("2024-01-17", "Rice 1kg", 45, 45.00)
    ]
    
    print(f"Test data: {len(sales_data)} records")
    print(f"Items: {list(set(record.item for record in sales_data))}")
    
    # Create Q&A system
    try:
        bedrock_client = create_bedrock_client()
        qa_system = create_qa_system(bedrock_client)
        print("✅ Q&A system created")
    except Exception as e:
        print(f"⚠️  Using mock Q&A system: {e}")
        qa_system = MockQASystem()
    
    context = LocalContext("")
    
    # Test the specific question
    question = "Tell me about Rice"
    print(f"\n🔍 Testing: '{question}'")
    
    # Debug the intent detection
    intent = qa_system._extract_intent_from_question(question)
    print(f"📋 Detected intent: {intent}")
    
    # Debug item extraction
    items = qa_system._extract_items_from_question(question)
    print(f"📋 Extracted items: {items}")
    
    # Test the full analysis
    result = qa_system.answer_question(question, sales_data, context)
    
    if result['success']:
        answer = result['answer']
        decision = answer['primary_decision']
        
        print(f"\n✅ Analysis successful")
        print(f"📊 Item analyzed: {decision['item']}")
        print(f"🎯 Decision: {decision['decision']}")
        print(f"🔧 Action: {decision['action'][:100]}...")
        print(f"💡 Why: {decision['why'][:100]}...")
        
        # Check if it's Rice-specific
        why_text = decision['why'].lower()
        if 'rice' in why_text and ('oil' not in why_text and 'tea' not in why_text):
            print("✅ Analysis is Rice-specific")
        elif 'rice' in why_text:
            print("⚠️  Analysis mentions Rice but also other items")
        else:
            print("❌ Analysis doesn't seem Rice-specific")
            
    else:
        print(f"❌ Analysis failed: {result.get('error')}")
    
    print("\n=== DEBUG COMPLETE ===")


class MockQASystem:
    """Mock Q&A system for testing when Bedrock is not available"""
    
    def _extract_intent_from_question(self, question):
        question_lower = question.lower()
        if 'tell me about' in question_lower and 'stock' not in question_lower:
            return 'specific_item_analysis'
        return 'daily_operations'
    
    def _extract_items_from_question(self, question):
        question_lower = question.lower()
        if 'rice' in question_lower:
            return ['rice']
        return []
    
    def answer_question(self, question, sales_data, context):
        intent = self._extract_intent_from_question(question)
        items = self._extract_items_from_question(question)
        
        if intent == 'specific_item_analysis' and 'rice' in items:
            # Calculate Rice-specific data
            rice_sales = [r for r in sales_data if 'rice' in r.item.lower()]
            rice_total = sum(r.quantity for r in rice_sales)
            rice_revenue = sum(r.quantity * r.price for r in rice_sales)
            
            return {
                'success': True,
                'answer': {
                    'primary_decision': {
                        'item': 'Rice 1kg',
                        'decision': 'STRONG PERFORMER - Rice is growing',
                        'action': f'Rice shows excellent performance with {rice_total} units sold',
                        'why': f'Rice detailed analysis: {rice_total} units sold, ₹{rice_revenue:.0f} revenue. Rice is your top performer with consistent daily sales.',
                        'confidence': 'High (detailed Rice analysis)',
                        'based_on': ['Complete Rice sales history']
                    }
                }
            }
        else:
            return {
                'success': False,
                'error': 'Mock system - intent not handled'
            }


if __name__ == "__main__":
    debug_rice_analysis()