#!/usr/bin/env python3
"""
Scrape FAISS series articles from Pinecone using cloudscraper
"""

import cloudscraper
from bs4 import BeautifulSoup
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

def html_to_markdown(soup, base_url):
    """Convert BeautifulSoup object to Markdown with proper formatting"""

    markdown_lines = []

    def process_element(element, indent=0):
        """Recursively process HTML elements and convert to Markdown"""
        if element.name is None:
            # Text node
            text = str(element).strip()
            if text:
                return text
            return ''

        result = ''
        indent_str = '  ' * indent

        if element.name == 'h1':
            result = f"\n# {element.get_text().strip()}\n"
        elif element.name == 'h2':
            result = f"\n## {element.get_text().strip()}\n"
        elif element.name == 'h3':
            result = f"\n### {element.get_text().strip()}\n"
        elif element.name == 'h4':
            result = f"\n#### {element.get_text().strip()}\n"
        elif element.name == 'h5':
            result = f"\n##### {element.get_text().strip()}\n"
        elif element.name == 'h6':
            result = f"\n###### {element.get_text().strip()}\n"
        elif element.name == 'p':
            text = element.get_text().strip()
            if text:
                # Process inline elements within paragraph
                para_content = ''
                for child in element.children:
                    para_content += process_element(child, indent)
                result = f"\n{para_content}\n"
        elif element.name == 'pre':
            code_elem = element.find('code')
            if code_elem:
                code = code_elem.get_text()
                lang = ''
                # Try to detect language from class
                if code_elem.get('class'):
                    classes = code_elem.get('class')
                    for cls in classes:
                        if cls.startswith('language-'):
                            lang = cls.replace('language-', '')
                            break
                        elif cls in ['python', 'javascript', 'bash', 'java', 'cpp', 'c', 'go', 'rust']:
                            lang = cls
                            break
                result = f"\n```{lang}\n{code}```\n"
            else:
                code = element.get_text()
                result = f"\n```\n{code}```\n"
        elif element.name == 'code' and element.parent.name != 'pre':
            result = f"`{element.get_text()}`"
        elif element.name == 'a':
            href = element.get('href', '')
            text = element.get_text().strip()
            if href:
                # Convert relative URLs to absolute
                if href.startswith('/') and not href.startswith('//'):
                    href = base_url.rstrip('/') + href
                elif href.startswith('//'):
                    href = 'https:' + href
                result = f"[{text}]({href})"
            else:
                result = text
        elif element.name == 'img':
            src = element.get('src', '')
            alt = element.get('alt', 'image')
            # Convert relative URLs to absolute
            if src.startswith('/') and not src.startswith('//'):
                src = base_url.rstrip('/') + src
            elif src.startswith('//'):
                src = 'https:' + src
            result = f"\n![{alt}]({src})\n"
        elif element.name == 'ul':
            items = []
            for li in element.find_all('li', recursive=False):
                item_text = ''
                for child in li.children:
                    item_text += process_element(child, indent + 1)
                items.append(f"{indent_str}- {item_text.strip()}")
            result = '\n' + '\n'.join(items) + '\n'
        elif element.name == 'ol':
            items = []
            for i, li in enumerate(element.find_all('li', recursive=False), 1):
                item_text = ''
                for child in li.children:
                    item_text += process_element(child, indent + 1)
                items.append(f"{indent_str}{i}. {item_text.strip()}")
            result = '\n' + '\n'.join(items) + '\n'
        elif element.name == 'li':
            result = ''
            for child in element.children:
                result += process_element(child, indent)
        elif element.name == 'blockquote':
            lines = element.get_text().strip().split('\n')
            result = '\n' + '\n'.join(f"> {line}" for line in lines) + '\n'
        elif element.name == 'strong' or element.name == 'b':
            result = f"**{element.get_text()}**"
        elif element.name == 'em' or element.name == 'i':
            result = f"*{element.get_text()}*"
        elif element.name == 'br':
            result = '  \n'
        elif element.name == 'hr':
            result = '\n---\n'
        elif element.name == 'table':
            result = '\n' + convert_table(element) + '\n'
        elif element.name in ['video', 'iframe']:
            src = element.get('src', '')
            if src:
                if src.startswith('/') and not src.startswith('//'):
                    src = base_url.rstrip('/') + src
                elif src.startswith('//'):
                    src = 'https:' + src
                result = f"\n**[Video/Embed]({src})**\n"
        elif element.name in ['div', 'section', 'article', 'span', 'main']:
            # Process children
            result = ''
            for child in element.children:
                result += process_element(child, indent)
        else:
            # For other elements, just process children
            result = ''
            for child in element.children:
                result += process_element(child, indent)

        return result

    def convert_table(table):
        """Convert HTML table to Markdown"""
        rows = []
        header_found = False

        for tr in table.find_all('tr'):
            cells = []
            is_header = False

            # Check for header cells
            ths = tr.find_all('th')
            if ths:
                is_header = True
                for th in ths:
                    cells.append(th.get_text().strip())
            else:
                for td in tr.find_all('td'):
                    cells.append(td.get_text().strip())

            if cells:
                rows.append('| ' + ' | '.join(cells) + ' |')

                # Add separator after header
                if is_header and not header_found:
                    sep = '| ' + ' | '.join(['---'] * len(cells)) + ' |'
                    rows.append(sep)
                    header_found = True

        return '\n'.join(rows)

    # Find main content
    article = soup.find('article')
    if not article:
        article = soup.find('main')
    if not article:
        article = soup.find(class_=re.compile(r'(article|content|post)', re.I))
    if not article:
        article = soup.find('body')

    if article:
        # Remove unwanted elements
        for element in article.find_all(['script', 'style', 'nav', 'header', 'footer']):
            element.decompose()

        markdown = process_element(article)
    else:
        markdown = "Could not find main content"

    # Clean up excessive newlines
    markdown = re.sub(r'\n{3,}', '\n\n', markdown)

    return markdown.strip()

def scrape_chapter(scraper, chapter_info):
    """Scrape a single chapter using cloudscraper"""
    num = chapter_info['num']
    url = chapter_info['url']
    title = chapter_info['title']

    print(f"\nChapter {num}: {title}")
    print(f"  URL: {url}")

    try:
        print(f"  Fetching...")
        response = scraper.get(url, timeout=30)
        response.raise_for_status()

        print(f"  Parsing HTML...")
        soup = BeautifulSoup(response.content, 'html.parser')

        print(f"  Converting to Markdown...")
        base_url = '/'.join(url.split('/')[:3])
        md_content = html_to_markdown(soup, base_url)

        # Save to file
        filename = f"chapter{num}.md"
        filepath = os.path.join('faiss', filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"# Chapter {num}: {title}\n\n")
            f.write(f"**Source:** {url}\n\n")
            f.write("---\n\n")
            f.write(md_content)

        print(f"  ✓ Saved to {filepath} ({len(md_content)} chars)")
        return True

    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def main():
    """Main scraping function"""
    print("=" * 60)
    print("Scraping FAISS Series from Pinecone (Cloudscraper)")
    print("=" * 60)

    # Create output directory
    os.makedirs('faiss', exist_ok=True)

    # Create scraper instance
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'windows',
            'desktop': True
        }
    )

    success_count = 0
    failed_chapters = []

    for chapter in CHAPTERS:
        if scrape_chapter(scraper, chapter):
            success_count += 1
        else:
            failed_chapters.append(chapter['num'])

        # Be polite - add delay between requests
        time.sleep(3)

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
