"""
AWS DynamoDB Handler for BharatSignal

Handles session management, caching, and analysis history storage in DynamoDB.
Implements TTL-based automatic cleanup and efficient data access patterns.
"""

import boto3
import os
import logging
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
from botocore.exceptions import ClientError, NoCredentialsError
import json
from decimal import Decimal

logger = logging.getLogger(__name__)


class DynamoDBHandler:
    """Handle DynamoDB operations for session and cache management"""
    
    def __init__(self, region: Optional[str] = None):
        """
        Initialize DynamoDB handler
        
        Args:
            region: AWS region (defaults to env variable)
        """
        self.region = region or os.getenv('AWS_REGION', 'us-east-1')
        self.sessions_table = os.getenv('DYNAMODB_SESSIONS_TABLE', 'BharatSignal_UserSessions')
        self.cache_table = os.getenv('DYNAMODB_CACHE_TABLE', 'BharatSignal_AnalysisCache')
        self.history_table = os.getenv('DYNAMODB_HISTORY_TABLE', 'BharatSignal_AnalysisHistory')
        
        try:
            self.dynamodb = boto3.resource(
                'dynamodb',
                region_name=self.region,
                aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
            )
            logger.info(f"DynamoDB handler initialized for region: {self.region}")
        except Exception as e:
            logger.error(f"Failed to initialize DynamoDB client: {str(e)}")
            raise
    
    # ===== Session Management =====
    
    def create_session(self, session_id: str, csv_s3_key: str, sales_summary: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Create a new user session
        
        Args:
            session_id: Unique session identifier
            csv_s3_key: S3 key for uploaded CSV
            sales_summary: Summary of sales data
            
        Returns:
            Tuple of (success, message)
        """
        try:
            table = self.dynamodb.Table(self.sessions_table)
            
            now = datetime.utcnow()
            expires_at = now + timedelta(hours=24)
            
            item = {
                'session_id': session_id,
                'created_at': now.isoformat(),
                'expires_at': int(expires_at.timestamp()),
                'csv_s3_key': csv_s3_key,
                'sales_data_summary': self._convert_to_dynamodb_format(sales_summary)
            }
            
            table.put_item(Item=item)
            logger.info(f"Session created: {session_id}")
            return True, "Session created successfully"
            
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            logger.error(f"Session creation failed: {error_code}")
            return False, f"Session creation failed: {error_code}"
        except Exception as e:
            logger.error(f"Unexpected error creating session: {str(e)}")
            return False, f"Session creation error: {str(e)}"
    
    def get_session(self, session_id: str) -> Tuple[bool, Optional[Dict], str]:
        """
        Retrieve session data
        
        Args:
            session_id: Session identifier
            
        Returns:
            Tuple of (success, session_data, message)
        """
        try:
            table = self.dynamodb.Table(self.sessions_table)
            
            response = table.get_item(Key={'session_id': session_id})
            
            if 'Item' in response:
                item = self._convert_from_dynamodb_format(response['Item'])
                logger.info(f"Session retrieved: {session_id}")
                return True, item, "Session found"
            else:
                logger.warning(f"Session not found: {session_id}")
                return False, None, "Session not found"
                
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            logger.error(f"Session retrieval failed: {error_code}")
            return False, None, f"Session retrieval failed: {error_code}"
        except Exception as e:
            logger.error(f"Unexpected error retrieving session: {str(e)}")
            return False, None, f"Session retrieval error: {str(e)}"
    
    def update_session(self, session_id: str, updates: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Update session data
        
        Args:
            session_id: Session identifier
            updates: Dictionary of fields to update
            
        Returns:
            Tuple of (success, message)
        """
        try:
            table = self.dynamodb.Table(self.sessions_table)
            
            # Build update expression
            update_expr = "SET "
            expr_attr_values = {}
            expr_attr_names = {}
            
            for i, (key, value) in enumerate(updates.items()):
                attr_name = f"#attr{i}"
                attr_value = f":val{i}"
                update_expr += f"{attr_name} = {attr_value}, "
                expr_attr_names[attr_name] = key
                expr_attr_values[attr_value] = self._convert_to_dynamodb_format(value)
            
            update_expr = update_expr.rstrip(', ')
            
            table.update_item(
                Key={'session_id': session_id},
                UpdateExpression=update_expr,
                ExpressionAttributeNames=expr_attr_names,
                ExpressionAttributeValues=expr_attr_values
            )
            
            logger.info(f"Session updated: {session_id}")
            return True, "Session updated successfully"
            
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            logger.error(f"Session update failed: {error_code}")
            return False, f"Session update failed: {error_code}"
        except Exception as e:
            logger.error(f"Unexpected error updating session: {str(e)}")
            return False, f"Session update error: {str(e)}"
    
    # ===== Cache Management =====
    
    def cache_analysis(self, cache_key: str, question: str, answer: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Cache analysis result
        
        Args:
            cache_key: Unique cache key (hash of question + session)
            question: User question
            answer: Analysis answer
            
        Returns:
            Tuple of (success, message)
        """
        try:
            table = self.dynamodb.Table(self.cache_table)
            
            now = datetime.utcnow()
            expires_at = now + timedelta(hours=1)  # 1-hour TTL
            
            item = {
                'cache_key': cache_key,
                'question': question,
                'answer': self._convert_to_dynamodb_format(answer),
                'created_at': now.isoformat(),
                'expires_at': int(expires_at.timestamp())
            }
            
            table.put_item(Item=item)
            logger.info(f"Analysis cached: {cache_key}")
            return True, "Analysis cached successfully"
            
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            logger.error(f"Cache write failed: {error_code}")
            return False, f"Cache write failed: {error_code}"
        except Exception as e:
            logger.error(f"Unexpected error caching analysis: {str(e)}")
            return False, f"Cache write error: {str(e)}"
    
    def get_cached_analysis(self, cache_key: str) -> Tuple[bool, Optional[Dict], str]:
        """
        Retrieve cached analysis
        
        Args:
            cache_key: Cache key
            
        Returns:
            Tuple of (success, cached_data, message)
        """
        try:
            table = self.dynamodb.Table(self.cache_table)
            
            response = table.get_item(Key={'cache_key': cache_key})
            
            if 'Item' in response:
                item = self._convert_from_dynamodb_format(response['Item'])
                
                # Check if expired (TTL might not have cleaned up yet)
                expires_at = item.get('expires_at', 0)
                if datetime.utcnow().timestamp() > expires_at:
                    logger.info(f"Cache expired: {cache_key}")
                    return False, None, "Cache expired"
                
                logger.info(f"Cache hit: {cache_key}")
                return True, item, "Cache hit"
            else:
                logger.info(f"Cache miss: {cache_key}")
                return False, None, "Cache miss"
                
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            logger.error(f"Cache read failed: {error_code}")
            return False, None, f"Cache read failed: {error_code}"
        except Exception as e:
            logger.error(f"Unexpected error reading cache: {str(e)}")
            return False, None, f"Cache read error: {str(e)}"
    
    # ===== History Management =====
    
    def add_to_history(self, session_id: str, question: str, answer: Dict[str, Any], 
                       items_analyzed: List[str]) -> Tuple[bool, str]:
        """
        Add analysis to history
        
        Args:
            session_id: Session identifier
            question: User question
            answer: Analysis answer
            items_analyzed: List of items analyzed
            
        Returns:
            Tuple of (success, message)
        """
        try:
            table = self.dynamodb.Table(self.history_table)
            
            now = datetime.utcnow()
            timestamp = int(now.timestamp() * 1000)  # Milliseconds for sort key
            expires_at = now + timedelta(days=7)  # 7-day TTL
            
            item = {
                'session_id': session_id,
                'timestamp': timestamp,
                'question': question,
                'answer': self._convert_to_dynamodb_format(answer),
                'items_analyzed': items_analyzed,
                'created_at': now.isoformat(),
                'expires_at': int(expires_at.timestamp())
            }
            
            table.put_item(Item=item)
            logger.info(f"Added to history: {session_id}")
            return True, "Added to history successfully"
            
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            logger.error(f"History write failed: {error_code}")
            return False, f"History write failed: {error_code}"
        except Exception as e:
            logger.error(f"Unexpected error adding to history: {str(e)}")
            return False, f"History write error: {str(e)}"
    
    def get_session_history(self, session_id: str, limit: int = 10) -> Tuple[bool, List[Dict], str]:
        """
        Retrieve session history
        
        Args:
            session_id: Session identifier
            limit: Maximum number of items to retrieve
            
        Returns:
            Tuple of (success, history_items, message)
        """
        try:
            table = self.dynamodb.Table(self.history_table)
            
            response = table.query(
                KeyConditionExpression='session_id = :sid',
                ExpressionAttributeValues={':sid': session_id},
                ScanIndexForward=False,  # Descending order (newest first)
                Limit=limit
            )
            
            items = [self._convert_from_dynamodb_format(item) for item in response.get('Items', [])]
            logger.info(f"Retrieved {len(items)} history items for session {session_id}")
            return True, items, f"Found {len(items)} history items"
            
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            logger.error(f"History read failed: {error_code}")
            return False, [], f"History read failed: {error_code}"
        except Exception as e:
            logger.error(f"Unexpected error reading history: {str(e)}")
            return False, [], f"History read error: {str(e)}"
    
    # ===== Table Management =====
    
    def create_tables_if_not_exist(self) -> Tuple[bool, str]:
        """
        Create DynamoDB tables if they don't exist
        
        Returns:
            Tuple of (success, message)
        """
        try:
            # Create Sessions table
            self._create_sessions_table()
            
            # Create Cache table
            self._create_cache_table()
            
            # Create History table
            self._create_history_table()
            
            logger.info("All DynamoDB tables created/verified")
            return True, "Tables created successfully"
            
        except Exception as e:
            logger.error(f"Table creation failed: {str(e)}")
            return False, f"Table creation failed: {str(e)}"
    
    def _create_sessions_table(self):
        """Create UserSessions table"""
        try:
            table = self.dynamodb.create_table(
                TableName=self.sessions_table,
                KeySchema=[
                    {'AttributeName': 'session_id', 'KeyType': 'HASH'}
                ],
                AttributeDefinitions=[
                    {'AttributeName': 'session_id', 'AttributeType': 'S'}
                ],
                BillingMode='PAY_PER_REQUEST'
            )
            
            # Wait for table to be created
            table.meta.client.get_waiter('table_exists').wait(TableName=self.sessions_table)
            
            # Enable TTL
            table.meta.client.update_time_to_live(
                TableName=self.sessions_table,
                TimeToLiveSpecification={
                    'Enabled': True,
                    'AttributeName': 'expires_at'
                }
            )
            
            logger.info(f"Created table: {self.sessions_table}")
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceInUseException':
                logger.info(f"Table already exists: {self.sessions_table}")
            else:
                raise
    
    def _create_cache_table(self):
        """Create AnalysisCache table"""
        try:
            table = self.dynamodb.create_table(
                TableName=self.cache_table,
                KeySchema=[
                    {'AttributeName': 'cache_key', 'KeyType': 'HASH'}
                ],
                AttributeDefinitions=[
                    {'AttributeName': 'cache_key', 'AttributeType': 'S'}
                ],
                BillingMode='PAY_PER_REQUEST'
            )
            
            table.meta.client.get_waiter('table_exists').wait(TableName=self.cache_table)
            
            # Enable TTL
            table.meta.client.update_time_to_live(
                TableName=self.cache_table,
                TimeToLiveSpecification={
                    'Enabled': True,
                    'AttributeName': 'expires_at'
                }
            )
            
            logger.info(f"Created table: {self.cache_table}")
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceInUseException':
                logger.info(f"Table already exists: {self.cache_table}")
            else:
                raise
    
    def _create_history_table(self):
        """Create AnalysisHistory table"""
        try:
            table = self.dynamodb.create_table(
                TableName=self.history_table,
                KeySchema=[
                    {'AttributeName': 'session_id', 'KeyType': 'HASH'},
                    {'AttributeName': 'timestamp', 'KeyType': 'RANGE'}
                ],
                AttributeDefinitions=[
                    {'AttributeName': 'session_id', 'AttributeType': 'S'},
                    {'AttributeName': 'timestamp', 'AttributeType': 'N'}
                ],
                BillingMode='PAY_PER_REQUEST'
            )
            
            table.meta.client.get_waiter('table_exists').wait(TableName=self.history_table)
            
            # Enable TTL
            table.meta.client.update_time_to_live(
                TableName=self.history_table,
                TimeToLiveSpecification={
                    'Enabled': True,
                    'AttributeName': 'expires_at'
                }
            )
            
            logger.info(f"Created table: {self.history_table}")
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceInUseException':
                logger.info(f"Table already exists: {self.history_table}")
            else:
                raise
    
    # ===== Helper Methods =====
    
    def _convert_to_dynamodb_format(self, data: Any) -> Any:
        """Convert Python types to DynamoDB-compatible types"""
        if isinstance(data, dict):
            return {k: self._convert_to_dynamodb_format(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._convert_to_dynamodb_format(item) for item in data]
        elif isinstance(data, float):
            return Decimal(str(data))
        else:
            return data
    
    def _convert_from_dynamodb_format(self, data: Any) -> Any:
        """Convert DynamoDB types to Python types"""
        if isinstance(data, dict):
            return {k: self._convert_from_dynamodb_format(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._convert_from_dynamodb_format(item) for item in data]
        elif isinstance(data, Decimal):
            return float(data)
        else:
            return data


def create_dynamodb_handler(region: Optional[str] = None) -> DynamoDBHandler:
    """
    Factory function to create DynamoDB handler
    
    Args:
        region: AWS region
        
    Returns:
        DynamoDBHandler instance
    """
    return DynamoDBHandler(region)
