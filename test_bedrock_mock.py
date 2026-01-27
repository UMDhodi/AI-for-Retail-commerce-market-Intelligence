"""
Mock test for Bedrock integration verification

This script tests the Bedrock integration logic without requiring AWS credentials
by mocking the Bedrock responses. This allows us to verify the complete flow
including prompt generation, response parsing, and recommendation validation.

Requirements: 2.1, 2.2, 2.3
"""

import json
from typing import List
from unittest.mock import Mock, patch

from models import SalesRecord, LocalContext, Recommendation
from bedrock_client import BedrockClient, BedrockConfig
from prompt_engineering import create_prompt_builder

def create_test_sales_data() -> List[SalesRecord]:
    """Create sample sales data for testing"""
    return [
        SalesRecord(date="2024-01-15", item="Rice 1kg", quantity=10, price=45.00),
        SalesRecord(date="2024-01-15", item="Tea 250g", quantity=12, price=120.00),
        SalesRecord(date="2024-01-15", item="Biscuits Pack", quantity=15, price=25.00),
        SalesRecord(date="2024-01-16", item="Rice 1kg", quantity=8, price=45.00),
        SalesRecord(date="2024-01-16", item="Cooking Oil 1L", quantity=6, price=150.00),
        SalesRecord(date="2024-01-17", item="Milk 1L", quantity=25, price=55.00),
    ]

def create_test_context() -> LocalContext:
    """Create sample local context for testing"""
    return LocalContext(
        "Diwali festival is coming next week. Weather has been hot and dry. "
        "Local school is having annual function."
    )

def create_mock_bedrock_response() -> dict:
    """Create a mock Bedrock API response"""
    mock_ai_text = """ITEM: Rice 1kg
ACTION: Increase weekly order from 18 to 25 bags
EXPLANATION: Rice is your top seller with consistent demand. Ordering more will prevent stockouts during Diwali festival rush.

ITEM: Tea 250g
ACTION: Stock up on premium tea varieties for festival season
EXPLANATION: Tea consumption increases during festivals. Consider stocking gift packs and premium varieties for higher margins.

ITEM: Cooking Oil 1L
ACTION: Maintain current stock levels but watch for price increases
EXPLANATION: Oil prices are stable but may rise during festival season. Current sales volume is good.

ITEM: Festival Sweets
ACTION: Add traditional sweets and mithai to inventory
EXPLANATION: Diwali is coming next week. Local customers will need sweets for celebrations and gifting."""

    return {
        'body': Mock(read=lambda: json.dumps({
            'content': [{'text': mock_ai_text}]
        }).encode())
    }

def test_prompt_generation_detailed():
    """Test detailed prompt generation"""
    print("=== Testing Detailed Prompt Generation ===")
    
    try:
        sales_data = create_test_sales_data()
        context = create_test_context()
        
        prompt_builder = create_prompt_builder()
        prompt = prompt_builder.build_recommendation_prompt(sales_data, context)
        
        print(f"✓ Prompt generated: {len(prompt)} characters")
        
        # Check for key components
        checks = [
            ("System role", "BharatSignal" in prompt),
            ("Sales analysis", "SALES DATA ANALYSIS" in prompt),
            ("Context info", "Diwali festival" in prompt),
            ("Task instructions", "TASK:" in prompt),
            ("Format guidelines", "RESPONSE FORMAT:" in prompt),
            ("Quality guidelines", "QUALITY GUIDELINES:" in prompt)
        ]
        
        all_passed = True
        for check_name, result in checks:
            status = "✓" if result else "✗"
            print(f"{status} {check_name}: {'Present' if result else 'Missing'}")
            if not result:
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"✗ Prompt generation failed: {str(e)}")
        return False

def test_response_parsing():
    """Test AI response parsing"""
    print("\n=== Testing Response Parsing ===")
    
    try:
        # Create mock response text
        mock_response = """ITEM: Rice 1kg
ACTION: Increase weekly order from 18 to 25 bags
EXPLANATION: Rice is your top seller with consistent demand. Ordering more will prevent stockouts.

ITEM: Tea 250g
ACTION: Stock premium varieties for festival season
EXPLANATION: Tea consumption increases during festivals. Premium varieties offer higher margins.

ITEM: Festival Items
ACTION: Add traditional sweets to inventory
EXPLANATION: Diwali is next week. Customers need sweets for celebrations."""

        # Test parsing with BedrockClient
        config = BedrockConfig(
            aws_access_key_id="mock_key",
            aws_secret_access_key="mock_secret"
        )
        
        # Mock the client initialization to avoid AWS calls
        with patch('bedrock_client.boto3.client'):
            client = BedrockClient(config)
            recommendations = client._parse_ai_response(mock_response)
        
        print(f"✓ Parsed {len(recommendations)} recommendations")
        
        # Validate each recommendation
        valid_count = 0
        for i, rec in enumerate(recommendations, 1):
            is_valid, error = rec.full_validate()
            if is_valid:
                valid_count += 1
                print(f"✓ Recommendation {i}: {rec.item}")
                print(f"  Action: {rec.action}")
                print(f"  Explanation: {rec.explanation[:60]}...")
            else:
                print(f"✗ Recommendation {i} invalid: {error}")
        
        success = valid_count == len(recommendations) and len(recommendations) >= 3
        print(f"\n✓ Validation: {valid_count}/{len(recommendations)} recommendations valid")
        
        return success
        
    except Exception as e:
        print(f"✗ Response parsing failed: {str(e)}")
        return False

def test_full_integration_mock():
    """Test full integration with mocked Bedrock calls"""
    print("\n=== Testing Full Integration (Mocked) ===")
    
    try:
        sales_data = create_test_sales_data()
        context = create_test_context()
        
        # Mock Bedrock client and response
        mock_response = create_mock_bedrock_response()
        
        config = BedrockConfig(
            aws_access_key_id="mock_key",
            aws_secret_access_key="mock_secret"
        )
        
        with patch('bedrock_client.boto3.client') as mock_boto_client:
            # Setup mock client
            mock_client_instance = Mock()
            mock_client_instance.invoke_model.return_value = mock_response
            mock_boto_client.return_value = mock_client_instance
            
            # Create client and generate recommendations
            client = BedrockClient(config)
            recommendations = client.generate_recommendations(sales_data, context)
        
        print(f"✓ Generated {len(recommendations)} recommendations")
        
        # Validate recommendations
        valid_count = 0
        for rec in recommendations:
            if rec.validate():
                valid_count += 1
        
        print(f"✓ {valid_count}/{len(recommendations)} recommendations are valid")
        
        # Check for expected content
        items = [rec.item for rec in recommendations]
        has_rice = any("Rice" in item for item in items)
        has_festival = any("Festival" in item or "Sweet" in item for item in items)
        
        print(f"✓ Contains rice recommendation: {has_rice}")
        print(f"✓ Contains festival-related recommendation: {has_festival}")
        
        # Show recommendations
        print("\n--- Generated Recommendations ---")
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec.item}: {rec.action}")
            print(f"   Why: {rec.explanation}")
        
        return len(recommendations) >= 3 and valid_count >= 3
        
    except Exception as e:
        print(f"✗ Full integration test failed: {str(e)}")
        return False

def test_error_handling():
    """Test error handling scenarios"""
    print("\n=== Testing Error Handling ===")
    
    try:
        config = BedrockConfig(
            aws_access_key_id="mock_key",
            aws_secret_access_key="mock_secret"
        )
        
        with patch('bedrock_client.boto3.client') as mock_boto_client:
            # Test 1: Invalid response format
            mock_client_instance = Mock()
            mock_client_instance.invoke_model.side_effect = Exception("Mock error")
            mock_boto_client.return_value = mock_client_instance
            
            client = BedrockClient(config)
            sales_data = create_test_sales_data()
            context = create_test_context()
            
            recommendations = client.generate_recommendations(sales_data, context)
            
            # Should return fallback recommendations
            print(f"✓ Error handling: Generated {len(recommendations)} fallback recommendations")
            
            # Test 2: Invalid AI response parsing
            invalid_response = "This is not a properly formatted response"
            fallback_recs = client._parse_ai_response(invalid_response)
            
            print(f"✓ Invalid response handling: Generated {len(fallback_recs)} fallback recommendations")
            
            return len(recommendations) > 0 and len(fallback_recs) > 0
        
    except Exception as e:
        print(f"✗ Error handling test failed: {str(e)}")
        return False

def run_mock_tests():
    """Run all mock tests"""
    print("BharatSignal Bedrock Integration Mock Test Suite")
    print("=" * 55)
    
    test_results = []
    
    # Run tests
    test_results.append(("Prompt Generation", test_prompt_generation_detailed()))
    test_results.append(("Response Parsing", test_response_parsing()))
    test_results.append(("Full Integration (Mock)", test_full_integration_mock()))
    test_results.append(("Error Handling", test_error_handling()))
    
    # Summary
    print("\n" + "=" * 55)
    print("MOCK TEST SUMMARY")
    print("=" * 55)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name:<30} {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All mock tests passed! Bedrock integration logic is working correctly.")
        print("💡 The integration is ready for deployment with proper AWS credentials.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = run_mock_tests()
    exit(0 if success else 1)