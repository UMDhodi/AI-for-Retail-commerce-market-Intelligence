#!/usr/bin/env python3
"""
Comprehensive test of the enhanced system via web interface
"""

import requests
import tempfile
import os
import time

def test_comprehensive_system():
    """Test the comprehensive enhanced system"""
    
    print("=== COMPREHENSIVE SYSTEM TEST ===\n")
    
    # Create test CSV with clear performance differences
    csv_content = """date,item,quantity,price
2024-01-15,Rice 1kg,50,45.00
2024-01-15,Oil 1L,30,150.00
2024-01-15,Tea 250g,25,85.00
2024-01-15,Biscuits,8,25.00
2024-01-15,Soap,3,35.00
2024-01-16,Rice 1kg,48,45.00
2024-01-16,Oil 1L,28,150.00
2024-01-16,Tea 250g,22,85.00
2024-01-16,Biscuits,5,25.00
2024-01-16,Soap,2,35.00
2024-01-17,Rice 1kg,45,45.00
2024-01-17,Oil 1L,25,150.00
2024-01-17,Tea 250g,20,85.00
2024-01-17,Biscuits,3,25.00
2024-01-17,Soap,1,35.00"""
    
    print("📊 Test Data Performance:")
    print("   Rice: 143 units (top seller)")
    print("   Oil: 83 units (second)")
    print("   Tea: 67 units (third)")
    print("   Biscuits: 16 units (slow)")
    print("   Soap: 6 units (slowest)")
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write(csv_content)
        csv_file_path = f.name
    
    try:
        test_cases = [
            {
                'name': 'Default Analysis',
                'context': '',
                'expected': 'Should analyze uploaded data, not rice'
            },
            {
                'name': 'Stock Overview',
                'context': 'Tell me about my stock',
                'expected': 'Should show complete inventory overview'
            },
            {
                'name': 'Top Selling Query',
                'context': 'Which product is top selling?',
                'expected': 'Should identify Rice as top seller'
            },
            {
                'name': 'Slow Selling Query',
                'context': 'Which items sold slowly this week?',
                'expected': 'Should identify Soap and Biscuits as slow'
            },
            {
                'name': 'Cash Saving Query',
                'context': 'What should I reduce to save cash?',
                'expected': 'Should suggest reducing slow items'
            },
            {
                'name': 'Focus Strategy',
                'context': 'Should I focus on my top-selling items?',
                'expected': 'Should recommend focusing on Rice, Oil, Tea'
            },
            {
                'name': 'Specific Item - Found',
                'context': 'Tell me about Rice',
                'expected': 'Should provide detailed Rice analysis'
            },
            {
                'name': 'Specific Item - Not Found',
                'context': 'Tell me about Sugar',
                'expected': 'Should say Sugar not found in data'
            },
            {
                'name': 'Multiple Items',
                'context': 'Tell me about Oil and Tea forecast',
                'expected': 'Should compare Oil and Tea performance'
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n🔍 Test {i}: {test_case['name']}")
            print(f"   Question: '{test_case['context']}'")
            print(f"   Expected: {test_case['expected']}")
            
            with open(csv_file_path, 'rb') as f:
                files = {'csv_file': ('test.csv', f, 'text/csv')}
                data = {'context': test_case['context']}
                
                try:
                    response = requests.post('http://localhost:5000/analyze', files=files, data=data, timeout=30)
                    
                    if response.status_code == 200:
                        print("   ✅ Upload successful")
                        
                        # Check for rice mentions (should be minimal)
                        rice_mentions = response.text.lower().count('rice')
                        if rice_mentions > 5:  # Allow some mentions in placeholders
                            print(f"   ⚠️  High rice mentions: {rice_mentions}")
                        else:
                            print(f"   ✅ Rice mentions controlled: {rice_mentions}")
                        
                        # Check for actual data items
                        response_lower = response.text.lower()
                        actual_items_found = sum([
                            'oil' in response_lower,
                            'tea' in response_lower,
                            'biscuit' in response_lower,
                            'soap' in response_lower
                        ])
                        
                        if actual_items_found >= 2:
                            print(f"   ✅ Contains actual uploaded items: {actual_items_found}/4")
                        else:
                            print(f"   ⚠️  Few actual items found: {actual_items_found}/4")
                        
                        # Specific checks
                        if test_case['name'] == 'Specific Item - Not Found' and 'sugar' in test_case['context'].lower():
                            if 'not found' in response_lower or 'no data' in response_lower:
                                print("   ✅ Correctly identified missing item")
                            else:
                                print("   ❌ Should have identified missing item")
                        
                    else:
                        print(f"   ❌ Upload failed: {response.status_code}")
                        
                except requests.exceptions.Timeout:
                    print("   ⏰ Request timed out (server may be processing)")
                except Exception as e:
                    print(f"   ❌ Request error: {e}")
            
            # Small delay between requests
            time.sleep(1)
        
        print("\n=== COMPREHENSIVE TEST COMPLETE ===")
        
    finally:
        os.unlink(csv_file_path)

if __name__ == "__main__":
    test_comprehensive_system()