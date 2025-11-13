#!/usr/bin/env python3
"""
FAISS Series Downloader using Jina AI
Run this script on your local machine (not in Docker)
"""

import requests
import time
import os
from pathlib import Path

API_KEY = "jina_ccf592ec8f8e470185afa074e7076614WpvRgv0U8B8R0yI8Dqte51xyw-Wi"

CHAPTERS = [
    {
        'num': '01',
        'url': 'https://www.pinecone.io/learn/series/faiss/faiss-tutorial/',
        'title': 'Introduction to Facebook AI Similarity Search (Faiss)'
    },
    {
        'num': '02',
        'url': 'https://www.pinecone.io/learn/series/faiss/vector-indexes/',
        'title': 'Nearest Neighbor Indexes for Similarity Search'
    },
    {
        'num': '03',
        'url': 'https://www.pinecone.io/learn/series/faiss/locality-sensitive-hashing/',
        'title': 'Locality Sensitive Hashing (LSH): The Illustrated Guide'
    },
    {
        'num': '04',
        'url': 'https://www.pinecone.io/learn/series/faiss/locality-sensitive-hashing-random-projection/',
        'title': 'Random Projection for Locality Sensitive Hashing'
    },
    {
        'num': '05',
        'url': 'https://www.pinecone.io/learn/series/faiss/product-quantization/',
        'title': 'Product Quantization: Compressing high-dimensional vectors by 97%'
    },
    {
        'num': '06',
        'url': 'https://www.pinecone.io/learn/series/faiss/hnsw/',
        'title': 'Hierarchical Navigable Small Worlds (HNSW)'
    },
    {
        'num': '07',
        'url': 'https://www.pinecone.io/learn/composite-indexes',
        'title': 'Facebook AI and the Index Factory'
    }
]

def download_chapter(num, url, title):
    """Download a single chapter using Jina AI"""
    print(f"📥 Downloading Chapter {num}: {title}...")

    headers = {
        'Authorization': f'Bearer {API_KEY}'
    }

    jina_url = f"https://r.jina.ai/{url}"

    try:
        response = requests.get(jina_url, headers=headers, timeout=60)

        if response.status_code == 200:
            content = response.text

            # Add metadata header
            header = f"""# Chapter {num}: {title}

**Source:** {url}

**Downloaded via:** Jina AI Reader

---

"""
            full_content = header + content

            # Save to file
            filepath = Path('faiss') / f'chapter{num}.md'
            filepath.write_text(full_content, encoding='utf-8')

            file_size = len(full_content)
            print(f"✅ Chapter {num} downloaded ({file_size:,} bytes)")
            return True

        else:
            print(f"❌ Chapter {num} failed: HTTP {response.status_code}")
            print(f"   Response: {response.text[:100]}")
            return False

    except Exception as e:
        print(f"❌ Chapter {num} failed: {e}")
        return False

def main():
    """Main download function"""
    print("=" * 60)
    print("Downloading FAISS Series Articles via Jina AI")
    print("=" * 60)
    print()

    # Create output directory
    Path('faiss').mkdir(exist_ok=True)

    success_count = 0
    failed_chapters = []

    for chapter in CHAPTERS:
        if download_chapter(chapter['num'], chapter['url'], chapter['title']):
            success_count += 1
        else:
            failed_chapters.append(chapter['num'])

        # Be polite to the API
        time.sleep(2)

    # Summary
    print()
    print("=" * 60)
    print("Download Complete!")
    print("=" * 60)
    print()
    print(f"✅ Success: {success_count}/{len(CHAPTERS)} chapters")

    if failed_chapters:
        print(f"❌ Failed: {', '.join(failed_chapters)}")

    print()
    print("Downloaded files:")
    for f in sorted(Path('faiss').glob('chapter*.md')):
        size = f.stat().st_size
        print(f"  - {f.name} ({size:,} bytes)")

    print()
    print("Next steps:")
    print("1. Review the downloaded files")
    print("2. Git add: git add faiss/")
    print("3. Git commit: git commit -m 'Add FAISS chapters downloaded via Jina AI'")
    print("4. Git push: git push")

if __name__ == '__main__':
    main()
