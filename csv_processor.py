"""
BharatSignal CSV Processing Module

This module provides comprehensive CSV parsing and validation functions for sales data.
Handles malformed CSV data with clear error messages and validates data integrity.

Requirements: 1.1, 1.2
"""

import csv
import io
from typing import List, Tuple, Optional, Dict, Any
from models import SalesRecord
import logging

logger = logging.getLogger(__name__)


class CSVProcessingError(Exception):
    """Custom exception for CSV processing errors"""
    pass


class CSVValidationResult:
    """Result object for CSV validation operations"""
    
    def __init__(self):
        self.valid_records: List[SalesRecord] = []
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.total_rows_processed: int = 0
        self.success: bool = False
    
    def add_error(self, row_num: int, message: str):
        """Add an error message for a specific row"""
        self.errors.append(f"Row {row_num}: {message}")
    
    def add_warning(self, row_num: int, message: str):
        """Add a warning message for a specific row"""
        self.warnings.append(f"Row {row_num}: {message}")
    
    def get_summary(self) -> str:
        """Get a summary of the validation results"""
        return (f"Processed {self.total_rows_processed} rows: "
                f"{len(self.valid_records)} valid, "
                f"{len(self.errors)} errors, "
                f"{len(self.warnings)} warnings")


def parse_csv(file_content) -> CSVValidationResult:
    """
    Parse CSV content into sales records with comprehensive validation.
    
    Args:
        file_content: File-like object or uploaded file content
        
    Returns:
        CSVValidationResult: Object containing valid records, errors, and warnings
        
    Raises:
        CSVProcessingError: For critical parsing failures
    """
    result = CSVValidationResult()
    
    try:
        # Read and decode file content
        if hasattr(file_content, 'read'):
            content = file_content.read()
            if isinstance(content, bytes):
                content = content.decode('utf-8')
        else:
            content = str(file_content)
        
        # Validate basic file structure
        if not content.strip():
            raise CSVProcessingError("CSV file is empty")
        
        lines = content.strip().split('\n')
        if len(lines) < 2:
            raise CSVProcessingError("CSV file must contain at least a header row and one data row")
        
        # Parse CSV with error handling
        csv_reader = csv.DictReader(io.StringIO(content))
        
        # Validate required columns
        required_columns = ['date', 'item', 'quantity', 'price']
        missing_columns = validate_csv_headers(csv_reader.fieldnames, required_columns)
        if missing_columns:
            raise CSVProcessingError(f"Missing required columns: {', '.join(missing_columns)}")
        
        # Process each row
        row_num = 1  # Start at 1 for header
        for row in csv_reader:
            row_num += 1
            result.total_rows_processed += 1
            
            try:
                # Validate and parse row
                record = parse_csv_row(row, row_num)
                if record:
                    result.valid_records.append(record)
                    
            except ValueError as e:
                result.add_error(row_num, str(e))
            except Exception as e:
                result.add_error(row_num, f"Unexpected error: {str(e)}")
        
        # Determine overall success
        result.success = len(result.valid_records) > 0
        
        if not result.success and not result.errors:
            result.add_error(0, "No valid sales records found in CSV file")
        
        logger.info(result.get_summary())
        return result
        
    except CSVProcessingError:
        raise  # Re-raise known errors
    except UnicodeDecodeError:
        raise CSVProcessingError("File encoding error. Please ensure the CSV file is saved in UTF-8 format")
    except Exception as e:
        raise CSVProcessingError(f"Failed to parse CSV file: {str(e)}")


def validate_csv_headers(fieldnames: Optional[List[str]], required_columns: List[str]) -> List[str]:
    """
    Validate that CSV contains all required column headers.
    
    Args:
        fieldnames: List of column names from CSV header
        required_columns: List of required column names
        
    Returns:
        List[str]: Missing column names (empty if all present)
    """
    if not fieldnames:
        return required_columns.copy()
    
    # Normalize column names (strip whitespace, convert to lowercase)
    normalized_fieldnames = [name.strip().lower() for name in fieldnames if name]
    normalized_required = [name.strip().lower() for name in required_columns]
    
    missing = []
    for required_col in normalized_required:
        if required_col not in normalized_fieldnames:
            missing.append(required_col)
    
    return missing


def parse_csv_row(row: Dict[str, str], row_num: int) -> Optional[SalesRecord]:
    """
    Parse a single CSV row into a SalesRecord with validation.
    
    Args:
        row: Dictionary representing a CSV row
        row_num: Row number for error reporting
        
    Returns:
        SalesRecord: Validated sales record, or None if invalid
        
    Raises:
        ValueError: For validation failures with descriptive messages
    """
    # Check for empty row
    if not any(value.strip() for value in row.values() if value):
        raise ValueError("Empty row")
    
    # Extract and validate required fields
    try:
        # Clean and extract fields
        date_str = row.get('date', '').strip()
        item_str = row.get('item', '').strip()
        quantity_str = row.get('quantity', '').strip()
        price_str = row.get('price', '').strip()
        
        # Check for missing fields
        if not date_str:
            raise ValueError("Missing date")
        if not item_str:
            raise ValueError("Missing item name")
        if not quantity_str:
            raise ValueError("Missing quantity")
        if not price_str:
            raise ValueError("Missing price")
        
        # Parse numeric fields with detailed error messages
        try:
            quantity = int(quantity_str)
        except ValueError:
            raise ValueError(f"Invalid quantity '{quantity_str}' - must be a whole number")
        
        try:
            price = float(price_str)
        except ValueError:
            raise ValueError(f"Invalid price '{price_str}' - must be a number")
        
        # Create record
        record = SalesRecord(
            date=date_str,
            item=item_str,
            quantity=quantity,
            price=price
        )
        
        # Comprehensive validation
        is_valid, error_msg = record.full_validate()
        if not is_valid:
            raise ValueError(error_msg)
        
        return record
        
    except ValueError:
        raise  # Re-raise validation errors
    except KeyError as e:
        raise ValueError(f"Missing column: {str(e)}")
    except Exception as e:
        raise ValueError(f"Unexpected error processing row: {str(e)}")


def validate_csv_file_format(file_content) -> Tuple[bool, str]:
    """
    Validate basic CSV file format without full parsing.
    
    Args:
        file_content: File content to validate
        
    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    try:
        # Read content
        if hasattr(file_content, 'read'):
            content = file_content.read()
            if isinstance(content, bytes):
                content = content.decode('utf-8')
            # Reset file pointer if possible
            if hasattr(file_content, 'seek'):
                file_content.seek(0)
        else:
            content = str(file_content)
        
        # Basic format checks
        if not content.strip():
            return False, "File is empty"
        
        lines = content.strip().split('\n')
        if len(lines) < 2:
            return False, "File must contain at least a header row and one data row"
        
        # Check if it looks like CSV
        try:
            csv_reader = csv.reader(io.StringIO(content))
            header = next(csv_reader)
            if len(header) < 4:
                return False, "CSV must have at least 4 columns (date, item, quantity, price)"
        except Exception:
            return False, "File does not appear to be valid CSV format"
        
        return True, ""
        
    except UnicodeDecodeError:
        return False, "File encoding error - please save as UTF-8"
    except Exception as e:
        return False, f"File format validation failed: {str(e)}"


def get_csv_sample_format() -> str:
    """
    Get a sample CSV format string for user guidance.
    
    Returns:
        str: Sample CSV format with headers and example data
    """
    return """date,item,quantity,price
2024-01-15,Rice 1kg,10,45.00
2024-01-15,Biscuits Pack,5,25.00
2024-01-16,Tea 250g,8,120.00"""


def generate_error_report(result: CSVValidationResult) -> str:
    """
    Generate a user-friendly error report from validation results.
    
    Args:
        result: CSV validation result object
        
    Returns:
        str: Formatted error report for display to users
    """
    if result.success and not result.errors:
        return f"✓ Successfully processed {len(result.valid_records)} sales records"
    
    report_lines = []
    
    # Summary
    report_lines.append(f"CSV Processing Summary:")
    report_lines.append(f"- Total rows processed: {result.total_rows_processed}")
    report_lines.append(f"- Valid records: {len(result.valid_records)}")
    report_lines.append(f"- Errors: {len(result.errors)}")
    report_lines.append(f"- Warnings: {len(result.warnings)}")
    report_lines.append("")
    
    # Errors
    if result.errors:
        report_lines.append("Errors found:")
        for error in result.errors[:10]:  # Limit to first 10 errors
            report_lines.append(f"  • {error}")
        if len(result.errors) > 10:
            report_lines.append(f"  ... and {len(result.errors) - 10} more errors")
        report_lines.append("")
    
    # Warnings
    if result.warnings:
        report_lines.append("Warnings:")
        for warning in result.warnings[:5]:  # Limit to first 5 warnings
            report_lines.append(f"  • {warning}")
        if len(result.warnings) > 5:
            report_lines.append(f"  ... and {len(result.warnings) - 5} more warnings")
        report_lines.append("")
    
    # Guidance
    if result.errors:
        report_lines.append("Expected CSV format:")
        report_lines.append(get_csv_sample_format())
    
    return "\n".join(report_lines)


def parse_csv_from_file(file_path_or_handle) -> CSVValidationResult:
    """
    Parse CSV from a file path or file handle.
    
    Args:
        file_path_or_handle: File path string or file handle
        
    Returns:
        CSVValidationResult: Object containing valid records, errors, and warnings
        
    Raises:
        CSVProcessingError: For critical parsing failures
    """
    try:
        if isinstance(file_path_or_handle, str):
            # It's a file path
            with open(file_path_or_handle, 'r', encoding='utf-8') as f:
                return parse_csv(f)
        else:
            # It's a file handle
            return parse_csv(file_path_or_handle)
    except FileNotFoundError:
        raise CSVProcessingError(f"CSV file not found: {file_path_or_handle}")
    except Exception as e:
        raise CSVProcessingError(f"Error reading CSV file: {str(e)}")


def create_sample_csv_data() -> str:
    """
    Create sample CSV data for testing and demonstration.
    
    Returns:
        str: Sample CSV content with realistic kirana shop data
    """
    sample_data = [
        "date,item,quantity,price",
        "2024-01-15,Rice 1kg,10,45.00",
        "2024-01-15,Wheat Flour 1kg,8,35.00",
        "2024-01-15,Sugar 1kg,5,42.00",
        "2024-01-15,Tea 250g,12,120.00",
        "2024-01-15,Biscuits Pack,15,25.00",
        "2024-01-16,Rice 1kg,8,45.00",
        "2024-01-16,Cooking Oil 1L,6,150.00",
        "2024-01-16,Onions 1kg,20,30.00",
        "2024-01-16,Potatoes 1kg,15,25.00",
        "2024-01-16,Tomatoes 1kg,10,40.00",
        "2024-01-17,Milk 1L,25,55.00",
        "2024-01-17,Bread,20,22.00",
        "2024-01-17,Eggs 12pc,8,72.00",
        "2024-01-17,Salt 1kg,3,18.00",
        "2024-01-17,Soap Bar,12,35.00"
    ]
    
    return "\n".join(sample_data)