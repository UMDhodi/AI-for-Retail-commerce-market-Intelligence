"""
Test script for Bedrock integration verification

This script tests the complete Bedrock integration including:
- Client initialization and authentication
- Prompt generation
- AI model invocation
- Response parsing and validation

Requirements: 2.1, 2.2, 2.3
"""

import os
import sys
from typing import List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import our modules
from models import SalesRecord, LocalContext, Recommendation
from bedrock_client import BedrockClient, BedrockClientError, test_bedrock_connection
from prompt_engineering import create_prompt_builder, test_prompt_generation
from csv_processor import create_sample_csv_data, parse_csv
import io

def create_test_sales_data() -> List[SalesRecord]:
    """Create sample sales data for testing"""
    return [
        SalesRecord(date="2024-01-15", item="Rice 1kg", quantity=10, price=45.00),
        SalesRecord(date="2024-01-15", item="Wheat Flour 1kg", quantity=8, price=35.00),
        SalesRecord(date="2024-01-15", item="Sugar 1kg", quantity=5, price=42.00),
        SalesRecord(date="2024-01-15", item="Tea 250g", quantity=12, price=120.00),
        SalesRecord(date="2024-01-15", item="Biscuits Pack", quantity=15, price=25.00),
        SalesRecord(date="2024-01-16", item="Rice 1kg", quantity=8, price=45.00),
        SalesRecord(date="2024-01-16", item="Cooking Oil 1L", quantity=6, price=150.00),
        SalesRecord(date="2024-01-16", item="Onions 1kg", quantity=20, price=30.00),
        SalesRecord(date="2024-01-16", item="Potatoes 1kg", quantity=15, price=25.00),
        SalesRecord(date="2024-01-17", item="Milk 1L", quantity=25, price=55.00),
        SalesRecord(date="2024-01-17", item="Bread", quantity=20, price=22.00),
        SalesRecord(date="2024-01-17", item="Tea 250g", quantity=8, price=120.00),
    ]

def create_test_context() -> LocalContext:
    """Create sample local context for testing"""
    return LocalContext(
        "Diwali festival is coming next week. Weather has been hot and dry. "
        "Local school is having annual function, expecting more families in the area."
    )

def test_environment_setup():
    """Test if environment variables are properly configured"""
    print("=== Testing Environment Setup ===")
    
    required_vars = ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'AWS_REGION']
    missing_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
        else:
            print(f"✓ {var}: {'*' * min(len(value), 10)}...")
    
    if missing_vars:
        print(f"✗ Missing environment variables: {', '.join(missing_vars)}")
        print("Please set these variables in your .env file")
        return False
    
    print("✓ All required environment variables are set")
    return True

def test_prompt_generation():
    """Test prompt generation functionality"""
    print("\n=== Testing Prompt Generation ===")
    
    try:
        sales_data = create_test_sales_data()
        context = create_test_context()
        
        # Test prompt builder
        prompt_builder = create_prompt_builder()
        prompt = prompt_builder.build_recommendation_prompt(sales_data, context)
        
        print(f"✓ Prompt generated successfully ({len(prompt)} characters)")
        print(f"✓ Sales data processed: {len(sales_data)} records")
        print(f"✓ Context processed: {len(context.text)} characters")
        
        # Verify prompt contains expected sections
        expected_sections = [
            "BharatSignal",
            "SALES DATA ANALYSIS",
            "CONTEXT INFORMATION", 
            "TASK:",
            "RESPONSE FORMAT:",
            "QUALITY GUIDELINES:"
        ]
        
        missing_sections = []
        for section in expected_sections:
            if section not in prompt:
                missing_sections.append(section)
        
        if missing_sections:
            print(f"✗ Missing prompt sections: {', '.join(missing_sections)}")
            return False
        
        print("✓ All expected prompt sections present")
        
        # Show sample of prompt (first 500 chars)
        print(f"\nPrompt preview:\n{prompt[:500]}...")
        
        return True
        
    except Exception as e:
        print(f"✗ Prompt generation failed: {str(e)}")
        return False

def test_bedrock_connection_only():
    """Test Bedrock connection without full model invocation"""
    print("\n=== Testing Bedrock Connection ===")
    
    try:
        success, message = test_bedrock_connection()
        
        if success:
            print(f"✓ {message}")
            return True
        else:
            print(f"✗ {message}")
            return False
            
    except Exception as e:
        print(f"✗ Connection test failed: {str(e)}")
        return False

def test_bedrock_client_initialization():
    """Test Bedrock client initialization"""
    print("\n=== Testing Bedrock Client Initialization ===")
    
    try:
        client = BedrockClient()
        print("✓ Bedrock client initialized successfully")
        
        # Test availability check
        if client.is_available():
            print("✓ Bedrock service is available")
            return True, client
        else:
            print("✗ Bedrock service is not available")
            return False, None
            
    except BedrockClientError as e:
        print(f"✗ Bedrock client error: {str(e)}")
        return False, None
    except Exception as e:
        print(f"✗ Unexpected error: {str(e)}")
        return False, None

def test_full_ai_integration(client: BedrockClient):
    """Test full AI integration with actual model invocation"""
    print("\n=== Testing Full AI Integration ===")
    
    try:
        sales_data = create_test_sales_data()
        context = create_test_context()
        
        print(f"Invoking AI model with {len(sales_data)} sales records...")
        
        # Generate recommendations
        recommendations = client.generate_recommendations(sales_data, context)
        
        print(f"✓ AI model invocation successful")
        print(f"✓ Generated {len(recommendations)} recommendations")
        
        # Validate recommendations
        valid_recommendations = 0
        for i, rec in enumerate(recommendations, 1):
            is_valid, error = rec.full_validate()
            if is_valid:
                valid_recommendations += 1
                print(f"✓ Recommendation {i}: {rec.item} - {rec.action[:50]}...")
            else:
                print(f"✗ Recommendation {i} invalid: {error}")
        
        if valid_recommendations == len(recommendations):
            print(f"✓ All {valid_recommendations} recommendations are valid")
        else:
            print(f"⚠ Only {valid_recommendations}/{len(recommendations)} recommendations are valid")
        
        # Show detailed recommendations
        print("\n--- Generated Recommendations ---")
        for i, rec in enumerate(recommendations, 1):
            print(f"\n{i}. ITEM: {rec.item}")
            print(f"   ACTION: {rec.action}")
            print(f"   EXPLANATION: {rec.explanation}")
        
        return len(recommendations) > 0 and valid_recommendations > 0
        
    except BedrockClientError as e:
        print(f"✗ Bedrock error: {str(e)}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {str(e)}")
        return False

def test_csv_integration():
    """Test CSV processing integration"""
    print("\n=== Testing CSV Integration ===")
    
    try:
        # Create sample CSV data
        csv_content = create_sample_csv_data()
        csv_file = io.StringIO(csv_content)
        
        # Parse CSV
        from csv_processor import parse_csv
        result = parse_csv(csv_file)
        
        if result.success:
            print(f"✓ CSV parsing successful: {len(result.valid_records)} records")
            
            # Test with Bedrock if available
            if len(result.valid_records) > 0:
                context = LocalContext("Sample context for CSV test")
                
                try:
                    client = BedrockClient()
                    recommendations = client.generate_recommendations(result.valid_records, context)
                    print(f"✓ AI recommendations from CSV data: {len(recommendations)} generated")
                    return True
                except Exception as e:
                    print(f"⚠ CSV data processed but AI integration failed: {str(e)}")
                    return True  # CSV processing worked
            else:
                print("✗ No valid records from CSV")
                return False
        else:
            print(f"✗ CSV parsing failed: {len(result.errors)} errors")
            return False
            
    except Exception as e:
        print(f"✗ CSV integration test failed: {str(e)}")
        return False

def run_all_tests():
    """Run all integration tests"""
    print("BharatSignal Bedrock Integration Test Suite")
    print("=" * 50)
    
    test_results = []
    
    # Test 1: Environment setup
    test_results.append(("Environment Setup", test_environment_setup()))
    
    # Test 2: Prompt generation
    test_results.append(("Prompt Generation", test_prompt_generation()))
    
    # Test 3: Bedrock connection
    test_results.append(("Bedrock Connection", test_bedrock_connection_only()))
    
    # Test 4: Client initialization
    client_success, client = test_bedrock_client_initialization()
    test_results.append(("Client Initialization", client_success))
    
    # Test 5: Full AI integration (only if client works)
    if client_success and client:
        test_results.append(("Full AI Integration", test_full_ai_integration(client)))
    else:
        test_results.append(("Full AI Integration", False))
    
    # Test 6: CSV integration
    test_results.append(("CSV Integration", test_csv_integration()))
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name:<25} {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Bedrock integration is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the configuration and try again.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)