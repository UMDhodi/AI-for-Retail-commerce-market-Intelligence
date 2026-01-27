"""
Unit tests for BharatSignal data models.

Tests the SalesRecord, LocalContext, and Recommendation data classes
for proper validation and functionality.
"""

import unittest
from models import SalesRecord, LocalContext, Recommendation


class TestSalesRecord(unittest.TestCase):
    """Test cases for SalesRecord data class."""
    
    def test_valid_sales_record(self):
        """Test creation and validation of valid sales record."""
        record = SalesRecord(
            date="2024-01-15",
            item="Rice 1kg",
            quantity=10,
            price=45.00
        )
        
        self.assertTrue(record.validate())
        self.assertTrue(record.validate_date_format())
        self.assertTrue(record.validate_item_name())
        self.assertTrue(record.validate_business_rules())
        
        is_valid, error = record.full_validate()
        self.assertTrue(is_valid)
        self.assertIsNone(error)
    
    def test_invalid_quantity(self):
        """Test validation fails for invalid quantities."""
        # Zero quantity
        record = SalesRecord("2024-01-15", "Rice 1kg", 0, 45.00)
        self.assertFalse(record.validate())
        
        # Negative quantity
        record = SalesRecord("2024-01-15", "Rice 1kg", -5, 45.00)
        self.assertFalse(record.validate())
        
        # Excessive quantity
        record = SalesRecord("2024-01-15", "Rice 1kg", 2000, 45.00)
        self.assertFalse(record.validate_business_rules())
    
    def test_invalid_price(self):
        """Test validation fails for invalid prices."""
        # Zero price
        record = SalesRecord("2024-01-15", "Rice 1kg", 10, 0.0)
        self.assertFalse(record.validate())
        
        # Negative price
        record = SalesRecord("2024-01-15", "Rice 1kg", 10, -45.00)
        self.assertFalse(record.validate())
        
        # Excessive price
        record = SalesRecord("2024-01-15", "Rice 1kg", 10, 50000.00)
        self.assertFalse(record.validate_business_rules())
    
    def test_invalid_item_name(self):
        """Test validation fails for invalid item names."""
        # Empty item name
        record = SalesRecord("2024-01-15", "", 10, 45.00)
        self.assertFalse(record.validate())
        
        # Whitespace only
        record = SalesRecord("2024-01-15", "   ", 10, 45.00)
        self.assertFalse(record.validate())
        
        # Too long item name
        long_name = "x" * 150
        record = SalesRecord("2024-01-15", long_name, 10, 45.00)
        self.assertFalse(record.validate_item_name())
    
    def test_invalid_date_format(self):
        """Test validation fails for invalid date formats."""
        # Invalid date format
        record = SalesRecord("15-01-2024", "Rice 1kg", 10, 45.00)
        self.assertFalse(record.validate_date_format())
        
        # Invalid date
        record = SalesRecord("2024-13-45", "Rice 1kg", 10, 45.00)
        self.assertFalse(record.validate_date_format())
        
        # Empty date
        record = SalesRecord("", "Rice 1kg", 10, 45.00)
        self.assertFalse(record.validate())
    
    def test_full_validate_with_errors(self):
        """Test full validation returns appropriate error messages."""
        # Invalid date format
        record = SalesRecord("invalid-date", "Rice 1kg", 10, 45.00)
        is_valid, error = record.full_validate()
        self.assertFalse(is_valid)
        self.assertIn("Invalid date format", error)
        
        # Business rule violation
        record = SalesRecord("2024-01-15", "Rice 1kg", 2000, 45.00)
        is_valid, error = record.full_validate()
        self.assertFalse(is_valid)
        self.assertIn("Business rule violation", error)


class TestLocalContext(unittest.TestCase):
    """Test cases for LocalContext data class."""
    
    def test_valid_context(self):
        """Test creation and validation of valid context."""
        context = LocalContext("Diwali festival next week, expecting higher sales")
        
        self.assertTrue(context.validate())
        self.assertTrue(context.validate_text_content())
        self.assertTrue(context.validate_length_limits())
        
        is_valid, error = context.full_validate()
        self.assertTrue(is_valid)
        self.assertIsNone(error)
    
    def test_empty_context(self):
        """Test empty context is valid."""
        context = LocalContext("")
        self.assertTrue(context.validate())
        
        context = LocalContext("   ")
        self.assertTrue(context.validate())
    
    def test_context_too_long(self):
        """Test validation fails for overly long context."""
        long_text = "x" * 1500
        context = LocalContext(long_text)
        self.assertFalse(context.validate())
        
        is_valid, error = context.full_validate()
        self.assertFalse(is_valid)
        self.assertIn("too long", error)
    
    def test_context_too_short(self):
        """Test validation fails for too short meaningful context."""
        context = LocalContext("hi")
        self.assertFalse(context.validate_text_content())
        
        is_valid, error = context.full_validate()
        self.assertFalse(is_valid)
        self.assertIn("too short", error)
    
    def test_to_prompt_context(self):
        """Test conversion to prompt context format."""
        context = LocalContext("Diwali festival next week")
        prompt = context.to_prompt_context()
        self.assertIn("Local context:", prompt)
        self.assertIn("Diwali festival next week", prompt)
        
        # Empty context
        empty_context = LocalContext("")
        prompt = empty_context.to_prompt_context()
        self.assertIn("No specific local context provided", prompt)
    
    def test_extract_keywords(self):
        """Test keyword extraction from context."""
        context = LocalContext("Diwali festival next week, monsoon rains expected, wedding season")
        keywords = context.extract_keywords()
        
        self.assertIn("festival:diwali", keywords)
        self.assertIn("weather:rain", keywords)
        self.assertIn("event:wedding", keywords)
        
        # Empty context
        empty_context = LocalContext("")
        keywords = empty_context.extract_keywords()
        self.assertEqual(keywords, [])


class TestRecommendation(unittest.TestCase):
    """Test cases for Recommendation data class."""
    
    def test_valid_recommendation(self):
        """Test creation and validation of valid recommendation."""
        rec = Recommendation(
            item="Rice 1kg",
            action="Stock 20% more units",
            explanation="Sales increased during festival season and demand is expected to continue"
        )
        
        self.assertTrue(rec.validate())
        self.assertTrue(rec.validate_language_simplicity())
        
        is_valid, error = rec.full_validate()
        self.assertTrue(is_valid)
        self.assertIsNone(error)
    
    def test_empty_fields(self):
        """Test validation fails for empty fields."""
        # Empty item
        rec = Recommendation("", "Stock more", "Good sales")
        self.assertFalse(rec.validate())
        
        # Empty action
        rec = Recommendation("Rice", "", "Good sales")
        self.assertFalse(rec.validate())
        
        # Empty explanation
        rec = Recommendation("Rice", "Stock more", "")
        self.assertFalse(rec.validate())
    
    def test_fields_too_long(self):
        """Test validation fails for overly long fields."""
        # Long item name
        long_item = "x" * 150
        rec = Recommendation(long_item, "Stock more", "Good sales")
        self.assertFalse(rec.validate())
        
        # Long action
        long_action = "x" * 250
        rec = Recommendation("Rice", long_action, "Good sales")
        self.assertFalse(rec.validate())
        
        # Long explanation
        long_explanation = "x" * 600
        rec = Recommendation("Rice", "Stock more", long_explanation)
        self.assertFalse(rec.validate())
    
    def test_technical_language_detection(self):
        """Test detection of overly technical language."""
        rec = Recommendation(
            item="Rice",
            action="Optimize inventory using statistical regression analysis",
            explanation="The correlation coefficient indicates significant variance"
        )
        self.assertFalse(rec.validate_language_simplicity())
        
        is_valid, error = rec.full_validate()
        self.assertFalse(is_valid)
        self.assertIn("too technical", error)
    
    def test_to_display_format(self):
        """Test formatting for display."""
        rec = Recommendation(
            item="Rice 1kg",
            action="Stock 20% more units",
            explanation="Higher demand expected"
        )
        
        display = rec.to_display_format()
        self.assertIn("Rice 1kg:", display)
        self.assertIn("Stock 20% more units", display)
        self.assertIn("Why:", display)
        self.assertIn("Higher demand expected", display)
    
    def test_to_structured_dict(self):
        """Test conversion to structured dictionary."""
        rec = Recommendation(
            item="Rice 1kg",
            action="Stock 20% more units",
            explanation="Higher demand expected"
        )
        
        result = rec.to_structured_dict()
        self.assertEqual(result['item'], "Rice 1kg")
        self.assertEqual(result['action'], "Stock 20% more units")
        self.assertEqual(result['explanation'], "Higher demand expected")
        self.assertIn('display_text', result)


if __name__ == '__main__':
    unittest.main()