"""
BharatSignal - AI-powered decision-support system for kirana shops
Main Flask application entry point
"""

from flask import Flask, request, render_template, jsonify, redirect, url_for
import csv
import json
from datetime import datetime
from typing import List, Dict, Any
import os
from dotenv import load_dotenv
import logging

# Import data models and CSV processing
from models import SalesRecord, LocalContext, Recommendation
from csv_processor import parse_csv, CSVProcessingError, generate_error_report
from bedrock_client import BedrockClient, BedrockClientError, create_bedrock_client
from recommendation_formatter import format_recommendations_for_web, validate_recommendation_formatting
from interactive_qa import create_qa_system
from demo_data_handler import get_demo_handler

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Add JSON filter for templates
import json
@app.template_filter('tojsonfilter')
def to_json_filter(obj):
    return json.dumps(obj)

# Initialize Bedrock client and Q&A system
bedrock_client = None
qa_system = None

def get_bedrock_client():
    """Get or create Bedrock client instance"""
    global bedrock_client
    if bedrock_client is None:
        try:
            bedrock_client = create_bedrock_client()
            logger.info("Bedrock client initialized successfully")
        except BedrockClientError as e:
            logger.error(f"Failed to initialize Bedrock client: {str(e)}")
            bedrock_client = None
    return bedrock_client

def get_qa_system():
    """Get or create Q&A system instance"""
    global qa_system
    if qa_system is None:
        client = get_bedrock_client()
        if client:
            qa_system = create_qa_system(client)
            logger.info("Q&A system initialized successfully")
    return qa_system

@app.route('/')
def index():
    """Main page route"""
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze_data():
    """Process uploaded CSV and generate recommendations"""
    try:
        # Handle file upload
        if 'csv_file' not in request.files:
            return jsonify({'error': 'No CSV file uploaded'}), 400
        
        csv_file = request.files['csv_file']
        if csv_file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Get user input from context field (now used as question input)
        user_input = request.form.get('context', '').strip()
        
        if user_input:
            # User wrote something - use it as the question
            user_question = user_input
            # Create context object for any contextual information
            context = LocalContext(user_input)
            logger.info(f"User question from homepage: {user_question}")
        else:
            # No input - analyze uploaded data with stock overview
            user_question = "Tell me about my stock"
            context = LocalContext("")
            logger.info(f"No user input - using default stock analysis")
        
        # Validate context (basic validation)
        is_valid, error_msg = context.full_validate()
        if not is_valid:
            # Don't fail on context validation, just log it
            logger.warning(f"Context validation warning: {error_msg}")
        
        # Process CSV data with enhanced validation
        try:
            csv_result = parse_csv(csv_file)
            
            if not csv_result.success:
                error_report = generate_error_report(csv_result)
                return jsonify({'error': f'CSV validation failed:\n{error_report}'}), 400
            
            sales_data = csv_result.valid_records
            
            # Log processing summary
            logger.info(f"CSV processed successfully: {len(sales_data)} valid records")
            if csv_result.warnings:
                logger.info(f"Warnings: {csv_result.warnings[:3]}")  # Log first 3 warnings
                
        except CSVProcessingError as e:
            return jsonify({'error': f'CSV processing error: {str(e)}'}), 400
        except Exception as e:
            logger.error(f"Unexpected CSV processing error: {str(e)}")
            return jsonify({'error': 'Failed to process CSV file. Please check the file format and try again.'}), 400
        
        # Generate recommendations using Q&A system for consistency
        try:
            qa_system = get_qa_system()
            if qa_system:
                # Use detected question (either from context or default)
                logger.info(f"Using Q&A system for initial analysis with question: '{user_question}'")
                logger.info(f"Analyzing {len(sales_data)} sales records")
                qa_result = qa_system.answer_question(user_question, sales_data, context)
                
                if qa_result['success']:
                    # Convert Q&A response to recommendation format for display
                    answer = qa_result['answer']
                    recommendations = [
                        Recommendation(
                            item=answer['primary_decision']['item'],
                            action=answer['primary_decision']['action'],
                            explanation=answer['primary_decision']['why'],
                            confidence=answer['primary_decision']['confidence']
                        )
                    ]
                    logger.info(f"Q&A system generated recommendation for: {answer['primary_decision']['item']}")
                else:
                    logger.error(f"Q&A system failed: {qa_result.get('error', 'Unknown error')}")
                    # Create fallback recommendation based on actual data
                    if sales_data:
                        # Find top selling item from actual data
                        item_totals = {}
                        for record in sales_data:
                            if record.item not in item_totals:
                                item_totals[record.item] = 0
                            item_totals[record.item] += record.quantity
                        
                        top_item = max(item_totals.items(), key=lambda x: x[1])[0]
                        recommendations = [
                            Recommendation(
                                item=top_item,
                                action=f"Focus on {top_item} - your top seller",
                                explanation=f"Based on analysis of your sales data, {top_item} is performing well with {item_totals[top_item]} units sold",
                                confidence="Medium (fallback analysis)"
                            )
                        ]
                        logger.info(f"Fallback: Using top seller {top_item}")
                    else:
                        recommendations = [
                            Recommendation(
                                item="No Data",
                                action="Upload sales data to get recommendations",
                                explanation="No sales data available for analysis"
                            )
                        ]
            else:
                logger.error("Q&A system not available")
                recommendations = [
                    Recommendation(
                        item="System Error",
                        action="Q&A system is not available",
                        explanation="Please try again later"
                    )
                ]
            
        except Exception as e:
            logger.error(f"Error in recommendation generation: {str(e)}")
            # Create fallback recommendation based on actual data
            if sales_data:
                # Find top selling item from actual data
                item_totals = {}
                for record in sales_data:
                    if record.item not in item_totals:
                        item_totals[record.item] = 0
                    item_totals[record.item] += record.quantity
                
                top_item = max(item_totals.items(), key=lambda x: x[1])[0]
                recommendations = [
                    Recommendation(
                        item=top_item,
                        action=f"Focus on {top_item} - your top seller",
                        explanation=f"Based on analysis of your sales data, {top_item} is performing well with {item_totals[top_item]} units sold",
                        confidence="Medium (fallback analysis)"
                    )
                ]
                logger.info(f"Exception fallback: Using top seller {top_item}")
            else:
                recommendations = [
                    Recommendation(
                        item="Error",
                        action="System error occurred",
                        explanation=f"Error: {str(e)}"
                    )
                ]
        
        # Validate and format recommendations
        validation_result = validate_recommendation_formatting(recommendations)
        
        if not validation_result['success']:
            logger.warning(f"Recommendation validation issues: {validation_result['formatting_errors']}")
        
        # Format recommendations for web display
        formatted_recommendations = format_recommendations_for_web(recommendations)
        
        return render_template('results.html', 
                             recommendations=formatted_recommendations,
                             sales_count=len(sales_data),
                             validation_summary=validation_result,
                             sales_data=[{
                                 'date': record.date,
                                 'item': record.item,
                                 'quantity': record.quantity,
                                 'price': record.price
                             } for record in sales_data],  # Convert to JSON-serializable format
                             context=context,  # Pass for Q&A system
                             user_question=user_question)  # Pass the actual question asked
        
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return jsonify({'error': 'An error occurred processing your request'}), 500


@app.route('/ask_question', methods=['POST'])
def ask_question():
    """Handle interactive Q&A requests - NEW DECISION BOARD LOGIC"""
    try:
        data = request.get_json()
        
        if not data or 'question' not in data:
            return jsonify({'error': 'No question provided'}), 400
        
        question = data['question'].strip()
        if not question:
            return jsonify({'error': 'Question cannot be empty'}), 400
        
        # Get sales data and context from request or session
        # In the new flow, this should come from the same data used for initial recommendations
        sales_data_raw = data.get('sales_data', [])
        context_text = data.get('context', '')
        
        logger.info(f"Received question: {question}")
        logger.info(f"Sales data count: {len(sales_data_raw)}")
        logger.info(f"Context: {context_text[:100]}...")
        
        # Convert raw sales data back to SalesRecord objects
        sales_data = []
        if sales_data_raw:
            try:
                for record in sales_data_raw:
                    if isinstance(record, dict) and all(k in record for k in ['date', 'item', 'quantity', 'price']):
                        sales_data.append(SalesRecord(
                            record['date'], 
                            record['item'], 
                            record['quantity'], 
                            record['price']
                        ))
                logger.info(f"Converted {len(sales_data)} sales records")
                if sales_data:
                    logger.info(f"Sample items: {[record.item for record in sales_data[:5]]}")
            except Exception as e:
                logger.warning(f"Could not parse sales data from request: {str(e)}")
        else:
            logger.warning("No sales data received in request")
        
        # Create context object
        context = LocalContext(context_text)
        
        # Use Q&A system for refined analysis
        qa_system = get_qa_system()
        if not qa_system:
            return jsonify({
                'success': False,
                'error': 'Q&A system not available',
                'fallback_answer': {
                    'title': 'Service Temporarily Unavailable',
                    'decision': 'Yes, but use conservative approach.',
                    'action': 'Focus on your best-selling items and increase by 10% maximum.',
                    'why': 'When AI service is unavailable, stick to proven sellers with small increases.',
                    'confidence': 'Low',
                    'based_on': 'Conservative business practices'
                }
            }), 503
        
        # Get refined recommendation based on question
        result = qa_system.answer_question(question, sales_data, context)
        
        # Ensure the response has the correct format for the decision board
        if result['success'] and 'answer' in result:
            # The answer should already be in the correct format from interactive_qa.py
            return jsonify(result)
        else:
            # Return fallback with proper format
            return jsonify({
                'success': False,
                'error': result.get('error', 'Unknown error'),
                'fallback_answer': result.get('fallback_answer', {
                    'title': 'Safe Action Without AI',
                    'decision': 'Yes, but be very careful with quantities.',
                    'action': 'Check last week\'s top 3 items and increase stock by 10% only.',
                    'why': 'When data is limited, small increases on fast-moving items reduce risk.',
                    'confidence': 'Low',
                    'based_on': 'Limited data available'
                })
            })
        
    except Exception as e:
        logger.error(f"Error in Q&A: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'fallback_answer': {
                'title': 'Error Processing Question',
                'decision': 'Yes, but proceed with caution.',
                'action': 'Review your recent sales and make small adjustments only.',
                'why': 'An error occurred while processing your question, so conservative action is safest.',
                'confidence': 'Low',
                'based_on': 'Error recovery mode'
            }
        }), 500


@app.route('/get_suggested_questions', methods=['POST'])
def get_suggested_questions():
    """Get suggested questions based on sales data and context"""
    try:
        qa_system = get_qa_system()
        if not qa_system:
            return jsonify({
                'success': False,
                'suggestions': [
                    "What items should I stock for the upcoming festival?",
                    "How can I improve my sales?",
                    "What pricing strategy should I use?"
                ]
            })
        
        # Mock data for demonstration
        mock_sales = [
            SalesRecord("2024-01-15", "Rice 1kg", 45, 45.00),
            SalesRecord("2024-01-15", "Tea 250g", 20, 85.00),
        ]
        mock_context = LocalContext("Diwali festival coming in 2 weeks")
        
        suggestions = qa_system.get_suggested_questions(mock_sales, mock_context)
        
        return jsonify({
            'success': True,
            'suggestions': suggestions
        })
        
    except Exception as e:
        logger.error(f"Error getting suggestions: {str(e)}")
        return jsonify({
            'success': False,
            'suggestions': [
                "What items should I stock more?",
                "Should I change my prices?",
                "How can I increase profits?"
            ]
        })



@app.route('/demo/scenarios', methods=['GET'])
def get_demo_scenarios():
    """Get available demo scenarios"""
    try:
        demo_handler = get_demo_handler()
        scenarios = demo_handler.get_available_scenarios()
        return jsonify({'scenarios': scenarios, 'success': True})
    except Exception as e:
        logger.error(f"Error getting demo scenarios: {str(e)}")
        return jsonify({'error': 'Failed to load demo scenarios', 'success': False}), 500


@app.route('/demo/load/<scenario_name>', methods=['POST'])
def load_demo_scenario(scenario_name):
    """Load a specific demo scenario"""
    try:
        demo_handler = get_demo_handler()
        sales_data, context, success = demo_handler.load_demo_data(scenario_name)
        
        if not success:
            return jsonify({'error': f'Demo scenario "{scenario_name}" not found or failed to load'}), 404
        
        # Generate recommendations using Q&A system for consistency
        try:
            qa_system = get_qa_system()
            if qa_system:
                # Use Q&A system with a default question to generate initial recommendations
                default_question = "What should I do today for my shop?"
                logger.info(f"Using Q&A system for demo analysis with {len(sales_data)} sales records")
                qa_result = qa_system.answer_question(default_question, sales_data, context)
                
                if qa_result['success']:
                    # Convert Q&A response to recommendation format for display
                    answer = qa_result['answer']
                    recommendations = [
                        Recommendation(
                            item=answer['primary_decision']['item'],
                            action=answer['primary_decision']['action'],
                            explanation=answer['primary_decision']['why'],
                            confidence=answer['primary_decision']['confidence']
                        )
                    ]
                    logger.info(f"Demo Q&A system generated recommendation for: {answer['primary_decision']['item']}")
                else:
                    logger.error(f"Demo Q&A system failed: {qa_result.get('error', 'Unknown error')}")
                    # Create fallback recommendation based on demo data
                    if sales_data:
                        top_item = max(set(record.item for record in sales_data), 
                                     key=lambda item: sum(r.quantity for r in sales_data if r.item == item))
                        recommendations = [
                            Recommendation(
                                item=f"Demo: {top_item}",
                                action=f"Focus on {top_item} - your top seller in this scenario",
                                explanation=f"Based on demo scenario '{scenario_name}', {top_item} is performing well",
                                confidence="Demo Mode"
                            )
                        ]
                    else:
                        recommendations = [
                            Recommendation(
                                item="Demo Mode - No Data",
                                action="Demo scenario has no sales data",
                                explanation=f"Demo scenario '{scenario_name}' contains no sales records"
                            )
                        ]
            else:
                logger.error("Q&A system not available for demo")
                recommendations = [
                    Recommendation(
                        item="Demo Mode - System Error",
                        action="Q&A system is not available",
                        explanation="Please try again later"
                    )
                ]
            
        except Exception as e:
            logger.error(f"Error in demo recommendation generation: {str(e)}")
            recommendations = [
                Recommendation(
                    item="Demo Mode - Error",
                    action="System error occurred",
                    explanation=f"Demo error: {str(e)}"
                )
            ]
        
        # Validate and format recommendations
        validation_result = validate_recommendation_formatting(recommendations)
        
        if not validation_result['success']:
            logger.warning(f"Demo recommendation validation issues: {validation_result['formatting_errors']}")
        
        # Format recommendations for web display
        formatted_recommendations = format_recommendations_for_web(recommendations)
        
        return render_template('results.html', 
                             recommendations=formatted_recommendations,
                             sales_count=len(sales_data),
                             validation_summary=validation_result,
                             demo_mode=True,
                             scenario_name=scenario_name,
                             context_text=context.text,
                             sales_data=[{
                                 'date': record.date,
                                 'item': record.item,
                                 'quantity': record.quantity,
                                 'price': record.price
                             } for record in sales_data],  # Convert to JSON-serializable format
                             context=context)
        
    except Exception as e:
        logger.error(f"Error loading demo scenario: {str(e)}")
        return jsonify({'error': 'Failed to load demo scenario'}), 500


@app.route('/demo/context/<scenario_name>', methods=['GET'])
def get_demo_context(scenario_name):
    """Get context text for a specific demo scenario"""
    try:
        demo_handler = get_demo_handler()
        scenario = demo_handler.get_scenario_by_name(scenario_name)
        
        if not scenario:
            return jsonify({'error': f'Demo scenario "{scenario_name}" not found'}), 404
        
        return jsonify({
            'context': scenario['context'],
            'scenario_name': scenario['name'],
            'success': True
        })
        
    except Exception as e:
        logger.error(f"Error getting demo context: {str(e)}")
        return jsonify({'error': 'Failed to get demo context', 'success': False}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)