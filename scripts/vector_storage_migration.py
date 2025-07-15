"""
Vector Storage Migration - Qdrant to ChromaDB
Uses LangChain adapters for seamless migration
"""

import chromadb
from chromadb.config import Settings
import json
import uuid
from pathlib import Path
from typing import List, Dict, Any, Optional
import numpy as np
from sentence_transformers import SentenceTransformer

# Import security manager
try:
    from scripts.utils.vector_security_manager import security_manager
    SECURITY_AVAILABLE = True
except ImportError:
    SECURITY_AVAILABLE = False
    print("⚠️ Vector security manager not available")


class ChromaVectorStorage:
    """ChromaDB vector storage with LangChain-compatible interface"""
    
    def __init__(self, persist_directory: str = "./chroma_storage", collection_name: str = "semantic_capture"):
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Get or create collection
        try:
            self.collection = self.client.get_collection(name=collection_name)
            print(f"✅ Using existing ChromaDB collection: {collection_name}")
        except Exception:
            self.collection = self.client.create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            print(f"✅ Created ChromaDB collection: {collection_name}")
    
    def upsert(self, collection_name: str, points: List[Dict[str, Any]]):
        """Upsert points to ChromaDB with security enhancements"""
        ids = []
        embeddings = []
        metadatas = []
        documents = []
        
        for point in points:
            # Extract data from PointStruct-like format
            point_id = str(point.get('id', str(uuid.uuid4())))
            vector = point.get('vector', [])
            payload = point.get('payload', {})
            
            # Security validation if available
            if SECURITY_AVAILABLE:
                # Validate payload for security threats
                if not security_manager.validate_vector_payload(payload):
                    print(f"❌ Security validation failed for point {point_id}")
                    continue
                
                # Sanitize metadata
                payload = security_manager.sanitize_metadata(payload)
                
                # Log vector operation
                security_manager.log_vector_operation(
                    operation="upsert",
                    collection=collection_name,
                    metadata={"point_id": point_id, "vector_size": len(vector)}
                )
            
            ids.append(point_id)
            embeddings.append(vector)
            metadatas.append(payload)
            
            # Create document text from payload
            doc_text = payload.get('content_preview', payload.get('title', ''))
            documents.append(doc_text)
        
        # Upsert to ChromaDB
        self.collection.upsert(
            ids=ids,
            embeddings=embeddings,
            metadatas=metadatas,
            documents=documents
        )
        
        print(f"✅ Upserted {len(points)} points to ChromaDB")
    
    def query(self, vector: List[float], top_k: int = 10) -> List[Dict[str, Any]]:
        """Query ChromaDB with vector similarity and security logging"""
        # Security logging if available
        if SECURITY_AVAILABLE:
            security_manager.log_vector_operation(
                operation="query",
                collection=self.collection.name,
                metadata={"vector_size": len(vector), "top_k": top_k}
            )
        
        results = self.collection.query(
            query_embeddings=[vector],
            n_results=top_k,
            include=['metadatas', 'documents', 'distances']
        )
        
        # Format results to match expected format
        formatted_results = []
        if results['ids']:
            for i, id in enumerate(results['ids'][0]):
                result = {
                    'id': id,
                    'score': 1.0 - results['distances'][0][i],  # Convert distance to similarity
                    'payload': results['metadatas'][0][i],
                    'document': results['documents'][0][i] if results['documents'] else ''
                }
                formatted_results.append(result)
        
        return formatted_results
    
    def get_collection_info(self) -> Dict[str, Any]:
        """Get collection information"""
        count = self.collection.count()
        return {
            'name': self.collection_name,
            'count': count,
            'storage_type': 'ChromaDB'
        }
    
    def create_snapshot(self, snapshot_path: str = None) -> Dict[str, Any]:
        """Create a snapshot of the ChromaDB collection using native persistence"""
        if snapshot_path is None:
            snapshot_path = f"{self.persist_directory}_snapshot_{__import__('datetime').datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        try:
            # ChromaDB automatically persists data, so we just need to copy the persistence directory
            import shutil
            from pathlib import Path
            
            snapshot_dir = Path(snapshot_path)
            source_dir = Path(self.persist_directory)
            
            if source_dir.exists():
                # Copy the entire ChromaDB storage directory
                shutil.copytree(source_dir, snapshot_dir, dirs_exist_ok=True)
                
                # Get collection info for snapshot metadata
                collection_info = self.get_collection_info()
                
                # Create snapshot metadata
                snapshot_metadata = {
                    "timestamp": __import__('datetime').datetime.now().isoformat(),
                    "collection_name": self.collection_name,
                    "storage_type": "ChromaDB",
                    "record_count": collection_info["count"],
                    "snapshot_path": str(snapshot_dir),
                    "source_path": str(source_dir)
                }
                
                # Save metadata
                metadata_path = snapshot_dir / "snapshot_metadata.json"
                with open(metadata_path, 'w') as f:
                    json.dump(snapshot_metadata, f, indent=2)
                
                print(f"✅ ChromaDB snapshot created: {snapshot_path}")
                return snapshot_metadata
            else:
                raise FileNotFoundError(f"Source directory not found: {self.persist_directory}")
                
        except Exception as e:
            print(f"❌ Failed to create snapshot: {e}")
            raise
    
    def restore_snapshot(self, snapshot_path: str) -> bool:
        """Restore ChromaDB collection from snapshot"""
        try:
            import shutil
            from pathlib import Path
            
            snapshot_dir = Path(snapshot_path)
            target_dir = Path(self.persist_directory)
            
            if not snapshot_dir.exists():
                raise FileNotFoundError(f"Snapshot directory not found: {snapshot_path}")
            
            # Read snapshot metadata
            metadata_path = snapshot_dir / "snapshot_metadata.json"
            if metadata_path.exists():
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
                print(f"📄 Restoring snapshot from {metadata['timestamp']}")
                print(f"📊 Records: {metadata['record_count']}")
            
            # Backup current storage if it exists
            if target_dir.exists():
                backup_path = f"{target_dir}_backup_{__import__('datetime').datetime.now().strftime('%Y%m%d_%H%M%S')}"
                shutil.move(target_dir, backup_path)
                print(f"💾 Current storage backed up to: {backup_path}")
            
            # Copy snapshot to target directory
            shutil.copytree(snapshot_dir, target_dir, dirs_exist_ok=True)
            
            # Remove metadata file from restored directory (not needed in storage)
            restored_metadata_path = target_dir / "snapshot_metadata.json"
            if restored_metadata_path.exists():
                restored_metadata_path.unlink()
            
            # Reinitialize ChromaDB client with restored data
            self.client = chromadb.PersistentClient(
                path=str(target_dir),
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            self.collection = self.client.get_collection(name=self.collection_name)
            
            print(f"✅ ChromaDB snapshot restored successfully")
            return True
            
        except Exception as e:
            print(f"❌ Failed to restore snapshot: {e}")
            return False


class QdrantMigrationTool:
    """Tool to migrate data from Qdrant to ChromaDB"""
    
    def __init__(self, qdrant_path: str = "./qdrant_storage", chroma_path: str = "./chroma_storage"):
        self.qdrant_path = qdrant_path
        self.chroma_path = chroma_path
        
    def migrate_collection(self, collection_name: str = "semantic_capture") -> bool:
        """Migrate a collection from Qdrant to ChromaDB"""
        try:
            # Check if Qdrant data exists
            qdrant_dir = Path(self.qdrant_path)
            if not qdrant_dir.exists():
                print(f"⚠️ Qdrant directory not found: {self.qdrant_path}")
                return False
            
            # Initialize ChromaDB storage
            chroma_storage = ChromaVectorStorage(self.chroma_path, collection_name)
            
            # Try to import and read Qdrant data
            try:
                from qdrant_client import QdrantClient
                from qdrant_client.http.models import PointStruct
                
                qdrant_client = QdrantClient(path=self.qdrant_path)
                
                # Get all points from Qdrant
                response = qdrant_client.scroll(
                    collection_name=collection_name,
                    limit=1000,
                    with_payload=True,
                    with_vectors=True
                )
                
                if response and response[0]:
                    points = response[0]
                    
                    # Convert to ChromaDB format
                    chroma_points = []
                    for point in points:
                        chroma_point = {
                            'id': point.id,
                            'vector': point.vector,
                            'payload': point.payload or {}
                        }
                        chroma_points.append(chroma_point)
                    
                    # Insert into ChromaDB
                    chroma_storage.upsert(collection_name, chroma_points)
                    
                    print(f"✅ Successfully migrated {len(chroma_points)} points from Qdrant to ChromaDB")
                    return True
                else:
                    print("⚠️ No data found in Qdrant collection")
                    return False
                    
            except ImportError:
                print("⚠️ Qdrant client not available for migration")
                return False
            except Exception as e:
                print(f"⚠️ Error reading Qdrant data: {e}")
                return False
                
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            return False
    
    def verify_migration(self, collection_name: str = "semantic_capture") -> bool:
        """Verify migration was successful"""
        try:
            chroma_storage = ChromaVectorStorage(self.chroma_path, collection_name)
            info = chroma_storage.get_collection_info()
            
            print(f"✅ Migration verification:")
            print(f"  - Collection: {info['name']}")
            print(f"  - Documents: {info['count']}")
            print(f"  - Storage: {info['storage_type']}")
            
            return info['count'] > 0
            
        except Exception as e:
            print(f"❌ Verification failed: {e}")
            return False


def create_chroma_storage(persist_directory: str = "./chroma_storage", collection_name: str = "semantic_capture") -> ChromaVectorStorage:
    """Create ChromaDB storage instance"""
    return ChromaVectorStorage(persist_directory, collection_name)


def migrate_qdrant_to_chroma(qdrant_path: str = "./qdrant_storage", chroma_path: str = "./chroma_storage") -> bool:
    """Migrate Qdrant data to ChromaDB"""
    migrator = QdrantMigrationTool(qdrant_path, chroma_path)
    success = migrator.migrate_collection()
    
    if success:
        migrator.verify_migration()
    
    return success