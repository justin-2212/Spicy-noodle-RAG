"""Tests for Qdrant Docker connection."""

import pytest
from qdrant_client import QdrantClient
from app.config.settings import VectorStoreSettings


class TestQdrantConnection:
    """Test Qdrant Docker connection and basic operations."""
    
    @pytest.fixture
    def vector_store_settings(self):
        """Get Qdrant settings."""
        return VectorStoreSettings()
    
    @pytest.fixture
    def qdrant_client(self, vector_store_settings):
        """Create Qdrant client."""
        client = QdrantClient(
            host="localhost",
            port=6333,
        )
        return client
    
    def test_qdrant_connection(self, qdrant_client):
        """Test basic connection to Qdrant Docker."""
        try:
            # Try to get collections
            info = qdrant_client.get_collections()
            assert info is not None
            print(f"✓ Connected to Qdrant Docker successfully")
            collection_names = [col.name for col in info.collections]
            print(f"✓ Collections found: {len(collection_names)}")
        except Exception as e:
            pytest.fail(f"Failed to connect to Qdrant: {str(e)}")
    
    def test_collection_operations(self, qdrant_client, vector_store_settings):
        """Test collection creation and listing."""
        collection_name = f"test_{vector_store_settings.collection_name}"
        vector_size = vector_store_settings.vector_size
        
        try:
            # Create test collection
            from qdrant_client.models import Distance, VectorParams
            
            # Delete if exists
            if qdrant_client.collection_exists(collection_name):
                qdrant_client.delete_collection(collection_name)
            
            # Create new collection
            qdrant_client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=Distance.COSINE
                ),
            )
            print(f"✓ Created test collection: {collection_name}")
            
            # List collections
            collections = qdrant_client.get_collections()
            collection_names = [col.name for col in collections.collections]
            assert collection_name in collection_names
            print(f"✓ Collection listed successfully")
            print(f"✓ Total collections: {len(collection_names)}")
            
            # Get collection info
            collection_info = qdrant_client.get_collection(collection_name)
            assert collection_info is not None
            print(f"✓ Retrieved collection info")
            print(f"✓ Vector size: {collection_info.config.params.vectors.size}")
            
            # Delete test collection
            qdrant_client.delete_collection(collection_name)
            print(f"✓ Deleted test collection")
            
        except Exception as e:
            pytest.fail(f"Collection operations failed: {str(e)}")
    
    def test_batch_operations(self, qdrant_client, vector_store_settings):
        """Test batch vector operations."""
        import numpy as np
        from qdrant_client.models import Distance, VectorParams, PointStruct
        
        collection_name = f"test_batch_{vector_store_settings.collection_name}"
        vector_size = vector_store_settings.vector_size
        
        try:
            # Create collection
            # Delete if exists
            if qdrant_client.collection_exists(collection_name):
                qdrant_client.delete_collection(collection_name)
            
            # Create new collection
            qdrant_client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=Distance.COSINE
                ),
            )
            
            # Create large batch of vectors
            batch_size = 100
            test_vectors = []
            for i in range(batch_size):
                vector = np.random.rand(vector_size).tolist()
                point = PointStruct(
                    id=i,
                    vector=vector,
                    payload={
                        "text": f"Batch document {i}",
                        "batch_index": i % 10
                    }
                )
                test_vectors.append(point)
            
            # Upsert batch
            qdrant_client.upsert(
                collection_name=collection_name,
                points=test_vectors,
            )
            print(f"✓ Upserted batch of {batch_size} vectors")
            
            # Get collection stats
            collection_info = qdrant_client.get_collection(collection_name)
            points_count = collection_info.points_count
            assert points_count == batch_size
            print(f"✓ Verified batch count: {points_count}")
            
            # Delete collection
            qdrant_client.delete_collection(collection_name)
            print(f"✓ Deleted batch test collection")
            
        except Exception as e:
            pytest.fail(f"Batch operations failed: {str(e)}")


class TestQdrantConnectionErrors:
    """Test error handling for Qdrant connection issues."""
    
    def test_invalid_host_connection(self):
        """Test connection with invalid host."""
        client = QdrantClient(
            host="invalid-host-that-does-not-exist",
            port=6333,
            timeout=2,
        )
        
        with pytest.raises(Exception):
            client.get_collections()
        
        print("✓ Invalid host properly raised exception")
    
    def test_invalid_port_connection(self):
        """Test connection with invalid port."""
        client = QdrantClient(
            host="localhost",
            port=9999,
            timeout=2,
        )
        
        with pytest.raises(Exception):
            client.get_collections()
        
        print("✓ Invalid port properly raised exception")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
