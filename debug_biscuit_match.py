#!/usr/bin/env python3
"""
Debug why 'biscuits' is not matching 'biscuit'
"""
import re

def debug_biscuit_match():
    question = "What about biscuits?"
    question_lower = question.lower()
    
    biscuit_patterns = ['biscuit', 'cookie', 'parle', 'britannia']
    
    print(f"Question: '{question}'")
    print(f"Question lower: '{question_lower}'")
    print()
    
    for pattern in biscuit_patterns:
        # Test both methods
        substring_match = pattern in question_lower
        word_boundary_match = bool(re.search(r'\b' + re.escape(pattern) + r'\b', question_lower))
        
        print(f"Pattern: '{pattern}'")
        print(f"  Substring match: {substring_match}")
        print(f"  Word boundary match: {word_boundary_match}")
        print()

if __name__ == "__main__":
    debug_biscuit_match()