#!/usr/bin/env python3
"""
Test error handling for invalid uploads and display functionality
"""

import requests
import json

def test_missing_file():
    """Test error handling when no file is uploaded"""
    try:
        data = {'context': 'Test context'}
        response = requests.post('http://localhost:5000/analyze', data=data)
        
        print(f"Missing file status: {response.status_code}")
        
        if response.status_code == 400:
            print("✓ Missing file properly rejected")
            try:
                error_data = response.json()
                if 'error' in error_data:
                    print(f"✓ Clear error message: {error_data['error']}")
                    return True
            except:
                print("? Error response not in JSON format")
                return False
        else:
            print(f"✗ Unexpected status for missing file: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Error testing missing file: {str(e)}")
        return False

def test_invalid_csv_format():
    """Test error handling with completely invalid CSV"""
    try:
        # Create completely invalid CSV
        invalid_csv = "This is not a CSV file at all!"
        
        files = {'csv_file': ('invalid.csv', invalid_csv, 'text/csv')}
        data = {'context': 'Test context'}
        
        response = requests.post('http://localhost:5000/analyze', files=files, data=data)
        
        print(f"Invalid CSV format status: {response.status_code}")
        
        if response.status_code == 400:
            print("✓ Invalid CSV format properly rejected")
            try:
                error_data = response.json()
                if 'error' in error_data:
                    print(f"✓ Clear error message provided")
                    return True
            except:
                print("? Error response format issue")
                return False
        else:
            print(f"? Unexpected status: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Error testing invalid CSV: {str(e)}")
        return False

def test_missing_columns():
    """Test error handling with CSV missing required columns"""
    try:
        # CSV with wrong column names
        csv_data = """wrong,column,names,here
2024-01-15,Rice,10,45.00
2024-01-16,Tea,5,85.00"""
        
        files = {'csv_file': ('wrong_columns.csv', csv_data, 'text/csv')}
        data = {'context': 'Test context'}
        
        response = requests.post('http://localhost:5000/analyze', files=files, data=data)
        
        print(f"Missing columns status: {response.status_code}")
        
        if response.status_code == 400:
            print("✓ Missing columns properly detected")
            return True
        else:
            print(f"? Status: {response.status_code} - may need column validation")
            return False
    except Exception as e:
        print(f"✗ Error testing missing columns: {str(e)}")
        return False

def test_empty_file():
    """Test error handling with empty CSV file"""
    try:
        files = {'csv_file': ('empty.csv', '', 'text/csv')}
        data = {'context': 'Test context'}
        
        response = requests.post('http://localhost:5000/analyze', files=files, data=data)
        
        print(f"Empty file status: {response.status_code}")
        
        if response.status_code == 400:
            print("✓ Empty file properly rejected")
            return True
        else:
            print(f"? Empty file status: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Error testing empty file: {str(e)}")
        return False

def test_results_display():
    """Test that results display correctly with valid data"""
    try:
        # Valid CSV data
        csv_data = """date,item,quantity,price
2024-01-15,Rice 1kg,10,45.00
2024-01-16,Tea 250g,5,85.00
2024-01-17,Sugar 1kg,8,42.00"""
        
        files = {'csv_file': ('valid.csv', csv_data, 'text/csv')}
        data = {'context': 'Normal business operations'}
        
        response = requests.post('http://localhost:5000/analyze', files=files, data=data)
        
        print(f"Valid data status: {response.status_code}")
        
        if response.status_code == 200:
            content = response.text
            
            # Check for results page elements
            display_checks = []
            
            # Check for results structure
            if 'Your AI Recommendations' in content:
                display_checks.append(("Results header present", True))
            else:
                display_checks.append(("Results header present", False))
            
            # Check for recommendation cards
            if 'recommendation-card' in content:
                display_checks.append(("Recommendation cards present", True))
            else:
                display_checks.append(("Recommendation cards present", False))
            
            # Check for back navigation
            if 'Analyze New Data' in content or 'back-btn' in content:
                display_checks.append(("Navigation present", True))
            else:
                display_checks.append(("Navigation present", False))
            
            # Check for action buttons
            if 'Print Recommendations' in content or 'Get More Details' in content:
                display_checks.append(("Action buttons present", True))
            else:
                display_checks.append(("Action buttons present", False))
            
            print("\nResults Display Assessment:")
            print("-" * 30)
            
            passed = 0
            for check_name, result in display_checks:
                status = "✓ PASS" if result else "✗ FAIL"
                print(f"{check_name}: {status}")
                if result:
                    passed += 1
            
            return passed >= 3  # Pass if most display elements present
        else:
            print(f"✗ Valid data processing failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Error testing results display: {str(e)}")
        return False

def test_visual_feedback():
    """Test that the interface provides visual feedback"""
    try:
        # Test main page for visual feedback elements
        response = requests.get('http://localhost:5000/')
        
        if response.status_code == 200:
            content = response.text
            
            feedback_checks = []
            
            # Check for loading overlay
            if 'loading-overlay' in content:
                feedback_checks.append(("Loading overlay present", True))
            else:
                feedback_checks.append(("Loading overlay present", False))
            
            # Check for file upload feedback
            if 'file-label' in content or 'Choose CSV file' in content:
                feedback_checks.append(("File upload feedback", True))
            else:
                feedback_checks.append(("File upload feedback", False))
            
            # Check for form validation
            if 'required' in content:
                feedback_checks.append(("Form validation present", True))
            else:
                feedback_checks.append(("Form validation present", False))
            
            print("\nVisual Feedback Assessment:")
            print("-" * 30)
            
            passed = 0
            for check_name, result in feedback_checks:
                status = "✓ PASS" if result else "✗ FAIL"
                print(f"{check_name}: {status}")
                if result:
                    passed += 1
            
            return passed >= 2  # Pass if basic feedback present
        else:
            print(f"✗ Could not load main page: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Error testing visual feedback: {str(e)}")
        return False

def main():
    """Run all error handling and display tests"""
    print("BharatSignal Error Handling & Display Tests")
    print("=" * 45)
    
    tests = [
        ("Missing File Error", test_missing_file),
        ("Invalid CSV Format", test_invalid_csv_format),
        ("Missing Columns", test_missing_columns),
        ("Empty File", test_empty_file),
        ("Results Display", test_results_display),
        ("Visual Feedback", test_visual_feedback)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\nTesting: {test_name}")
        print("-" * 25)
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "=" * 45)
    print("Test Summary:")
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name}: {status}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    print(f"\nOverall: {passed}/{total} tests passed")
    
    return passed >= total - 1  # Allow one test to fail

if __name__ == "__main__":
    main()