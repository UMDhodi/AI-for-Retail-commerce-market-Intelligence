"""
Prompt Engineering Module for BharatSignal

This module provides sophisticated prompt templates and building functions
for generating contextually appropriate AI recommendations for kirana shops.
Focuses on Indian retail context and simple language output.

Requirements: 2.1, 2.2, 2.3
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from models import SalesRecord, LocalContext
import logging

logger = logging.getLogger(__name__)


class PromptTemplate:
    """Template class for structured AI prompts"""
    
    def __init__(self, template: str, variables: List[str]):
        self.template = template
        self.variables = variables
    
    def format(self, **kwargs) -> str:
        """Format template with provided variables"""
        missing_vars = [var for var in self.variables if var not in kwargs]
        if missing_vars:
            raise ValueError(f"Missing required variables: {missing_vars}")
        
        return self.template.format(**kwargs)


class KiranaPromptBuilder:
    """
    Specialized prompt builder for kirana shop recommendations.
    
    Handles sales data analysis, context integration, and prompt formatting
    optimized for Claude 3 Sonnet model and Indian retail context.
    """
    
    def __init__(self):
        self.base_template = self._load_base_template()
        self.context_templates = self._load_context_templates()
    
    def build_recommendation_prompt(self, sales_data: List[SalesRecord], context: LocalContext) -> str:
        """
        Build comprehensive prompt for AI recommendation generation.
        
        Args:
            sales_data: Validated sales records
            context: Local context information
            
        Returns:
            str: Formatted prompt optimized for Claude 3 Sonnet
        """
        try:
            # Analyze sales data
            sales_analysis = self._analyze_sales_data(sales_data)
            
            # Process context
            context_analysis = self._analyze_context(context)
            
            # Build prompt sections
            prompt_sections = {
                'system_role': self._build_system_role(),
                'sales_analysis': sales_analysis['formatted_summary'],
                'context_information': context_analysis['formatted_context'],
                'task_instructions': self._build_task_instructions(),
                'format_guidelines': self._build_format_guidelines(),
                'quality_guidelines': self._build_quality_guidelines()
            }
            
            # Combine into final prompt
            final_prompt = self.base_template.format(**prompt_sections)
            
            logger.info(f"Built prompt with {len(sales_data)} sales records and context: {len(context.text)} chars")
            return final_prompt
            
        except Exception as e:
            logger.error(f"Error building prompt: {str(e)}")
            return self._build_fallback_prompt(sales_data, context)
    
    def _load_base_template(self) -> str:
        """Load the base prompt template"""
        return """{system_role}

{sales_analysis}

{context_information}

{task_instructions}

{format_guidelines}

{quality_guidelines}

Generate your recommendations now:"""
    
    def _load_context_templates(self) -> Dict[str, str]:
        """Load context-specific prompt templates"""
        return {
            'festival': "Festival Context: {festival_info} - Consider increased demand for festival-related items and traditional products.",
            'weather': "Weather Context: {weather_info} - Factor in weather-related demand changes for seasonal products.",
            'event': "Local Event Context: {event_info} - Account for special events that may affect customer traffic and product needs.",
            'general': "Local Context: {general_info}"
        }
    
    def _build_system_role(self) -> str:
        """Build system role definition"""
        return """You are BharatSignal, an AI assistant specifically designed for Indian kirana shop owners. 
Your expertise includes:
- Understanding Indian retail market dynamics
- Knowledge of local festivals, seasons, and cultural preferences
- Practical business advice for small family-owned stores
- Simple communication suitable for non-technical business owners

Your role is to provide actionable, practical business recommendations that kirana shop owners can implement immediately to improve their business performance."""
    
    def _analyze_sales_data(self, sales_data: List[SalesRecord]) -> Dict[str, Any]:
        """
        Comprehensive sales data analysis for prompt building.
        
        Args:
            sales_data: List of sales records
            
        Returns:
            Dict containing analysis results and formatted summary
        """
        if not sales_data:
            return {
                'formatted_summary': "SALES DATA: No sales data available for analysis.",
                'items': {},
                'metrics': {}
            }
        
        # Aggregate data by item
        items = {}
        total_revenue = 0
        total_units = 0
        date_range = {'earliest': None, 'latest': None}
        
        for record in sales_data:
            # Item aggregation
            if record.item not in items:
                items[record.item] = {
                    'quantity': 0,
                    'revenue': 0,
                    'transactions': 0,
                    'avg_price': 0,
                    'price_range': {'min': float('inf'), 'max': 0}
                }
            
            item_data = items[record.item]
            item_data['quantity'] += record.quantity
            item_data['revenue'] += record.quantity * record.price
            item_data['transactions'] += 1
            item_data['price_range']['min'] = min(item_data['price_range']['min'], record.price)
            item_data['price_range']['max'] = max(item_data['price_range']['max'], record.price)
            
            total_revenue += record.quantity * record.price
            total_units += record.quantity
            
            # Date range tracking
            try:
                record_date = datetime.strptime(record.date, '%Y-%m-%d')
                if date_range['earliest'] is None or record_date < date_range['earliest']:
                    date_range['earliest'] = record_date
                if date_range['latest'] is None or record_date > date_range['latest']:
                    date_range['latest'] = record_date
            except ValueError:
                pass  # Skip invalid dates
        
        # Calculate averages and performance metrics
        for item in items:
            if items[item]['quantity'] > 0:
                items[item]['avg_price'] = items[item]['revenue'] / items[item]['quantity']
        
        # Sort items by performance
        sorted_by_revenue = sorted(items.items(), key=lambda x: x[1]['revenue'], reverse=True)
        sorted_by_quantity = sorted(items.items(), key=lambda x: x[1]['quantity'], reverse=True)
        
        # Calculate business insights
        avg_transaction_value = total_revenue / len(sales_data) if sales_data else 0
        unique_items = len(items)
        
        # Build formatted summary
        summary_lines = [
            "SALES DATA ANALYSIS:",
            f"Period: {date_range['earliest'].strftime('%Y-%m-%d') if date_range['earliest'] else 'Unknown'} to {date_range['latest'].strftime('%Y-%m-%d') if date_range['latest'] else 'Unknown'}",
            f"Total Revenue: ₹{total_revenue:.2f} from {len(sales_data)} transactions",
            f"Total Units Sold: {total_units} across {unique_items} different products",
            "",
            "EXACT ITEM PERFORMANCE (USE THESE NAMES):"
        ]
        
        # Add detailed item performance with exact names
        for i, (item, data) in enumerate(sorted_by_revenue[:10], 1):
            revenue_percentage = (data['revenue'] / total_revenue * 100) if total_revenue > 0 else 0
            summary_lines.append(
                f"{i}. {item}: {data['quantity']} units sold, ₹{data['revenue']:.2f} revenue ({revenue_percentage:.1f}% of total), "
                f"₹{data['avg_price']:.2f} avg price, {data['transactions']} transactions"
            )
        
        # Add performance categories for easy reference
        if len(sorted_by_revenue) >= 3:
            top_performers = [item for item, _ in sorted_by_revenue[:3]]
            bottom_performers = [item for item, _ in sorted_by_revenue[-3:]]
            
            summary_lines.extend([
                "",
                f"TOP PERFORMERS (stock more): {', '.join(top_performers)}",
                f"POOR PERFORMERS (reduce stock): {', '.join(bottom_performers)}"
            ])
        
        return {
            'formatted_summary': '\n'.join(summary_lines),
            'items': items,
            'metrics': {
                'total_revenue': total_revenue,
                'total_units': total_units,
                'avg_transaction_value': avg_transaction_value,
                'unique_items': unique_items,
                'date_range': date_range
            },
            'sorted_by_revenue': sorted_by_revenue,
            'sorted_by_quantity': sorted_by_quantity
        }
    
    def _analyze_context(self, context: LocalContext) -> Dict[str, Any]:
        """
        Analyze and format local context for prompt inclusion.
        
        Args:
            context: Local context object
            
        Returns:
            Dict containing context analysis and formatted text
        """
        if not context.text or len(context.text.strip()) == 0:
            return {
                'formatted_context': "CONTEXT INFORMATION:\nNo specific local context provided.",
                'keywords': [],
                'context_type': 'none'
            }
        
        # Extract keywords and determine context type
        keywords = context.extract_keywords()
        context_type = self._determine_context_type(keywords, context.text)
        
        # Format context based on type
        formatted_context = self._format_context_by_type(context, context_type, keywords)
        
        return {
            'formatted_context': formatted_context,
            'keywords': keywords,
            'context_type': context_type
        }
    
    def _determine_context_type(self, keywords: List[str], text: str) -> str:
        """Determine the primary type of context provided"""
        text_lower = text.lower()
        
        # Check for festival context
        if any('festival:' in kw for kw in keywords) or any(term in text_lower for term in ['festival', 'diwali', 'holi', 'eid', 'celebration']):
            return 'festival'
        
        # Check for weather context
        if any('weather:' in kw for kw in keywords) or any(term in text_lower for term in ['weather', 'rain', 'monsoon', 'hot', 'cold']):
            return 'weather'
        
        # Check for event context
        if any('event:' in kw for kw in keywords) or any(term in text_lower for term in ['event', 'wedding', 'market', 'fair']):
            return 'event'
        
        return 'general'
    
    def _format_context_by_type(self, context: LocalContext, context_type: str, keywords: List[str]) -> str:
        """Format context information based on its type"""
        base_text = f"CONTEXT INFORMATION:\n{context.text.strip()}"
        
        if context_type == 'festival':
            return f"{base_text}\n\nFESTIVAL CONSIDERATIONS:\n- Increased demand for traditional items, sweets, and decorative products\n- Higher customer traffic and bulk purchases\n- Opportunity for premium pricing on festival-specific items"
        
        elif context_type == 'weather':
            return f"{base_text}\n\nWEATHER CONSIDERATIONS:\n- Seasonal demand changes for beverages, food items, and household products\n- Weather-related shopping patterns and customer preferences\n- Opportunity to stock weather-appropriate items"
        
        elif context_type == 'event':
            return f"{base_text}\n\nEVENT CONSIDERATIONS:\n- Special occasion demand for specific products\n- Potential for increased customer traffic\n- Opportunity to cater to event-specific needs"
        
        else:
            return base_text
    
    def _build_task_instructions(self) -> str:
        """Build detailed task instructions"""
        return """TASK: Generate 3-5 specific, actionable recommendations for this kirana shop owner. 

MANDATORY REQUIREMENTS FOR EACH RECOMMENDATION:
1. MUST use EXACT ITEM NAMES from sales data (e.g., "Rice 1kg", "Tea 250g")
2. MUST include SPECIFIC NUMBERS (e.g., "order 25 more bags", "increase by 40%")
3. MUST reference CONTEXT (festivals, weather, events, dates)
4. MUST reference SALES DATA (e.g., "sold 45 units last week")
5. MUST be actionable TODAY

RECOMMENDATION CATEGORIES:

1. STOCK MORE OF THESE ITEMS:
   - Name the exact item from sales data
   - Give specific quantity increase
   - Reference sales performance AND context
   - Example: "Rice 1kg: Order 30 bags instead of 20 (50% increase) because you sold 45 units last week and Diwali festival starts in 10 days"

2. REDUCE STOCK FOR THESE ITEMS:
   - Name the exact slow-moving item
   - Give specific quantity reduction
   - Reference poor sales AND context
   - Example: "Biscuit Pack: Reduce weekly order from 20 to 12 packs (40% reduction) because only 3 sold last week and monsoon reduces snack demand"

3. PRICING OPPORTUNITIES:
   - Name specific items for price changes
   - Give exact price amounts
   - Reference demand AND context
   - Example: "Cooking Oil 1L: Increase price from ₹150 to ₹160 because you sold 25 bottles last week and Diwali cooking will increase demand"

VALIDATION CHECKLIST FOR EACH RECOMMENDATION:
✓ Contains exact item name from sales data?
✓ Contains specific number/quantity/percentage?
✓ References festival/weather/event/date?
✓ References actual sales performance?
✓ Actionable today?
✓ No generic phrases?"""
    
    def _build_format_guidelines(self) -> str:
        """Build response format guidelines"""
        return """RESPONSE FORMAT:
For each recommendation, use this EXACT format:

ITEM: [specific item name from sales data - e.g., "Rice 1kg", "Tea 250g"]
ACTION: [specific action with quantities - e.g., "Increase weekly order from 20 to 30 bags"]
EXPLANATION: [simple 1-2 sentence explanation referencing sales data and context]
CONFIDENCE: [data source - e.g., "Based on: last 14 days sales + festival context (Diwali)"]

Example:
ITEM: Rice 1kg
ACTION: Increase weekly order from 20 to 30 bags (50% increase)
EXPLANATION: Rice is your top seller with 45 units sold last week. Diwali festival will increase demand for staple foods.
CONFIDENCE: Based on: 14 days sales data + festival context (Diwali)

MANDATORY RULES:
- Always use actual item names from the sales data
- Always include specific numbers (quantities, percentages, prices)
- Always reference the context provided (festivals, weather, events)
- Always explain which data points support the recommendation"""
    
    def _build_quality_guidelines(self) -> str:
        """Build quality and language guidelines"""
        return """CRITICAL RULES (MUST FOLLOW):
- Do NOT give generic advice
- Do NOT say "best practices", "generally", or "consider"
- Every recommendation MUST mention a specific product name from the data
- Every recommendation MUST reference a festival, date, or quantity
- If data is insufficient, say "Data is limited" and reduce confidence
- Answer as if the shop owner will act today

LANGUAGE REQUIREMENTS:
- Use simple English suitable for small business owners
- Avoid technical jargon, statistics, or complex business terms
- Provide specific numbers when suggesting quantities or prices
- Reference actual data from the sales analysis
- Consider Indian retail context and local factors
- Focus on immediate, practical actions the owner can take today
- Make recommendations that are realistic for a small kirana shop

FORBIDDEN PHRASES:
- "Best practices suggest..."
- "Generally speaking..."
- "You should consider..."
- "It might be good to..."
- "Typically..."
- "Usually..."
- "In general..."

REQUIRED ELEMENTS PER RECOMMENDATION:
1. Specific item name (e.g., "Rice 1kg", not "staple items")
2. Exact quantity or percentage (e.g., "increase by 15 bags", not "increase stock")
3. Context reference (e.g., "for Diwali festival", "due to monsoon")
4. Sales data reference (e.g., "sold 45 units last week")"""
    
    def _build_fallback_prompt(self, sales_data: List[SalesRecord], context: LocalContext) -> str:
        """Build a simple fallback prompt when main prompt building fails"""
        item_count = len(set(record.item for record in sales_data)) if sales_data else 0
        total_revenue = sum(record.quantity * record.price for record in sales_data) if sales_data else 0
        
        # Get specific item names for fallback
        item_names = list(set(record.item for record in sales_data))[:5] if sales_data else []
        
        return f"""You are BharatSignal, an AI assistant for Indian kirana shop owners.

CRITICAL RULES - MUST FOLLOW:
- Do NOT give generic advice
- MUST mention specific item names: {', '.join(item_names) if item_names else 'No items available'}
- MUST include exact quantities or percentages
- MUST reference context: {context.text if context.text else 'No context provided'}

Sales Summary: {len(sales_data)} transactions, {item_count} different items, ₹{total_revenue:.2f} total revenue.

Generate 3-4 recommendations using this EXACT format:

ITEM: [exact item name from list above]
ACTION: [specific action with numbers - e.g., "Order 25 bags instead of 15"]
EXPLANATION: [reference sales data AND context]
CONFIDENCE: [Based on: sales data + context factors]

FORBIDDEN: Do not use "consider", "generally", "best practices", or generic advice."""


def create_prompt_builder() -> KiranaPromptBuilder:
    """Factory function to create prompt builder instance"""
    return KiranaPromptBuilder()


def test_prompt_generation(sales_data: List[SalesRecord], context: LocalContext) -> str:
    """Test function for prompt generation"""
    try:
        builder = create_prompt_builder()
        prompt = builder.build_recommendation_prompt(sales_data, context)
        return prompt
    except Exception as e:
        logger.error(f"Prompt generation test failed: {str(e)}")
        return f"Error: {str(e)}"