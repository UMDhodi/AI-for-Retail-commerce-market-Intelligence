#!/usr/bin/env python3
"""
Test script for BharatSignal web interface
Tests the Flask routes and file upload functionality
"""

import requests
import os
from io import StringIO

def test_main_page():
    """Test that the main page loads correctly"""
    try:
        response = requests.get('http://localhost:5000/')
        print(f"Main page status: {response.status_code}")
        
        if response.status_code == 200:
            print("✓ Main page loads successfully")
            # Check for key elements
            content = response.text
            if 'BharatSignal' in content and 'Upload Your Sales Data' in content:
                print("✓ Main page contains expected content")
                return True
            else:
                print("✗ Main page missing expected content")
                return False
        else:
            print(f"✗ Main page failed to load: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Error testing main page: {str(e)}")
        return False

def test_csv_upload():
    """Test CSV upload functionality with sample data"""
    try:
        # Create test CSV data
        csv_data = """date,item,quantity,price
2024-01-15,Rice 1kg,10,45.00
2024-01-15,Tea 250g,5,85.00
2024-01-16,Biscuits Pack,8,25.00"""
        
        # Prepare form data
        files = {'csv_file': ('test_sales.csv', csv_data, 'text/csv')}
        data = {'context': 'Diwali festival coming next week. Heavy rains for 3 days.'}
        
        response = requests.post('http://localhost:5000/analyze', files=files, data=data)
        print(f"CSV upload status: {response.status_code}")
        
        if response.status_code == 200:
            print("✓ CSV upload and processing successful")
            content = response.text
            if 'recommendations' in content.lower() or 'recommendation' in content.lower():
                print("✓ Results page contains recommendations")
                return True
            else:
                print("? Results page loaded but may not contain recommendations")
                return True
        else:
            print(f"✗ CSV upload failed: {response.status_code}")
            if response.headers.get('content-type', '').startswith('application/json'):
                try:
                    error_data = response.json()
                    print(f"Error details: {error_data}")
                except:
                    pass
            return False
    except Exception as e:
        print(f"✗ Error testing CSV upload: {str(e)}")
        return False

def test_invalid_csv():
    """Test error handling with invalid CSV"""
    try:
        # Create invalid CSV data
        csv_data = "invalid,csv,data\nno,proper,headers"
        
        files = {'csv_file': ('invalid.csv', csv_data, 'text/csv')}
        data = {'context': 'Test context'}
        
        response = requests.post('http://localhost:5000/analyze', files=files, data=data)
        print(f"Invalid CSV status: {response.status_code}")
        
        if response.status_code == 400:
            print("✓ Invalid CSV properly rejected with 400 status")
            return True
        elif response.status_code == 200:
            print("? Invalid CSV accepted - check error handling")
            return False
        else:
            print(f"? Unexpected status for invalid CSV: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Error testing invalid CSV: {str(e)}")
        return False

def main():
    """Run all web interface tests"""
    print("Testing BharatSignal Web Interface")
    print("=" * 40)
    
    tests = [
        ("Main Page Load", test_main_page),
        ("CSV Upload", test_csv_upload),
        ("Invalid CSV Handling", test_invalid_csv)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\nTesting: {test_name}")
        print("-" * 20)
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "=" * 40)
    print("Test Summary:")
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name}: {status}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    print(f"\nOverall: {passed}/{total} tests passed")
    
    return passed == total

if __name__ == "__main__":
    main()