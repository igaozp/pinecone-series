#!/usr/bin/env python3
"""
Scrape FAISS series articles from Pinecone and convert to Markdown
"""

import requests
from bs4 import BeautifulSoup
import html2text
import time
import os
import re

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

def setup_html2text():
    """Configure html2text converter"""
    h = html2text.HTML2Text()
    h.ignore_links = False
    h.ignore_images = False
    h.ignore_emphasis = False
    h.body_width = 0  # Don't wrap lines
    h.single_line_break = False
    h.mark_code = True
    return h

def fetch_article(url, retries=3):
    """Fetch article content with retries"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"  Attempt {attempt + 1} failed: {e}")
            if attempt < retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                raise
    return None

def extract_main_content(html_content, url):
    """Extract main article content from HTML"""
    soup = BeautifulSoup(html_content, 'html.parser')

    # Try to find the main article content
    # Common selectors for article content
    article = None

    # Try different selectors
    selectors = [
        'article',
        '[role="main"]',
        '.article-content',
        '.post-content',
        'main',
        '.content'
    ]

    for selector in selectors:
        article = soup.select_one(selector)
        if article:
            break

    if not article:
        # Fallback to body if no article found
        article = soup.find('body')

    # Remove unwanted elements
    for element in article.find_all(['script', 'style', 'nav', 'header', 'footer', 'aside']):
        element.decompose()

    # Convert relative URLs to absolute URLs for images and videos
    for img in article.find_all('img'):
        src = img.get('src', '')
        if src and not src.startswith(('http://', 'https://', 'data:')):
            if src.startswith('//'):
                img['src'] = 'https:' + src
            elif src.startswith('/'):
                base_url = '/'.join(url.split('/')[:3])
                img['src'] = base_url + src

    # Handle video elements
    for video in article.find_all(['video', 'iframe']):
        src = video.get('src', '')
        if src and not src.startswith(('http://', 'https://')):
            if src.startswith('//'):
                video['src'] = 'https:' + src
            elif src.startswith('/'):
                base_url = '/'.join(url.split('/')[:3])
                video['src'] = base_url + src

    return article

def clean_markdown(md_content):
    """Clean up markdown content"""
    # Remove excessive blank lines
    md_content = re.sub(r'\n{3,}', '\n\n', md_content)

    # Ensure code blocks are properly formatted
    # Look for code blocks that might be malformed
    md_content = re.sub(r'```(\w+)\n\n', r'```\1\n', md_content)

    return md_content.strip()

def save_article(chapter_num, title, content, output_dir='faiss'):
    """Save article content to markdown file"""
    filename = f"chapter{chapter_num}.md"
    filepath = os.path.join(output_dir, filename)

    # Create header
    header = f"# Chapter {chapter_num}: {title}\n\n"

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(header)
        f.write(content)

    print(f"  ✓ Saved to {filepath}")

def scrape_chapter(chapter_info):
    """Scrape a single chapter"""
    num = chapter_info['num']
    url = chapter_info['url']
    title = chapter_info['title']

    print(f"\nChapter {num}: {title}")
    print(f"  URL: {url}")

    try:
        # Fetch the page
        print(f"  Fetching...")
        html_content = fetch_article(url)

        if not html_content:
            print(f"  ✗ Failed to fetch content")
            return False

        # Extract main content
        print(f"  Extracting content...")
        article = extract_main_content(html_content, url)

        # Convert to markdown
        print(f"  Converting to Markdown...")
        h = setup_html2text()
        md_content = h.handle(str(article))

        # Clean up markdown
        md_content = clean_markdown(md_content)

        # Save to file
        save_article(num, title, md_content)

        return True

    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def main():
    """Main scraping function"""
    print("=" * 60)
    print("Scraping FAISS Series from Pinecone")
    print("=" * 60)

    # Create output directory
    os.makedirs('faiss', exist_ok=True)

    success_count = 0
    failed_chapters = []

    for chapter in CHAPTERS:
        if scrape_chapter(chapter):
            success_count += 1
        else:
            failed_chapters.append(chapter['num'])

        # Be polite - add delay between requests
        time.sleep(2)

    # Summary
    print("\n" + "=" * 60)
    print(f"Scraping complete: {success_count}/{len(CHAPTERS)} chapters successful")

    if failed_chapters:
        print(f"Failed chapters: {', '.join(failed_chapters)}")
    else:
        print("All chapters scraped successfully!")

    print("=" * 60)

if __name__ == '__main__':
    main()
