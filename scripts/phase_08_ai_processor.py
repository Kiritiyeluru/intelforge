#!/usr/bin/env python3
"""
Phase 08: AI Article Processor
Process organized articles with embeddings and semantic search capabilities.
Uses free/open-source tools: sentence-transformers + FAISS
"""

import os
import json
import pickle
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple
import hashlib

# Will install these if needed
try:
    from sentence_transformers import SentenceTransformer
    import faiss
    import numpy as np
except ImportError:
    print("Required packages not installed. Run: pip install sentence-transformers faiss-cpu")
    exit(1)

# Configuration
PROJECT_ROOT = Path(__file__).parent
ARTICLES_DIR = PROJECT_ROOT / "knowledge_management/articles"
VECTOR_DB_DIR = PROJECT_ROOT / "knowledge_management/vector_db"
LOG_FILE = PROJECT_ROOT / "knowledge_management/logs/ai_processor.log"

# AI Configuration
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # 384 dimensions, fast, good quality
CHUNK_SIZE = 512  # Characters per chunk
CHUNK_OVERLAP = 50  # Overlap between chunks

class ArticleAIProcessor:
    def __init__(self):
        self.model = None
        self.index = None
        self.chunks_metadata = []
        self.vector_db_path = VECTOR_DB_DIR / "article_index.faiss"
        self.metadata_path = VECTOR_DB_DIR / "chunks_metadata.json"
        
        # Ensure directories exist
        VECTOR_DB_DIR.mkdir(parents=True, exist_ok=True)
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    def log_action(self, message):
        """Log AI processor actions with timestamp."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        with open(LOG_FILE, 'a') as f:
            f.write(log_entry)
        print(log_entry.strip())
    
    def load_model(self):
        """Load sentence transformer model."""
        if self.model is None:
            self.log_action(f"Loading embedding model: {EMBEDDING_MODEL}")
            self.model = SentenceTransformer(EMBEDDING_MODEL)
            self.log_action("Model loaded successfully")
    
    def chunk_text(self, text: str, title: str = "") -> List[Dict]:
        """Split text into overlapping chunks for better embeddings."""
        chunks = []
        
        # Add title context to chunks
        if title:
            text = f"Title: {title}\n\n{text}"
        
        # Simple character-based chunking
        start = 0
        chunk_id = 0
        
        while start < len(text):
            end = start + CHUNK_SIZE
            
            # Try to break at sentence/paragraph boundaries
            if end < len(text):
                # Look for good break points
                for break_char in ['\n\n', '\n', '. ', '! ', '? ']:
                    break_pos = text.rfind(break_char, start, end)
                    if break_pos > start + CHUNK_SIZE // 2:
                        end = break_pos + len(break_char)
                        break
            
            chunk_text = text[start:end].strip()
            if chunk_text:
                chunks.append({
                    'chunk_id': chunk_id,
                    'text': chunk_text,
                    'start_pos': start,
                    'end_pos': end
                })
                chunk_id += 1
            
            # Move start position with overlap
            start = max(start + 1, end - CHUNK_OVERLAP)
        
        return chunks
    
    def process_article(self, file_path: Path, category: str) -> List[Dict]:
        """Process single article into chunks with metadata."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            title = file_path.stem
            chunks = self.chunk_text(content, title)
            
            # Add metadata to chunks
            for chunk in chunks:
                chunk.update({
                    'file_path': str(file_path),
                    'filename': file_path.name,
                    'title': title,
                    'category': category,
                    'content_hash': hashlib.md5(content.encode()).hexdigest()[:8]
                })
            
            self.log_action(f"Processed '{file_path.name}' -> {len(chunks)} chunks")
            return chunks
            
        except Exception as e:
            self.log_action(f"Error processing {file_path}: {e}")
            return []
    
    def build_embeddings(self, dry_run=False):
        """Build embeddings for all organized articles."""
        self.load_model()
        
        all_chunks = []
        
        # Process each category
        for category_dir in ARTICLES_DIR.iterdir():
            if not category_dir.is_dir():
                continue
                
            category = category_dir.name
            self.log_action(f"Processing category: {category}")
            
            for article_file in category_dir.glob("*.md"):
                chunks = self.process_article(article_file, category)
                all_chunks.extend(chunks)
        
        if not all_chunks:
            self.log_action("No articles found to process")
            return
        
        self.log_action(f"Total chunks to process: {len(all_chunks)}")
        
        if dry_run:
            self.log_action("[DRY RUN] Would generate embeddings and build FAISS index")
            return
        
        # Generate embeddings
        self.log_action("Generating embeddings...")
        texts = [chunk['text'] for chunk in all_chunks]
        embeddings = self.model.encode(texts, show_progress_bar=True)
        
        # Build FAISS index
        self.log_action("Building FAISS index...")
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
        
        # Normalize embeddings for cosine similarity
        faiss.normalize_L2(embeddings)
        self.index.add(embeddings.astype('float32'))
        
        # Save index and metadata
        faiss.write_index(self.index, str(self.vector_db_path))
        
        with open(self.metadata_path, 'w') as f:
            json.dump(all_chunks, f, indent=2)
        
        self.log_action(f"✅ Built vector database: {len(all_chunks)} chunks, {dimension}D embeddings")
        self.log_action(f"Index saved to: {self.vector_db_path}")
    
    def load_index(self):
        """Load existing FAISS index and metadata."""
        if not self.vector_db_path.exists():
            self.log_action("No existing index found. Run build_embeddings first.")
            return False
        
        self.load_model()
        self.index = faiss.read_index(str(self.vector_db_path))
        
        with open(self.metadata_path, 'r') as f:
            self.chunks_metadata = json.load(f)
        
        self.log_action(f"Loaded index with {len(self.chunks_metadata)} chunks")
        return True
    
    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """Semantic search through articles."""
        if not self.load_index():
            return []
        
        # Generate query embedding
        query_embedding = self.model.encode([query])
        faiss.normalize_L2(query_embedding)
        
        # Search
        scores, indices = self.index.search(query_embedding.astype('float32'), top_k)
        
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < len(self.chunks_metadata):
                result = self.chunks_metadata[idx].copy()
                result['similarity_score'] = float(score)
                results.append(result)
        
        self.log_action(f"Search query: '{query}' -> {len(results)} results")
        return results

def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="AI processing for article knowledge base")
    parser.add_argument("--build", action="store_true", help="Build embeddings and vector index")
    parser.add_argument("--search", type=str, help="Search query")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done")
    parser.add_argument("--top-k", type=int, default=5, help="Number of search results")
    
    args = parser.parse_args()
    
    processor = ArticleAIProcessor()
    
    if args.build:
        processor.build_embeddings(dry_run=args.dry_run)
    elif args.search:
        results = processor.search(args.search, args.top_k)
        print(f"\n🔍 Search results for: '{args.search}'\n")
        for i, result in enumerate(results, 1):
            print(f"{i}. [{result['category']}] {result['title']}")
            print(f"   Score: {result['similarity_score']:.3f}")
            print(f"   File: {result['filename']}")
            print(f"   Preview: {result['text'][:150]}...")
            print()
    else:
        print("Use --build to create embeddings or --search 'query' to search")

if __name__ == "__main__":
    main()