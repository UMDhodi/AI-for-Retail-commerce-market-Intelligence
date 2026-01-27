#!/usr/bin/env python3
"""
Test real CSV upload to trace the exact issue
"""

import requests
import tempfile
import os

def test_real_csv_upload():
    """Test uploading a real CSV file and see what happens"""
    
    print("=== TESTING REAL CSV UPLOAD ===\n")
    
    # Create a CSV file with NON-RICE data
    csv_content = """date,item,quantity,price
2024-01-15,Chocolate Bar,25,45.00
2024-01-15,Potato Chips,30,20.00
2024-01-15,Orange Juice,15,85.00
2024-01-16,Chocolate Bar,20,45.00
2024-01-16,Potato Chips,35,20.00
2024-01-16,Cookies Pack,18,35.00
2024-01-17,Orange Juice,12,85.00
2024-01-17,Cookies Pack,22,35.00"""
    
    print("📄 CSV Content:")
    print(csv_content)
    print()
    
    # Write to temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write(csv_content)
        csv_file_path = f.name
    
    try:
        # Test 1: Upload with empty context (default analysis)
        print("🔍 Test 1: Upload CSV with empty context (should analyze uploaded data)")
        
        with open(csv_file_path, 'rb') as f:
            files = {'csv_file': ('test_data.csv', f, 'text/csv')}
            data = {'context': ''}  # Empty context
            
            response = requests.post('http://localhost:5000/analyze', files=files, data=data)
            
            if response.status_code == 200:
                print("✅ Upload successful")
                
                # Check response content
                response_text = response.text.lower()
                
                # Check for rice mentions
                if 'rice' in response_text:
                    print("❌ ERROR: Response contains 'rice'!")
                    print("🔍 Rice mentions found in response")
                    
                    # Find rice mentions
                    lines = response.text.split('\n')
                    for i, line in enumerate(lines):
                        if 'rice' in line.lower():
                            print(f"   Line {i}: {line.strip()}")
                else:
                    print("✅ No rice mentions found")
                
                # Check for actual uploaded items
                uploaded_items = ['chocolate', 'potato', 'chips', 'orange', 'juice', 'cookies']
                found_items = []
                for item in uploaded_items:
                    if item in response_text:
                        found_items.append(item)
                
                if found_items:
                    print(f"✅ Found uploaded items in response: {found_items}")
                else:
                    print("❌ ERROR: No uploaded items found in response!")
                
                # Save response for inspection
                with open('debug_response.html', 'w') as f:
                    f.write(response.text)
                print("💾 Response saved to debug_response.html")
                
            else:
                print(f"❌ Upload failed: {response.status_code}")
                print(f"Error: {response.text}")
        
        print("\n" + "="*50)
        
        # Test 2: Upload with specific question
        print("🔍 Test 2: Upload CSV with specific question about chocolate")
        
        with open(csv_file_path, 'rb') as f:
            files = {'csv_file': ('test_data.csv', f, 'text/csv')}
            data = {'context': 'Should I stock more chocolate?'}
            
            response = requests.post('http://localhost:5000/analyze', files=files, data=data)
            
            if response.status_code == 200:
                print("✅ Upload with question successful")
                
                response_text = response.text.lower()
                
                if 'chocolate' in response_text:
                    print("✅ Response mentions chocolate")
                else:
                    print("❌ ERROR: Response doesn't mention chocolate!")
                
                if 'rice' in response_text:
                    print("❌ ERROR: Response still mentions rice!")
                else:
                    print("✅ No rice mentions")
                    
            else:
                print(f"❌ Upload with question failed: {response.status_code}")
    
    finally:
        # Clean up
        os.unlink(csv_file_path)
    
    print("\n=== TEST COMPLETE ===")

if __name__ == "__main__":
    test_real_csv_upload()