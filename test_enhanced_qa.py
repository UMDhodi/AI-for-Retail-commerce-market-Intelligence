#!/usr/bin/env python3
"""
Test the enhanced Q&A functionality
"""

from models import SalesRecord, LocalContext
from interactive_qa import create_qa_system
from bedrock_client import create_bedrock_client
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_enhanced_qa():
    """Test the enhanced Q&A system with new question types"""
    
    print("=== TESTING ENHANCED Q&A SYSTEM ===\n")
    
    # Create test data
    sales_data = [
        SalesRecord("2024-01-15", "Rice 1kg", 50, 45.00),
        SalesRecord("2024-01-15", "Oil 1L", 30, 150.00),
        SalesRecord("2024-01-15", "Tea 250g", 25, 85.00),
        SalesRecord("2024-01-15", "Biscuits", 15, 25.00),
        SalesRecord("2024-01-16", "Rice 1kg", 45, 45.00),
        SalesRecord("2024-01-16", "Oil 1L", 28, 150.00),
        SalesRecord("2024-01-16", "Tea 250g", 20, 85.00),
        SalesRecord("2024-01-16", "Biscuits", 8, 25.00),
        SalesRecord("2024-01-17", "Rice 1kg", 40, 45.00),
        SalesRecord("2024-01-17", "Oil 1L", 25, 150.00),
        SalesRecord("2024-01-17", "Tea 250g", 18, 85.00),
        SalesRecord("2024-01-17", "Biscuits", 5, 25.00)
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
    
    # Test cases
    test_questions = [
        "Which items sold slowly this week?",
        "What should I reduce to save cash?",
        "Should I focus on my top-selling items?",
        "Which product is top selling?",
        "Top 3 products",
        "Tell me about Sugar",  # Item not in data
        "Tell me about Rice",   # Item in data
        "Tell me about Oil and Tea forecast"  # Multiple items
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n🔍 Test {i}: '{question}'")
        
        try:
            result = qa_system.answer_question(question, sales_data, context)
            
            if result['success']:
                answer = result['answer']
                decision = answer['primary_decision']
                
                print(f"✅ Success")
                print(f"   Item: {decision['item']}")
                print(f"   Decision: {decision['decision']}")
                print(f"   Action: {decision['action'][:80]}...")
                
                # Check for specific expectations
                if "sugar" in question.lower():
                    if "not found" in decision['decision'].lower() or "no data" in decision['decision'].lower():
                        print("   ✅ Correctly identified missing item")
                    else:
                        print("   ❌ Should have identified missing item")
                
                elif "slow" in question.lower():
                    if "slow" in decision['decision'].lower() or "biscuits" in decision['action'].lower():
                        print("   ✅ Correctly identified slow sellers")
                    else:
                        print("   ⚠️  May not have identified slow sellers correctly")
                
                elif "top" in question.lower():
                    if "rice" in decision['action'].lower() or "top" in decision['decision'].lower():
                        print("   ✅ Correctly identified top sellers")
                    else:
                        print("   ⚠️  May not have identified top sellers correctly")
                        
            else:
                print(f"❌ Failed: {result.get('error')}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")
    
    print("\n=== ENHANCED Q&A TEST COMPLETE ===")


class MockQASystem:
    """Mock Q&A system for testing when Bedrock is not available"""
    
    def answer_question(self, question, sales_data, context):
        question_lower = question.lower()
        
        # Calculate item performance
        item_totals = {}
        for record in sales_data:
            if record.item not in item_totals:
                item_totals[record.item] = 0
            item_totals[record.item] += record.quantity
        
        sorted_items = sorted(item_totals.items(), key=lambda x: x[1], reverse=True)
        
        # Handle different question types
        if "slow" in question_lower:
            slow_items = sorted_items[-2:]  # Bottom 2
            return {
                'success': True,
                'answer': {
                    'primary_decision': {
                        'item': 'Slow Selling Items',
                        'decision': 'REDUCE SLOW MOVERS',
                        'action': f'Consider reducing {slow_items[0][0]} and {slow_items[1][0]} stock',
                        'why': f'These items have lowest sales: {slow_items}',
                        'confidence': 'High (mock analysis)',
                        'based_on': ['Sales performance data']
                    }
                }
            }
        
        elif "top" in question_lower:
            top_items = sorted_items[:3]  # Top 3
            return {
                'success': True,
                'answer': {
                    'primary_decision': {
                        'item': 'Top Selling Items',
                        'decision': 'FOCUS ON TOP PERFORMERS',
                        'action': f'Focus on {top_items[0][0]}, {top_items[1][0]}, {top_items[2][0]}',
                        'why': f'Top performers: {top_items}',
                        'confidence': 'High (mock analysis)',
                        'based_on': ['Sales performance data']
                    }
                }
            }
        
        elif "sugar" in question_lower:
            return {
                'success': True,
                'answer': {
                    'primary_decision': {
                        'item': 'Sugar',
                        'decision': 'NO DATA FOUND',
                        'action': 'No sales data available for Sugar',
                        'why': 'Sugar not found in your uploaded CSV file',
                        'confidence': 'High (data verification)',
                        'based_on': ['Complete CSV search']
                    }
                }
            }
        
        elif "rice" in question_lower:
            rice_qty = item_totals.get('Rice 1kg', 0)
            return {
                'success': True,
                'answer': {
                    'primary_decision': {
                        'item': 'Rice 1kg',
                        'decision': 'TOP PERFORMER',
                        'action': f'Rice is your best seller with {rice_qty} units sold',
                        'why': 'Rice shows consistent high sales performance',
                        'confidence': 'High (actual data)',
                        'based_on': ['Sales data analysis']
                    }
                }
            }
        
        else:
            # Default response
            top_item = sorted_items[0][0]
            return {
                'success': True,
                'answer': {
                    'primary_decision': {
                        'item': top_item,
                        'decision': f'FOCUS ON {top_item.upper()}',
                        'action': f'{top_item} is performing well',
                        'why': f'{top_item} is your top seller',
                        'confidence': 'Medium (mock analysis)',
                        'based_on': ['Mock analysis']
                    }
                }
            }


if __name__ == "__main__":
    test_enhanced_qa()