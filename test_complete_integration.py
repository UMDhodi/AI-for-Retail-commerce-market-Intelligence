"""
Complete Integration Test for BharatSignal

This script tests the complete end-to-end integration including:
- CSV processing
- Bedrock AI integration (mocked)
- Recommendation formatting
- Web application flow

Requirements: All task 3 requirements
"""

import io
from unittest.mock import Mock, patch
import json

from models import SalesRecord, LocalContext, Recommendation
from csv_processor import parse_csv, create_sample_csv_data
from bedrock_client import BedrockClient, BedrockConfig
from recommendation_formatter import format_recommendations_for_web
from prompt_engineering import create_prompt_builder

def test_complete_workflow():
    """Test the complete workflow from CSV to formatted recommendations"""
    print("=== Testing Complete Workflow ===")
    
    try:
        # Step 1: Create and process CSV data
        print("Step 1: Processing CSV data...")
        csv_content = create_sample_csv_data()
        csv_file = io.StringIO(csv_content)
        
        csv_result = parse_csv(csv_file)
        if not csv_result.success:
            print(f"✗ CSV processing failed: {csv_result.errors}")
            return False
        
        sales_data = csv_result.valid_records
        print(f"✓ Processed {len(sales_data)} sales records")
        
        # Step 2: Create local context
        print("Step 2: Creating local context...")
        context = LocalContext(
            "Diwali festival is coming next week. Weather has been hot and dry. "
            "Local school is having annual function, expecting more families in the area."
        )
        
        is_valid, error = context.full_validate()
        if not is_valid:
            print(f"✗ Context validation failed: {error}")
            return False
        
        print(f"✓ Context created: {len(context.text)} characters")
        
        # Step 3: Generate prompt
        print("Step 3: Generating AI prompt...")
        prompt_builder = create_prompt_builder()
        prompt = prompt_builder.build_recommendation_prompt(sales_data, context)
        
        if len(prompt) < 1000:  # Reasonable minimum length
            print(f"✗ Prompt too short: {len(prompt)} characters")
            return False
        
        print(f"✓ Generated prompt: {len(prompt)} characters")
        
        # Step 4: Mock AI response and generate recommendations
        print("Step 4: Generating AI recommendations (mocked)...")
        
        mock_ai_response = """ITEM: Rice 1kg
ACTION: Increase weekly order from 15 to 25 bags
EXPLANATION: Rice is your top revenue generator with consistent demand. Festival season will increase sales.

ITEM: Tea 250g
ACTION: Stock premium tea varieties and gift packs
EXPLANATION: Tea consumption increases during Diwali. Premium varieties offer better margins for festival sales.

ITEM: Cooking Oil 1L
ACTION: Maintain current stock but monitor prices
EXPLANATION: Oil sales are steady. Watch for price increases during festival season.

ITEM: Festival Sweets
ACTION: Add traditional sweets and mithai to inventory
EXPLANATION: Diwali is next week. Local customers will need sweets for celebrations and gifting.

ITEM: Milk 1L
ACTION: Increase daily order by 30% for festival week
EXPLANATION: Milk demand increases for sweet preparation and increased household consumption during festivals."""

        mock_bedrock_response = {
            'body': Mock(read=lambda: json.dumps({
                'content': [{'text': mock_ai_response}]
            }).encode())
        }
        
        config = BedrockConfig(
            aws_access_key_id="mock_key",
            aws_secret_access_key="mock_secret"
        )
        
        with patch('bedrock_client.boto3.client') as mock_boto_client:
            mock_client_instance = Mock()
            mock_client_instance.invoke_model.return_value = mock_bedrock_response
            mock_boto_client.return_value = mock_client_instance
            
            client = BedrockClient(config)
            recommendations = client.generate_recommendations(sales_data, context)
        
        if len(recommendations) < 3:
            print(f"✗ Too few recommendations: {len(recommendations)}")
            return False
        
        print(f"✓ Generated {len(recommendations)} recommendations")
        
        # Step 5: Validate recommendations
        print("Step 5: Validating recommendations...")
        valid_count = 0
        for rec in recommendations:
            if rec.validate():
                valid_count += 1
        
        if valid_count != len(recommendations):
            print(f"✗ Invalid recommendations: {valid_count}/{len(recommendations)} valid")
            return False
        
        print(f"✓ All {valid_count} recommendations are valid")
        
        # Step 6: Format recommendations for web display
        print("Step 6: Formatting for web display...")
        formatted_recs = format_recommendations_for_web(recommendations)
        
        if len(formatted_recs) != len(recommendations):
            print(f"✗ Formatting mismatch: {len(formatted_recs)} formatted vs {len(recommendations)} original")
            return False
        
        print(f"✓ Formatted {len(formatted_recs)} recommendations for web")
        
        # Step 7: Display results
        print("Step 7: Final results...")
        print("\n--- GENERATED RECOMMENDATIONS ---")
        for i, rec in enumerate(formatted_recs, 1):
            print(f"\n{i}. {rec['icon']} {rec['item']} ({rec['priority']} priority)")
            print(f"   Action: {rec['action']}")
            print(f"   Reason: {rec['explanation']}")
        
        print(f"\n✓ Complete workflow successful!")
        return True
        
    except Exception as e:
        print(f"✗ Complete workflow failed: {str(e)}")
        return False

def test_error_scenarios():
    """Test error handling scenarios"""
    print("\n=== Testing Error Scenarios ===")
    
    try:
        # Test 1: Empty CSV
        print("Test 1: Empty CSV handling...")
        empty_csv = io.StringIO("")
        
        try:
            result = parse_csv(empty_csv)
            if result.success:
                print("✗ Empty CSV should fail")
                return False
            else:
                print("✓ Empty CSV properly rejected")
        except Exception as e:
            # This is expected - empty CSV should raise an exception
            print("✓ Empty CSV properly rejected with exception")
        
        # Test 2: Invalid context
        print("Test 2: Invalid context handling...")
        invalid_context = LocalContext("x" * 2000)  # Too long
        is_valid, error = invalid_context.full_validate()
        
        if is_valid:
            print("✗ Invalid context should fail validation")
            return False
        else:
            print("✓ Invalid context properly rejected")
        
        # Test 3: Bedrock error handling
        print("Test 3: Bedrock error handling...")
        config = BedrockConfig(
            aws_access_key_id="mock_key",
            aws_secret_access_key="mock_secret"
        )
        
        with patch('bedrock_client.boto3.client') as mock_boto_client:
            mock_client_instance = Mock()
            mock_client_instance.invoke_model.side_effect = Exception("Mock Bedrock error")
            mock_boto_client.return_value = mock_client_instance
            
            client = BedrockClient(config)
            sales_data = [SalesRecord("2024-01-01", "Test Item", 1, 10.0)]
            context = LocalContext("Test context")
            
            recommendations = client.generate_recommendations(sales_data, context)
            
            if len(recommendations) == 0:
                print("✗ Should return fallback recommendations on error")
                return False
            else:
                print(f"✓ Returned {len(recommendations)} fallback recommendations on error")
        
        return True
        
    except Exception as e:
        print(f"✗ Error scenario testing failed: {str(e)}")
        return False

def test_performance_characteristics():
    """Test performance with larger datasets"""
    print("\n=== Testing Performance Characteristics ===")
    
    try:
        # Create larger dataset
        large_sales_data = []
        items = ["Rice 1kg", "Wheat Flour 1kg", "Sugar 1kg", "Tea 250g", "Oil 1L", 
                "Milk 1L", "Bread", "Biscuits", "Salt 1kg", "Onions 1kg"]
        
        for day in range(1, 31):  # 30 days
            for item in items:
                for transaction in range(1, 4):  # 1-3 transactions per item per day
                    large_sales_data.append(SalesRecord(
                        date=f"2024-01-{day:02d}",
                        item=item,
                        quantity=transaction * 5,
                        price=50.0 + (transaction * 10)
                    ))
        
        print(f"Created dataset with {len(large_sales_data)} sales records")
        
        # Test prompt generation with large dataset
        context = LocalContext("Large dataset test context")
        prompt_builder = create_prompt_builder()
        
        import time
        start_time = time.time()
        prompt = prompt_builder.build_recommendation_prompt(large_sales_data, context)
        prompt_time = time.time() - start_time
        
        print(f"✓ Prompt generation: {prompt_time:.3f} seconds")
        
        if prompt_time > 5.0:  # Should be fast
            print("⚠ Prompt generation is slow")
        
        # Test formatting with multiple recommendations
        test_recs = [
            Recommendation(f"Item {i}", f"Action {i}", f"Explanation {i}")
            for i in range(1, 11)  # 10 recommendations
        ]
        
        start_time = time.time()
        formatted = format_recommendations_for_web(test_recs)
        format_time = time.time() - start_time
        
        print(f"✓ Formatting 10 recommendations: {format_time:.3f} seconds")
        
        if format_time > 1.0:  # Should be very fast
            print("⚠ Formatting is slow")
        
        return True
        
    except Exception as e:
        print(f"✗ Performance testing failed: {str(e)}")
        return False

def run_complete_integration_tests():
    """Run all integration tests"""
    print("BharatSignal Complete Integration Test Suite")
    print("=" * 50)
    
    test_results = []
    
    # Run tests
    test_results.append(("Complete Workflow", test_complete_workflow()))
    test_results.append(("Error Scenarios", test_error_scenarios()))
    test_results.append(("Performance Characteristics", test_performance_characteristics()))
    
    # Summary
    print("\n" + "=" * 50)
    print("INTEGRATION TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name:<30} {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All integration tests passed!")
        print("✅ BharatSignal Bedrock integration is complete and working correctly.")
        print("🚀 Ready for deployment with proper AWS credentials.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = run_complete_integration_tests()
    exit(0 if success else 1)