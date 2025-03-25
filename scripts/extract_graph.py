#!/usr/bin/env python
"""
Script to extract entities and relationships from a document using graphrag
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = str(Path(__file__).parent.parent)
sys.path.insert(0, project_root)

from lpm_kernel.file_data.memory_service import StorageService
from lpm_kernel.configs.config import Config
from graphrag.index.operations.extract_graph.extract_graph import extract_graph
from graphrag.callbacks.workflow_callbacks import WorkflowCallbacks
from graphrag.cache.pipeline_cache import PipelineCache
import pandas as pd

def extract_graph_from_document():
    """Extract entities and relationships from the test document"""
    try:
        # Initialize storage service
        config = Config.from_env()
        storage_service = StorageService(config)
        
        # Read the test file
        file_path = os.path.join(project_root, "resources", "raw_content", "test.txt")
        with open(file_path, "r") as f:
            file_content = f.read()
            
        # Create a dataframe with the document
        df = pd.DataFrame({
            "id": [1],
            "text": [file_content]
        })
        
        # Initialize callbacks and cache
        callbacks = WorkflowCallbacks()
        cache = PipelineCache()
        
        # Extract entities and relationships
        entities_df, relationships_df = extract_graph(
            text_units=df,
            callbacks=callbacks,
            cache=cache,
            text_column="text",
            id_column="id",
            strategy={
                "type": "graph_intelligence",
                "extraction_prompt": os.path.join(project_root, "lpm_kernel/L2/data_pipeline/graphrag_indexing/prompts/extract_graph.txt"),
                "completion_delimiter": "<|COMPLETE|>",
                "tuple_delimiter": "<|>",
                "record_delimiter": "##",
                "encoding_name": "cl100k_base",
                "llm": {
                    "type": "openai",
                    "api_key": os.getenv("OPENAI_API_KEY"),
                    "model": "gpt-4-turbo-preview",
                    "max_tokens": 6000
                }
            },
            entity_types=["person", "organization"]
        )
        
        # Print results
        print("\nEntities:")
        print(entities_df)
        print("\nRelationships:")
        print(relationships_df)
            
    except Exception as e:
        print(f"Error extracting graph: {str(e)}")
        raise

if __name__ == "__main__":
    extract_graph_from_document() 