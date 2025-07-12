#!/usr/bin/env python3
"""
Rebuild AI Embeddings for Financial Content
Processes all content in vault/notes/ including new stealth-scraped financial data
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
PROJECT_ROOT = Path(__file__).parent.parent
VAULT_DIR = PROJECT_ROOT / "vault/notes"
VECTOR_DB_DIR = PROJECT_ROOT / "vault/vector_db"
LOG_FILE = PROJECT_ROOT / "vault/logs/financial_ai_processor.log"

# AI Configuration  
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # 384 dimensions, fast, good quality
CHUNK_SIZE = 512  # Characters per chunk
CHUNK_OVERLAP = 50  # Overlap between chunks

class FinancialAIProcessor:
    def __init__(self):
        self.model = None
        self.index = None
        self.chunks_metadata = []
        self.vector_db_path = VECTOR_DB_DIR / "financial_index.faiss"
        self.metadata_path = VECTOR_DB_DIR / "financial_metadata.json"
        
        # Ensure directories exist
        VECTOR_DB_DIR.mkdir(parents=True, exist_ok=True)
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    def log_action(self, message):
        """Log AI processor actions with timestamp."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        print(log_message)
        
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(log_message + '\n')
    
    def load_model(self):
        """Load the sentence transformer model."""
        if self.model is None:
            self.log_action(f"Loading embedding model: {EMBEDDING_MODEL}")
            self.model = SentenceTransformer(EMBEDDING_MODEL)
            self.log_action("Model loaded successfully")
    
    def chunk_text(self, text: str, source_file: str) -> List[Dict]:
        """Split text into overlapping chunks with metadata."""
        chunks = []
        text_length = len(text)
        
        for i in range(0, text_length, CHUNK_SIZE - CHUNK_OVERLAP):
            chunk_text = text[i:i + CHUNK_SIZE]
            if len(chunk_text.strip()) < 50:  # Skip very short chunks
                continue
                
            chunk_id = hashlib.md5(f"{source_file}_{i}_{chunk_text[:50]}".encode()).hexdigest()[:16]
            
            chunks.append({
                'id': chunk_id,
                'text': chunk_text,
                'source_file': source_file,
                'chunk_index': len(chunks),
                'start_pos': i,
                'end_pos': min(i + CHUNK_SIZE, text_length)
            })
        
        return chunks
    
    def extract_metadata_from_file(self, file_path: Path) -> Dict:
        """Extract metadata from markdown file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            metadata = {
                'file_path': str(file_path),
                'file_name': file_path.name,
                'file_size': file_path.stat().st_size,
                'modified_time': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
            }
            
            # Extract frontmatter if present
            if content.startswith('---'):
                try:
                    frontmatter_end = content.find('---', 3)
                    if frontmatter_end > 0:
                        frontmatter = content[3:frontmatter_end].strip()
                        for line in frontmatter.split('\n'):
                            if ':' in line:
                                key, value = line.split(':', 1)
                                metadata[key.strip()] = value.strip().strip('"\'')
                except:
                    pass
            
            # Determine content type based on path
            path_str = str(file_path)
            if 'stealth_http' in path_str:
                metadata['content_type'] = 'financial_web'
            elif 'academic' in path_str:
                metadata['content_type'] = 'academic_research'
            elif 'web_scraping' in path_str:
                metadata['content_type'] = 'web_scraping'
            else:
                metadata['content_type'] = 'general'
            
            return metadata, content
            
        except Exception as e:
            self.log_action(f"Error reading file {file_path}: {e}")
            return {}, ""
    
    def build_embeddings(self):
        """Build embeddings from all markdown files in vault."""
        self.load_model()
        
        all_chunks = []
        all_texts = []
        
        self.log_action("Scanning vault directory for markdown files...")
        
        # Find all markdown files
        md_files = list(VAULT_DIR.rglob("*.md"))
        self.log_action(f"Found {len(md_files)} markdown files")
        
        for i, md_file in enumerate(md_files):
            self.log_action(f"Processing [{i+1}/{len(md_files)}]: {md_file.name}")
            
            metadata, content = self.extract_metadata_from_file(md_file)
            if not content:
                continue
            
            # Chunk the content
            chunks = self.chunk_text(content, str(md_file))
            
            for chunk in chunks:
                chunk.update(metadata)  # Add file metadata to each chunk
                all_chunks.append(chunk)
                all_texts.append(chunk['text'])
        
        if not all_texts:
            self.log_action("No content found to process!")
            return
        
        self.log_action(f"Generated {len(all_texts)} text chunks from {len(md_files)} files")
        
        # Generate embeddings
        self.log_action("Generating embeddings...")
        embeddings = self.model.encode(all_texts, show_progress_bar=True)
        self.log_action(f"Generated embeddings: {embeddings.shape}")
        
        # Build FAISS index
        self.log_action("Building FAISS index...")
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
        
        # Normalize embeddings for cosine similarity
        embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
        self.index.add(embeddings.astype('float32'))
        
        # Save index and metadata
        faiss.write_index(self.index, str(self.vector_db_path))
        
        with open(self.metadata_path, 'w', encoding='utf-8') as f:
            json.dump(all_chunks, f, indent=2, ensure_ascii=False)
        
        self.log_action(f"Saved vector index to: {self.vector_db_path}")
        self.log_action(f"Saved metadata to: {self.metadata_path}")
        
        # Summary statistics
        content_types = {}
        for chunk in all_chunks:
            content_type = chunk.get('content_type', 'unknown')
            content_types[content_type] = content_types.get(content_type, 0) + 1
        
        self.log_action("Content type distribution:")
        for content_type, count in content_types.items():
            self.log_action(f"  {content_type}: {count} chunks")
        
        total_chars = sum(len(chunk['text']) for chunk in all_chunks)
        self.log_action(f"Total content processed: {total_chars:,} characters")
        self.log_action(f"Average chunk size: {total_chars // len(all_chunks)} characters")
        
        return len(all_chunks), len(md_files)
    
    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """Search for similar content using semantic similarity."""
        if not self.vector_db_path.exists():
            self.log_action("No vector database found. Run with --build first.")
            return []
        
        self.load_model()
        
        # Load index and metadata
        self.index = faiss.read_index(str(self.vector_db_path))
        
        with open(self.metadata_path, 'r', encoding='utf-8') as f:
            self.chunks_metadata = json.load(f)
        
        # Generate query embedding
        query_embedding = self.model.encode([query])
        query_embedding = query_embedding / np.linalg.norm(query_embedding)
        
        # Search
        scores, indices = self.index.search(query_embedding.astype('float32'), top_k)
        
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < len(self.chunks_metadata):
                result = self.chunks_metadata[idx].copy()
                result['similarity_score'] = float(score)
                results.append(result)
        
        return results

def main():
    """Main function with command line interface."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Financial AI Processor - Embeddings & Search")
    parser.add_argument('--build', action='store_true', help='Build/rebuild embeddings')
    parser.add_argument('--search', type=str, help='Search query')
    parser.add_argument('--top-k', type=int, default=5, help='Number of results to return')
    
    args = parser.parse_args()
    
    processor = FinancialAIProcessor()
    
    if args.build:
        chunks_count, files_count = processor.build_embeddings()
        print(f"\n✅ Successfully built embeddings:")
        print(f"   📄 Files processed: {files_count}")
        print(f"   🧩 Chunks created: {chunks_count}")
        print(f"   💾 Vector DB size: {processor.vector_db_path.stat().st_size / 1024 / 1024:.1f} MB")
        
    elif args.search:
        results = processor.search(args.search, args.top_k)
        
        if results:
            print(f"\n🔍 Search results for: '{args.search}'")
            print("=" * 60)
            
            for i, result in enumerate(results, 1):
                print(f"\n[{i}] Score: {result['similarity_score']:.3f}")
                print(f"File: {Path(result['source_file']).name}")
                print(f"Type: {result.get('content_type', 'unknown')}")
                print(f"Text: {result['text'][:200]}...")
                
        else:
            print("No results found.")
    
    else:
        print("Use --build to create embeddings or --search 'query' to search")

if __name__ == "__main__":
    main()