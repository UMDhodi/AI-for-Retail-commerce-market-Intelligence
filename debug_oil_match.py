#!/usr/bin/env python3
"""
Debug why 'stock' is matching 'oil'
"""

def debug_oil_match():
    question = "Tell me about my stock"
    question_lower = question.lower()
    
    oil_patterns = ['oil', 'tel', 'cooking oil', 'mustard oil', 'sunflower oil']
    
    print(f"Question: '{question}'")
    print(f"Question lower: '{question_lower}'")
    print()
    
    for pattern in oil_patterns:
        if pattern in question_lower:
            print(f"MATCH FOUND: '{pattern}' in '{question_lower}'")
        else:
            print(f"No match: '{pattern}' not in '{question_lower}'")
    
    # Let's also check character by character
    print(f"\nCharacter analysis:")
    print(f"'oil' characters: {list('oil')}")
    print(f"'stock' characters: {list('stock')}")
    
    # Check if 'oil' is somehow in 'stock'
    if 'oil' in 'stock':
        print("ERROR: 'oil' found in 'stock'!")
    else:
        print("'oil' is NOT in 'stock' - this is correct")

if __name__ == "__main__":
    debug_oil_match()