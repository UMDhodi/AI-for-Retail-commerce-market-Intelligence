#!/usr/bin/env python3
"""
Final verification that the home page issue is fixed
"""

import requests
import tempfile
import os

def test_final_verification():
    """Final test to verify the home page works correctly"""
    
    print("=== FINAL VERIFICATION TEST ===\n")
    
    # Test with completely different items (no rice, oil, tea)
    csv_content = """date,item,quantity,price
2024-01-15,Soap Bar,15,25.00
2024-01-15,Toothpaste,20,45.00
2024-01-15,Shampoo 200ml,8,120.00
2024-01-16,Soap Bar,18,25.00
2024-01-16,Toothpaste,25,45.00
2024-01-17,Shampoo 200ml,5,120.00"""
    
    print("📄 Test data: Soap, Toothpaste, Shampoo (NO rice/oil/tea)")
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write(csv_content)
        csv_file_path = f.name
    
    try:
        # Test 1: Default analysis
        print("\n🔍 Test 1: Upload CSV with default analysis")
        
        with open(csv_file_path, 'rb') as f:
            files = {'csv_file': ('test.csv', f, 'text/csv')}
            data = {'context': ''}
            
            response = requests.post('http://localhost:5000/analyze', files=files, data=data)
            
            if response.status_code == 200:
                print("✅ Upload successful")
                
                # Check decision line
                lines = response.text.split('\n')
                decision_line = None
                action_line = None
                why_line = None
                
                for line in lines:
                    if 'primary-decision' in line and 'decision-text-bold' in line:
                        decision_line = line.strip()
                    elif 'primary-action' in line:
                        action_line = line.strip()
                    elif 'primary-why' in line:
                        why_line = line.strip()
                
                print(f"🎯 Decision: {decision_line}")
                print(f"🔧 Action: {action_line}")
                print(f"💡 Why: {why_line[:100]}...")
                
                # Check for rice mentions in main content
                main_content = decision_line + " " + action_line + " " + why_line
                if 'rice' in main_content.lower():
                    print("❌ ERROR: Main content still contains rice!")
                    return False
                else:
                    print("✅ No rice in main recommendation content")
                
                # Check for actual uploaded items
                response_lower = response.text.lower()
                if any(item in response_lower for item in ['soap', 'toothpaste', 'shampoo']):
                    print("✅ Response contains actual uploaded items")
                else:
                    print("⚠️  Response may not contain uploaded items")
                    
            else:
                print(f"❌ Upload failed: {response.status_code}")
                return False
        
        # Test 2: Specific item question
        print("\n🔍 Test 2: Ask about specific uploaded item")
        
        with open(csv_file_path, 'rb') as f:
            files = {'csv_file': ('test.csv', f, 'text/csv')}
            data = {'context': 'Should I stock more toothpaste?'}
            
            response = requests.post('http://localhost:5000/analyze', files=files, data=data)
            
            if response.status_code == 200:
                print("✅ Specific question upload successful")
                
                if 'toothpaste' in response.text.lower():
                    print("✅ Response analyzes toothpaste as requested")
                else:
                    print("❌ ERROR: Response doesn't analyze toothpaste!")
                    return False
                    
                if 'rice' in response.text.lower() and 'placeholder' not in response.text.lower():
                    print("❌ ERROR: Response contains rice in main content!")
                    return False
                else:
                    print("✅ No rice in main content")
                    
            else:
                print(f"❌ Specific question failed: {response.status_code}")
                return False
        
        print("\n=== FINAL VERIFICATION COMPLETE ===")
        return True
    
    finally:
        os.unlink(csv_file_path)

if __name__ == "__main__":
    success = test_final_verification()
    if success:
        print("\n🎉 ALL TESTS PASSED! Home page issue is FIXED!")
    else:
        print("\n❌ Some tests failed - issue not fully resolved")