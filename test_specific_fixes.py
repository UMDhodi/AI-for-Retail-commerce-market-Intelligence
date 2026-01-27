#!/usr/bin/env python3
"""
Test the specific fixes for the three issues
"""

import requests
import tempfile
import os

def test_specific_fixes():
    """Test the three specific issues that were reported"""
    
    print("=== TESTING SPECIFIC FIXES ===\n")
    
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
    
    print("📊 Test Data:")
    print("   Rice: 143 units (top seller)")
    print("   Oil: 83 units (second)")  
    print("   Tea: 67 units (third)")
    print("   Biscuits: 16 units (slow)")
    print("   Soap: 6 units (slowest)")
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write(csv_content)
        csv_file_path = f.name
    
    try:
        # Issue 1: "Tell me about Rice" should show Rice details, not all inventory
        print("\n🔍 Issue 1: Tell me about Rice (should show Rice details only)")
        
        with open(csv_file_path, 'rb') as f:
            files = {'csv_file': ('test.csv', f, 'text/csv')}
            data = {'context': 'Tell me about Rice'}
            
            response = requests.post('http://localhost:5000/analyze', files=files, data=data)
            
            if response.status_code == 200:
                print("   ✅ Upload successful")
                
                # Check if response focuses on Rice specifically
                response_lower = response.text.lower()
                
                # Look for Rice-specific content
                rice_specific_indicators = [
                    'rice' in response_lower,
                    '143' in response.text or '50' in response.text,  # Rice quantities
                    'strong performer' in response_lower or 'top seller' in response_lower
                ]
                
                if sum(rice_specific_indicators) >= 2:
                    print("   ✅ Response focuses on Rice specifically")
                else:
                    print("   ❌ Response may not be Rice-specific enough")
                    
                # Check it's not showing all inventory
                if 'soap' in response_lower and 'biscuit' in response_lower:
                    print("   ⚠️  Response may be showing all inventory instead of Rice only")
                else:
                    print("   ✅ Response appears to focus on Rice, not all inventory")
            else:
                print(f"   ❌ Upload failed: {response.status_code}")
        
        # Issue 2: "What should I reduce to save cash" should give proper answer
        print("\n🔍 Issue 2: What should I reduce to save cash (should identify slow movers)")
        
        with open(csv_file_path, 'rb') as f:
            files = {'csv_file': ('test.csv', f, 'text/csv')}
            data = {'context': 'What should I reduce to save cash?'}
            
            response = requests.post('http://localhost:5000/analyze', files=files, data=data)
            
            if response.status_code == 200:
                print("   ✅ Upload successful")
                
                response_lower = response.text.lower()
                
                # Check for cash saving specific content
                cash_saving_indicators = [
                    'reduce' in response_lower,
                    'cash' in response_lower or 'save' in response_lower,
                    'soap' in response_lower or 'biscuit' in response_lower,  # Slow movers
                    'slow' in response_lower
                ]
                
                if sum(cash_saving_indicators) >= 3:
                    print("   ✅ Response addresses cash saving with slow movers")
                else:
                    print("   ❌ Response may not properly address cash saving")
                    print(f"   Debug: Found {sum(cash_saving_indicators)}/4 indicators")
            else:
                print(f"   ❌ Upload failed: {response.status_code}")
        
        # Issue 3: "Which items are selling slowly" should give right answer
        print("\n🔍 Issue 3: Which items are selling slowly (should identify Soap, Biscuits)")
        
        with open(csv_file_path, 'rb') as f:
            files = {'csv_file': ('test.csv', f, 'text/csv')}
            data = {'context': 'Which items are selling slowly?'}
            
            response = requests.post('http://localhost:5000/analyze', files=files, data=data)
            
            if response.status_code == 200:
                print("   ✅ Upload successful")
                
                response_lower = response.text.lower()
                
                # Check for slow selling specific content
                slow_selling_indicators = [
                    'slow' in response_lower,
                    'soap' in response_lower,  # Slowest item
                    'biscuit' in response_lower,  # Second slowest
                    'selling' in response_lower
                ]
                
                if sum(slow_selling_indicators) >= 3:
                    print("   ✅ Response identifies slow selling items correctly")
                else:
                    print("   ❌ Response may not identify slow sellers properly")
                    print(f"   Debug: Found {sum(slow_selling_indicators)}/4 indicators")
                    
                # Check it's not showing generic message
                if 'stock overview' in response_lower and 'soap' not in response_lower:
                    print("   ❌ Still showing generic stock overview instead of slow sellers")
                else:
                    print("   ✅ Not showing generic stock overview")
            else:
                print(f"   ❌ Upload failed: {response.status_code}")
        
        print("\n=== SPECIFIC FIXES TEST COMPLETE ===")
        
    finally:
        os.unlink(csv_file_path)

if __name__ == "__main__":
    test_specific_fixes()