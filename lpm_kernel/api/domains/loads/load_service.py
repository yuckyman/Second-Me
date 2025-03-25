"""
Load Service Module

This module provides service functions for managing Load entities.
"""

import logging
from typing import Optional, Dict, Any, List, Tuple
from lpm_kernel.models.load import Load
from lpm_kernel.common.repository.database_session import DatabaseSession
from lpm_kernel.api.domains.loads.dto import LoadDTO

logger = logging.getLogger(__name__)

class LoadService:
    """Service class for Load operations"""
    
    @staticmethod
    def get_current_load(with_password: bool = False) -> Tuple[Optional[LoadDTO], Optional[str], int]:
        """
        Get the current load record
        
        Returns:
            Tuple containing:
            - Load DTO or None if not found
            - Error message or None if successful
            - Status code (200 for success, 400/404/500 for errors)
        """
        try:
            with DatabaseSession.session() as session:
                # Check if there are multiple loads
                load_count = session.query(Load).count()
                if load_count > 1:
                    return None, "Multiple load records exist in the system, please clean up first", 400
                
                current_load = session.query(Load).first()
                if not current_load:
                    return None, "Load record not found", 404
                
                return LoadDTO.from_model(current_load, with_password), None, 200
        except Exception as e:
            logger.error(f"Error getting current load: {str(e)}", exc_info=True)
            return None, f"Internal server error: {str(e)}", 500
    
    @staticmethod
    def create_load(name: str, description: Optional[str] = None, email: str = "", instance_id: Optional[str] = None) -> Tuple[Optional[Dict[str, Any]], Optional[str], int]:
        """
        Create a new load record
        
        Args:
            name: Load name
            description: Optional description
            email: Optional email
            instance_id: Optional instance ID
            
        Returns:
            Tuple containing:
            - Load object or None if creation failed
            - Error message or None if successful
            - Status code (200 for success, 400/500 for errors)
        """
        try:
            with DatabaseSession.session() as session:
                # Check if a load record with the same name exists
                existing_load = session.query(Load).filter(Load.name == name).first()
                if existing_load:
                    return None, f"A load record with name '{name}' already exists", 400
                
                # Create a new Load instance
                new_load = Load(
                    name=name,
                    description=description,
                    email=email,
                    instance_id=instance_id
                )
                session.add(new_load)
                session.commit()
                
                # Convert to dictionary before returning to avoid DetachedInstanceError
                load_dict = new_load.to_dict()
                
                # Return the dictionary instead of the detached object
                return load_dict, None, 200
        except Exception as e:
            logger.error(f"Error creating load: {str(e)}", exc_info=True)
            return None, f"Internal server error: {str(e)}", 500
    
    @staticmethod
    def update_load(load_id: str, data: Dict[str, Any]) -> Tuple[Optional[Dict[str, Any]], Optional[str], int]:
        """
        Update a load record
        
        Args:
            load_id: ID of the load to update
            data: Dictionary containing fields to update
            
        Returns:
            Tuple containing:
            - Updated Load dictionary or None if update failed
            - Error message or None if successful
            - Status code (200 for success, 400/404/500 for errors)
        """
        try:
            with DatabaseSession.session() as session:
                load = session.query(Load).filter(Load.id == load_id).first()
                if not load:
                    return None, "Load record not found", 404
                
                # Update fields
                updatable_fields = ["name", "description", "email", "avatar_data", "instance_id", "status"]
                for field in updatable_fields:
                    if field in data:
                        # Special validation for status field
                        if field == "status" and data[field] not in ["active", "inactive", "deleted"]:
                            return None, f"Status must be one of 'active', 'inactive', or 'deleted'", 400
                        
                        setattr(load, field, data[field])
                
                session.commit()
                # Convert to dictionary before returning to avoid DetachedInstanceError
                load_dict = load.to_dict()
                return load_dict, None, 200
        except Exception as e:
            logger.error(f"Error updating load: {str(e)}", exc_info=True)
            return None, f"Internal server error: {str(e)}", 500
    
    @staticmethod
    def update_current_load(data: Dict[str, Any]) -> Tuple[Optional[Dict[str, Any]], Optional[str], int]:
        """
        Update the current load record
        
        Args:
            data: Dictionary containing fields to update
            
        Returns:
            Tuple containing:
            - Updated Load dictionary or None if update failed
            - Error message or None if successful
            - Status code (200 for success, 400/404/500 for errors)
        """
        current_load, error, status_code = LoadService.get_current_load()
        if error:
            return None, error, status_code
        
        return LoadService.update_load(current_load.id, data)
    
    @staticmethod
    def update_instance_id(instance_id: str, instance_password: str = None) -> Tuple[bool, Optional[str], int]:
        """
        Update the instance_id and instance_password of the current load
        
        Args:
            instance_id: New instance ID
            instance_password: New instance password
            
        Returns:
            Tuple containing:
            - Boolean indicating success
            - Error message or None if successful
            - Status code (200 for success, 400/404/500 for errors)
        """
        try:
            logger.info(f"Updating instance_id to {instance_id} and instance_password to {instance_password}")
            with DatabaseSession.session() as session:
                load = session.query(Load).first()
                if not load:
                    logger.warning("Load record not found")
                    return False, "Load record not found", 404
                
                load.instance_id = instance_id
                if instance_password:
                    load.instance_password = instance_password
                session.commit()
                logger.info(f"Updated instance_id in database to: {instance_id}, instance_password: {instance_password}")
                return True, None, 200
        except Exception as e:
            logger.error(f"Error updating instance_id: {str(e)}", exc_info=True)
            return False, f"Internal server error: {str(e)}", 500
    
    @staticmethod
    def get_load_by_name(name: str) -> Tuple[Optional[Load], Optional[str], int]:
        """
        Get a load record by name
        
        Args:
            name: Load name
            
        Returns:
            Tuple containing:
            - Load object or None if not found
            - Error message or None if successful
            - Status code (200 for success, 404/500 for errors)
        """
        try:
            with DatabaseSession.session() as session:
                load = session.query(Load).filter(Load.name == name).first()
                if not load:
                    return None, f"Load record with name '{name}' not found", 404
                
                return load, None, 200
        except Exception as e:
            logger.error(f"Error getting load by name: {str(e)}", exc_info=True)
            return None, f"Internal server error: {str(e)}", 500
    
    @staticmethod
    def clean_directory(directory, keep_structure=True, is_logs_dir=False):
        """Clean files in directory
        
        Args:
            directory (str): Path of directory to clean
            keep_structure (bool): Whether to keep directory structure
            is_logs_dir (bool): Whether it is logs directory
        """
        import os
        if not os.path.exists(directory):
            logger.warning(f"Directory does not exist: {directory}")
            return

        try:
            for root, dirs, files in os.walk(directory, topdown=False):
                # Process files
                for file in files:
                    # Skip .gitkeep files
                    if file == '.gitkeep':
                        continue
                        
                    file_path = os.path.join(root, file)
                    try:
                        if is_logs_dir:
                            # Clear file content instead of deleting file
                            with open(file_path, 'w') as f:
                                f.truncate(0)
                            logger.info(f"Successfully emptied file content: {file_path}")
                        else:
                            # Delete file
                            os.remove(file_path)
                            logger.info(f"Successfully deleted file: {file_path}")
                    except Exception as e:
                        logger.error(f"Failed to process file {file_path}: {str(e)}")
            
            # If not keeping directory structure, delete empty directories
            if not keep_structure:
                for dir in dirs:
                    dir_path = os.path.join(root, dir)
                    try:
                        # Check if directory is empty (except .gitkeep)
                        dir_contents = os.listdir(dir_path)
                        if not dir_contents or (len(dir_contents) == 1 and '.gitkeep' in dir_contents):
                            continue  # Skip directories containing .gitkeep
                        os.rmdir(dir_path)
                        logger.info(f"Successfully deleted directory: {dir_path}")
                    except Exception as e:
                        logger.error(f"Failed to delete directory {dir_path}: {str(e)}")
        except Exception as e:
            logger.error(f"Failed to clean directory {directory}: {str(e)}")

    @staticmethod
    def _unregister_from_registry(load_name: str, instance_id: str) -> None:
        """Unregister the load from registry center
        
        Args:
            load_name: Name of the load
            instance_id: Instance ID of the load
        """
        try:
            from lpm_kernel.api.domains.upload.client import RegistryClient
            registry_client = RegistryClient()
            registry_client.unregister_upload(load_name, instance_id)
            logger.info(f"Successfully unregistered from registry center: {load_name}/{instance_id}")
        except Exception as e:
            logger.error(f"Failed to unregister from registry center: {str(e)}")
            # Continue with deletion even if unregistration fails

    @staticmethod
    def _clean_graphrag_keys() -> None:
        """Clean GraphRAG keys"""
        try:
            from lpm_kernel.L2.l2_generator import L2Generator
            l2_generator = L2Generator()
            l2_generator.clean_graphrag_keys()
            logger.info("Successfully cleaned GraphRAG keys")
        except Exception as e:
            logger.error(f"Failed to clean GraphRAG keys: {str(e)}")
            # Continue with deletion even if cleaning GraphRAG keys fails

    @staticmethod
    def _reinitialize_database(session, load, load_name: str) -> Tuple[Optional[str], int]:
        """Reinitialize database by deleting all tables and recreating them
        
        Args:
            session: Database session
            load: Load object to delete
            load_name: Name of the load
            
        Returns:
            Tuple containing:
            - Error message or None if successful
            - Status code (200 for success, 500 for errors)
        """
        from sqlalchemy import text
        import os
        
        try:
            # Delete load record
            try:
                session.delete(load)
                session.flush()  # Immediately execute delete operation but do not commit
                logger.info(f"Successfully deleted load record: {load_name}")
            except Exception as e:
                logger.error(f"Failed to delete load record: {str(e)}")
                return f"Failed to delete load record: {str(e)}", 500
            
            # Get all user tables (exclude system tables)
            tables = session.execute(
                text("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
            ).fetchall()
            
            # Temporarily disable foreign key constraints
            session.execute(text("PRAGMA foreign_keys = OFF;"))
            
            # Delete all tables
            for table in tables:
                table_name = table[0]
                session.execute(text(f"DROP TABLE IF EXISTS {table_name}"))
                logger.info(f"Dropped table {table_name}")
            
            # Re-enable foreign key constraints
            session.execute(text("PRAGMA foreign_keys = ON;"))
            
            # Read and execute initialization SQL script
            init_sql_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))), 
                                       "docker", "sqlite", "init.sql")
            
            with open(init_sql_path, 'r') as f:
                init_sql = f.read()
                
            # Split and execute by statement
            sql_statements = init_sql.split(';')
            for statement in sql_statements:
                if statement.strip():
                    session.execute(text(statement))
            
            session.commit()
            logger.info("Successfully reinitialized all database tables")
            return None, 200
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to reinitialize database: {str(e)}")
            return f"Failed to clean database: {str(e)}", 500

    @staticmethod
    def _clear_vector_database() -> None:
        """Clear ChromaDB vector database collections and reinitialize them"""
        try:
            import chromadb
            import os
            from lpm_kernel.file_data.embedding_service import EmbeddingService
            
            # Get ChromaDB path
            chroma_path = os.getenv("CHROMA_PERSIST_DIRECTORY", "./data/chroma_db")
            
            # Create ChromaDB client
            client = chromadb.PersistentClient(path=chroma_path)
            
            # Delete document-level collection
            try:
                client.delete_collection(name="documents")
                logger.info("Successfully deleted 'documents' collection")
            except ValueError as e:
                logger.info(f"Collection 'documents' does not exist: {str(e)}")
            except Exception as e:
                logger.error(f"Error deleting 'documents' collection: {str(e)}")
            
            # Delete chunk-level collection
            try:
                client.delete_collection(name="document_chunks")
                logger.info("Successfully deleted 'document_chunks' collection")
            except ValueError as e:
                logger.info(f"Collection 'document_chunks' does not exist: {str(e)}")
            except Exception as e:
                logger.error(f"Error deleting 'document_chunks' collection: {str(e)}")
            
            # Reinitialize collections
            try:
                # Create document-level collection
                client.create_collection(
                    name="documents",
                    metadata={
                        "hnsw:space": "cosine",
                        "dimension": 1536
                    }
                )
                logger.info("Successfully reinitialized 'documents' collection")
                
                # Create chunk-level collection
                client.create_collection(
                    name="document_chunks",
                    metadata={
                        "hnsw:space": "cosine",
                        "dimension": 1536
                    }
                )
                logger.info("Successfully reinitialized 'document_chunks' collection")
                
                # Reset embedding service to use new collections
                from lpm_kernel.file_data.document_service import document_service
                document_service.embedding_service = EmbeddingService()
                logger.info("Successfully reset embedding service")
                
            except Exception as e:
                logger.error(f"Error reinitializing collections: {str(e)}")
            
        except Exception as e:
            logger.error(f"Failed to clear and reinitialize ChromaDB collections: {str(e)}")

    @staticmethod
    def _clean_data_directories() -> None:
        """Clean data directories"""
        import os
        
        base_dir = os.getenv('LOCAL_BASE_DIR', '.')
        directories_to_clean = {
            'logs': os.path.join(base_dir, 'logs'),
            'progress': os.path.join(base_dir, 'data', 'progress'),
            'model_output': os.path.join(base_dir, 'resources', 'model', 'output')
        }

        # Clean all directories, preserve directory structure
        for dir_name, dir_path in directories_to_clean.items():
            logger.info(f"Starting to clean up {dir_name} directory: {dir_path}")
            # Special handling for logs directory: only clear file content
            is_logs_dir = dir_name == 'logs'
            LoadService.clean_directory(dir_path, keep_structure=True, is_logs_dir=is_logs_dir)

    @staticmethod
    def _reset_training_progress() -> None:
        """Reset training progress objects in memory"""
        try:
            import os
            # Import training service
            from lpm_kernel.file_data.trainprocess_service import TrainProcessService
            
            # Get all possible training progress file patterns
            base_dir = os.getenv('LOCAL_BASE_DIR', '.')
            progress_dir = os.path.join(base_dir, 'data', 'progress')
            if os.path.exists(progress_dir):
                for file in os.listdir(progress_dir):
                    if file.startswith('trainprocess_progress_'):
                        # Extract model name
                        model_name = file.replace('trainprocess_progress_', '').replace('.json', '')
                        # Create a new service instance for each model and reset progress
                        train_service = TrainProcessService(model_name=model_name)
                        train_service.progress.reset_progress()
                        logger.info(f"Reset training progress for model: {model_name}")
            
            # Reset default training progress
            default_train_service = TrainProcessService()
            default_train_service.progress.reset_progress()
            logger.info("Reset default training progress")
            
            # Reset global training process variables
            from lpm_kernel.api.domains.kernel2.routes_l2 import _training_process, _training_thread, _stopping_training
            if _training_process is not None:
                logger.info("Resetting global training process variables")
                _training_process = None
                _training_thread = None
                _stopping_training = False
            
        except Exception as e:
            logger.error(f"Failed to reset training progress objects: {str(e)}")

    @staticmethod
    def delete_load(load_name: str) -> Tuple[Optional[str], int]:
        """Delete a load record and clean up related data
        
        Args:
            load_name: Name of the load to delete
            
        Returns:
            Tuple containing:
            - Error message or None if successful
            - Status code (200 for success, 404/500 for errors)
        """
        try:
            with DatabaseSession.session() as session:
                # 1. Find and verify load record
                load = session.query(Load).filter(Load.name == load_name).first()
                if not load:
                    logger.warning(f"Load record not found: {load_name}")
                    return f"Specified load record not found", 404
                
                logger.info(f"Starting to clean up load-related data: {load_name}")

                # 2. Unregister from registry center if instance_id exists
                if load.instance_id:
                    LoadService._unregister_from_registry(load_name, load.instance_id)
                
                # 3. Clean GraphRAG keys
                LoadService._clean_graphrag_keys()
                
                # 4. Reinitialize database
                error, status_code = LoadService._reinitialize_database(session, load, load_name)
                if error:
                    return error, status_code
                    
                # 5. Clear vector database
                LoadService._clear_vector_database()
                
                # 6. Clean data directories
                LoadService._clean_data_directories()
                
                # 7. Reset training progress
                LoadService._reset_training_progress()

                return None, 200

        except Exception as e:
            logger.error(f"An unknown error occurred during deletion: {str(e)}")
            return f"An error occurred during deletion: {str(e)}", 500
    
    @staticmethod
    def update_avatar(load_name: str, base64_string: str) -> Tuple[Optional[Load], Optional[str], int]:
        """
        Update the avatar data for a load
        
        Args:
            load_name: Name of the load
            base64_string: Base64 encoded avatar data
            
        Returns:
            Tuple containing:
            - Updated Load object or None if update failed
            - Error message or None if successful
            - Status code (200 for success, 404/500 for errors)
        """
        try:
            with DatabaseSession.session() as session:
                # Find load record
                load = session.query(Load).filter(Load.name == load_name).first()
                if not load:
                    return None, "Specified load record not found", 404
                
                # Store base64 string directly to database
                load.avatar_data = base64_string
                session.commit()
                
                return load, None, 200
        except Exception as e:
            logger.error(f"An error occurred while updating avatar: {str(e)}")
            return None, f"An error occurred while updating avatar: {str(e)}", 500
    
    @staticmethod
    def get_avatar(load_name: str) -> Tuple[Optional[str], Optional[str], int]:
        """
        Get the avatar data for a load
        
        Args:
            load_name: Name of the load
            
        Returns:
            Tuple containing:
            - Avatar data or None if not found
            - Error message or None if successful
            - Status code (200 for success, 404/500 for errors)
        """
        try:
            with DatabaseSession.session() as session:
                # Find load record
                load = session.query(Load).filter(Load.name == load_name).first()
                if not load:
                    return None, "Specified load record not found", 404
                
                return load.avatar_data, None, 200
        except Exception as e:
            logger.error(f"An error occurred while getting avatar: {str(e)}")
            return None, f"An error occurred while getting avatar: {str(e)}", 500
