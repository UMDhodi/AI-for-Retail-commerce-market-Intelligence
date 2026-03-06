"""
AWS S3 Handler for BharatSignal

Handles CSV file uploads, storage, and retrieval from Amazon S3.
Implements secure file handling with encryption and lifecycle policies.
"""

import boto3
import os
import logging
from typing import Tuple, Optional
from datetime import datetime
from botocore.exceptions import ClientError, NoCredentialsError
import hashlib
import json

logger = logging.getLogger(__name__)


class S3Handler:
    """Handle S3 operations for CSV file storage"""
    
    def __init__(self, bucket_name: Optional[str] = None, region: Optional[str] = None):
        """
        Initialize S3 handler
        
        Args:
            bucket_name: S3 bucket name (defaults to env variable)
            region: AWS region (defaults to env variable)
        """
        self.bucket_name = bucket_name or os.getenv('S3_BUCKET_NAME', 'bharatsignal-csv-uploads')
        self.region = region or os.getenv('AWS_REGION', 'us-east-1')
        
        try:
            self.s3_client = boto3.client(
                's3',
                region_name=self.region,
                aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
            )
            logger.info(f"S3 handler initialized for bucket: {self.bucket_name}")
        except Exception as e:
            logger.error(f"Failed to initialize S3 client: {str(e)}")
            raise
    
    def upload_csv(self, file_content: bytes, session_id: str, filename: str) -> Tuple[bool, str, Optional[str]]:
        """
        Upload CSV file to S3
        
        Args:
            file_content: CSV file content as bytes
            session_id: User session ID
            filename: Original filename
            
        Returns:
            Tuple of (success, message, s3_key)
        """
        try:
            # Generate unique S3 key
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            file_hash = hashlib.md5(file_content).hexdigest()[:8]
            s3_key = f"{session_id}/{timestamp}_{file_hash}_{filename}"
            
            # Upload with server-side encryption
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=file_content,
                ServerSideEncryption='AES256',
                ContentType='text/csv',
                Metadata={
                    'session_id': session_id,
                    'original_filename': filename,
                    'upload_timestamp': timestamp
                }
            )
            
            logger.info(f"CSV uploaded successfully: {s3_key}")
            return True, "File uploaded successfully", s3_key
            
        except NoCredentialsError:
            logger.error("AWS credentials not found")
            return False, "AWS credentials not configured", None
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            logger.error(f"S3 upload failed: {error_code}")
            return False, f"Upload failed: {error_code}", None
        except Exception as e:
            logger.error(f"Unexpected error during upload: {str(e)}")
            return False, f"Upload error: {str(e)}", None
    
    def download_csv(self, s3_key: str) -> Tuple[bool, Optional[bytes], str]:
        """
        Download CSV file from S3
        
        Args:
            s3_key: S3 object key
            
        Returns:
            Tuple of (success, file_content, message)
        """
        try:
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            
            file_content = response['Body'].read()
            logger.info(f"CSV downloaded successfully: {s3_key}")
            return True, file_content, "File downloaded successfully"
            
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            if error_code == 'NoSuchKey':
                logger.error(f"File not found: {s3_key}")
                return False, None, "File not found"
            else:
                logger.error(f"S3 download failed: {error_code}")
                return False, None, f"Download failed: {error_code}"
        except Exception as e:
            logger.error(f"Unexpected error during download: {str(e)}")
            return False, None, f"Download error: {str(e)}"
    
    def delete_csv(self, s3_key: str) -> Tuple[bool, str]:
        """
        Delete CSV file from S3
        
        Args:
            s3_key: S3 object key
            
        Returns:
            Tuple of (success, message)
        """
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            
            logger.info(f"CSV deleted successfully: {s3_key}")
            return True, "File deleted successfully"
            
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            logger.error(f"S3 delete failed: {error_code}")
            return False, f"Delete failed: {error_code}"
        except Exception as e:
            logger.error(f"Unexpected error during delete: {str(e)}")
            return False, f"Delete error: {str(e)}"
    
    def list_session_files(self, session_id: str) -> Tuple[bool, list, str]:
        """
        List all CSV files for a session
        
        Args:
            session_id: User session ID
            
        Returns:
            Tuple of (success, file_list, message)
        """
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=f"{session_id}/"
            )
            
            files = []
            if 'Contents' in response:
                for obj in response['Contents']:
                    files.append({
                        'key': obj['Key'],
                        'size': obj['Size'],
                        'last_modified': obj['LastModified'].isoformat()
                    })
            
            logger.info(f"Listed {len(files)} files for session {session_id}")
            return True, files, f"Found {len(files)} files"
            
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            logger.error(f"S3 list failed: {error_code}")
            return False, [], f"List failed: {error_code}"
        except Exception as e:
            logger.error(f"Unexpected error during list: {str(e)}")
            return False, [], f"List error: {str(e)}"
    
    def create_bucket_if_not_exists(self) -> Tuple[bool, str]:
        """
        Create S3 bucket if it doesn't exist
        
        Returns:
            Tuple of (success, message)
        """
        try:
            # Check if bucket exists
            try:
                self.s3_client.head_bucket(Bucket=self.bucket_name)
                logger.info(f"Bucket {self.bucket_name} already exists")
                return True, "Bucket already exists"
            except ClientError as e:
                error_code = e.response.get('Error', {}).get('Code', 'Unknown')
                if error_code == '404':
                    # Bucket doesn't exist, create it
                    if self.region == 'us-east-1':
                        self.s3_client.create_bucket(Bucket=self.bucket_name)
                    else:
                        self.s3_client.create_bucket(
                            Bucket=self.bucket_name,
                            CreateBucketConfiguration={'LocationConstraint': self.region}
                        )
                    
                    # Enable versioning
                    self.s3_client.put_bucket_versioning(
                        Bucket=self.bucket_name,
                        VersioningConfiguration={'Status': 'Enabled'}
                    )
                    
                    # Set lifecycle policy (30-day expiration)
                    lifecycle_policy = {
                        'Rules': [
                            {
                                'ID': 'DeleteOldCSVs',
                                'Status': 'Enabled',
                                'Prefix': '',
                                'Expiration': {'Days': 30}
                            }
                        ]
                    }
                    self.s3_client.put_bucket_lifecycle_configuration(
                        Bucket=self.bucket_name,
                        LifecycleConfiguration=lifecycle_policy
                    )
                    
                    logger.info(f"Bucket {self.bucket_name} created successfully")
                    return True, "Bucket created successfully"
                else:
                    raise
                    
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            logger.error(f"Bucket creation failed: {error_code}")
            return False, f"Bucket creation failed: {error_code}"
        except Exception as e:
            logger.error(f"Unexpected error during bucket creation: {str(e)}")
            return False, f"Bucket creation error: {str(e)}"


def create_s3_handler(bucket_name: Optional[str] = None, region: Optional[str] = None) -> S3Handler:
    """
    Factory function to create S3 handler
    
    Args:
        bucket_name: S3 bucket name
        region: AWS region
        
    Returns:
        S3Handler instance
    """
    return S3Handler(bucket_name, region)
