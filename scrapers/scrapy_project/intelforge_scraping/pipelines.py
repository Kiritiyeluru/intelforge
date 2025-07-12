# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import os
import re
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

from itemadapter import ItemAdapter


class ObsidianMarkdownPipeline:
    """Pipeline to save articles as Obsidian-compatible markdown files."""
    
    def __init__(self):
        self.output_dir = Path("vault/notes/web/")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        
        # Generate filename from title
        title = adapter.get('title', 'Untitled')
        filename = self._generate_filename(title)
        
        # Create markdown content
        markdown_content = self._create_markdown(adapter)
        
        # Save to file
        filepath = self.output_dir / f"{filename}.md"
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        spider.logger.info(f"Saved article: {filepath}")
        return item
    
    def _generate_filename(self, title: str) -> str:
        """Generate safe filename from title."""
        # Remove or replace problematic characters
        filename = re.sub(r'[^\w\s-]', '', title)
        filename = re.sub(r'[-\s]+', '-', filename)
        filename = filename.strip('-').lower()
        
        # Limit length
        if len(filename) > 50:
            filename = filename[:50]
        
        # Add timestamp to avoid duplicates
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        return f"{filename}_{timestamp}"
    
    def _create_markdown(self, adapter) -> str:
        """Create Obsidian-compatible markdown content."""
        # Extract data
        title = adapter.get('title', 'Untitled')
        content = adapter.get('content', '')
        url = adapter.get('url', '')
        author = adapter.get('author', 'Unknown')
        site = adapter.get('site', '')
        keywords = adapter.get('keywords', [])
        scraped_at = adapter.get('scraped_at', datetime.now().isoformat())
        content_hash = adapter.get('content_hash', '')
        
        # Format keywords as tags
        tags = ['web'] + [kw.replace(' ', '-').lower() for kw in keywords]
        tag_string = ', '.join(tags)
        
        # Create markdown
        markdown = f"""---
source: web
url: {url}
site: {site}
author: {author}
date: {scraped_at[:10]}
tags: [{tag_string}]
content_hash: {content_hash}
extraction_method: trafilatura
---

# {title}

**Source:** [{site}]({url})  
**Author:** {author}  
**Scraped:** {scraped_at[:10]}

---

{content}

---

**Keywords:** {', '.join(keywords)}  
**URL:** {url}
"""
        
        return markdown
