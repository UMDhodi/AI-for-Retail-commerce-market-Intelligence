#!/usr/bin/env python3
"""
Manual verification test for recommendation quality
Tests that recommendations include clear explanations and simple language
"""

import requests
import json
import re

def test_recommendation_quality():
    """Test that recommendations include clear explanations and use simple language"""
    try:
        # Create test CSV data with realistic kirana shop sales
        csv_data = """date,item,quantity,price
2024-01-15,Rice 1kg,10,45.00
2024-01-15,Tea 250g,5,85.00
2024-01-15,Biscuits Pack,8,25.00
2024-01-16,Rice 1kg,12,45.00
2024-01-16,Sugar 1kg,6,42.00
2024-01-17,Cooking Oil 1L,4,180.00
2024-01-17,Milk 500ml,15,28.00
2024-01-18,Tea 250g,7,85.00
2024-01-19,Onions 1kg,20,30.00
2024-01-20,Rice 1kg,8,45.00"""
        
        # Test context with festival and weather information
        context = """Diwali festival is coming in 2 weeks - expect high demand for sweets, oil, and decorative items.
        
Weather: Heavy monsoon rains for the past week, people buying more tea, biscuits, and indoor snacks.

Local events: Three weddings scheduled in the neighborhood this month."""
        
        files = {'csv_file': ('test_sales.csv', csv_data, 'text/csv')}
        data = {'context': context}
        
        response = requests.post('http://localhost:5000/analyze', files=files, data=data)
        
        if response.status_code != 200:
            print(f"✗ Request failed with status {response.status_code}")
            return False
        
        content = response.text
        print("✓ Successfully generated recommendations")
        
        # Check for recommendation structure
        quality_checks = []
        
        # Check 1: Contains recommendation cards
        if 'recommendation-card' in content:
            quality_checks.append(("Contains recommendation structure", True))
        else:
            quality_checks.append(("Contains recommendation structure", False))
        
        # Check 2: Contains action items
        if 'Action:' in content:
            quality_checks.append(("Contains clear actions", True))
        else:
            quality_checks.append(("Contains clear actions", False))
        
        # Check 3: Contains explanations
        if 'Why:' in content or 'explanation' in content.lower():
            quality_checks.append(("Contains explanations", True))
        else:
            quality_checks.append(("Contains explanations", False))
        
        # Check 4: Avoids technical jargon (basic check)
        technical_terms = ['algorithm', 'regression', 'correlation', 'statistical', 'variance', 'deviation']
        has_jargon = any(term in content.lower() for term in technical_terms)
        quality_checks.append(("Avoids technical jargon", not has_jargon))
        
        # Check 5: References context factors
        context_factors = ['diwali', 'festival', 'rain', 'wedding', 'weather']
        references_context = any(factor in content.lower() for factor in context_factors)
        quality_checks.append(("References local context", references_context))
        
        # Check 6: Contains specific item recommendations
        items = ['rice', 'tea', 'oil', 'sugar', 'milk', 'biscuits']
        mentions_items = any(item in content.lower() for item in items)
        quality_checks.append(("Mentions specific items", mentions_items))
        
        # Print quality assessment
        print("\nRecommendation Quality Assessment:")
        print("-" * 40)
        
        passed_checks = 0
        for check_name, passed in quality_checks:
            status = "✓ PASS" if passed else "✗ FAIL"
            print(f"{check_name}: {status}")
            if passed:
                passed_checks += 1
        
        print(f"\nQuality Score: {passed_checks}/{len(quality_checks)}")
        
        # Extract and display sample recommendations for manual review
        print("\nSample Content for Manual Review:")
        print("-" * 40)
        
        # Try to extract recommendation text (basic parsing)
        lines = content.split('\n')
        in_recommendation = False
        sample_text = []
        
        for line in lines:
            line = line.strip()
            if 'recommendation-card' in line:
                in_recommendation = True
            elif in_recommendation and ('Action:' in line or 'Why:' in line):
                # Clean HTML tags for display
                clean_line = re.sub(r'<[^>]+>', '', line)
                if clean_line.strip():
                    sample_text.append(clean_line.strip())
                if len(sample_text) >= 6:  # Show first few lines
                    break
        
        if sample_text:
            for line in sample_text[:6]:
                print(f"  {line}")
        else:
            print("  Could not extract recommendation text for display")
        
        return passed_checks >= 4  # Pass if at least 4/6 checks pass
        
    except Exception as e:
        print(f"✗ Error testing recommendation quality: {str(e)}")
        return False

def test_language_accessibility():
    """Test that language is simple and accessible"""
    try:
        # Test with minimal context to see basic language patterns
        csv_data = """date,item,quantity,price
2024-01-15,Rice 1kg,5,45.00
2024-01-16,Tea 250g,3,85.00"""
        
        context = "Normal business day, no special events."
        
        files = {'csv_file': ('simple_test.csv', csv_data, 'text/csv')}
        data = {'context': context}
        
        response = requests.post('http://localhost:5000/analyze', files=files, data=data)
        
        if response.status_code != 200:
            print(f"✗ Language test request failed: {response.status_code}")
            return False
        
        content = response.text.lower()
        
        # Check for simple language indicators
        accessibility_checks = []
        
        # Check for complex words that should be avoided
        complex_words = ['optimization', 'methodology', 'implementation', 'sophisticated', 'comprehensive']
        has_complex = any(word in content for word in complex_words)
        accessibility_checks.append(("Avoids complex vocabulary", not has_complex))
        
        # Check for Indian retail context terms
        indian_terms = ['shop', 'store', 'customer', 'business', 'sales', 'stock']
        uses_context_terms = any(term in content for term in indian_terms)
        accessibility_checks.append(("Uses appropriate retail terms", uses_context_terms))
        
        print("\nLanguage Accessibility Assessment:")
        print("-" * 40)
        
        passed = 0
        for check_name, result in accessibility_checks:
            status = "✓ PASS" if result else "✗ FAIL"
            print(f"{check_name}: {status}")
            if result:
                passed += 1
        
        return passed >= 1  # Pass if basic accessibility maintained
        
    except Exception as e:
        print(f"✗ Error testing language accessibility: {str(e)}")
        return False

def main():
    """Run recommendation quality verification"""
    print("BharatSignal Recommendation Quality Verification")
    print("=" * 50)
    
    tests = [
        ("Recommendation Quality", test_recommendation_quality),
        ("Language Accessibility", test_language_accessibility)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\nTesting: {test_name}")
        print("-" * 30)
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "=" * 50)
    print("Verification Summary:")
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name}: {status}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    print(f"\nOverall: {passed}/{total} verifications passed")
    
    if passed == total:
        print("\n✓ All quality checks passed - recommendations meet requirements")
    else:
        print("\n⚠ Some quality checks failed - review recommendations")
    
    return passed == total

if __name__ == "__main__":
    main()