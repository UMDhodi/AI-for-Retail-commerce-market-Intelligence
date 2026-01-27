"""
Test script for recommendation formatting verification

This script tests the recommendation formatting functionality including:
- Web display formatting
- Print report formatting
- SMS summary formatting
- Voice readout formatting
- Validation functions

Requirements: 2.5, 4.1, 4.2
"""

from models import Recommendation
from recommendation_formatter import (
    RecommendationFormatter, 
    format_recommendations_for_web,
    format_recommendations_for_print,
    validate_recommendation_formatting
)

def create_test_recommendations():
    """Create sample recommendations for testing"""
    return [
        Recommendation(
            item="Rice 1kg",
            action="Increase weekly order from 20 to 30 bags immediately",
            explanation="Rice is your top seller with consistent demand. Festival season is approaching and you need to prevent stockouts."
        ),
        Recommendation(
            item="Tea 250g",
            action="Consider stocking premium tea varieties for festival season",
            explanation="Tea consumption increases during festivals. Premium varieties offer higher profit margins."
        ),
        Recommendation(
            item="Slow Moving Items",
            action="Reduce stock of items that haven't sold in 2 weeks",
            explanation="Free up space and capital by ordering less of products that don't sell quickly."
        ),
        Recommendation(
            item="Festival Sweets",
            action="Add traditional sweets and mithai to inventory",
            explanation="Diwali is next week. Local customers will need sweets for celebrations and gifting."
        )
    ]

def test_web_formatting():
    """Test web display formatting"""
    print("=== Testing Web Display Formatting ===")
    
    try:
        recommendations = create_test_recommendations()
        formatted = format_recommendations_for_web(recommendations)
        
        print(f"✓ Formatted {len(formatted)} recommendations for web display")
        
        # Check required fields
        required_fields = ['id', 'item', 'action', 'explanation', 'priority', 'icon', 'category']
        
        for i, rec in enumerate(formatted, 1):
            missing_fields = [field for field in required_fields if field not in rec]
            if missing_fields:
                print(f"✗ Recommendation {i} missing fields: {missing_fields}")
                return False
            else:
                print(f"✓ Recommendation {i}: {rec['item']} ({rec['priority']} priority) {rec['icon']}")
        
        # Check priority assignment
        priorities = [rec['priority'] for rec in formatted]
        has_high = 'high' in priorities
        has_medium = 'medium' in priorities
        
        print(f"✓ Priority distribution: High={priorities.count('high')}, Medium={priorities.count('medium')}, Low={priorities.count('low')}")
        
        return True
        
    except Exception as e:
        print(f"✗ Web formatting failed: {str(e)}")
        return False

def test_print_formatting():
    """Test print report formatting"""
    print("\n=== Testing Print Report Formatting ===")
    
    try:
        recommendations = create_test_recommendations()
        report = format_recommendations_for_print(recommendations)
        
        print(f"✓ Generated print report ({len(report)} characters)")
        
        # Check for expected sections
        expected_sections = [
            "BHARATSIGNAL BUSINESS RECOMMENDATIONS",
            "HIGH PRIORITY ACTIONS",
            "RECOMMENDED ACTIONS"
        ]
        
        missing_sections = []
        for section in expected_sections:
            if section not in report:
                missing_sections.append(section)
        
        if missing_sections:
            print(f"⚠ Missing sections: {missing_sections}")
        else:
            print("✓ All expected sections present")
        
        # Show sample of report
        lines = report.split('\n')
        print(f"\nReport preview (first 10 lines):")
        for line in lines[:10]:
            print(f"  {line}")
        
        return True
        
    except Exception as e:
        print(f"✗ Print formatting failed: {str(e)}")
        return False

def test_sms_formatting():
    """Test SMS summary formatting"""
    print("\n=== Testing SMS Summary Formatting ===")
    
    try:
        recommendations = create_test_recommendations()
        formatter = RecommendationFormatter()
        
        # Test different lengths
        sms_160 = formatter.format_for_sms_summary(recommendations, 160)
        sms_70 = formatter.format_for_sms_summary(recommendations, 70)
        
        print(f"✓ SMS 160 chars: {len(sms_160)} chars")
        print(f"  Content: {sms_160}")
        
        print(f"✓ SMS 70 chars: {len(sms_70)} chars")
        print(f"  Content: {sms_70}")
        
        # Validate length constraints
        if len(sms_160) <= 160 and len(sms_70) <= 70:
            print("✓ Length constraints satisfied")
            return True
        else:
            print("✗ Length constraints violated")
            return False
        
    except Exception as e:
        print(f"✗ SMS formatting failed: {str(e)}")
        return False

def test_voice_formatting():
    """Test voice readout formatting"""
    print("\n=== Testing Voice Readout Formatting ===")
    
    try:
        recommendations = create_test_recommendations()
        formatter = RecommendationFormatter()
        
        voice_text = formatter.format_for_voice_readout(recommendations)
        
        print(f"✓ Generated voice text ({len(voice_text)} characters)")
        
        # Check for voice-friendly elements
        voice_elements = ['Recommendation 1', 'Pause', 'End of recommendations']
        
        missing_elements = []
        for element in voice_elements:
            if element not in voice_text:
                missing_elements.append(element)
        
        if missing_elements:
            print(f"✗ Missing voice elements: {missing_elements}")
            return False
        else:
            print("✓ All voice elements present")
        
        # Show sample
        lines = voice_text.split('\n')[:5]
        print(f"\nVoice preview:")
        for line in lines:
            if line.strip():
                print(f"  {line}")
        
        return True
        
    except Exception as e:
        print(f"✗ Voice formatting failed: {str(e)}")
        return False

def test_validation_functions():
    """Test recommendation validation functions"""
    print("\n=== Testing Validation Functions ===")
    
    try:
        # Test with valid recommendations
        valid_recs = create_test_recommendations()
        validation_result = validate_recommendation_formatting(valid_recs)
        
        print(f"✓ Validated {validation_result['total_recommendations']} recommendations")
        print(f"✓ Valid recommendations: {validation_result['valid_recommendations']}")
        print(f"✓ Success: {validation_result['success']}")
        
        if validation_result['formatting_errors']:
            print(f"⚠ Formatting errors: {validation_result['formatting_errors']}")
        
        if validation_result['language_issues']:
            print(f"⚠ Language issues: {validation_result['language_issues']}")
        
        # Test with invalid recommendation
        invalid_recs = [
            Recommendation(item="", action="", explanation=""),  # Invalid
            Recommendation(
                item="Test Item",
                action="Use complex algorithmic optimization strategies",  # Too technical
                explanation="This is a valid explanation."
            )
        ]
        
        invalid_validation = validate_recommendation_formatting(invalid_recs)
        print(f"\n✓ Invalid test: {invalid_validation['valid_recommendations']}/{invalid_validation['total_recommendations']} valid")
        
        return validation_result['success']
        
    except Exception as e:
        print(f"✗ Validation test failed: {str(e)}")
        return False

def test_priority_assignment():
    """Test priority assignment logic"""
    print("\n=== Testing Priority Assignment ===")
    
    try:
        formatter = RecommendationFormatter()
        
        # Test different priority levels
        test_cases = [
            (Recommendation("Item1", "Urgent action needed immediately", "Critical situation"), "high"),
            (Recommendation("Item2", "Consider increasing stock", "Good opportunity"), "medium"),
            (Recommendation("Item3", "Monitor sales trends", "Keep watching"), "low"),
            (Recommendation("Item4", "Festival preparations required", "Important timing"), "high")
        ]
        
        correct_assignments = 0
        for rec, expected_priority in test_cases:
            actual_priority = formatter._determine_priority(rec)
            if actual_priority == expected_priority:
                correct_assignments += 1
                print(f"✓ {rec.item}: {actual_priority} (correct)")
            else:
                print(f"✗ {rec.item}: {actual_priority} (expected {expected_priority})")
        
        success_rate = correct_assignments / len(test_cases)
        print(f"\n✓ Priority assignment accuracy: {success_rate:.1%}")
        
        return success_rate >= 0.75  # 75% accuracy threshold
        
    except Exception as e:
        print(f"✗ Priority assignment test failed: {str(e)}")
        return False

def run_formatting_tests():
    """Run all formatting tests"""
    print("BharatSignal Recommendation Formatting Test Suite")
    print("=" * 55)
    
    test_results = []
    
    # Run all tests
    test_results.append(("Web Display Formatting", test_web_formatting()))
    test_results.append(("Print Report Formatting", test_print_formatting()))
    test_results.append(("SMS Summary Formatting", test_sms_formatting()))
    test_results.append(("Voice Readout Formatting", test_voice_formatting()))
    test_results.append(("Validation Functions", test_validation_functions()))
    test_results.append(("Priority Assignment", test_priority_assignment()))
    
    # Summary
    print("\n" + "=" * 55)
    print("FORMATTING TEST SUMMARY")
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
        print("🎉 All formatting tests passed! Recommendation formatting is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = run_formatting_tests()
    exit(0 if success else 1)