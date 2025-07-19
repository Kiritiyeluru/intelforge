#!/usr/bin/env python3
"""
Enhanced Storage Layer for IntelForge Content Enrichment

Integrates enriched content with existing Qdrant vector storage and
provides advanced search and retrieval capabilities.
"""

import orjson as json
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import uuid

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False
    print("⚠️ Qdrant client not available")

from crawl_ops.enrichment.schemas import SchemaValidator, SchemaTransformer


class EnrichedContentStorage:
    """Enhanced storage layer for enriched content with Qdrant integration"""
    
    def __init__(self, qdrant_host: str = "localhost", qdrant_port: int = 6333):
        self.qdrant_host = qdrant_host
        self.qdrant_port = qdrant_port
        self.client = None
        self.collection_name = "enriched_content"
        self.validator = SchemaValidator()
        self.transformer = SchemaTransformer()
        
        if QDRANT_AVAILABLE:
            self._initialize_qdrant()
        else:
            print("⚠️ Qdrant not available, storage will be local only")
    
    def _initialize_qdrant(self):
        """Initialize Qdrant client and collection"""
        try:
            self.client = QdrantClient(host=self.qdrant_host, port=self.qdrant_port)
            
            # Check if collection exists, create if not
            collections = self.client.get_collections()
            collection_names = [col.name for col in collections.collections]
            
            if self.collection_name not in collection_names:
                print(f"📂 Creating Qdrant collection: {self.collection_name}")
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(size=384, distance=Distance.COSINE)  # sentence-transformers default
                )
            else:
                print(f"✅ Using existing Qdrant collection: {self.collection_name}")
                
        except Exception as e:
            print(f"❌ Failed to initialize Qdrant: {e}")
            self.client = None
    
    def store_enriched_content(self, enriched_data: Dict[str, Any], 
                              vector: Optional[List[float]] = None) -> bool:
        """Store enriched content with optional vector embedding"""
        
        # Validate data
        if not self.validator.validate_enriched_content(enriched_data):
            print(f"❌ Invalid enriched content schema")
            return False
        
        try:
            # Generate unique ID
            content_id = str(uuid.uuid4())
            
            # Prepare metadata for Qdrant
            metadata = self._prepare_metadata(enriched_data)
            
            # Store in Qdrant if available and vector provided
            if self.client and vector:
                point = PointStruct(
                    id=content_id,
                    vector=vector,
                    payload=metadata
                )
                
                self.client.upsert(
                    collection_name=self.collection_name,
                    points=[point]
                )
                
                print(f"✅ Stored enriched content in Qdrant: {content_id}")
            
            # Store full data locally as backup
            self._store_local_backup(enriched_data, content_id)
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to store enriched content: {e}")
            return False
    
    def _prepare_metadata(self, enriched_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare metadata for Qdrant storage"""
        
        # Extract key fields for efficient filtering
        metadata = {
            "content_id": enriched_data.get("content_hash", ""),
            "url": enriched_data.get("url", ""),
            "title": enriched_data.get("title", ""),
            "site": enriched_data.get("site", ""),
            "quality_score": enriched_data.get("quality_score", 0),
            "strategy_density": enriched_data.get("strategy_density", 0),
            "technical_level": enriched_data.get("technical_level", "intermediate"),
            "enrichment_timestamp": enriched_data.get("enrichment_timestamp", ""),
            
            # Content tags as arrays for filtering
            "content_types": enriched_data.get("content_tags", {}).get("content_type", []),
            "topic_areas": enriched_data.get("topic_areas", []),
            "tools_languages": enriched_data.get("content_tags", {}).get("tools_languages", []),
            "strategy_types": enriched_data.get("content_tags", {}).get("strategy_types", []),
            
            # Strategy keywords for search
            "technical_indicators": list(enriched_data.get("technical_indicators", {}).keys()),
            "key_concepts": enriched_data.get("key_concepts", []),
            
            # Quality metrics
            "has_code": enriched_data.get("enrichment_summary", {}).get("has_code", False),
            "actionable": enriched_data.get("enrichment_summary", {}).get("actionable", False),
            "enrichment_quality": enriched_data.get("enrichment_summary", {}).get("enrichment_quality", "basic"),
            
            # Full content for retrieval
            "content_preview": enriched_data.get("content", "")[:500]  # First 500 chars
        }
        
        return metadata
    
    def _store_local_backup(self, enriched_data: Dict[str, Any], content_id: str):
        """Store full enriched data as local backup"""
        
        backup_dir = Path("crawl_ops/enhanced_storage/backups")
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        backup_file = backup_dir / f"{content_id}.json"
        
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(enriched_data, f, indent=2, ensure_ascii=False)
    
    def search_by_quality(self, min_quality: float = 70.0, 
                         limit: int = 10) -> List[Dict[str, Any]]:
        """Search content by quality score"""
        
        if not self.client:
            return []
        
        try:
            results = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=Filter(
                    must=[
                        FieldCondition(
                            key="quality_score",
                            range={"gte": min_quality}
                        )
                    ]
                ),
                limit=limit
            )
            
            return [self._format_search_result(point) for point in results[0]]
            
        except Exception as e:
            print(f"❌ Search by quality failed: {e}")
            return []
    
    def search_by_tags(self, content_types: List[str] = None,
                      strategy_types: List[str] = None,
                      technical_level: str = None,
                      limit: int = 10) -> List[Dict[str, Any]]:
        """Search content by tags and categories"""
        
        if not self.client:
            return []
        
        try:
            conditions = []
            
            if content_types:
                for content_type in content_types:
                    conditions.append(
                        FieldCondition(
                            key="content_types",
                            match=MatchValue(value=content_type)
                        )
                    )
            
            if strategy_types:
                for strategy_type in strategy_types:
                    conditions.append(
                        FieldCondition(
                            key="strategy_types", 
                            match=MatchValue(value=strategy_type)
                        )
                    )
            
            if technical_level:
                conditions.append(
                    FieldCondition(
                        key="technical_level",
                        match=MatchValue(value=technical_level)
                    )
                )
            
            if not conditions:
                return []
            
            results = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=Filter(must=conditions),
                limit=limit
            )
            
            return [self._format_search_result(point) for point in results[0]]
            
        except Exception as e:
            print(f"❌ Search by tags failed: {e}")
            return []
    
    def search_by_indicators(self, indicators: List[str], 
                           limit: int = 10) -> List[Dict[str, Any]]:
        """Search content by technical indicators"""
        
        if not self.client:
            return []
        
        try:
            conditions = []
            
            for indicator in indicators:
                conditions.append(
                    FieldCondition(
                        key="technical_indicators",
                        match=MatchValue(value=indicator)
                    )
                )
            
            results = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=Filter(should=conditions),  # OR condition
                limit=limit
            )
            
            return [self._format_search_result(point) for point in results[0]]
            
        except Exception as e:
            print(f"❌ Search by indicators failed: {e}")
            return []
    
    def get_actionable_content(self, min_quality: float = 75.0,
                              limit: int = 10) -> List[Dict[str, Any]]:
        """Get high-quality actionable content"""
        
        if not self.client:
            return []
        
        try:
            results = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=Filter(
                    must=[
                        FieldCondition(
                            key="actionable",
                            match=MatchValue(value=True)
                        ),
                        FieldCondition(
                            key="quality_score",
                            range={"gte": min_quality}
                        )
                    ]
                ),
                limit=limit
            )
            
            return [self._format_search_result(point) for point in results[0]]
            
        except Exception as e:
            print(f"❌ Get actionable content failed: {e}")
            return []
    
    def _format_search_result(self, point) -> Dict[str, Any]:
        """Format Qdrant search result"""
        
        payload = point.payload
        
        return {
            "id": point.id,
            "score": getattr(point, 'score', None),
            "url": payload.get("url", ""),
            "title": payload.get("title", ""),
            "quality_score": payload.get("quality_score", 0),
            "strategy_density": payload.get("strategy_density", 0),
            "technical_level": payload.get("technical_level", ""),
            "content_types": payload.get("content_types", []),
            "strategy_types": payload.get("strategy_types", []),
            "technical_indicators": payload.get("technical_indicators", []),
            "key_concepts": payload.get("key_concepts", []),
            "actionable": payload.get("actionable", False),
            "content_preview": payload.get("content_preview", "")
        }
    
    def get_storage_statistics(self) -> Dict[str, Any]:
        """Get storage statistics and metrics"""
        
        if not self.client:
            return {"error": "Qdrant not available"}
        
        try:
            collection_info = self.client.get_collection(self.collection_name)
            
            # Get sample data for analysis
            sample_results = self.client.scroll(
                collection_name=self.collection_name,
                limit=100
            )
            
            points = sample_results[0]
            
            if not points:
                return {"total_points": 0, "message": "No data stored"}
            
            # Calculate statistics
            quality_scores = [p.payload.get("quality_score", 0) for p in points]
            strategy_densities = [p.payload.get("strategy_density", 0) for p in points]
            
            # Count actionable content
            actionable_count = sum(1 for p in points 
                                 if p.payload.get("actionable", False))
            
            # Count content types
            content_types = {}
            for point in points:
                for content_type in point.payload.get("content_types", []):
                    content_types[content_type] = content_types.get(content_type, 0) + 1
            
            return {
                "total_points": collection_info.points_count,
                "vector_size": collection_info.config.params.vectors.size,
                "sample_size": len(points),
                "quality_statistics": {
                    "average_quality": sum(quality_scores) / len(quality_scores) if quality_scores else 0,
                    "max_quality": max(quality_scores) if quality_scores else 0,
                    "min_quality": min(quality_scores) if quality_scores else 0
                },
                "strategy_statistics": {
                    "average_density": sum(strategy_densities) / len(strategy_densities) if strategy_densities else 0,
                    "max_density": max(strategy_densities) if strategy_densities else 0
                },
                "actionable_content": {
                    "count": actionable_count,
                    "percentage": (actionable_count / len(points)) * 100 if points else 0
                },
                "content_type_distribution": content_types,
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": f"Failed to get statistics: {e}"}


def main():
    """CLI interface for enhanced storage"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Enhanced Content Storage')
    parser.add_argument('--search-quality', type=float, help='Search by minimum quality score')
    parser.add_argument('--search-type', help='Search by content type')
    parser.add_argument('--search-indicator', help='Search by technical indicator')
    parser.add_argument('--actionable', action='store_true', help='Get actionable content only')
    parser.add_argument('--stats', action='store_true', help='Show storage statistics')
    parser.add_argument('--limit', type=int, default=10, help='Limit search results')
    
    args = parser.parse_args()
    
    storage = EnrichedContentStorage()
    
    if args.stats:
        stats = storage.get_storage_statistics()
        print("📊 Storage Statistics:")
        print(json.dumps(stats, indent=2))
        return
    
    results = []
    
    if args.search_quality:
        results = storage.search_by_quality(args.search_quality, args.limit)
        print(f"🔍 Found {len(results)} items with quality >= {args.search_quality}")
    
    elif args.search_type:
        results = storage.search_by_tags(content_types=[args.search_type], limit=args.limit)
        print(f"🏷️ Found {len(results)} items of type '{args.search_type}'")
    
    elif args.search_indicator:
        results = storage.search_by_indicators([args.search_indicator], args.limit)
        print(f"📈 Found {len(results)} items with indicator '{args.search_indicator}'")
    
    elif args.actionable:
        results = storage.get_actionable_content(limit=args.limit)
        print(f"⚡ Found {len(results)} actionable items")
    
    # Display results
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result['title']}")
        print(f"   URL: {result['url']}")
        print(f"   Quality: {result['quality_score']:.1f}")
        print(f"   Strategy Density: {result['strategy_density']:.2f}%")
        print(f"   Types: {', '.join(result['content_types'])}")
        print(f"   Actionable: {'✅' if result['actionable'] else '❌'}")


if __name__ == "__main__":
    main()