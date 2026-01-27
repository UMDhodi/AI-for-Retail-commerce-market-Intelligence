#!/usr/bin/env python3
"""
Complete test for home page functionality
"""

import requests
import json
from io import StringIO

def test_home_page_upload():
    """Test home page CSV upload with different scenarios"""
    
    base_url = "http://localhost:5000"
    
    # Test data - different from rice
    csv_content = """date,item,quantity,price
2024-01-15,Chocolate Bar,15,45.00
2024-01-15,Chips Pack,25,20.00
2024-01-15,Juice 1L,12,85.00
2024-01-16,Chocolate Bar,18,45.00
2024-01-16,Chips Pack,30,20.00
2024-01-17,Juice 1L,8,85.00"""
    
    print("=== TESTING HOME PAGE UPLOAD ===\n")
    
    # Test 1: Upload CSV with default analysis
    print("1. Testing CSV upload with default analysis...")
    
    files = {'csv_file': ('test.csv', csv_content, 'text/csv')}
    data = {'context': ''}  # Empty context - should trigger default analysis
    
    try:
        response = requests.post(f"{base_url}/analyze", files=files, data=data)
        if response.status_code == 200:
            print("✅ Upload successful")
            # Check if response contains actual items, not rice
            if 'rice' in response.text.lower() and 'chocolate' not in response.text.lower():
                print("❌ ERROR: Still showing rice instead of uploaded items!")
                return False
            elif 'chocolate' in response.text.lower() or 'chips' in response.text.lower():
                print("✅ Response contains actual uploaded items")
            else:
                print("⚠️  Response unclear - need manual verification")
        else:
            print(f"❌ Upload failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False
    
    # Test 2: Upload CSV with specific question
    print("\n2. Testing CSV upload with specific question...")
    
    files = {'csv_file': ('test.csv', csv_content, 'text/csv')}
    data = {'context': 'Should I stock more chocolate?'}
    
    try:
        response = requests.post(f"{base_url}/analyze", files=files, data=data)
        if response.status_code == 200:
            print("✅ Upload with question successful")
            if 'chocolate' in response.text.lower():
                print("✅ Response analyzes chocolate as requested")
            else:
                print("❌ ERROR: Didn't analyze chocolate when asked!")
                return False
        else:
            print(f"❌ Upload with question failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False
    
    print("\n=== HOME PAGE TEST COMPLETE ===")
    return True

if __name__ == "__main__":
    success = test_home_page_upload()
    if success:
        print("\n✅ All home page tests passed!")
    else:
        print("\n❌ Some home page tests failed!")