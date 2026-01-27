"""
Recommendation Formatting Module

This module provides comprehensive formatting functions for AI-generated
recommendations, ensuring they are displayed in simple, accessible language
suitable for kirana shop owners.

Requirements: 2.5, 4.1, 4.2
"""

from typing import List, Dict, Any, Optional
from models import Recommendation
import logging

logger = logging.getLogger(__name__)


class RecommendationFormatter:
    """
    Formatter for AI recommendations with multiple output formats.
    
    Provides various formatting options for displaying recommendations
    in web interface, reports, and other contexts.
    """
    
    def __init__(self):
        self.priority_keywords = {
            'high': ['urgent', 'immediately', 'critical', 'important', 'festival', 'stockout'],
            'medium': ['consider', 'recommend', 'suggest', 'improve', 'increase'],
            'low': ['monitor', 'watch', 'maintain', 'continue', 'observe']
        }
    
    def format_for_web_display(self, recommendations: List[Recommendation]) -> List[Dict[str, Any]]:
        """
        Format recommendations for web interface display.
        
        Args:
            recommendations: List of recommendation objects
            
        Returns:
            List of formatted recommendation dictionaries
        """
        formatted_recs = []
        
        for i, rec in enumerate(recommendations, 1):
            try:
                # Determine priority based on keywords
                priority = self._determine_priority(rec)
                
                # Format action with emphasis
                formatted_action = self._format_action_text(rec.action)
                
                # Format explanation with simple language
                formatted_explanation = self._format_explanation_text(rec.explanation)
                
                # Create formatted recommendation
                formatted_rec = {
                    'id': i,
                    'item': rec.item.strip(),
                    'action': formatted_action,
                    'explanation': formatted_explanation,
                    'confidence': rec.confidence.strip() if rec.confidence else "",
                    'priority': priority,
                    'priority_class': f'priority-{priority}',
                    'icon': self._get_recommendation_icon(rec),
                    'category': self._categorize_recommendation(rec),
                    'display_text': self._create_display_text(rec),
                    'summary': self._create_summary(rec)
                }
                
                formatted_recs.append(formatted_rec)
                
            except Exception as e:
                logger.error(f"Error formatting recommendation {i}: {str(e)}")
                # Add fallback formatting
                formatted_recs.append(self._create_fallback_format(rec, i))
        
        return formatted_recs
    
    def format_for_print_report(self, recommendations: List[Recommendation]) -> str:
        """
        Format recommendations for printable report.
        
        Args:
            recommendations: List of recommendation objects
            
        Returns:
            Formatted text report
        """
        report_lines = [
            "BHARATSIGNAL BUSINESS RECOMMENDATIONS",
            "=" * 40,
            ""
        ]
        
        # Group by priority
        high_priority = []
        medium_priority = []
        low_priority = []
        
        for rec in recommendations:
            priority = self._determine_priority(rec)
            if priority == 'high':
                high_priority.append(rec)
            elif priority == 'medium':
                medium_priority.append(rec)
            else:
                low_priority.append(rec)
        
        # Add high priority recommendations first
        if high_priority:
            report_lines.extend([
                "🔴 HIGH PRIORITY ACTIONS",
                "-" * 25
            ])
            for i, rec in enumerate(high_priority, 1):
                report_lines.extend(self._format_recommendation_for_print(rec, i))
            report_lines.append("")
        
        # Add medium priority recommendations
        if medium_priority:
            report_lines.extend([
                "🟡 RECOMMENDED ACTIONS",
                "-" * 22
            ])
            for i, rec in enumerate(medium_priority, 1):
                report_lines.extend(self._format_recommendation_for_print(rec, i))
            report_lines.append("")
        
        # Add low priority recommendations
        if low_priority:
            report_lines.extend([
                "🟢 MONITORING SUGGESTIONS",
                "-" * 25
            ])
            for i, rec in enumerate(low_priority, 1):
                report_lines.extend(self._format_recommendation_for_print(rec, i))
        
        return "\n".join(report_lines)
    
    def format_for_sms_summary(self, recommendations: List[Recommendation], max_length: int = 160) -> str:
        """
        Format recommendations for SMS summary (short format).
        
        Args:
            recommendations: List of recommendation objects
            max_length: Maximum SMS length
            
        Returns:
            Condensed SMS-friendly text
        """
        if not recommendations:
            return "No recommendations available."
        
        # Get top 2-3 most important recommendations
        sorted_recs = sorted(recommendations, key=lambda r: self._get_priority_score(r), reverse=True)
        top_recs = sorted_recs[:3]
        
        summary_parts = []
        for rec in top_recs:
            # Create very short summary
            short_summary = f"{rec.item}: {self._shorten_action(rec.action)}"
            if len(short_summary) <= 40:  # Reasonable length for SMS
                summary_parts.append(short_summary)
        
        summary = "BharatSignal: " + " | ".join(summary_parts)
        
        # Truncate if too long
        if len(summary) > max_length:
            summary = summary[:max_length-3] + "..."
        
        return summary
    
    def format_for_voice_readout(self, recommendations: List[Recommendation]) -> str:
        """
        Format recommendations for voice/audio readout.
        
        Args:
            recommendations: List of recommendation objects
            
        Returns:
            Voice-friendly text with natural pauses
        """
        if not recommendations:
            return "No recommendations are available at this time."
        
        voice_lines = [
            "Here are your business recommendations from BharatSignal.",
            ""
        ]
        
        for i, rec in enumerate(recommendations, 1):
            # Format for natural speech
            voice_text = (
                f"Recommendation {i}. "
                f"For {rec.item}, {self._format_for_speech(rec.action)}. "
                f"{self._format_explanation_for_speech(rec.explanation)}. "
                f"Pause."
            )
            voice_lines.append(voice_text)
            voice_lines.append("")  # Pause between recommendations
        
        voice_lines.append("End of recommendations.")
        
        return "\n".join(voice_lines)
    
    def _determine_priority(self, rec: Recommendation) -> str:
        """Determine priority level based on content analysis"""
        text_to_analyze = f"{rec.action} {rec.explanation}".lower()
        
        # Check for high priority keywords
        for keyword in self.priority_keywords['high']:
            if keyword in text_to_analyze:
                return 'high'
        
        # Check for medium priority keywords
        for keyword in self.priority_keywords['medium']:
            if keyword in text_to_analyze:
                return 'medium'
        
        return 'low'
    
    def _get_priority_score(self, rec: Recommendation) -> int:
        """Get numeric priority score for sorting"""
        priority = self._determine_priority(rec)
        return {'high': 3, 'medium': 2, 'low': 1}[priority]
    
    def _format_action_text(self, action: str) -> str:
        """Format action text for better readability"""
        # Ensure proper capitalization
        formatted = action.strip()
        if formatted and not formatted[0].isupper():
            formatted = formatted[0].upper() + formatted[1:]
        
        # Ensure proper punctuation
        if formatted and formatted[-1] not in '.!?':
            formatted += '.'
        
        return formatted
    
    def _format_explanation_text(self, explanation: str) -> str:
        """Format explanation text for clarity"""
        # Clean up and ensure proper formatting
        formatted = explanation.strip()
        if formatted and not formatted[0].isupper():
            formatted = formatted[0].upper() + formatted[1:]
        
        if formatted and formatted[-1] not in '.!?':
            formatted += '.'
        
        return formatted
    
    def _get_recommendation_icon(self, rec: Recommendation) -> str:
        """Get appropriate icon for recommendation type"""
        action_lower = rec.action.lower()
        item_lower = rec.item.lower()
        
        # Stock-related icons based on improved categories
        if any(word in item_lower for word in ['stock more', 'top', 'best']):
            return '📈'
        elif any(word in item_lower for word in ['reduce stock', 'slow', 'moving']):
            return '📉'
        elif any(word in action_lower for word in ['increase', 'order more', 'stock up']):
            return '📈'
        elif any(word in action_lower for word in ['reduce', 'decrease', 'less']):
            return '📉'
        elif any(word in action_lower for word in ['price', 'pricing']):
            return '💰'
        elif any(word in item_lower for word in ['festival', 'sweet', 'celebration']):
            return '🎉'
        elif any(word in item_lower for word in ['rice', 'wheat', 'grain']):
            return '🌾'
        elif any(word in item_lower for word in ['milk', 'dairy']):
            return '🥛'
        elif any(word in item_lower for word in ['oil', 'cooking']):
            return '🛢️'
        else:
            return '📍'
    
    def _categorize_recommendation(self, rec: Recommendation) -> str:
        """Categorize recommendation by type"""
        action_lower = rec.action.lower()
        
        if any(word in action_lower for word in ['increase', 'order more', 'stock up', 'add']):
            return 'stock_increase'
        elif any(word in action_lower for word in ['reduce', 'decrease', 'less', 'discontinue']):
            return 'stock_decrease'
        elif any(word in action_lower for word in ['price', 'pricing', 'cost']):
            return 'pricing'
        elif any(word in action_lower for word in ['maintain', 'continue', 'keep']):
            return 'maintain'
        else:
            return 'general'
    
    def _create_display_text(self, rec: Recommendation) -> str:
        """Create formatted display text"""
        return f"{rec.item}: {rec.action}\n\nWhy: {rec.explanation}"
    
    def _create_summary(self, rec: Recommendation) -> str:
        """Create short summary for quick view"""
        # Take first part of action (up to first comma or period)
        action_parts = rec.action.split(',')[0].split('.')[0]
        return f"{rec.item}: {action_parts}"
    
    def _create_fallback_format(self, rec: Recommendation, index: int) -> Dict[str, Any]:
        """Create fallback formatting when main formatting fails"""
        return {
            'id': index,
            'item': rec.item or 'Unknown Item',
            'action': rec.action or 'No action specified',
            'explanation': rec.explanation or 'No explanation provided',
            'confidence': rec.confidence or 'No confidence data',
            'priority': 'medium',
            'priority_class': 'priority-medium',
            'icon': '📍',
            'category': 'general',
            'display_text': f"{rec.item}: {rec.action}",
            'summary': f"{rec.item}: Action needed"
        }
    
    def _format_recommendation_for_print(self, rec: Recommendation, index: int) -> List[str]:
        """Format single recommendation for print report"""
        return [
            f"{index}. {rec.item.upper()}",
            f"   Action: {rec.action}",
            f"   Reason: {rec.explanation}",
            ""
        ]
    
    def _shorten_action(self, action: str) -> str:
        """Shorten action text for SMS"""
        # Take first meaningful part
        short = action.split(',')[0].split('.')[0]
        if len(short) > 30:
            short = short[:27] + "..."
        return short
    
    def _format_for_speech(self, action: str) -> str:
        """Format action text for natural speech"""
        # Replace numbers with words for better speech
        speech_text = action.replace('%', ' percent')
        speech_text = speech_text.replace('₹', 'rupees ')
        
        # Add natural pauses
        speech_text = speech_text.replace(',', ', pause,')
        
        return speech_text
    
    def _format_explanation_for_speech(self, explanation: str) -> str:
        """Format explanation for natural speech"""
        speech_text = explanation.replace('%', ' percent')
        speech_text = speech_text.replace('₹', 'rupees ')
        return speech_text


def create_formatter() -> RecommendationFormatter:
    """Factory function to create recommendation formatter"""
    return RecommendationFormatter()


def format_recommendations_for_web(recommendations: List[Recommendation]) -> List[Dict[str, Any]]:
    """Convenience function for web formatting"""
    formatter = create_formatter()
    return formatter.format_for_web_display(recommendations)


def format_recommendations_for_print(recommendations: List[Recommendation]) -> str:
    """Convenience function for print formatting"""
    formatter = create_formatter()
    return formatter.format_for_print_report(recommendations)


def validate_recommendation_formatting(recommendations: List[Recommendation]) -> Dict[str, Any]:
    """
    Validate that recommendations are properly formatted.
    
    Args:
        recommendations: List of recommendations to validate
        
    Returns:
        Dict with validation results
    """
    results = {
        'total_recommendations': len(recommendations),
        'valid_recommendations': 0,
        'formatting_errors': [],
        'language_issues': [],
        'success': True
    }
    
    for i, rec in enumerate(recommendations, 1):
        try:
            # Validate basic structure
            is_valid, error = rec.full_validate()
            if is_valid:
                results['valid_recommendations'] += 1
            else:
                results['formatting_errors'].append(f"Recommendation {i}: {error}")
                results['success'] = False
            
            # Check language simplicity
            if not rec.validate_language_simplicity():
                results['language_issues'].append(f"Recommendation {i}: Language too technical")
                results['success'] = False
                
        except Exception as e:
            results['formatting_errors'].append(f"Recommendation {i}: Validation error - {str(e)}")
            results['success'] = False
    
    return results