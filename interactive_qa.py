"""
Interactive Q&A Module for BharatSignal

This module provides direct question-answering capabilities for kirana shop owners,
allowing them to ask specific questions about their business and get AI-powered
answers based on their sales data and local context.

CRITICAL: This module MUST analyze the exact items mentioned in user questions
and provide item-specific, data-driven recommendations.
"""

from typing import List, Dict, Any, Optional
from models import SalesRecord, LocalContext
from bedrock_client import BedrockClient, BedrockClientError
import logging
import re
import json

logger = logging.getLogger(__name__)


class InteractiveQASystem:
    """
    Interactive Q&A system for BharatSignal that answers specific shop owner questions
    using their sales data and local context.
    
    CRITICAL RULES:
    1. ITEM OVERRIDE: If user mentions specific item, analyze ONLY that item
    2. QUESTION-DRIVEN: Every answer tied to current active question
    3. DYNAMIC SUGGESTIONS: Generate fresh follow-up questions each time
    """
    
    def __init__(self, bedrock_client: BedrockClient):
        self.bedrock_client = bedrock_client
    
    def answer_question(self, 
                       user_question: str, 
                       sales_data: List[SalesRecord], 
                       context: LocalContext) -> Dict[str, Any]:
        """
        Answer a specific business question from the shop owner using their data.
        
        CRITICAL: Must analyze exact items mentioned in question, not default to top sellers.
        """
        try:
            # STEP 1: Extract item(s) mentioned in question
            mentioned_items = self._extract_items_from_question(user_question)
            
            # STEP 2: Extract intent from question
            intent = self._extract_intent_from_question(user_question)
            
            # STEP 3: Filter sales data to relevant items only
            if mentioned_items:
                relevant_sales = self._filter_sales_by_items(sales_data, mentioned_items)
                primary_item = mentioned_items[0]  # Focus on first mentioned item
                
                # CRITICAL: If no sales data found for mentioned item, be explicit
                if not relevant_sales:
                    return {
                        'success': True,
                        'question': user_question,
                        'answer': {
                            "answer_to": user_question,
                            "primary_decision": {
                                "decision": f"CAUTION - No recent sales data found for {primary_item}",
                                "item": primary_item,
                                "recent_sales_summary": [f"No {primary_item} transactions found in recent data"],
                                "action": f"Monitor {primary_item} demand and start with small stock (5-10 units)",
                                "why": f"Without recent {primary_item} sales data, conservative approach is safest",
                                "confidence": "Low (no sales data for this item)",
                                "based_on": ["Limited data available", "Conservative business practices"]
                            },
                            "supporting_signals": [f"No recent {primary_item} sales recorded"],
                            "risk_and_safety": [f"Start with minimal {primary_item} stock", "Monitor customer demand closely"],
                            "suggested_questions": [
                                f"What items are selling well instead of {primary_item}?",
                                "Should I focus on my top-selling items?",
                                "Tell me about my stock"
                            ]
                        },
                        'data_days': 0
                    }
            else:
                # No specific item mentioned - use all data for analysis
                relevant_sales = sales_data
                if intent == 'stock_overview':
                    primary_item = "Stock Overview"
                else:
                    # Find the actual top-selling item from the data
                    if sales_data:
                        item_totals = {}
                        for record in sales_data:
                            if record.item not in item_totals:
                                item_totals[record.item] = 0
                            item_totals[record.item] += record.quantity
                        
                        primary_item = max(item_totals.items(), key=lambda x: x[1])[0]
                        logger.info(f"No specific item mentioned, using top seller: {primary_item}")
                    else:
                        primary_item = "No Data Available"
            
            # STEP 4: Analyze sales data based on intent and items
            if intent == 'stock_overview':
                # For stock overview, analyze all data
                sales_analysis = self._analyze_item_sales(sales_data, "All Items")
                sales_analysis['raw_sales_data'] = sales_data
                primary_item = "Stock Overview"
            elif intent == 'top_selling_analysis':
                # Analyze top selling items
                top_analysis = self._analyze_top_selling_items(sales_data, 3)
                sales_analysis = {
                    "summary_points": top_analysis["summary_points"],
                    "key_signals": top_analysis["key_signals"],
                    "raw_sales_data": sales_data,
                    "days_of_data": top_analysis["days_of_data"],
                    "trend": top_analysis["trend"],
                    "avg_daily": top_analysis["avg_daily"]
                }
                primary_item = "Top Selling Items"
            elif intent == 'slow_selling_analysis':
                # Analyze slow selling items
                slow_analysis = self._analyze_slow_selling_items(sales_data, 3)
                sales_analysis = {
                    "summary_points": slow_analysis["summary_points"],
                    "key_signals": slow_analysis["key_signals"],
                    "raw_sales_data": sales_data,
                    "days_of_data": slow_analysis["days_of_data"],
                    "trend": slow_analysis["trend"],
                    "avg_daily": slow_analysis["avg_daily"]
                }
                primary_item = "Slow Selling Items"
            elif intent == 'focus_analysis':
                # Should I focus on top selling items?
                top_analysis = self._analyze_top_selling_items(sales_data, 3)
                sales_analysis = {
                    "summary_points": top_analysis["summary_points"],
                    "key_signals": ["Focus recommendation based on top performers"] + top_analysis["key_signals"],
                    "raw_sales_data": sales_data,
                    "days_of_data": top_analysis["days_of_data"],
                    "trend": top_analysis["trend"],
                    "avg_daily": top_analysis["avg_daily"]
                }
                primary_item = "Focus Strategy"
            elif intent == 'cash_saving_analysis':
                # What should I reduce to save cash?
                slow_analysis = self._analyze_slow_selling_items(sales_data, 3)
                sales_analysis = {
                    "summary_points": ["Items to consider reducing for cash flow:"] + slow_analysis["summary_points"][1:],
                    "key_signals": ["Cash saving recommendations"] + slow_analysis["key_signals"],
                    "raw_sales_data": sales_data,
                    "days_of_data": slow_analysis["days_of_data"],
                    "trend": slow_analysis["trend"],
                    "avg_daily": slow_analysis["avg_daily"]
                }
                primary_item = "Cash Saving Strategy"
            elif intent == 'specific_item_analysis' and mentioned_items:
                # Specific item analysis - "Tell me about Rice"
                item_analysis = self._analyze_specific_item_details(sales_data, mentioned_items[0])
                if not item_analysis['item_found']:
                    # Item not found in data
                    return {
                        'success': True,
                        'question': user_question,
                        'answer': {
                            "answer_to": user_question,
                            "primary_decision": {
                                "decision": f"NO DATA - {mentioned_items[0]} not found in your sales data",
                                "item": mentioned_items[0],
                                "recent_sales_summary": [f"No sales records found for '{mentioned_items[0]}' in uploaded CSV"],
                                "action": f"Check if '{mentioned_items[0]}' is spelled correctly or add sales data for this item",
                                "why": f"Your uploaded CSV file doesn't contain any sales records for '{mentioned_items[0]}'",
                                "confidence": "High (data verification)",
                                "based_on": ["Uploaded CSV file analysis", "Complete data search"]
                            },
                            "supporting_signals": [f"Searched all {len(sales_data)} sales records", "No matching items found"],
                            "risk_and_safety": ["Verify item name spelling", "Check if item was sold during the data period", "Add sales data for this item if needed"],
                            "suggested_questions": [
                                "What items do I actually have in my data?",
                                "Show me my top selling items",
                                "Tell me about my stock"
                            ]
                        },
                        'data_days': 0
                    }
                else:
                    sales_analysis = item_analysis
                    primary_item = mentioned_items[0]
            elif mentioned_items:
                # Specific item(s) mentioned
                if len(mentioned_items) == 1:
                    # Single item analysis
                    item_analysis = self._analyze_specific_item_details(sales_data, mentioned_items[0])
                    if not item_analysis['item_found']:
                        # Item not found in data
                        return {
                            'success': True,
                            'question': user_question,
                            'answer': {
                                "answer_to": user_question,
                                "primary_decision": {
                                    "decision": f"NO DATA - {mentioned_items[0]} not found in your sales data",
                                    "item": mentioned_items[0],
                                    "recent_sales_summary": [f"No sales records found for '{mentioned_items[0]}' in uploaded CSV"],
                                    "action": f"Check if '{mentioned_items[0]}' is spelled correctly or add sales data for this item",
                                    "why": f"Your uploaded CSV file doesn't contain any sales records for '{mentioned_items[0]}'",
                                    "confidence": "High (data verification)",
                                    "based_on": ["Uploaded CSV file analysis", "Complete data search"]
                                },
                                "supporting_signals": [f"Searched all {len(sales_data)} sales records", "No matching items found"],
                                "risk_and_safety": ["Verify item name spelling", "Check if item was sold during the data period", "Add sales data for this item if needed"],
                                "suggested_questions": [
                                    "What items do I actually have in my data?",
                                    "Show me my top selling items",
                                    "Tell me about my stock"
                                ]
                            },
                            'data_days': 0
                        }
                    else:
                        sales_analysis = item_analysis
                        primary_item = mentioned_items[0]
                else:
                    # Multiple items analysis
                    multi_analysis = self._analyze_multiple_items(sales_data, mentioned_items)
                    sales_analysis = multi_analysis
                    primary_item = f"{len(mentioned_items)} Items Comparison"
            elif intent == 'general_analysis':
                # For general analysis, find the top-selling item and analyze it
                if sales_data:
                    # Calculate top item by total quantity
                    item_totals = {}
                    for record in sales_data:
                        if record.item not in item_totals:
                            item_totals[record.item] = 0
                        item_totals[record.item] += record.quantity
                    
                    top_item_name = max(item_totals.items(), key=lambda x: x[1])[0]
                    logger.info(f"General analysis: Top item is {top_item_name} with {item_totals[top_item_name]} total units")
                    
                    # Filter sales data for the top item
                    top_item_sales = [record for record in sales_data if record.item == top_item_name]
                    sales_analysis = self._analyze_item_sales(top_item_sales, top_item_name)
                    sales_analysis['raw_sales_data'] = top_item_sales
                    primary_item = top_item_name
                else:
                    sales_analysis = self._analyze_item_sales([], "No Data")
                    sales_analysis['raw_sales_data'] = []
                    primary_item = "No Data Available"
            else:
                # No specific item mentioned - use all data for analysis
                relevant_sales = sales_data
                if sales_data:
                    # Find the actual top-selling item from the data
                    item_totals = {}
                    for record in sales_data:
                        if record.item not in item_totals:
                            item_totals[record.item] = 0
                        item_totals[record.item] += record.quantity
                    
                    primary_item = max(item_totals.items(), key=lambda x: x[1])[0]
                    logger.info(f"No specific item mentioned, using top seller: {primary_item}")
                else:
                    primary_item = "No Data Available"
                
                sales_analysis = self._analyze_item_sales(relevant_sales, primary_item)
                sales_analysis['raw_sales_data'] = relevant_sales
            
            # STEP 5: Apply local context only if relevant
            context_signals = self._extract_relevant_context(context, primary_item, intent)
            
            # STEP 6: Make decision based on data + context
            decision_result = self._make_item_decision(
                user_question, primary_item, sales_analysis, context_signals, intent
            )
            
            # STEP 7: Generate dynamic follow-up questions
            suggested_questions = self._generate_dynamic_suggestions(
                primary_item, decision_result, context_signals, intent, relevant_sales
            )
            
            # STEP 8: Format response in required JSON structure
            response = {
                "answer_to": user_question,
                "primary_decision": {
                    "decision": decision_result["decision"],
                    "item": primary_item,
                    "recent_sales_summary": sales_analysis["summary_points"],
                    "action": decision_result["action"],
                    "why": decision_result["reasoning"],
                    "confidence": decision_result["confidence"],
                    "based_on": decision_result["based_on"]
                },
                "supporting_signals": sales_analysis["key_signals"],
                "risk_and_safety": decision_result["risk_advice"],
                "suggested_questions": suggested_questions
            }
            
            return {
                'success': True,
                'question': user_question,
                'answer': response,
                'data_days': len(set(record.date for record in relevant_sales)) if relevant_sales else 0
            }
            
        except Exception as e:
            logger.error(f"Error answering question: {str(e)}")
            return {
                'success': False,
                'question': user_question,
                'error': str(e),
                'fallback_answer': self._generate_fallback_answer(user_question)
            }
    
    def _extract_items_from_question(self, question: str) -> List[str]:
        """Extract specific item names mentioned in the user's question"""
        import re
        question_lower = question.lower()
        
        # Common kirana items to look for - expanded list
        item_patterns = {
            'rice': ['rice', 'chawal', 'basmati', 'sona masoori'],
            'oil': ['oil', 'tel', 'cooking oil', 'mustard oil', 'sunflower oil'],
            'tea': ['tea', 'chai', 'green tea', 'black tea'],
            'dal': ['dal', 'lentil', 'toor dal', 'moong dal', 'chana dal', 'masoor dal'],
            'sugar': ['sugar', 'cheeni', 'jaggery', 'gud'],
            'milk': ['milk', 'doodh', 'dairy'],
            'bread': ['bread', 'pav', 'roti'],
            'biscuit': ['biscuit', 'biscuits', 'cookie', 'cookies', 'parle', 'britannia'],
            'flour': ['flour', 'atta', 'maida', 'wheat flour'],
            'onion': ['onion', 'onions', 'pyaz', 'kanda'],
            'potato': ['potato', 'potatoes', 'aloo', 'batata'],
            'tomato': ['tomato', 'tomatoes', 'tamatar'],
            'ghee': ['ghee', 'clarified butter'],
            'spice': ['spice', 'spices', 'masala', 'turmeric', 'chili', 'coriander'],
            'sweet': ['sweet', 'sweets', 'mithai', 'laddu', 'barfi'],
            'snack': ['snack', 'snacks', 'namkeen', 'chips', 'mixture'],
            'cold drink': ['cold drink', 'cold drinks', 'soft drink', 'soft drinks', 'soda', 'pepsi', 'coke', 'sprite', 'thums up'],
            'water': ['water', 'paani', 'bottle water'],
            'soap': ['soap', 'detergent', 'washing powder'],
            'shampoo': ['shampoo', 'hair oil'],
            'toothpaste': ['toothpaste', 'colgate', 'pepsodent'],
            'cigarette': ['cigarette', 'cigarettes', 'bidi', 'tobacco'],
            'match': ['match', 'matches', 'matchbox', 'lighter'],
            'candle': ['candle', 'candles', 'diya'],
            'incense': ['incense', 'agarbatti', 'dhoop']
        }
        
        found_items = []
        for item, patterns in item_patterns.items():
            for pattern in patterns:
                # Use word boundaries for single words, substring for multi-word patterns
                if ' ' in pattern:
                    # Multi-word pattern - use substring matching
                    if pattern in question_lower:
                        found_items.append(item)
                        break
                else:
                    # Single word - use word boundary matching to avoid false positives
                    if re.search(r'\b' + re.escape(pattern) + r'\b', question_lower):
                        found_items.append(item)
                        break
        
        return found_items
    
    def _extract_intent_from_question(self, question: str) -> str:
        """Extract the business intent from the question"""
        question_lower = question.lower()
        
        # Check if specific item is mentioned with "tell me about" - this should be item analysis
        if any(phrase in question_lower for phrase in ['tell me about']) and not any(phrase in question_lower for phrase in ['my stock', 'stock details', 'inventory']):
            return 'specific_item_analysis'
        
        # Stock overview queries
        elif any(phrase in question_lower for phrase in ['tell me about', 'show me', 'what is my', 'my stock', 'stock details', 'inventory']):
            return 'stock_overview'
        elif any(phrase in question_lower for phrase in ['what should i do', 'what to do', 'today for my shop', 'general advice']):
            return 'general_analysis'
        
        # Top/bottom selling analysis
        elif any(phrase in question_lower for phrase in ['top selling', 'best selling', 'top 3', 'top three', 'which product top', 'highest selling']):
            return 'top_selling_analysis'
        elif any(phrase in question_lower for phrase in ['slow selling', 'slowly', 'less sold', 'worst selling', 'bottom', 'not selling', 'selling slowly']):
            return 'slow_selling_analysis'
        elif any(phrase in question_lower for phrase in ['should i focus', 'focus on top', 'concentrate on']):
            return 'focus_analysis'
        
        # Cash flow and reduction
        elif any(phrase in question_lower for phrase in ['save cash', 'reduce to save', 'free up cash', 'what should i reduce']):
            return 'cash_saving_analysis'
        elif any(word in question_lower for word in ['reduce', 'decrease', 'less', 'cut down', 'stop buying']):
            return 'reduce'
        
        # Restocking
        elif any(word in question_lower for word in ['restock', 'stock more', 'increase', 'buy more', 'order more']):
            return 'restock'
        
        # Seasonal and contextual
        elif any(word in question_lower for word in ['festival', 'diwali', 'holi', 'eid', 'navratri', 'durga puja']):
            return 'festival_prep'
        elif any(word in question_lower for word in ['rain', 'monsoon', 'weather', 'hot', 'cold', 'summer', 'winter']):
            return 'weather_impact'
        elif any(word in question_lower for word in ['price', 'pricing', 'cost', 'expensive', 'cheap']):
            return 'pricing'
        elif any(word in question_lower for word in ['competition', 'competitor', 'nearby shop', 'other shop']):
            return 'competition'
        elif any(word in question_lower for word in ['demand', 'customer', 'selling', 'popular']):
            return 'demand_analysis'
        
        # Forecast and prediction
        elif any(word in question_lower for word in ['forecast', 'predict', 'future', 'next week', 'tomorrow']):
            return 'forecast_analysis'
        
        else:
            return 'daily_operations'
    
    def _filter_sales_by_items(self, sales_data: List[SalesRecord], items: List[str]) -> List[SalesRecord]:
        """Filter sales data to only include records for mentioned items"""
        filtered_sales = []
        
        for record in sales_data:
            record_item_lower = record.item.lower()
            for item in items:
                item_lower = item.lower()
                
                # Direct substring match
                if item_lower in record_item_lower:
                    filtered_sales.append(record)
                    break
                
                # Specific item matching patterns
                elif item_lower == 'oil' and any(oil_pattern in record_item_lower for oil_pattern in ['oil', 'tel']):
                    filtered_sales.append(record)
                    break
                elif item_lower == 'rice' and any(rice_pattern in record_item_lower for rice_pattern in ['rice', 'chawal']):
                    filtered_sales.append(record)
                    break
                elif item_lower == 'tea' and any(tea_pattern in record_item_lower for tea_pattern in ['tea', 'chai']):
                    filtered_sales.append(record)
                    break
                elif item_lower == 'dal' and any(dal_pattern in record_item_lower for dal_pattern in ['dal', 'lentil', 'toor', 'moong', 'chana']):
                    filtered_sales.append(record)
                    break
                elif item_lower == 'milk' and any(milk_pattern in record_item_lower for milk_pattern in ['milk', 'doodh']):
                    filtered_sales.append(record)
                    break
        
        # Debug logging
        logger.info(f"Filtering for items: {items}")
        logger.info(f"Available items in data: {[record.item for record in sales_data[:10]]}")
        logger.info(f"Found {len(filtered_sales)} records out of {len(sales_data)} total")
        if filtered_sales:
            logger.info(f"Filtered records: {[(record.item, record.quantity) for record in filtered_sales]}")
        else:
            logger.warning(f"No records found for items: {items}")
        
        return filtered_sales
    
    def _analyze_top_selling_items(self, sales_data: List[SalesRecord], limit: int = 3) -> Dict[str, Any]:
        """Analyze top selling items from sales data"""
        if not sales_data:
            return {
                "summary_points": ["No sales data available for top selling analysis"],
                "key_signals": ["No data to analyze"],
                "top_items": []
            }
        
        # Calculate item totals
        item_totals = {}
        item_revenue = {}
        for record in sales_data:
            if record.item not in item_totals:
                item_totals[record.item] = 0
                item_revenue[record.item] = 0
            item_totals[record.item] += record.quantity
            item_revenue[record.item] += record.quantity * record.price
        
        # Sort by quantity
        sorted_by_quantity = sorted(item_totals.items(), key=lambda x: x[1], reverse=True)
        top_items = sorted_by_quantity[:limit]
        
        summary_points = [f"Top {len(top_items)} selling items by quantity:"]
        for i, (item, qty) in enumerate(top_items, 1):
            revenue = item_revenue[item]
            summary_points.append(f"{i}. {item}: {qty} units sold (₹{revenue:.0f} revenue)")
        
        key_signals = [
            f"Top performer: {top_items[0][0]} with {top_items[0][1]} units" if top_items else "No clear top performer",
            f"Total items analyzed: {len(item_totals)}"
        ]
        
        return {
            "summary_points": summary_points,
            "key_signals": key_signals,
            "top_items": top_items,
            "item_revenue": item_revenue,
            "days_of_data": len(set(record.date for record in sales_data)) if sales_data else 0,
            "trend": "analysis_complete",
            "avg_daily": sum(item[1] for item in top_items) / len(set(record.date for record in sales_data)) if sales_data else 0
        }
    
    def _analyze_slow_selling_items(self, sales_data: List[SalesRecord], limit: int = 3) -> Dict[str, Any]:
        """Analyze slow selling items from sales data"""
        if not sales_data:
            return {
                "summary_points": ["No sales data available for slow selling analysis"],
                "key_signals": ["No data to analyze"],
                "slow_items": []
            }
        
        # Calculate item totals
        item_totals = {}
        item_revenue = {}
        for record in sales_data:
            if record.item not in item_totals:
                item_totals[record.item] = 0
                item_revenue[record.item] = 0
            item_totals[record.item] += record.quantity
            item_revenue[record.item] += record.quantity * record.price
        
        # Sort by quantity (ascending for slow sellers)
        sorted_by_quantity = sorted(item_totals.items(), key=lambda x: x[1])
        slow_items = sorted_by_quantity[:limit]
        
        summary_points = [f"Slowest {len(slow_items)} selling items:"]
        for i, (item, qty) in enumerate(slow_items, 1):
            revenue = item_revenue[item]
            summary_points.append(f"{i}. {item}: Only {qty} units sold (₹{revenue:.0f} revenue)")
        
        key_signals = [
            f"Slowest mover: {slow_items[0][0]} with only {slow_items[0][1]} units" if slow_items else "No clear slow mover",
            f"Consider reducing slow-moving stock to free up cash"
        ]
        
        return {
            "summary_points": summary_points,
            "key_signals": key_signals,
            "slow_items": slow_items,
            "item_revenue": item_revenue,
            "days_of_data": len(set(record.date for record in sales_data)) if sales_data else 0,
            "trend": "analysis_complete",
            "avg_daily": sum(item[1] for item in slow_items) / len(set(record.date for record in sales_data)) if sales_data else 0
        }
    
    def _analyze_specific_item_details(self, sales_data: List[SalesRecord], item_name: str) -> Dict[str, Any]:
        """Provide detailed analysis for a specific item"""
        # Filter data for the specific item
        item_sales = [record for record in sales_data if item_name.lower() in record.item.lower()]
        
        if not item_sales:
            return {
                "summary_points": [f"No sales data found for '{item_name}' in your uploaded CSV"],
                "key_signals": [f"'{item_name}' not found in recent transactions"],
                "item_found": False,
                "suggestion": f"Check if '{item_name}' is spelled correctly or if you have sales data for this item",
                "days_of_data": 0,
                "trend": "no_data",
                "avg_daily": 0
            }
        
        # Calculate metrics
        total_quantity = sum(record.quantity for record in item_sales)
        total_revenue = sum(record.quantity * record.price for record in item_sales)
        unique_dates = len(set(record.date for record in item_sales))
        avg_daily = total_quantity / unique_dates if unique_dates > 0 else 0
        avg_price = total_revenue / total_quantity if total_quantity > 0 else 0
        
        # Get date range
        dates = [record.date for record in item_sales]
        first_date = min(dates)
        last_date = max(dates)
        
        summary_points = [
            f"{item_name} detailed analysis:",
            f"Total sold: {total_quantity} units over {unique_dates} days",
            f"Total revenue: ₹{total_revenue:.2f}",
            f"Average daily sales: {avg_daily:.1f} units",
            f"Average price: ₹{avg_price:.2f} per unit",
            f"Sales period: {first_date} to {last_date}"
        ]
        
        # Analyze trend
        if len(item_sales) >= 3:
            recent_sales = item_sales[-2:]  # Last 2 transactions
            older_sales = item_sales[:-2]   # Earlier transactions
            
            recent_avg = sum(r.quantity for r in recent_sales) / len(recent_sales)
            older_avg = sum(r.quantity for r in older_sales) / len(older_sales) if older_sales else recent_avg
            
            if recent_avg > older_avg * 1.2:
                trend = "increasing"
                key_signals = [f"{item_name} sales trending upward", "Good time to consider restocking"]
            elif recent_avg < older_avg * 0.8:
                trend = "decreasing"
                key_signals = [f"{item_name} sales declining", "Monitor closely before restocking"]
            else:
                trend = "stable"
                key_signals = [f"{item_name} sales relatively stable", "Consistent performer"]
        else:
            trend = "insufficient_data"
            key_signals = [f"Limited {item_name} sales data", "Need more transactions for trend analysis"]
        
        return {
            "summary_points": summary_points,
            "key_signals": key_signals,
            "item_found": True,
            "trend": trend,
            "total_quantity": total_quantity,
            "total_revenue": total_revenue,
            "avg_daily": avg_daily,
            "days_of_data": unique_dates,
            "avg_daily": avg_daily
        }
    
    def _analyze_multiple_items(self, sales_data: List[SalesRecord], item_names: List[str]) -> Dict[str, Any]:
        """Analyze multiple items and compare them"""
        results = {}
        found_items = []
        not_found_items = []
        
        for item_name in item_names:
            analysis = self._analyze_specific_item_details(sales_data, item_name)
            results[item_name] = analysis
            
            if analysis['item_found']:
                found_items.append(item_name)
            else:
                not_found_items.append(item_name)
        
        # Create comparison summary
        summary_points = []
        if found_items:
            summary_points.append(f"Comparison of {len(found_items)} items:")
            
            # Sort found items by performance
            item_performance = []
            for item in found_items:
                analysis = results[item]
                item_performance.append((item, analysis['total_quantity'], analysis['total_revenue']))
            
            item_performance.sort(key=lambda x: x[1], reverse=True)  # Sort by quantity
            
            for i, (item, qty, revenue) in enumerate(item_performance, 1):
                summary_points.append(f"{i}. {item}: {qty} units, ₹{revenue:.0f} revenue")
        
        if not_found_items:
            summary_points.append(f"Items not found in data: {', '.join(not_found_items)}")
        
        key_signals = []
        if found_items:
            best_item = item_performance[0][0]
            key_signals.append(f"Best performer among requested items: {best_item}")
            
            if len(found_items) > 1:
                worst_item = item_performance[-1][0]
                key_signals.append(f"Needs attention: {worst_item}")
        
        if not_found_items:
            key_signals.append(f"{len(not_found_items)} items not found in your sales data")
        
        return {
            "summary_points": summary_points,
            "key_signals": key_signals,
            "found_items": found_items,
            "not_found_items": not_found_items,
            "results": results,
            "days_of_data": len(set(record.date for record in sales_data)) if sales_data else 0,
            "trend": "multi_item_analysis",
            "avg_daily": 0  # Not applicable for multi-item
        }
        """Get the top-selling item from sales data"""
        if not sales_data:
            return "General Business"
        
        item_totals = {}
        for record in sales_data:
            if record.item not in item_totals:
                item_totals[record.item] = 0
            item_totals[record.item] += record.quantity
        
        top_item = max(item_totals.items(), key=lambda x: x[1])
        return top_item[0]
    
    def _analyze_item_sales(self, sales_data: List[SalesRecord], item: str) -> Dict[str, Any]:
        """Analyze sales data for a specific item"""
        if not sales_data:
            return {
                "summary_points": [f"No recent sales data found for {item}"],
                "key_signals": ["Limited data available"],
                "total_quantity": 0,
                "total_revenue": 0,
                "days_of_data": 0,
                "trend": "unknown"
            }
        
        # Calculate metrics
        total_quantity = sum(record.quantity for record in sales_data)
        total_revenue = sum(record.quantity * record.price for record in sales_data)
        unique_dates = len(set(record.date for record in sales_data))
        avg_daily_quantity = total_quantity / unique_dates if unique_dates > 0 else 0
        
        # Analyze trend (simple: compare first half vs second half)
        if len(sales_data) >= 4:
            mid_point = len(sales_data) // 2
            first_half_avg = sum(r.quantity for r in sales_data[:mid_point]) / mid_point
            second_half_avg = sum(r.quantity for r in sales_data[mid_point:]) / (len(sales_data) - mid_point)
            
            if second_half_avg > first_half_avg * 1.1:
                trend = "increasing"
            elif second_half_avg < first_half_avg * 0.9:
                trend = "decreasing"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"
        
        # Generate summary points
        summary_points = [
            f"{item}: {total_quantity} units sold over {unique_dates} days",
            f"Average daily sales: {avg_daily_quantity:.1f} units",
            f"Total revenue: ₹{total_revenue:.2f}"
        ]
        
        # Generate key signals
        key_signals = []
        if trend == "increasing":
            key_signals.append(f"{item} sales trending upward")
        elif trend == "decreasing":
            key_signals.append(f"{item} sales declining recently")
        else:
            key_signals.append(f"{item} sales relatively stable")
        
        if unique_dates < 7:
            key_signals.append("Limited data - only few days available")
        
        return {
            "summary_points": summary_points,
            "key_signals": key_signals,
            "total_quantity": total_quantity,
            "total_revenue": total_revenue,
            "days_of_data": unique_dates,
            "trend": trend,
            "avg_daily": avg_daily_quantity
        }
    
    def _extract_relevant_context(self, context: LocalContext, item: str, intent: str) -> List[str]:
        """Extract context signals relevant to the specific item and intent"""
        if not context.text:
            return []
        
        context_lower = context.text.lower()
        relevant_signals = []
        
        # Festival context - expanded
        festival_keywords = ['diwali', 'festival', 'holi', 'eid', 'navratri', 'durga puja', 'ganesh', 'karva chauth']
        if any(festival in context_lower for festival in festival_keywords):
            if item in ['rice', 'oil', 'sweet', 'ghee', 'flour', 'dal', 'sugar']:
                relevant_signals.append("Festival season increases demand for cooking essentials and sweets")
            elif item in ['cold drink', 'ice cream']:
                relevant_signals.append("Festival season may not significantly boost cold item sales")
            elif item in ['candle', 'incense']:
                relevant_signals.append("Festival season dramatically increases demand for religious items")
        
        # Weather context - expanded
        weather_keywords = {
            'rain': ['rain', 'monsoon', 'wet', 'flooding'],
            'hot': ['hot', 'summer', 'heat', 'temperature'],
            'cold': ['cold', 'winter', 'chilly']
        }
        
        for weather_type, keywords in weather_keywords.items():
            if any(keyword in context_lower for keyword in keywords):
                if weather_type == 'rain':
                    if item in ['tea', 'biscuit', 'snack', 'bread']:
                        relevant_signals.append("Rainy weather increases demand for hot beverages and indoor snacks")
                    elif item in ['cold drink', 'ice cream']:
                        relevant_signals.append("Rainy weather significantly reduces cold item demand")
                elif weather_type == 'hot':
                    if item in ['cold drink', 'water', 'ice cream']:
                        relevant_signals.append("Hot weather dramatically increases cold beverage demand")
                    elif item in ['tea', 'hot snack']:
                        relevant_signals.append("Hot weather reduces hot beverage consumption")
                elif weather_type == 'cold':
                    if item in ['tea', 'biscuit', 'soup']:
                        relevant_signals.append("Cold weather increases hot beverage and comfort food demand")
        
        # Local demand context
        demand_keywords = ['demand', 'popular', 'selling well', 'customers asking', 'high demand', 'low demand']
        if any(keyword in context_lower for keyword in demand_keywords):
            relevant_signals.append("Local demand patterns affecting item popularity")
        
        # Competition context
        if any(keyword in context_lower for keyword in ['competition', 'competitor', 'new shop', 'nearby store']):
            relevant_signals.append("Local competition may affect pricing and demand patterns")
        
        # Economic context
        if any(keyword in context_lower for keyword in ['expensive', 'cheap', 'price increase', 'inflation']):
            relevant_signals.append("Economic factors affecting customer purchasing behavior")
        
        # Seasonal context
        seasonal_keywords = ['wedding season', 'school season', 'harvest', 'crop', 'farming']
        if any(keyword in context_lower for keyword in seasonal_keywords):
            relevant_signals.append("Seasonal patterns affecting local purchasing power and demand")
        
        return relevant_signals
    
    def _generate_stock_overview(self, sales_data: List[SalesRecord]) -> Dict[str, Any]:
        """Generate comprehensive stock overview for 'tell me about my stock' queries"""
        if not sales_data:
            return {
                "summary_points": ["No sales data available for analysis"],
                "key_signals": ["No recent transactions found"],
                "recommendations": ["Upload recent sales data to get stock insights"]
            }
        
        # Get latest date data
        latest_date = max(record.date for record in sales_data)
        latest_sales = [record for record in sales_data if record.date == latest_date]
        
        # Analyze all items
        item_analysis = {}
        for record in sales_data:
            if record.item not in item_analysis:
                item_analysis[record.item] = {
                    'total_quantity': 0,
                    'total_revenue': 0,
                    'days_sold': set(),
                    'latest_quantity': 0
                }
            
            item_analysis[record.item]['total_quantity'] += record.quantity
            item_analysis[record.item]['total_revenue'] += record.quantity * record.price
            item_analysis[record.item]['days_sold'].add(record.date)
            
            if record.date == latest_date:
                item_analysis[record.item]['latest_quantity'] += record.quantity
        
        # Sort by performance
        sorted_items = sorted(
            item_analysis.items(), 
            key=lambda x: x[1]['total_revenue'], 
            reverse=True
        )
        
        # Generate insights
        total_items = len(item_analysis)
        total_revenue = sum(data['total_revenue'] for data in item_analysis.values())
        unique_dates = len(set(record.date for record in sales_data))
        
        summary_points = [
            f"Stock analysis for {total_items} different items",
            f"Total revenue: ₹{total_revenue:.2f} over {unique_dates} days",
            f"Latest sales date: {latest_date} ({len(latest_sales)} transactions)"
        ]
        
        # Top performers
        top_3 = sorted_items[:3]
        top_performers_text = ', '.join([f'{item} (₹{data["total_revenue"]:.0f})' for item, data in top_3])
        summary_points.append(f"Top performers: {top_performers_text}")
        
        # Slow movers
        slow_movers = [item for item, data in sorted_items if len(data['days_sold']) <= 2]
        if slow_movers:
            summary_points.append(f"Slow movers: {', '.join(slow_movers[:3])}")
        
        key_signals = []
        if len(latest_sales) > 5:
            key_signals.append(f"Active sales day: {len(latest_sales)} items sold on {latest_date}")
        else:
            key_signals.append(f"Light sales day: Only {len(latest_sales)} items sold on {latest_date}")
        
        # Generate recommendations
        recommendations = []
        if top_3:
            recommendations.append(f"Focus on restocking {top_3[0][0]} - your best performer")
        if slow_movers:
            recommendations.append(f"Consider reducing {slow_movers[0]} stock to free up cash")
        recommendations.append("Monitor daily sales patterns for better inventory planning")
        
        return {
            "summary_points": summary_points,
            "key_signals": key_signals,
            "recommendations": recommendations,
            "item_details": item_analysis,
            "latest_date": latest_date
        }
    
    def _make_item_decision(self, question: str, item: str, sales_analysis: Dict, 
                           context_signals: List[str], intent: str) -> Dict[str, Any]:
        """Make a specific decision for the item based on data and context"""
        
        days_of_data = sales_analysis["days_of_data"]
        trend = sales_analysis["trend"]
        avg_daily = sales_analysis["avg_daily"]
        
        # Handle new analysis types
        if intent == 'top_selling_analysis':
            return {
                "decision": "FOCUS ON TOP PERFORMERS",
                "action": "Prioritize restocking your best-selling items",
                "reasoning": "\n".join(sales_analysis["summary_points"]),
                "confidence": f"High (based on complete sales data)",
                "based_on": ["Complete sales data analysis", "Performance ranking"],
                "risk_advice": ["Monitor inventory levels of top items daily", "Ensure adequate stock of best performers"]
            }
        
        elif intent == 'slow_selling_analysis':
            return {
                "decision": "REDUCE SLOW MOVERS",
                "action": "Consider reducing stock of slow-selling items",
                "reasoning": "\n".join(sales_analysis["summary_points"]),
                "confidence": f"High (based on complete sales data)",
                "based_on": ["Complete sales data analysis", "Performance ranking"],
                "risk_advice": ["Reduce slow-moving stock gradually", "Free up cash for better-performing items"]
            }
        
        elif intent == 'focus_analysis':
            return {
                "decision": "YES - FOCUS ON TOP SELLERS",
                "action": "Concentrate resources on your best-performing items",
                "reasoning": "\n".join(sales_analysis["summary_points"]),
                "confidence": f"High (based on performance data)",
                "based_on": ["Sales performance analysis", "Resource optimization strategy"],
                "risk_advice": ["Don't completely ignore other items", "Monitor market changes"]
            }
        
        elif intent == 'cash_saving_analysis':
            return {
                "decision": "REDUCE THESE ITEMS",
                "action": "Cut stock on slow-moving items to improve cash flow",
                "reasoning": "\n".join(sales_analysis["summary_points"]),
                "confidence": f"High (based on sales performance)",
                "based_on": ["Cash flow optimization", "Sales performance data"],
                "risk_advice": ["Reduce gradually, not all at once", "Monitor customer demand"]
            }
        
        elif intent == 'specific_item_analysis':
            # Handle specific item analysis - "Tell me about Rice"
            if sales_analysis.get('item_found') == False:
                return {
                    "decision": f"NO DATA FOUND",
                    "action": f"No sales data available for {item}",
                    "reasoning": sales_analysis.get('suggestion', f"Check if {item} is in your sales data"),
                    "confidence": "High (data verification complete)",
                    "based_on": ["Complete CSV file search"],
                    "risk_advice": ["Verify item name spelling", "Check data period coverage"]
                }
            else:
                # Item found - provide detailed analysis
                total_qty = sales_analysis.get('total_quantity', 0)
                total_revenue = sales_analysis.get('total_revenue', 0)
                item_trend = sales_analysis.get('trend', 'unknown')
                
                if item_trend == "increasing":
                    decision = f"STRONG PERFORMER - {item} is growing"
                    action = f"Consider increasing {item} stock by 15-20%"
                elif item_trend == "decreasing":
                    decision = f"DECLINING - {item} needs attention"
                    action = f"Monitor {item} closely, consider reducing stock"
                else:
                    decision = f"STABLE PERFORMER - {item} is consistent"
                    action = f"Maintain current {item} stock levels"
                
                return {
                    "decision": decision,
                    "action": action,
                    "reasoning": "\n".join(sales_analysis["summary_points"]),
                    "confidence": f"High (detailed {item} analysis)",
                    "based_on": [f"Complete {item} sales history", "Performance trend analysis"],
                    "risk_advice": [f"Monitor {item} inventory daily", "Track customer demand patterns"]
                }
        
        elif "Items Comparison" in item:
            # Multiple items comparison - "Should I refill tea and biscuits?"
            found_items = sales_analysis.get('found_items', [])
            not_found_items = sales_analysis.get('not_found_items', [])
            
            if found_items and not not_found_items:
                # All items found - provide comparison and recommendation
                results = sales_analysis.get('results', {})
                
                # Analyze performance of found items
                item_recommendations = []
                for item_name in found_items:
                    item_data = results[item_name]
                    if item_data['item_found']:
                        qty = item_data.get('total_quantity', 0)
                        trend = item_data.get('trend', 'unknown')
                        
                        if trend == 'increasing':
                            item_recommendations.append(f"✅ {item_name}: YES - increase stock (growing trend)")
                        elif trend == 'decreasing':
                            item_recommendations.append(f"⚠️ {item_name}: CAUTION - monitor closely (declining)")
                        else:
                            item_recommendations.append(f"✅ {item_name}: YES - maintain/increase stock (stable)")
                
                decision = f"MULTI-ITEM ANALYSIS - {len(found_items)} items reviewed"
                action = f"Individual recommendations: {'; '.join(item_recommendations)}"
                
            elif found_items and not_found_items:
                # Some items found, some missing
                decision = f"PARTIAL DATA - {len(found_items)} found, {len(not_found_items)} missing"
                action = f"Analysis available for {', '.join(found_items)}. No data for {', '.join(not_found_items)}"
            else:
                # No items found
                decision = f"NO DATA FOUND"
                action = f"None of the requested items found in sales data"
            
            return {
                "decision": decision,
                "action": action,
                "reasoning": "\n".join(sales_analysis["summary_points"]),
                "confidence": "High (complete data search)" if found_items else "High (data verification)",
                "based_on": ["Multi-item analysis", "CSV data verification"],
                "risk_advice": ["Focus on items with available data", "Verify missing item names"] if not_found_items else ["Monitor each item's performance individually", "Adjust quantities based on individual trends"]
            }
        
        # Handle stock overview intent
        elif intent == 'stock_overview':
            stock_overview = self._generate_stock_overview(sales_analysis.get('raw_sales_data', []))
            return {
                "decision": "OVERVIEW - Current stock status",
                "action": "Review your inventory based on recent performance",
                "reasoning": "\n".join(stock_overview["summary_points"]),
                "confidence": f"High (based on {days_of_data} days of data)",
                "based_on": ["Complete sales data analysis", "Recent transaction patterns"],
                "risk_advice": stock_overview["recommendations"]
            }
        
        # Handle general analysis intent
        if intent == 'general_analysis':
            if item == "No Data Available":
                return {
                    "decision": "NO DATA - Upload sales data first",
                    "action": "Please upload your sales data to get recommendations",
                    "reasoning": "No sales data available for analysis",
                    "confidence": "N/A",
                    "based_on": ["No data provided"],
                    "risk_advice": ["Upload recent sales data", "Include at least 7 days of transactions"]
                }
            else:
                # Determine base confidence for general analysis
                if days_of_data >= 7:
                    base_confidence = "High"
                elif days_of_data >= 3:
                    base_confidence = "Medium"
                else:
                    base_confidence = "Low"
                
                # Analyze the top-selling item
                if trend == "increasing":
                    decision = f"FOCUS ON {item.upper()}"
                    action = f"Your top seller {item} is growing - increase stock by 15-20%"
                    reasoning = f"{item} is your best performer with {avg_daily:.1f} units sold daily on average"
                elif trend == "stable":
                    decision = f"MAINTAIN {item.upper()}"
                    action = f"Keep {item} stock steady - it's your reliable seller"
                    reasoning = f"{item} shows consistent sales with stable demand patterns"
                else:
                    decision = f"MONITOR {item.upper()}"
                    action = f"Watch {item} closely - sales may be declining"
                    reasoning = f"{item} is your top seller but recent trend shows some decline"
                
                return {
                    "decision": decision,
                    "action": action,
                    "reasoning": reasoning,
                    "confidence": f"{base_confidence} (analyzing top seller)",
                    "based_on": ["Sales data analysis", "Top performer identification"],
                    "risk_advice": [f"Monitor {item} inventory daily", "Consider diversifying product focus"]
                }
        
        # Determine base confidence
        if days_of_data >= 7:
            base_confidence = "High"
        elif days_of_data >= 3:
            base_confidence = "Medium"
        else:
            base_confidence = "Low"
        
        # Make decision based on intent and data
        if intent == 'restock':
            if trend == "increasing" or any("demand" in signal.lower() for signal in context_signals):
                decision = "YES"
                if days_of_data >= 7:
                    action = f"Increase {item} stock by 15-20%"
                else:
                    action = f"Increase {item} stock by 10% (limited data)"
                reasoning = f"{item} shows positive signals for restocking based on recent trends"
            elif trend == "decreasing":
                decision = "CAUTION"
                action = f"Small increase in {item} stock (5-10% only)"
                reasoning = f"{item} sales declining, so conservative increase recommended"
            else:
                decision = "YES"
                action = f"Moderate increase in {item} stock (10-15%)"
                reasoning = f"{item} sales stable, safe to increase moderately"
        
        elif intent == 'reduce':
            if trend == "decreasing":
                decision = "YES"
                action = f"Reduce {item} stock by 20-30%"
                reasoning = f"{item} sales declining, reduction makes sense to free up cash"
            elif trend == "increasing":
                decision = "NO"
                action = f"Do not reduce {item} stock - sales are growing"
                reasoning = f"{item} showing growth, reduction would be counterproductive"
            else:
                decision = "CAUTION"
                action = f"Small reduction in {item} stock (10-15% only)"
                reasoning = f"{item} sales stable, minor reduction acceptable if needed"
        
        elif intent == 'weather_impact':
            weather_boost_items = ['tea', 'biscuit', 'snack', 'cold drink', 'water']
            if item in weather_boost_items:
                if any("rain" in signal.lower() for signal in context_signals) and item in ['tea', 'biscuit']:
                    decision = "YES"
                    action = f"Increase {item} stock by 20-25% during rainy period"
                    reasoning = f"Rainy weather significantly boosts {item} demand"
                elif any("hot" in signal.lower() for signal in context_signals) and item in ['cold drink', 'water']:
                    decision = "YES"
                    action = f"Increase {item} stock by 25-30% during hot weather"
                    reasoning = f"Hot weather dramatically increases {item} sales"
                else:
                    decision = "MONITOR"
                    action = f"Watch {item} sales closely for weather impact"
                    reasoning = f"Weather conditions may affect {item} demand patterns"
            elif item == 'oil':
                # Special handling for oil during rain
                if any("rain" in signal.lower() for signal in context_signals):
                    if trend == "increasing" or avg_daily > 0:
                        decision = "YES"
                        action = f"Increase {item} stock by 15-20% during rainy period"
                        reasoning = f"Rainy weather increases home cooking, boosting {item} demand for frying and cooking"
                    else:
                        decision = "CAUTION"
                        action = f"Small increase in {item} stock (10-15%) for cooking demand"
                        reasoning = f"Rain increases cooking at home, but limited {item} sales data suggests conservative approach"
                else:
                    decision = "NEUTRAL"
                    action = f"Weather unlikely to significantly impact {item} sales"
                    reasoning = f"{item} demand is generally stable regardless of weather"
            else:
                decision = "NEUTRAL"
                action = f"Weather unlikely to significantly impact {item} sales"
                reasoning = f"{item} demand is generally stable regardless of weather"
        
        else:  # general analysis
            if trend == "increasing":
                decision = "YES - Stock more"
                action = f"Increase {item} stock by 15-20%"
                reasoning = f"{item} sales trending upward, good opportunity to capitalize"
            elif trend == "decreasing":
                decision = "CAUTION - Monitor closely"
                action = f"Maintain current {item} stock, watch for 3-5 days"
                reasoning = f"{item} sales declining, avoid overstock until trend improves"
            else:
                decision = "YES - Maintain current levels"
                action = f"Keep {item} stock at current levels"
                reasoning = f"{item} sales stable, no major changes needed currently"
        
        # Adjust confidence based on context
        confidence_reason = f"({days_of_data} days of data"
        if context_signals:
            confidence_reason += ", local context considered"
        confidence_reason += ")"
        
        # Build based_on list
        based_on = ["Recent sales data"]
        if context_signals:
            based_on.extend(context_signals)
        
        # Risk advice
        risk_advice = []
        if days_of_data < 7:
            risk_advice.append("Limited data - monitor results closely")
        if trend == "decreasing":
            risk_advice.append(f"Watch {item} sales for next 3-5 days before major decisions")
        else:
            risk_advice.append(f"Track {item} inventory levels daily")
        
        return {
            "decision": decision,
            "action": action,
            "reasoning": reasoning,
            "confidence": f"{base_confidence} {confidence_reason}",
            "based_on": based_on,
            "risk_advice": risk_advice
        }
    
    def _generate_dynamic_suggestions(self, primary_item: str, decision_result: Dict, 
                                    context_signals: List[str], intent: str, 
                                    sales_data: List[SalesRecord] = None) -> List[str]:
        """Generate dynamic follow-up questions based on the current analysis and actual sales data"""
        suggestions = []
        
        # If we have sales data, generate suggestions based on actual items
        if sales_data:
            # Get all unique items from sales data
            all_items = list(set(record.item for record in sales_data))
            
            # Calculate item performance
            item_totals = {}
            for record in sales_data:
                if record.item not in item_totals:
                    item_totals[record.item] = 0
                item_totals[record.item] += record.quantity
            
            # Sort items by performance
            sorted_items = sorted(item_totals.items(), key=lambda x: x[1], reverse=True)
            
            # Generate suggestions based on actual data
            if len(sorted_items) > 1:
                top_item = sorted_items[0][0]
                second_item = sorted_items[1][0] if len(sorted_items) > 1 else None
                bottom_item = sorted_items[-1][0] if len(sorted_items) > 2 else None
                
                # If analyzing a specific item, suggest related items from actual data
                if primary_item != "Stock Overview" and primary_item in [item[0] for item in sorted_items]:
                    # Find other items to suggest
                    other_items = [item[0] for item in sorted_items if item[0] != primary_item]
                    if other_items:
                        suggestions.append(f"Should I also stock more {other_items[0]}?")
                    if len(other_items) > 1:
                        suggestions.append(f"What about {other_items[1]} - is it selling well?")
                
                # General suggestions based on actual data
                if top_item != primary_item:
                    suggestions.append(f"Should I focus more on {top_item} since it's selling best?")
                
                if bottom_item and bottom_item != primary_item:
                    suggestions.append(f"Should I reduce {bottom_item} stock since it's selling slowly?")
                
                # Stock overview suggestions
                if intent == 'stock_overview':
                    suggestions.extend([
                        f"Should I restock {top_item} first?",
                        f"What should I do about {bottom_item}?",
                        "Which items need price adjustments?"
                    ])
                else:
                    # Add one more general suggestion
                    suggestions.append("Tell me about my complete stock situation")
        
        # Fallback to item-specific suggestions if no sales data or need more suggestions
        if len(suggestions) < 3:
            primary_item_lower = primary_item.lower()
            
            # Smart item matching for suggestions
            if any(keyword in primary_item_lower for keyword in ['rice', 'chawal']):
                suggestions.extend([
                    "Should I stock more dal and oil for cooking?",
                    "What about flour for festival season?",
                    "Should I adjust rice prices?"
                ])
            elif any(keyword in primary_item_lower for keyword in ['oil', 'tel']):
                suggestions.extend([
                    "Should I increase rice stock for cooking?",
                    "What about ghee for festival season?",
                    "Should I stock more spices too?"
                ])
            elif any(keyword in primary_item_lower for keyword in ['tea', 'chai']):
                suggestions.extend([
                    "Should I stock more biscuits with tea?",
                    "What about reducing cold drinks?",
                    "Should I increase milk stock too?"
                ])
            elif any(keyword in primary_item_lower for keyword in ['cold drink', 'soft drink', 'soda']):
                suggestions.extend([
                    "Should I stock more tea for rainy days?",
                    "What about hot snacks instead?",
                    "Should I reduce cold drink prices?"
                ])
            elif primary_item == "Stock Overview":
                suggestions.extend([
                    "Which items should I restock first?",
                    "What items are moving slowly?",
                    "Should I reduce any stock to save money?"
                ])
        
        # Context-based follow-ups
        if any("festival" in signal.lower() for signal in context_signals):
            suggestions.append("Which items should I reduce to free up cash for festival stock?")
        
        if any("rain" in signal.lower() for signal in context_signals):
            suggestions.append("What items sell better during monsoon?")
        
        # Intent-based follow-ups
        if intent == 'restock':
            suggestions.append("Which slow-moving items should I reduce?")
        elif intent == 'reduce':
            suggestions.append("What should I stock more of instead?")
        
        # General business follow-ups (only add if we don't have enough suggestions)
        if len(suggestions) < 3:
            suggestions.extend([
                "What's my best-selling item this week?",
                "Should I change prices for any items?",
                "Tell me about my stock"
            ])
        
        # Return only first 3 unique suggestions
        unique_suggestions = []
        for suggestion in suggestions:
            if suggestion not in unique_suggestions:
                unique_suggestions.append(suggestion)
            if len(unique_suggestions) >= 3:
                break
        
        return unique_suggestions
    
    def _generate_fallback_answer(self, question: str) -> Dict[str, str]:
        """Generate a fallback answer when AI fails"""
        return {
            'title': 'Safe Action Without AI',
            'decision': 'Yes, but be very careful with quantities.',
            'action': 'Check last week\'s top 3 items and increase stock by 10% only.',
            'why': 'When data is limited, small increases on fast-moving items reduce risk.',
            'confidence': 'Low',
            'based_on': 'Limited data available'
        }
    
    def get_suggested_questions(self, sales_data: List[SalesRecord], context: LocalContext) -> List[str]:
        """
        Generate suggested questions based on the sales data and context.
        """
        suggestions = []
        
        if not sales_data:
            return [
                "Should I increase rice stock because Diwali comes next week?",
                "Do I need more oil and sweets for the festival?",
                "Should I reduce cold drinks because of monsoon rains?"
            ]
        
        # Analyze sales data for suggestions
        item_sales = {}
        for record in sales_data:
            if record.item not in item_sales:
                item_sales[record.item] = 0
            item_sales[record.item] += record.quantity
        
        # Get top and bottom performers
        sorted_items = sorted(item_sales.items(), key=lambda x: x[1], reverse=True)
        
        if len(sorted_items) > 0:
            top_item = sorted_items[0][0]
            suggestions.append(f"Should I increase {top_item} stock because it's selling well?")
            
            if len(sorted_items) > 1:
                second_item = sorted_items[1][0]
                suggestions.append(f"What about {second_item} - should I stock more?")
            
            if len(sorted_items) > 2:
                bottom_item = sorted_items[-1][0]
                suggestions.append(f"Should I reduce {bottom_item} stock because it's selling slowly?")
        
        # Context-based suggestions
        if context.text:
            context_lower = context.text.lower()
            if 'festival' in context_lower or 'diwali' in context_lower:
                if len(sorted_items) > 0:
                    top_item = sorted_items[0][0]
                    suggestions.append(f"Should I increase {top_item} stock for the festival?")
                suggestions.append("Which items should I stock for festival season?")
            if 'rain' in context_lower or 'monsoon' in context_lower:
                # Find tea/hot items in actual data
                hot_items = [item for item, _ in sorted_items if any(keyword in item.lower() for keyword in ['tea', 'chai', 'biscuit', 'hot'])]
                cold_items = [item for item, _ in sorted_items if any(keyword in item.lower() for keyword in ['cold', 'drink', 'soda', 'ice'])]
                
                if hot_items:
                    suggestions.append(f"Should I stock more {hot_items[0]} for rainy weather?")
                if cold_items:
                    suggestions.append(f"Should I reduce {cold_items[0]} because of monsoon rains?")
                else:
                    suggestions.append("What items sell better during monsoon?")
            if 'competition' in context_lower or 'competitor' in context_lower:
                if len(sorted_items) > 0:
                    top_item = sorted_items[0][0]
                    suggestions.append(f"Should I lower {top_item} prices because new shop opened nearby?")
        
        # General business questions based on actual data
        if len(sorted_items) > 0:
            suggestions.append("Tell me about my stock")
            suggestions.append(f"Should I focus more on {sorted_items[0][0]}?")
        
        # Ensure we have at least some suggestions
        if len(suggestions) < 3:
            suggestions.extend([
                "What items should I stock more?",
                "Should I change my prices?",
                "Which items are moving slowly?"
            ])
        
        return suggestions[:6]  # Return top 6 suggestions


def create_qa_system(bedrock_client: BedrockClient) -> InteractiveQASystem:
    """Factory function to create Q&A system"""
    return InteractiveQASystem(bedrock_client)