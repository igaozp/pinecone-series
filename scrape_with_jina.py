#!/usr/bin/env python3
"""
Scrape FAISS series articles using Jina AI Reader
"""

import requests
import time
import os

# Jina AI configuration
JINA_API_KEY = "jina_ccf592ec8f8e470185afa074e7076614WpvRgv0U8B8R0yI8Dqte51xyw-Wi"
JINA_READER_URL = "https://r.jina.ai/"

# Chapter URLs
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

def fetch_with_jina(url, api_key):
    """Fetch content using Jina AI Reader"""
    headers = {
        'Authorization': f'Bearer {api_key}',
        'X-Return-Format': 'markdown',
        'X-With-Generated-Alt': 'true'
    }

    jina_url = f"{JINA_READER_URL}{url}"

    try:
        response = requests.get(jina_url, headers=headers, timeout=60)
        print(f"    Status: {response.status_code}")
        print(f"    Headers: {dict(response.headers)}")

        if response.status_code == 200:
            return response.text
        else:
            print(f"    Error: {response.text[:500]}")
            return None
    except Exception as e:
        print(f"    Exception: {e}")
        return None

def save_article(chapter_num, title, content, source_url):
    """Save article to markdown file"""
    filepath = os.path.join('faiss', f'chapter{chapter_num}.md')

    header = f"""# Chapter {chapter_num}: {title}

**Source:** {source_url}

---

"""

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(header)
        f.write(content)

    return filepath

def scrape_chapter(chapter_info):
    """Scrape a single chapter"""
    num = chapter_info['num']
    url = chapter_info['url']
    title = chapter_info['title']

    print(f"\nChapter {num}: {title}")
    print(f"  URL: {url}")
    print(f"  Fetching with Jina AI...")

    content = fetch_with_jina(url, JINA_API_KEY)

    if content and len(content) > 100:  # Basic validation
        filepath = save_article(num, title, content, url)
        print(f"  ✓ Saved to {filepath} ({len(content)} chars)")
        return True
    else:
        print(f"  ✗ Failed to fetch content")
        return False

def main():
    """Main function"""
    print("=" * 70)
    print("Scraping FAISS Series using Jina AI Reader")
    print("=" * 70)

    os.makedirs('faiss', exist_ok=True)

    success_count = 0
    failed_chapters = []

    for chapter in CHAPTERS:
        if scrape_chapter(chapter):
            success_count += 1
        else:
            failed_chapters.append(chapter['num'])

        # Be polite
        time.sleep(2)

    # Summary
    print("\n" + "=" * 70)
    print(f"Complete: {success_count}/{len(CHAPTERS)} chapters successful")
    if failed_chapters:
        print(f"Failed: {', '.join(failed_chapters)}")
    else:
        print("All chapters downloaded successfully!")
    print("=" * 70)

if __name__ == '__main__':
    main()
