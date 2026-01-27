"""
BharatSignal Data Models

This module contains the core data classes for the BharatSignal system:
- SalesRecord: Represents individual sales transactions from CSV data
- LocalContext: Represents local context information (festivals, weather, events)
- Recommendation: Represents AI-generated business recommendations

Requirements: 1.4, 1.5
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import re


@dataclass
class SalesRecord:
    """
    Data class for sales records from CSV files.
    
    Represents individual sales transactions with validation for data integrity.
    
    Attributes:
        date: Transaction date in YYYY-MM-DD format
        item: Product name or description
        quantity: Number of units sold (must be positive)
        price: Price per unit in INR (must be positive)
    """
    date: str
    item: str
    quantity: int
    price: float
    
    def validate(self) -> bool:
        """
        Basic validation for required fields and data integrity.
        
        Returns:
            bool: True if all validation checks pass, False otherwise
        """
        # Check quantity is positive
        if self.quantity <= 0:
            return False
        
        # Check price is positive
        if self.price <= 0:
            return False
        
        # Check item name is not empty
        if not self.item or len(self.item.strip()) == 0:
            return False
        
        # Check date format (basic validation)
        if not self.date or len(self.date.strip()) == 0:
            return False
        
        return True
    
    def validate_date_format(self) -> bool:
        """
        Validate date format is YYYY-MM-DD.
        
        Returns:
            bool: True if date format is valid, False otherwise
        """
        try:
            # Try to parse the date to validate format
            datetime.strptime(self.date, '%Y-%m-%d')
            return True
        except ValueError:
            return False
    
    def validate_item_name(self) -> bool:
        """
        Validate item name contains reasonable characters and length.
        
        Returns:
            bool: True if item name is valid, False otherwise
        """
        if not self.item:
            return False
        
        # Check length (reasonable bounds for product names)
        item_clean = self.item.strip()
        if len(item_clean) < 1 or len(item_clean) > 100:
            return False
        
        # Check for reasonable characters (allow Unicode letters, numbers, spaces, and common punctuation)
        # More permissive pattern for international product names
        # Exclude only control characters and very unusual symbols
        if not re.match(r'^[^\x00-\x1f\x7f-\x9f]+$', item_clean):
            return False
        
        return True
    
    def validate_business_rules(self) -> bool:
        """
        Validate business-specific rules for kirana shop context.
        
        Returns:
            bool: True if business rules are satisfied, False otherwise
        """
        # Reasonable price range for kirana shop items (₹0.50 to ₹10,000)
        if self.price < 0.5 or self.price > 10000:
            return False
        
        # Reasonable quantity range (1 to 1000 units per transaction)
        if self.quantity < 1 or self.quantity > 1000:
            return False
        
        return True
    
    def full_validate(self) -> tuple[bool, Optional[str]]:
        """
        Comprehensive validation with error message.
        
        Returns:
            tuple: (is_valid, error_message)
                is_valid: True if all validations pass
                error_message: Description of validation failure, None if valid
        """
        if not self.validate():
            return False, "Basic validation failed: quantity and price must be positive, item name required"
        
        if not self.validate_date_format():
            return False, f"Invalid date format '{self.date}'. Expected YYYY-MM-DD format"
        
        if not self.validate_item_name():
            return False, f"Invalid item name '{self.item}'. Must be 1-100 characters with standard characters only"
        
        if not self.validate_business_rules():
            return False, f"Business rule violation: price (₹{self.price}) should be ₹0.50-₹10,000, quantity ({self.quantity}) should be 1-1000"
        
        return True, None


@dataclass
class LocalContext:
    """
    Data class for local context information.
    
    Represents manual inputs about festivals, weather, and local events
    that influence business decisions.
    
    Attributes:
        text: Free-form text describing local context
    """
    text: str
    
    def validate(self) -> bool:
        """
        Basic validation for context text.
        
        Returns:
            bool: True if validation passes, False otherwise
        """
        # Allow empty context (optional input)
        if not self.text:
            return True
        
        # Check reasonable length limits
        text_clean = self.text.strip()
        if len(text_clean) > 1000:  # Reasonable limit for context input
            return False
        
        return True
    
    def validate_text_content(self) -> bool:
        """
        Validate text content for reasonable characters and structure.
        
        Returns:
            bool: True if text content is valid, False otherwise
        """
        if not self.text:
            return True  # Empty context is valid
        
        text_clean = self.text.strip()
        
        # Check for minimum meaningful content if provided
        if len(text_clean) > 0 and len(text_clean) < 3:
            return False
        
        # Allow wide range of characters for international context
        # but exclude control characters and excessive special characters
        if any(ord(char) < 32 for char in text_clean if char not in '\n\r\t'):
            return False
        
        return True
    
    def validate_length_limits(self) -> bool:
        """
        Validate text length is within reasonable bounds.
        
        Returns:
            bool: True if length is acceptable, False otherwise
        """
        if not self.text:
            return True
        
        text_clean = self.text.strip()
        
        # Minimum length if provided (avoid single character inputs)
        if len(text_clean) > 0 and len(text_clean) < 3:
            return False
        
        # Maximum length for practical processing
        if len(text_clean) > 1000:
            return False
        
        return True
    
    def full_validate(self) -> tuple[bool, Optional[str]]:
        """
        Comprehensive validation with error message.
        
        Returns:
            tuple: (is_valid, error_message)
                is_valid: True if all validations pass
                error_message: Description of validation failure, None if valid
        """
        if not self.validate():
            return False, "Basic validation failed: context text too long (max 1000 characters)"
        
        if not self.validate_text_content():
            return False, "Invalid text content: contains invalid characters or too short"
        
        if not self.validate_length_limits():
            return False, "Text length invalid: must be 3-1000 characters if provided"
        
        return True, None
    
    def to_prompt_context(self) -> str:
        """
        Convert context to natural language for AI prompt.
        
        Returns:
            str: Formatted context string for AI processing
        """
        if not self.text or len(self.text.strip()) == 0:
            return "Local context: No specific local context provided."
        
        return f"Local context: {self.text.strip()}"
    
    def extract_keywords(self) -> list[str]:
        """
        Extract potential keywords from context for analysis.
        
        Returns:
            list[str]: List of potential keywords found in context
        """
        if not self.text:
            return []
        
        # Simple keyword extraction for festivals, weather, events
        text_lower = self.text.lower()
        keywords = []
        
        # Festival keywords
        festival_terms = ['diwali', 'holi', 'eid', 'christmas', 'dussehra', 'navratri', 'festival', 'celebration']
        for term in festival_terms:
            if term in text_lower:
                keywords.append(f"festival:{term}")
        
        # Weather keywords
        weather_terms = ['rain', 'monsoon', 'hot', 'cold', 'summer', 'winter', 'weather']
        for term in weather_terms:
            if term in text_lower:
                keywords.append(f"weather:{term}")
        
        # Event keywords
        event_terms = ['wedding', 'market', 'fair', 'event', 'holiday', 'school']
        for term in event_terms:
            if term in text_lower:
                keywords.append(f"event:{term}")
        
        return keywords


@dataclass
class Recommendation:
    """
    Data class for AI-generated business recommendations.
    
    Represents structured recommendations with explanations for kirana shop owners.
    
    Attributes:
        item: Product or category the recommendation applies to
        action: Specific action to take
        explanation: Simple language explanation of the reasoning
        confidence: Data source and confidence indicator
    """
    item: str
    action: str
    explanation: str
    confidence: str = ""
    
    def validate(self) -> bool:
        """
        Basic validation for recommendation fields.
        
        Returns:
            bool: True if all fields are present and reasonable, False otherwise
        """
        # Check all fields are present and non-empty
        if not self.item or len(self.item.strip()) == 0:
            return False
        
        if not self.action or len(self.action.strip()) == 0:
            return False
        
        if not self.explanation or len(self.explanation.strip()) == 0:
            return False
        
        # Check reasonable length limits
        if len(self.item.strip()) > 100:
            return False
        
        if len(self.action.strip()) > 200:
            return False
        
        if len(self.explanation.strip()) > 500:
            return False
        
        return True
    
    def validate_language_simplicity(self) -> bool:
        """
        Validate that language is simple and accessible.
        
        Returns:
            bool: True if language appears simple, False if too complex
        """
        # Check for overly technical terms that should be avoided
        technical_terms = [
            'algorithm', 'optimization', 'correlation', 'regression', 'statistical',
            'variance', 'deviation', 'coefficient', 'probability', 'stochastic'
        ]
        
        text_to_check = f"{self.action} {self.explanation}".lower()
        
        for term in technical_terms:
            if term in text_to_check:
                return False
        
        return True
    
    def full_validate(self) -> tuple[bool, Optional[str]]:
        """
        Comprehensive validation with error message.
        
        Returns:
            tuple: (is_valid, error_message)
                is_valid: True if all validations pass
                error_message: Description of validation failure, None if valid
        """
        if not self.validate():
            return False, "Basic validation failed: all fields required with reasonable lengths"
        
        if not self.validate_language_simplicity():
            return False, "Language too technical: recommendations should use simple, accessible language"
        
        return True, None
    
    def to_display_format(self) -> str:
        """
        Format recommendation for display to users.
        
        Returns:
            str: Formatted recommendation string
        """
        display_text = f"{self.item}: {self.action}\nWhy: {self.explanation}"
        if self.confidence:
            display_text += f"\nBased on: {self.confidence}"
        return display_text
    
    def to_structured_dict(self) -> dict:
        """
        Convert recommendation to structured dictionary for API responses.
        
        Returns:
            dict: Structured representation of the recommendation
        """
        return {
            'item': self.item.strip(),
            'action': self.action.strip(),
            'explanation': self.explanation.strip(),
            'confidence': self.confidence.strip() if self.confidence else "",
            'display_text': self.to_display_format()
        }