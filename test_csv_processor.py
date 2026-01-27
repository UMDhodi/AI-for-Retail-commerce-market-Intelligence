"""
Tests for CSV processing functionality

Tests the parse_csv function and validation with various CSV formats and edge cases.
Requirements: 1.1, 1.2
"""

import pytest
import io
from csv_processor import (
    parse_csv, 
    CSVProcessingError, 
    validate_csv_headers, 
    parse_csv_row,
    validate_csv_file_format,
    generate_error_report,
    create_sample_csv_data
)
from models import SalesRecord


class TestCSVParsing:
    """Test CSV parsing functionality"""
    
    def test_valid_csv_parsing(self):
        """Test parsing valid CSV data"""
        csv_content = """date,item,quantity,price
2024-01-15,Rice 1kg,10,45.00
2024-01-16,Tea 250g,5,120.00"""
        
        result = parse_csv(io.StringIO(csv_content))
        
        assert result.success
        assert len(result.valid_records) == 2
        assert len(result.errors) == 0
        
        # Check first record
        record1 = result.valid_records[0]
        assert record1.date == "2024-01-15"
        assert record1.item == "Rice 1kg"
        assert record1.quantity == 10
        assert record1.price == 45.00
    
    def test_empty_csv_file(self):
        """Test handling of empty CSV file"""
        with pytest.raises(CSVProcessingError, match="CSV file is empty"):
            parse_csv(io.StringIO(""))
    
    def test_csv_with_only_header(self):
        """Test CSV with only header row"""
        csv_content = "date,item,quantity,price"
        
        with pytest.raises(CSVProcessingError, match="at least a header row and one data row"):
            parse_csv(io.StringIO(csv_content))
    
    def test_missing_required_columns(self):
        """Test CSV missing required columns"""
        csv_content = """date,item,quantity
2024-01-15,Rice 1kg,10"""
        
        with pytest.raises(CSVProcessingError, match="Missing required columns: price"):
            parse_csv(io.StringIO(csv_content))
    
    def test_invalid_numeric_data(self):
        """Test handling of invalid numeric data"""
        csv_content = """date,item,quantity,price
2024-01-15,Rice 1kg,abc,45.00
2024-01-16,Tea 250g,5,xyz"""
        
        result = parse_csv(io.StringIO(csv_content))
        
        assert not result.success
        assert len(result.valid_records) == 0
        assert len(result.errors) == 2
        assert "Invalid quantity 'abc'" in result.errors[0]
        assert "Invalid price 'xyz'" in result.errors[1]
    
    def test_mixed_valid_invalid_rows(self):
        """Test CSV with mix of valid and invalid rows"""
        csv_content = """date,item,quantity,price
2024-01-15,Rice 1kg,10,45.00
2024-01-16,,5,120.00
2024-01-17,Tea 250g,8,100.00"""
        
        result = parse_csv(io.StringIO(csv_content))
        
        assert result.success  # Should succeed if at least one valid record
        assert len(result.valid_records) == 2
        assert len(result.errors) == 1
        assert "Missing item name" in result.errors[0]
    
    def test_business_rule_validation(self):
        """Test business rule validation in CSV processing"""
        csv_content = """date,item,quantity,price
2024-01-15,Rice 1kg,10,45.00
2024-01-16,Expensive Item,5,15000.00
2024-01-17,Tea 250g,0,120.00"""
        
        result = parse_csv(io.StringIO(csv_content))
        
        assert len(result.valid_records) == 1  # Only first record should be valid
        assert len(result.errors) == 2
        assert "Business rule violation" in result.errors[0]
        assert "Basic validation failed" in result.errors[1]  # Zero quantity fails basic validation
    
    def test_whitespace_handling(self):
        """Test handling of whitespace in CSV data"""
        csv_content = """date,item,quantity,price
  2024-01-15  ,  Rice 1kg  ,  10  ,  45.00  
2024-01-16,Tea 250g,5,120.00"""
        
        result = parse_csv(io.StringIO(csv_content))
        
        assert result.success
        assert len(result.valid_records) == 2
        
        # Check whitespace is stripped
        record1 = result.valid_records[0]
        assert record1.date == "2024-01-15"
        assert record1.item == "Rice 1kg"


class TestCSVValidation:
    """Test CSV validation functions"""
    
    def test_validate_csv_headers_valid(self):
        """Test header validation with valid headers"""
        headers = ['date', 'item', 'quantity', 'price']
        required = ['date', 'item', 'quantity', 'price']
        
        missing = validate_csv_headers(headers, required)
        assert missing == []
    
    def test_validate_csv_headers_missing(self):
        """Test header validation with missing headers"""
        headers = ['date', 'item', 'quantity']
        required = ['date', 'item', 'quantity', 'price']
        
        missing = validate_csv_headers(headers, required)
        assert 'price' in missing
    
    def test_validate_csv_headers_case_insensitive(self):
        """Test header validation is case insensitive"""
        headers = ['DATE', 'Item', 'QUANTITY', 'Price']
        required = ['date', 'item', 'quantity', 'price']
        
        missing = validate_csv_headers(headers, required)
        assert missing == []
    
    def test_parse_csv_row_valid(self):
        """Test parsing valid CSV row"""
        row = {
            'date': '2024-01-15',
            'item': 'Rice 1kg',
            'quantity': '10',
            'price': '45.00'
        }
        
        record = parse_csv_row(row, 2)
        
        assert record is not None
        assert record.date == '2024-01-15'
        assert record.item == 'Rice 1kg'
        assert record.quantity == 10
        assert record.price == 45.00
    
    def test_parse_csv_row_empty_row(self):
        """Test parsing empty CSV row"""
        row = {'date': '', 'item': '', 'quantity': '', 'price': ''}
        
        with pytest.raises(ValueError, match="Empty row"):
            parse_csv_row(row, 2)
    
    def test_parse_csv_row_missing_fields(self):
        """Test parsing row with missing fields"""
        row = {
            'date': '2024-01-15',
            'item': '',
            'quantity': '10',
            'price': '45.00'
        }
        
        with pytest.raises(ValueError, match="Missing item name"):
            parse_csv_row(row, 2)


class TestCSVFileFormat:
    """Test CSV file format validation"""
    
    def test_validate_csv_file_format_valid(self):
        """Test validation of valid CSV file format"""
        csv_content = """date,item,quantity,price
2024-01-15,Rice 1kg,10,45.00"""
        
        is_valid, error_msg = validate_csv_file_format(io.StringIO(csv_content))
        
        assert is_valid
        assert error_msg == ""
    
    def test_validate_csv_file_format_empty(self):
        """Test validation of empty file"""
        is_valid, error_msg = validate_csv_file_format(io.StringIO(""))
        
        assert not is_valid
        assert "File is empty" in error_msg
    
    def test_validate_csv_file_format_insufficient_columns(self):
        """Test validation of CSV with insufficient columns"""
        csv_content = """date,item
2024-01-15,Rice 1kg"""
        
        is_valid, error_msg = validate_csv_file_format(io.StringIO(csv_content))
        
        assert not is_valid
        assert "at least 4 columns" in error_msg


class TestErrorReporting:
    """Test error reporting functionality"""
    
    def test_generate_error_report_success(self):
        """Test error report generation for successful processing"""
        csv_content = """date,item,quantity,price
2024-01-15,Rice 1kg,10,45.00"""
        
        result = parse_csv(io.StringIO(csv_content))
        report = generate_error_report(result)
        
        assert "Successfully processed 1 sales records" in report
    
    def test_generate_error_report_with_errors(self):
        """Test error report generation with errors"""
        csv_content = """date,item,quantity,price
2024-01-15,Rice 1kg,abc,45.00"""
        
        result = parse_csv(io.StringIO(csv_content))
        report = generate_error_report(result)
        
        assert "CSV Processing Summary:" in report
        assert "Errors found:" in report
        assert "Expected CSV format:" in report


class TestSampleData:
    """Test sample data generation"""
    
    def test_create_sample_csv_data(self):
        """Test creation of sample CSV data"""
        sample_data = create_sample_csv_data()
        
        assert "date,item,quantity,price" in sample_data
        assert "Rice 1kg" in sample_data
        assert "2024-01-15" in sample_data
        
        # Test that sample data can be parsed
        result = parse_csv(io.StringIO(sample_data))
        assert result.success
        assert len(result.valid_records) > 10  # Should have multiple records


class TestEdgeCases:
    """Test edge cases and error conditions"""
    
    def test_unicode_handling(self):
        """Test handling of Unicode characters in CSV"""
        csv_content = """date,item,quantity,price
2024-01-15,चावल 1kg,10,45.00
2024-01-16,Tea 250g,5,120.00"""
        
        result = parse_csv(io.StringIO(csv_content))
        
        assert result.success
        assert len(result.valid_records) == 2
        assert result.valid_records[0].item == "चावल 1kg"
    
    def test_large_numbers(self):
        """Test handling of large numbers"""
        csv_content = """date,item,quantity,price
2024-01-15,Rice 1kg,999,9999.99"""
        
        result = parse_csv(io.StringIO(csv_content))
        
        assert result.success
        assert len(result.valid_records) == 1
        assert result.valid_records[0].quantity == 999
        assert result.valid_records[0].price == 9999.99
    
    def test_decimal_precision(self):
        """Test handling of decimal precision"""
        csv_content = """date,item,quantity,price
2024-01-15,Rice 1kg,10,45.123456"""
        
        result = parse_csv(io.StringIO(csv_content))
        
        assert result.success
        assert len(result.valid_records) == 1
        assert abs(result.valid_records[0].price - 45.123456) < 0.000001
    
    def test_date_format_validation(self):
        """Test date format validation"""
        csv_content = """date,item,quantity,price
15-01-2024,Rice 1kg,10,45.00
2024/01/16,Tea 250g,5,120.00"""
        
        result = parse_csv(io.StringIO(csv_content))
        
        # Both should fail date format validation
        assert not result.success
        assert len(result.errors) == 2
        assert "Invalid date format" in result.errors[0]
        assert "Invalid date format" in result.errors[1]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])