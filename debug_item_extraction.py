#!/usr/bin/env python3
"""
Debug script to test item extraction
"""

from interactive_qa import InteractiveQASystem
from bedrock_client import create_bedrock_client

def test_item_extraction():
    """Test item extraction from questions"""
    
    # Create a mock QA system just to test the method
    class MockBedrock:
        pass
    
    qa_system = InteractiveQASystem(MockBedrock())
    
    test_questions = [
        "Tell me about my stock",
        "Should I restock oil?",
        "What about biscuits?",
        "Should I stock more rice?",
        "Tell me about my business",
        "What should I do today?"
    ]
    
    print("=== TESTING ITEM EXTRACTION ===\n")
    
    for question in test_questions:
        items = qa_system._extract_items_from_question(question)
        print(f"Question: '{question}'")
        print(f"Extracted items: {items}")
        print()

if __name__ == "__main__":
    test_item_extraction()