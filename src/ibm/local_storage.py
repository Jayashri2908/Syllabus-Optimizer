"""
Local File Storage for SCDO (FREE - No Cloud Storage)
Handles document storage and retrieval using local filesystem
"""

import os
import shutil
from typing import Optional
from pathlib import Path
import logging


class LocalStorage:
    """Local file storage client (replaces IBM Cloud Object Storage)"""
    
    def __init__(self, base_dir: Optional[str] = None):
        """
        Initialize local storage
        
        Args:
            base_dir: Base directory for storage (defaults to project root)
        """
        self.logger = logging.getLogger(__name__)
        
        if base_dir is None:
            # Resolve project root relative to this file: src/ibm/ -> project root
            base_dir = Path(__file__).resolve().parent.parent.parent
        
        self.base_dir = Path(base_dir)
        
        # Create storage directories
        self.upload_dir = self.base_dir / "uploads"
        self.output_dir = self.base_dir / "output"
        self.cache_dir = self.base_dir / "cache"
        
        self._create_directories()
        
    def _create_directories(self):
        """Create storage directories if they don't exist"""
        for directory in [self.upload_dir, self.output_dir, self.cache_dir]:
            directory.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"Storage directory ready: {directory}")

    async def save_upload(self, upload_file, content: bytes = None, filename: str = None) -> str:
        """
        Save FastAPI UploadFile to local storage
        
        Args:
            upload_file: FastAPI UploadFile object
            content: Pre-read file content (skips reading from upload_file if provided)
            filename: Override filename (use sanitized name to prevent path traversal)
            
        Returns:
            Path to saved file
        """
        try:
            safe_filename = filename if filename else upload_file.filename
            dest_path = self.upload_dir / safe_filename
            
            # Use pre-read content or read from upload_file
            if content is None:
                content = await upload_file.read()
            
            # Write to file
            with open(dest_path, "wb") as f:
                f.write(content)
                
            self.logger.info(f"Saved upload to {dest_path}")
            return str(dest_path)
            
        except Exception as e:
            self.logger.error(f"Save upload failed: {e}")
            raise e
            
    def upload_file(self, file_path: str, object_name: Optional[str] = None, 
                   storage_type: str = "uploads") -> bool:
        """
        Copy file to local storage
        
        Args:
            file_path: Source file path
            object_name: Destination filename (defaults to source basename)
            storage_type: Storage category (uploads, output, cache)
            
        Returns:
            True if successful
        """
        if object_name is None:
            object_name = Path(file_path).name
            
        # Determine destination directory
        if storage_type == "uploads":
            dest_dir = self.upload_dir
        elif storage_type == "output":
            dest_dir = self.output_dir
        elif storage_type == "cache":
            dest_dir = self.cache_dir
        else:
            dest_dir = self.base_dir / storage_type
            dest_dir.mkdir(parents=True, exist_ok=True)
            
        dest_path = dest_dir / object_name
        
        try:
            shutil.copy2(file_path, dest_path)
            self.logger.info(f"Copied {file_path} to {dest_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Upload failed: {e}")
            return False
            
    def download_file(self, object_name: str, file_path: str,
                     storage_type: str = "uploads") -> bool:
        """
        Copy file from local storage
        
        Args:
            object_name: Source filename in storage
            file_path: Destination path
            storage_type: Storage category
            
        Returns:
            True if successful
        """
        # Determine source directory
        if storage_type == "uploads":
            src_dir = self.upload_dir
        elif storage_type == "output":
            src_dir = self.output_dir
        elif storage_type == "cache":
            src_dir = self.cache_dir
        else:
            src_dir = self.base_dir / storage_type
            
        src_path = src_dir / object_name
        
        try:
            if not src_path.exists():
                self.logger.error(f"File not found: {src_path}")
                return False
                
            shutil.copy2(src_path, file_path)
            self.logger.info(f"Copied {src_path} to {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Download failed: {e}")
            return False
            
    def list_files(self, prefix: str = "", storage_type: str = "uploads") -> list:
        """
        List files in storage directory
        
        Args:
            prefix: Filter by filename prefix
            storage_type: Storage category
            
        Returns:
            List of filenames
        """
        # Determine directory
        if storage_type == "uploads":
            directory = self.upload_dir
        elif storage_type == "output":
            directory = self.output_dir
        elif storage_type == "cache":
            directory = self.cache_dir
        else:
            directory = self.base_dir / storage_type
            
        try:
            if not directory.exists():
                return []
                
            files = []
            for file_path in directory.iterdir():
                if file_path.is_file():
                    if not prefix or file_path.name.startswith(prefix):
                        files.append(file_path.name)
                        
            return sorted(files)
            
        except Exception as e:
            self.logger.error(f"List failed: {e}")
            return []
            
    def delete_file(self, object_name: str, storage_type: str = "uploads") -> bool:
        """
        Delete file from storage
        
        Args:
            object_name: Filename to delete
            storage_type: Storage category
            
        Returns:
            True if successful
        """
        # Determine directory
        if storage_type == "uploads":
            directory = self.upload_dir
        elif storage_type == "output":
            directory = self.output_dir
        elif storage_type == "cache":
            directory = self.cache_dir
        else:
            directory = self.base_dir / storage_type
            
        file_path = directory / object_name
        
        try:
            if file_path.exists():
                file_path.unlink()
                self.logger.info(f"Deleted {file_path}")
                return True
            else:
                self.logger.warning(f"File not found: {file_path}")
                return False
                
        except Exception as e:
            self.logger.error(f"Delete failed: {e}")
            return False
            
    def get_file_path(self, object_name: str, storage_type: str = "uploads") -> Path:
        """
        Get full path to file in storage
        
        Args:
            object_name: Filename
            storage_type: Storage category
            
        Returns:
            Full path to file
        """
        if storage_type == "uploads":
            directory = self.upload_dir
        elif storage_type == "output":
            directory = self.output_dir
        elif storage_type == "cache":
            directory = self.cache_dir
        else:
            directory = self.base_dir / storage_type
            
        return directory / object_name
