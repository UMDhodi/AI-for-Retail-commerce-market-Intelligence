#!/usr/bin/env python3
"""
Save the HTML response to inspect it
"""

import requests
import tempfile
import os

def test_save_response():
    """Save the HTML response to a file for inspection"""
    
    # Create CSV with non-rice data
    csv_content = """date,item,quantity,price
2024-01-15,Chocolate Bar,25,45.00
2024-01-15,Potato Chips,30,20.00
2024-01-16,Chocolate Bar,20,45.00
2024-01-16,Potato Chips,35,20.00"""
    
    # Write to temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write(csv_content)
        csv_file_path = f.name
    
    try:
        # Upload CSV
        with open(csv_file_path, 'rb') as f:
            files = {'csv_file': ('test_data.csv', f, 'text/csv')}
            data = {'context': ''}  # Empty context
            
            response = requests.post('http://localhost:5000/analyze', files=files, data=data)
            
            if response.status_code == 200:
                # Save response as UTF-8
                with open('response.html', 'w', encoding='utf-8') as f:
                    f.write(response.text)
                print("✅ Response saved to response.html")
                
                # Check for rice in decision line specifically
                lines = response.text.split('\n')
                for i, line in enumerate(lines):
                    if 'primary-decision' in line and 'decision-text-bold' in line:
                        print(f"🎯 Decision line {i}: {line.strip()}")
                        if 'rice' in line.lower():
                            print("❌ ERROR: Decision line contains rice!")
                        else:
                            print("✅ Decision line does not contain rice")
                        break
                else:
                    print("⚠️  Could not find decision line")
                    
            else:
                print(f"❌ Upload failed: {response.status_code}")
    
    finally:
        os.unlink(csv_file_path)

if __name__ == "__main__":
    test_save_response()