"""
IBM Cloud Object Storage utilities for SCDO
Handles document storage and retrieval
"""

import os
import yaml
from typing import Optional, BinaryIO
from pathlib import Path
import logging

try:
    import ibm_boto3
    from ibm_botocore.client import Config
except ImportError:
    logging.warning("IBM boto3 not installed. Install with: pip install ibm-cos-sdk")


class CloudStorage:
    """IBM Cloud Object Storage client"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize cloud storage client
        
        Args:
            config_path: Path to IBM config YAML file
        """
        self.logger = logging.getLogger(__name__)
        self.config = self._load_config(config_path)
        self.client = self._initialize_client()
        
    def _load_config(self, config_path: Optional[str] = None) -> dict:
        """Load configuration from YAML file"""
        if config_path is None:
            config_path = Path(__file__).parent.parent.parent / "configs" / "ibm_config.yaml"
            
        with open(config_path, 'r') as f:
            config_data = yaml.safe_load(f)
            
        return config_data['cloud_object_storage']
        
    def _initialize_client(self):
        """Initialize IBM COS client"""
        try:
            api_key = os.getenv('IBM_COS_API_KEY', self.config.get('api_key'))
            service_instance_id = os.getenv('IBM_COS_INSTANCE_ID', 
                                           self.config.get('service_instance_id'))
            
            client = ibm_boto3.client(
                's3',
                ibm_api_key_id=api_key,
                ibm_service_instance_id=service_instance_id,
                config=Config(signature_version='oauth'),
                endpoint_url=self.config['endpoint_url']
            )
            
            self.logger.info("IBM Cloud Object Storage client initialized")
            return client
            
        except Exception as e:
            self.logger.error(f"Failed to initialize COS client: {e}")
            raise
            
    def upload_file(self, file_path: str, object_name: Optional[str] = None) -> bool:
        """
        Upload file to cloud storage
        
        Args:
            file_path: Local file path
            object_name: S3 object name (defaults to file basename)
            
        Returns:
            True if successful
        """
        if object_name is None:
            object_name = Path(file_path).name
            
        try:
            self.client.upload_file(
                Filename=file_path,
                Bucket=self.config['bucket'],
                Key=object_name
            )
            self.logger.info(f"Uploaded {file_path} to {object_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Upload failed: {e}")
            return False
            
    def download_file(self, object_name: str, file_path: str) -> bool:
        """
        Download file from cloud storage
        
        Args:
            object_name: S3 object name
            file_path: Local destination path
            
        Returns:
            True if successful
        """
        try:
            self.client.download_file(
                Bucket=self.config['bucket'],
                Key=object_name,
                Filename=file_path
            )
            self.logger.info(f"Downloaded {object_name} to {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Download failed: {e}")
            return False
            
    def list_files(self, prefix: str = "") -> list:
        """
        List files in bucket
        
        Args:
            prefix: Filter by prefix
            
        Returns:
            List of object names
        """
        try:
            response = self.client.list_objects_v2(
                Bucket=self.config['bucket'],
                Prefix=prefix
            )
            
            return [obj['Key'] for obj in response.get('Contents', [])]
            
        except Exception as e:
            self.logger.error(f"List failed: {e}")
            return []
