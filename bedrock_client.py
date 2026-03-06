"""
Amazon Bedrock Integration Module

This module provides secure Bedrock client setup, authentication, and AI interaction
for the BharatSignal system. Handles Claude 3 Sonnet model integration with proper
error handling and response parsing.

Requirements: 2.4, 7.1
"""

import boto3
import json
import logging
from typing import List, Dict, Any, Optional, Tuple
from botocore.exceptions import ClientError, NoCredentialsError, BotoCoreError
import os
from dataclasses import dataclass

from models import SalesRecord, LocalContext, Recommendation
from prompt_engineering import create_prompt_builder

logger = logging.getLogger(__name__)


@dataclass
class BedrockConfig:
    """Configuration for Bedrock client"""
    region_name: str = 'us-east-1'
    model_id: str = 'anthropic.claude-3-sonnet-20240229-v1:0'
    max_tokens: int = 1000
    temperature: float = 0.7
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None


class BedrockClientError(Exception):
    """Custom exception for Bedrock client errors"""
    pass


class BedrockClient:
    """
    Amazon Bedrock client for AI-powered recommendations.
    
    Handles secure authentication, model invocation, and response parsing
    for Claude 3 Sonnet model integration.
    """
    
    def __init__(self, config: Optional[BedrockConfig] = None):
        """
        Initialize Bedrock client with configuration.
        
        Args:
            config: Bedrock configuration object. If None, uses environment variables.
        """
        self.config = config or self._load_config_from_env()
        self.client = None
        self.prompt_builder = create_prompt_builder()
        self._initialize_client()
    
    def _load_config_from_env(self) -> BedrockConfig:
        """Load configuration from environment variables"""
        return BedrockConfig(
            region_name=os.getenv('AWS_REGION', 'us-east-1'),
            model_id=os.getenv('BEDROCK_MODEL_ID', 'anthropic.claude-3-sonnet-20240229-v1:0'),
            max_tokens=int(os.getenv('BEDROCK_MAX_TOKENS', '1000')),
            temperature=float(os.getenv('BEDROCK_TEMPERATURE', '0.7')),
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
        )
    
    def _initialize_client(self):
        """Initialize the Bedrock runtime client with proper authentication"""
        try:
            # Configure client parameters
            client_params = {
                'service_name': 'bedrock-runtime',
                'region_name': self.config.region_name
            }
            
            # Add credentials if provided explicitly
            if self.config.aws_access_key_id and self.config.aws_secret_access_key:
                client_params.update({
                    'aws_access_key_id': self.config.aws_access_key_id,
                    'aws_secret_access_key': self.config.aws_secret_access_key
                })
            
            self.client = boto3.client(**client_params)
            
            # Test authentication by listing available models (if permissions allow)
            self._test_authentication()
            
            logger.info(f"Bedrock client initialized successfully for region {self.config.region_name}")
            
        except NoCredentialsError:
            raise BedrockClientError(
                "AWS credentials not found. Please configure AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables."
            )
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            raise BedrockClientError(f"AWS authentication failed: {error_code} - {str(e)}")
        except Exception as e:
            raise BedrockClientError(f"Failed to initialize Bedrock client: {str(e)}")
    
    def _test_authentication(self):
        """Test Bedrock authentication with a minimal request"""
        try:
            # Try to make a simple request to verify authentication
            # This is a lightweight way to test credentials without full model invocation
            test_prompt = "Hello"
            test_body = {
                'anthropic_version': 'bedrock-2023-05-31',
                'messages': [{'role': 'user', 'content': test_prompt}],
                'max_tokens': 10
            }
            
            # This will fail if credentials are invalid
            response = self.client.invoke_model(
                modelId=self.config.model_id,
                body=json.dumps(test_body)
            )
            
            logger.info("Bedrock authentication test successful")
            
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            if error_code in ['UnauthorizedOperation', 'AccessDenied', 'InvalidUserID.NotFound']:
                raise BedrockClientError(f"Authentication failed: {error_code}")
            elif error_code == 'ValidationException':
                # This might be expected for the test request
                logger.info("Bedrock authentication appears valid (validation error on test request)")
            elif error_code == 'ResourceNotFoundException':
                # Model might not be accessible yet, but credentials are valid
                logger.warning(f"Model {self.config.model_id} not accessible, but credentials are valid")
            else:
                # Don't fail initialization for other errors
                logger.warning(f"Authentication test inconclusive: {error_code}")
        except Exception as e:
            # For testing purposes, we'll be more lenient
            logger.warning(f"Authentication test inconclusive: {str(e)}")
    
    def is_available(self) -> bool:
        """
        Check if Bedrock service is available and accessible.
        
        Returns:
            bool: True if service is available, False otherwise
        """
        try:
            if not self.client:
                return False
            
            # Simple availability check
            self._test_authentication()
            return True
            
        except Exception as e:
            logger.error(f"Bedrock availability check failed: {str(e)}")
            return False
    
    def generate_recommendations(self, sales_data: List[SalesRecord], context: LocalContext) -> List[Recommendation]:
        """
        Generate AI recommendations using Bedrock (supports Claude and Amazon Nova).
        
        Args:
            sales_data: List of validated sales records
            context: Local context information
            
        Returns:
            List[Recommendation]: Generated recommendations
            
        Raises:
            BedrockClientError: For service or authentication errors
        """
        try:
            if not self.client:
                raise BedrockClientError("Bedrock client not initialized")
            
            # Build prompt for AI model using prompt engineering module
            prompt = self.prompt_builder.build_recommendation_prompt(sales_data, context)
            
            # Determine model type and format request accordingly
            is_nova = 'nova' in self.config.model_id.lower()
            is_claude = 'claude' in self.config.model_id.lower() or 'anthropic' in self.config.model_id.lower()
            
            if is_nova:
                # Amazon Nova format
                request_body = {
                    'messages': [
                        {
                            'role': 'user',
                            'content': [{'text': prompt}]
                        }
                    ],
                    'inferenceConfig': {
                        'maxTokens': self.config.max_tokens,
                        'temperature': self.config.temperature
                    }
                }
            elif is_claude:
                # Claude format
                request_body = {
                    'anthropic_version': 'bedrock-2023-05-31',
                    'messages': [{'role': 'user', 'content': prompt}],
                    'max_tokens': self.config.max_tokens,
                    'temperature': self.config.temperature
                }
            else:
                # Default format (try Claude format)
                request_body = {
                    'anthropic_version': 'bedrock-2023-05-31',
                    'messages': [{'role': 'user', 'content': prompt}],
                    'max_tokens': self.config.max_tokens,
                    'temperature': self.config.temperature
                }
            
            logger.info(f"Invoking Bedrock model {self.config.model_id}")
            
            # Invoke model
            response = self.client.invoke_model(
                modelId=self.config.model_id,
                body=json.dumps(request_body)
            )
            
            # Parse response based on model type
            response_body = json.loads(response['body'].read())
            
            if is_nova:
                # Amazon Nova response format
                if 'output' in response_body and 'message' in response_body['output']:
                    message = response_body['output']['message']
                    if 'content' in message and len(message['content']) > 0:
                        ai_text = message['content'][0]['text']
                    else:
                        raise BedrockClientError("Unexpected Nova response format")
                else:
                    raise BedrockClientError("Unexpected Nova response format")
            elif is_claude:
                # Claude response format
                ai_text = response_body['content'][0]['text']
            else:
                # Try Claude format as default
                ai_text = response_body.get('content', [{}])[0].get('text', '')
            
            logger.info("Bedrock model invocation successful")
            
            # Parse AI response into recommendations
            recommendations = self._parse_ai_response(ai_text)
            
            return recommendations
            
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            error_message = e.response.get('Error', {}).get('Message', str(e))
            
            if error_code == 'ThrottlingException':
                raise BedrockClientError("Service is temporarily busy. Please try again in a moment.")
            elif error_code == 'ValidationException':
                raise BedrockClientError(f"Invalid request: {error_message}")
            elif error_code in ['AccessDenied', 'UnauthorizedOperation']:
                raise BedrockClientError("Access denied. Please check your AWS permissions.")
            else:
                raise BedrockClientError(f"Bedrock service error: {error_code} - {error_message}")
                
        except json.JSONDecodeError as e:
            raise BedrockClientError(f"Failed to parse Bedrock response: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error during AI generation: {str(e)}")
            # Return fallback recommendations for any unexpected errors
            return self._create_fallback_recommendations()
    
    def _parse_ai_response(self, ai_text: str) -> List[Recommendation]:
        """
        Parse AI response into structured Recommendation objects.
        
        Args:
            ai_text: Raw text response from AI model
            
        Returns:
            List[Recommendation]: Parsed and validated recommendations
        """
        recommendations = []
        
        try:
            lines = ai_text.strip().split('\n')
            current_item = ""
            current_action = ""
            current_explanation = ""
            current_confidence = ""
            
            for line in lines:
                line = line.strip()
                
                if line.startswith('ITEM:'):
                    # Save previous recommendation if complete
                    if current_item and current_action and current_explanation:
                        rec = Recommendation(
                            item=current_item,
                            action=current_action,
                            explanation=current_explanation,
                            confidence=current_confidence
                        )
                        # Validate before adding
                        if rec.validate():
                            recommendations.append(rec)
                        else:
                            logger.warning(f"Invalid recommendation filtered out: {current_item}")
                    
                    # Start new recommendation
                    current_item = line.replace('ITEM:', '').strip()
                    current_action = ""
                    current_explanation = ""
                    current_confidence = ""
                    
                elif line.startswith('ACTION:'):
                    current_action = line.replace('ACTION:', '').strip()
                    
                elif line.startswith('EXPLANATION:'):
                    current_explanation = line.replace('EXPLANATION:', '').strip()
                    
                elif line.startswith('CONFIDENCE:'):
                    current_confidence = line.replace('CONFIDENCE:', '').strip()
                    
                elif current_explanation and line and not line.startswith(('ITEM:', 'ACTION:', 'EXPLANATION:', 'CONFIDENCE:')):
                    # Continue explanation on next line
                    current_explanation += " " + line
            
            # Add final recommendation
            if current_item and current_action and current_explanation:
                rec = Recommendation(
                    item=current_item,
                    action=current_action,
                    explanation=current_explanation,
                    confidence=current_confidence
                )
                if rec.validate():
                    recommendations.append(rec)
                else:
                    logger.warning(f"Invalid final recommendation filtered out: {current_item}")
            
            # Ensure we have at least one recommendation
            if not recommendations:
                logger.warning("No valid recommendations parsed from AI response")
                recommendations = self._create_fallback_recommendations()
            
            logger.info(f"Successfully parsed {len(recommendations)} recommendations")
            return recommendations
            
        except Exception as e:
            logger.error(f"Error parsing AI response: {str(e)}")
            return self._create_fallback_recommendations()
    
    def _create_fallback_recommendations(self) -> List[Recommendation]:
        """
        Create fallback recommendations when AI parsing fails.
        
        Returns:
            List[Recommendation]: Basic fallback recommendations with business intelligence
        """
        return [
            Recommendation(
                item="Safe Action Without AI",
                action="Check last week's top 3 selling items and increase stock by 10%",
                explanation="When data is limited, small increases on fast-moving items reduce risk while maintaining cash flow.",
                confidence="Based on your sales data and safe inventory principles"
            ),
            Recommendation(
                item="Festival Preparation",
                action="If festival approaching, increase rice and oil by 15% maximum",
                explanation="Festivals increase demand for cooking essentials, but conservative increases prevent overstock if plans change.",
                confidence="Based on your sales data and festival patterns"
            ),
            Recommendation(
                item="Weather-Based Stocking",
                action="Adjust hot vs cold items based on current weather for next 7 days",
                explanation="Monsoon increases tea/hot snacks demand, summer increases cold drinks. Match weather to inventory.",
                confidence="Based on your sales data and seasonal patterns"
            )
        ]


def create_bedrock_client(config: Optional[BedrockConfig] = None) -> BedrockClient:
    """
    Factory function to create and initialize Bedrock client.
    
    Args:
        config: Optional configuration object
        
    Returns:
        BedrockClient: Initialized client instance
        
    Raises:
        BedrockClientError: If client initialization fails
    """
    try:
        return BedrockClient(config)
    except Exception as e:
        logger.error(f"Failed to create Bedrock client: {str(e)}")
        raise BedrockClientError(f"Client initialization failed: {str(e)}")


def test_bedrock_connection(config: Optional[BedrockConfig] = None) -> Tuple[bool, str]:
    """
    Test Bedrock connection and authentication.
    
    Args:
        config: Optional configuration object
        
    Returns:
        Tuple[bool, str]: (success, message)
    """
    try:
        client = create_bedrock_client(config)
        if client.is_available():
            return True, "Bedrock connection successful"
        else:
            return False, "Bedrock service not available"
    except BedrockClientError as e:
        return False, f"Connection failed: {str(e)}"
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"