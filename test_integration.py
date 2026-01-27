"""
Integration tests for BharatSignal data models with CSV processing.

Tests the integration between the models and the main application functions.
"""

import unittest
import io
from models import SalesRecord, LocalContext, Recommendation
from app import parse_csv, validate_csv_row


class TestCSVIntegration(unittest.TestCase):
    """Test CSV processing with enhanced data models."""
    
    def test_valid_csv_parsing(self):
        """Test parsing valid CSV data."""
        csv_content = """date,item,quantity,price
2024-01-15,Rice 1kg,10,45.00
2024-01-15,Biscuits Pack,5,25.00
2024-01-16,Tea 250g,8,120.00"""
        
        # Create file-like object
        csv_file = io.StringIO(csv_content)
        csv_file = io.BytesIO(csv_content.encode('utf-8'))
        
        records = parse_csv(csv_file)
        
        self.assertEqual(len(records), 3)
        self.assertIsInstance(records[0], SalesRecord)
        self.assertEqual(records[0].item, "Rice 1kg")
        self.assertEqual(records[0].quantity, 10)
        self.assertEqual(records[0].price, 45.00)
    
    def test_invalid_csv_data_filtered(self):
        """Test that invalid CSV data is properly filtered out."""
        csv_content = """date,item,quantity,price
2024-01-15,Rice 1kg,10,45.00
invalid-date,Biscuits Pack,5,25.00
2024-01-16,Tea 250g,-8,120.00
2024-01-17,Valid Item,5,30.00"""
        
        csv_file = io.BytesIO(csv_content.encode('utf-8'))
        records = parse_csv(csv_file)
        
        # Should only get valid records (first and last)
        self.assertEqual(len(records), 2)
        self.assertEqual(records[0].item, "Rice 1kg")
        self.assertEqual(records[1].item, "Valid Item")
    
    def test_empty_csv_handling(self):
        """Test handling of empty or header-only CSV."""
        # Empty CSV
        csv_content = ""
        csv_file = io.BytesIO(csv_content.encode('utf-8'))
        records = parse_csv(csv_file)
        self.assertEqual(len(records), 0)
        
        # Header only
        csv_content = "date,item,quantity,price"
        csv_file = io.BytesIO(csv_content.encode('utf-8'))
        records = parse_csv(csv_file)
        self.assertEqual(len(records), 0)
    
    def test_csv_row_validation(self):
        """Test CSV row validation function."""
        # Valid row
        valid_row = {
            'date': '2024-01-15',
            'item': 'Rice 1kg',
            'quantity': '10',
            'price': '45.00'
        }
        self.assertTrue(validate_csv_row(valid_row))
        
        # Missing field
        invalid_row = {
            'date': '2024-01-15',
            'item': 'Rice 1kg',
            'quantity': '10'
            # Missing price
        }
        self.assertFalse(validate_csv_row(invalid_row))
        
        # Invalid numeric field
        invalid_row = {
            'date': '2024-01-15',
            'item': 'Rice 1kg',
            'quantity': 'not-a-number',
            'price': '45.00'
        }
        self.assertFalse(validate_csv_row(invalid_row))


class TestContextIntegration(unittest.TestCase):
    """Test LocalContext integration with application."""
    
    def test_context_prompt_generation(self):
        """Test context conversion to AI prompt format."""
        context = LocalContext("Diwali festival next week, expecting higher sales of sweets and decorations")
        prompt_text = context.to_prompt_context()
        
        self.assertIn("Local context:", prompt_text)
        self.assertIn("Diwali festival", prompt_text)
        self.assertIn("higher sales", prompt_text)
    
    def test_empty_context_handling(self):
        """Test handling of empty context."""
        context = LocalContext("")
        prompt_text = context.to_prompt_context()
        
        self.assertIn("No specific local context provided", prompt_text)
    
    def test_context_keyword_extraction(self):
        """Test keyword extraction for context analysis."""
        context = LocalContext("Monsoon season starting, Ganesh festival in 2 weeks, local school reopening")
        keywords = context.extract_keywords()
        
        # Should extract relevant keywords
        keyword_strings = [kw for kw in keywords]
        self.assertTrue(any("weather" in kw for kw in keyword_strings))
        self.assertTrue(any("festival" in kw for kw in keyword_strings))
        self.assertTrue(any("school" in kw for kw in keyword_strings))


class TestRecommendationIntegration(unittest.TestCase):
    """Test Recommendation integration with application."""
    
    def test_recommendation_display_format(self):
        """Test recommendation formatting for display."""
        rec = Recommendation(
            item="Rice 1kg",
            action="Stock 25% more units for next week",
            explanation="Festival season increases demand for staple foods like rice"
        )
        
        display_text = rec.to_display_format()
        self.assertIn("Rice 1kg:", display_text)
        self.assertIn("Stock 25% more units", display_text)
        self.assertIn("Why:", display_text)
        self.assertIn("Festival season", display_text)
    
    def test_recommendation_structured_output(self):
        """Test recommendation structured dictionary output."""
        rec = Recommendation(
            item="Sweets",
            action="Increase sweet inventory by 50%",
            explanation="Diwali festival creates high demand for traditional sweets"
        )
        
        structured = rec.to_structured_dict()
        self.assertEqual(structured['item'], "Sweets")
        self.assertEqual(structured['action'], "Increase sweet inventory by 50%")
        self.assertIn('display_text', structured)
        self.assertIn('explanation', structured)


if __name__ == '__main__':
    unittest.main()