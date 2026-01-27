#!/usr/bin/env python3
"""
Test the multi-item analysis fix
"""

import requests
import tempfile
import os

def test_multi_item_fix():
    """Test the multi-item analysis for 'Should I refill tea and biscuits today?'"""
    
    print("=== TESTING MULTI-ITEM ANALYSIS FIX ===\n")
    
    # Create test CSV with tea and biscuits data
    csv_content = """date,item,quantity,price
2024-01-15,Rice 1kg,50,45.00
2024-01-15,Oil 1L,30,150.00
2024-01-15,Tea 250g,25,85.00
2024-01-15,Biscuits Pack,15,25.00
2024-01-15,Soap,3,35.00
2024-01-16,Rice 1kg,48,45.00
2024-01-16,Oil 1L,28,150.00
2024-01-16,Tea 250g,28,85.00
2024-01-16,Biscuits Pack,18,25.00
2024-01-16,Soap,2,35.00
2024-01-17,Rice 1kg,45,45.00
2024-01-17,Oil 1L,25,150.00
2024-01-17,Tea 250g,30,85.00
2024-01-17,Biscuits Pack,20,25.00
2024-01-17,Soap,1,35.00"""
    
    print("📊 Test Data:")
    print("   Tea: 25+28+30 = 83 units (increasing trend)")
    print("   Biscuits: 15+18+20 = 53 units (increasing trend)")
    print("   Both items should get positive recommendations")
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write(csv_content)
        csv_file_path = f.name
    
    try:
        # Test the multi-item question
        print("\n🔍 Testing: 'Should I refill tea and biscuits today?'")
        
        with open(csv_file_path, 'rb') as f:
            files = {'csv_file': ('test.csv', f, 'text/csv')}
            data = {'context': 'Should I refill tea and biscuits today?'}
            
            response = requests.post('http://localhost:5000/analyze', files=files, data=data)
            
            if response.status_code == 200:
                print("✅ Upload successful")
                
                response_lower = response.text.lower()
                
                # Check for multi-item analysis indicators
                multi_item_indicators = [
                    'tea' in response_lower,
                    'biscuit' in response_lower,
                    'multi-item' in response_lower or 'comparison' in response_lower,
                    'individual' in response_lower or 'each' in response_lower
                ]
                
                print(f"📊 Multi-item indicators found: {sum(multi_item_indicators)}/4")
                
                if sum(multi_item_indicators) >= 3:
                    print("✅ Response appears to analyze both tea and biscuits")
                else:
                    print("❌ Response may not properly analyze both items")
                
                # Check it's not showing generic fallback
                generic_indicators = [
                    'limited data available' in response_lower,
                    'check last week' in response_lower,
                    'increase stock by 10% only' in response_lower
                ]
                
                if sum(generic_indicators) >= 2:
                    print("❌ Still showing generic fallback response")
                else:
                    print("✅ Not showing generic fallback")
                
                # Check for specific recommendations
                if 'yes' in response_lower and ('tea' in response_lower or 'biscuit' in response_lower):
                    print("✅ Provides specific recommendations for the items")
                else:
                    print("⚠️  May not provide specific item recommendations")
                    
            else:
                print(f"❌ Upload failed: {response.status_code}")
        
        # Test with one item not in data
        print("\n🔍 Testing: 'Should I refill tea and sugar today?' (sugar not in data)")
        
        with open(csv_file_path, 'rb') as f:
            files = {'csv_file': ('test.csv', f, 'text/csv')}
            data = {'context': 'Should I refill tea and sugar today?'}
            
            response = requests.post('http://localhost:5000/analyze', files=files, data=data)
            
            if response.status_code == 200:
                print("✅ Upload successful")
                
                response_lower = response.text.lower()
                
                # Check for partial data handling
                if 'tea' in response_lower and ('sugar' in response_lower or 'not found' in response_lower):
                    print("✅ Handles partial data correctly (tea found, sugar missing)")
                else:
                    print("⚠️  May not handle partial data properly")
                    
            else:
                print(f"❌ Upload failed: {response.status_code}")
        
        print("\n=== MULTI-ITEM TEST COMPLETE ===")
        
    finally:
        os.unlink(csv_file_path)

if __name__ == "__main__":
    test_multi_item_fix()