#!/usr/bin/env python
"""
Script to create a document in the database from a text file
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = str(Path(__file__).parent.parent)
sys.path.insert(0, project_root)

from lpm_kernel.file_data.memory_service import StorageService
from lpm_kernel.configs.config import Config

def create_document():
    """Create a document from the test.txt file"""
    try:
        # Initialize storage service
        config = Config.from_env()
        storage_service = StorageService(config)
        
        # Read the test file
        file_path = os.path.join(project_root, "resources", "raw_content", "test.txt")
        with open(file_path, "rb") as f:
            file_data = f.read()
            
        # Create metadata
        metadata = {
            "name": "test.txt",
            "description": "A test document with some content"
        }
        
        # Save file and process document
        memory, document = storage_service.save_file(file_data, metadata)
        print(f"Created document with ID: {document.id}")
            
    except Exception as e:
        print(f"Error creating document: {str(e)}")
        raise

if __name__ == "__main__":
    create_document() 