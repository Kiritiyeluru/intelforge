#!/usr/bin/env python3
"""
Data Organizer for IntelForge

Simple utility to organize and manage scraped data.
Provides data organization, deduplication, and basic analytics.

Usage:
    python data_organizer.py [--action ACTION] [--config CONFIG]

Example:
    python data_organizer.py --action stats     # Show statistics
    python data_organizer.py --action cleanup   # Remove duplicates
    python data_organizer.py --action organize  # Organize files
"""

import argparse
import hashlib
import os
import sqlite3
import shutil
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

import yaml


class DataOrganizer:
    """Simple data organization and management utility."""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """Initialize the data organizer."""
        self.config_path = config_path
        self.config = self._load_config()
        self.output_dir = Path(self.config['paths']['output_dir'])
        self.db_path = self.output_dir / "scraped_data.db"
        
        print(f"Data organizer initialized - Database: {self.db_path}")
    
    def _load_config(self):
        """Load configuration from YAML file."""
        try:
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            exit(1)
    
    def show_statistics(self):
        """Show statistics about scraped data."""
        print("\n=== IntelForge Data Statistics ===")
        
        if not self.db_path.exists():
            print("No database found. Run some scrapers first.")
            return
        
        with sqlite3.connect(self.db_path) as conn:
            # Total content count
            cursor = conn.execute("SELECT COUNT(*) FROM scraped_content")
            total_count = cursor.fetchone()[0]
            print(f"Total articles scraped: {total_count}")
            
            # Count by source
            cursor = conn.execute("SELECT source, COUNT(*) FROM scraped_content GROUP BY source")
            source_counts = cursor.fetchall()
            print(f"\nBy source:")
            for source, count in source_counts:
                print(f"  {source}: {count} articles")
            
            # Recent content
            cursor = conn.execute("""
                SELECT title, source, scraped_at 
                FROM scraped_content 
                ORDER BY scraped_at DESC 
                LIMIT 5
            """)
            recent = cursor.fetchall()
            print(f"\nMost recent articles:")
            for title, source, scraped_at in recent:
                print(f"  [{source}] {title[:50]}... ({scraped_at})")
            
            # Content size stats
            cursor = conn.execute("""
                SELECT AVG(LENGTH(content)), MIN(LENGTH(content)), MAX(LENGTH(content))
                FROM scraped_content
            """)
            avg_len, min_len, max_len = cursor.fetchone()
            if avg_len:
                print(f"\nContent size:")
                print(f"  Average: {int(avg_len)} characters")
                print(f"  Range: {min_len} - {max_len} characters")
    
    def find_duplicates(self) -> List[Tuple]:
        """Find duplicate content based on content hash."""
        if not self.db_path.exists():
            print("No database found.")
            return []
        
        duplicates = []
        
        with sqlite3.connect(self.db_path) as conn:
            # Find duplicate content hashes
            cursor = conn.execute("""
                SELECT content_hash, COUNT(*) as count
                FROM scraped_content 
                GROUP BY content_hash 
                HAVING count > 1
            """)
            
            duplicate_hashes = cursor.fetchall()
            
            for content_hash, count in duplicate_hashes:
                # Get all entries with this hash
                cursor = conn.execute("""
                    SELECT id, url, title, source, scraped_at
                    FROM scraped_content 
                    WHERE content_hash = ?
                    ORDER BY scraped_at
                """, (content_hash,))
                
                entries = cursor.fetchall()
                duplicates.append((content_hash, entries))
        
        return duplicates
    
    def cleanup_duplicates(self):
        """Remove duplicate content, keeping the oldest entry."""
        print("\n=== Cleaning up duplicates ===")
        
        duplicates = self.find_duplicates()
        
        if not duplicates:
            print("No duplicates found.")
            return
        
        print(f"Found {len(duplicates)} sets of duplicate content")
        
        removed_count = 0
        
        with sqlite3.connect(self.db_path) as conn:
            for content_hash, entries in duplicates:
                # Keep the first (oldest) entry, remove the rest
                entries_to_remove = entries[1:]  # Skip the first one
                
                print(f"\nDuplicate content: {entries[0][2][:50]}...")
                print(f"  Keeping: {entries[0][1]} (scraped: {entries[0][4]})")
                
                for entry in entries_to_remove:
                    entry_id, url, title, source, scraped_at = entry
                    print(f"  Removing: {url} (scraped: {scraped_at})")
                    
                    # Remove from database
                    conn.execute("DELETE FROM scraped_content WHERE id = ?", (entry_id,))
                    removed_count += 1
            
            conn.commit()
        
        print(f"\nRemoved {removed_count} duplicate entries")
    
    def organize_files(self):
        """Organize markdown files by date and source."""
        print("\n=== Organizing files ===")
        
        # Organize by source and date
        for source_dir in ['reddit', 'github', 'web']:
            source_path = self.output_dir / source_dir
            if not source_path.exists():
                continue
            
            print(f"\nOrganizing {source_dir} files...")
            
            # Create date-based subdirectories
            for md_file in source_path.glob("*.md"):
                try:
                    # Get file creation date
                    stat = md_file.stat()
                    file_date = datetime.fromtimestamp(stat.st_mtime)
                    date_dir = source_path / file_date.strftime("%Y-%m")
                    
                    # Create date directory if it doesn't exist
                    date_dir.mkdir(exist_ok=True)
                    
                    # Move file to date directory
                    new_path = date_dir / md_file.name
                    if not new_path.exists():
                        shutil.move(str(md_file), str(new_path))
                        print(f"  Moved: {md_file.name} -> {date_dir.name}/")
                    
                except Exception as e:
                    print(f"  Error organizing {md_file.name}: {e}")
    
    def generate_index(self):
        """Generate an index file for all scraped content."""
        print("\n=== Generating content index ===")
        
        if not self.db_path.exists():
            print("No database found.")
            return
        
        index_path = self.output_dir / "index.md"
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT source, title, url, scraped_at, metadata
                FROM scraped_content 
                ORDER BY source, scraped_at DESC
            """)
            
            content = cursor.fetchall()
        
        # Generate markdown index
        index_md = "# IntelForge Content Index\n\n"
        index_md += f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        # Group by source
        by_source = defaultdict(list)
        for source, title, url, scraped_at, metadata in content:
            by_source[source].append((title, url, scraped_at, metadata))
        
        for source, items in by_source.items():
            index_md += f"## {source.title()} ({len(items)} articles)\n\n"
            
            for title, url, scraped_at, metadata in items:
                # Create a safe link
                safe_title = title.replace('[', '').replace(']', '')
                index_md += f"- [{safe_title}]({url}) - {scraped_at}\n"
            
            index_md += "\n"
        
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(index_md)
        
        print(f"Index generated: {index_path}")
    
    def search_content(self, query: str) -> List[Tuple]:
        """Search for content containing the query."""
        if not self.db_path.exists():
            print("No database found.")
            return []
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT title, url, source, scraped_at
                FROM scraped_content 
                WHERE title LIKE ? OR content LIKE ?
                ORDER BY scraped_at DESC
            """, (f"%{query}%", f"%{query}%"))
            
            results = cursor.fetchall()
        
        return results
    
    def backup_database(self):
        """Create a backup of the database."""
        if not self.db_path.exists():
            print("No database found.")
            return
        
        backup_dir = Path("backups")
        backup_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = backup_dir / f"scraped_data_backup_{timestamp}.db"
        
        shutil.copy2(self.db_path, backup_path)
        print(f"Database backed up to: {backup_path}")


def main():
    """Main function with command line interface."""
    parser = argparse.ArgumentParser(description="Data Organizer for IntelForge")
    parser.add_argument('--action', type=str, default='stats',
                       choices=['stats', 'cleanup', 'organize', 'index', 'search', 'backup'],
                       help="Action to perform")
    parser.add_argument('--query', type=str, help="Search query (for search action)")
    parser.add_argument('--config', type=str, default="config/config.yaml", help="Path to config file")
    
    args = parser.parse_args()
    
    try:
        organizer = DataOrganizer(config_path=args.config)
        
        if args.action == 'stats':
            organizer.show_statistics()
            
        elif args.action == 'cleanup':
            organizer.cleanup_duplicates()
            
        elif args.action == 'organize':
            organizer.organize_files()
            
        elif args.action == 'index':
            organizer.generate_index()
            
        elif args.action == 'search':
            if not args.query:
                print("Please provide a search query with --query")
                return
            
            results = organizer.search_content(args.query)
            if results:
                print(f"\nFound {len(results)} results for '{args.query}':")
                for title, url, source, scraped_at in results:
                    print(f"  [{source}] {title[:60]}... - {scraped_at}")
                    print(f"    {url}")
            else:
                print(f"No results found for '{args.query}'")
                
        elif args.action == 'backup':
            organizer.backup_database()
            
    except KeyboardInterrupt:
        print("\nOperation interrupted by user")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()