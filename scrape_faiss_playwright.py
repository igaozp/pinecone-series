#!/usr/bin/env python3
"""
Scrape FAISS series articles from Pinecone using Playwright
"""

from playwright.sync_api import sync_playwright
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

def html_to_markdown(html_content, base_url):
    """Convert HTML to Markdown with proper formatting"""
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html_content, 'html.parser')

    # Find main article content
    article = soup.find('article') or soup.find('main') or soup.find('body')

    if not article:
        return html_content

    # Remove unwanted elements
    for element in article.find_all(['script', 'style', 'nav', 'header', 'footer']):
        element.decompose()

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
                result = f"\n{text}\n"
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
                result = f"\n```{lang}\n{code}\n```\n"
            else:
                code = element.get_text()
                result = f"\n```\n{code}\n```\n"
        elif element.name == 'code' and element.parent.name != 'pre':
            result = f"`{element.get_text()}`"
        elif element.name == 'a':
            href = element.get('href', '')
            text = element.get_text().strip()
            if href:
                # Convert relative URLs to absolute
                if href.startswith('/') and not href.startswith('//'):
                    href = base_url.rstrip('/') + href
                result = f"[{text}]({href})"
            else:
                result = text
        elif element.name == 'img':
            src = element.get('src', '')
            alt = element.get('alt', '')
            # Convert relative URLs to absolute
            if src.startswith('/') and not src.startswith('//'):
                src = base_url.rstrip('/') + src
            elif src.startswith('//'):
                src = 'https:' + src
            result = f"\n![{alt}]({src})\n"
        elif element.name == 'ul':
            items = []
            for li in element.find_all('li', recursive=False):
                item_text = ''.join(process_element(child, indent) for child in li.children)
                items.append(f"{indent_str}- {item_text.strip()}")
            result = '\n' + '\n'.join(items) + '\n'
        elif element.name == 'ol':
            items = []
            for i, li in enumerate(element.find_all('li', recursive=False), 1):
                item_text = ''.join(process_element(child, indent) for child in li.children)
                items.append(f"{indent_str}{i}. {item_text.strip()}")
            result = '\n' + '\n'.join(items) + '\n'
        elif element.name == 'li':
            result = ''.join(process_element(child, indent) for child in element.children)
        elif element.name == 'blockquote':
            lines = element.get_text().strip().split('\n')
            result = '\n' + '\n'.join(f"> {line}" for line in lines) + '\n'
        elif element.name == 'strong' or element.name == 'b':
            result = f"**{element.get_text()}**"
        elif element.name == 'em' or element.name == 'i':
            result = f"*{element.get_text()}*"
        elif element.name == 'br':
            result = '\n'
        elif element.name == 'hr':
            result = '\n---\n'
        elif element.name == 'table':
            # Simple table conversion
            result = '\n' + convert_table(element) + '\n'
        elif element.name in ['video', 'iframe']:
            src = element.get('src', '')
            if src:
                if src.startswith('/') and not src.startswith('//'):
                    src = base_url.rstrip('/') + src
                elif src.startswith('//'):
                    src = 'https:' + src
                result = f"\n[Video/Embed]({src})\n"
        elif element.name in ['div', 'section', 'article', 'span']:
            # Process children
            result = ''.join(process_element(child, indent) for child in element.children)
        else:
            # For other elements, just process children
            result = ''.join(process_element(child, indent) for child in element.children)

        return result

    def convert_table(table):
        """Convert HTML table to Markdown"""
        rows = []
        for tr in table.find_all('tr'):
            cells = []
            for td in tr.find_all(['td', 'th']):
                cells.append(td.get_text().strip())
            if cells:
                rows.append('| ' + ' | '.join(cells) + ' |')

        if len(rows) > 0:
            # Add header separator after first row
            if table.find('th'):
                header_sep = '| ' + ' | '.join(['---'] * len(rows[0].split('|')[1:-1])) + ' |'
                rows.insert(1, header_sep)

        return '\n'.join(rows)

    markdown = process_element(article)

    # Clean up excessive newlines
    markdown = re.sub(r'\n{3,}', '\n\n', markdown)

    return markdown.strip()

def scrape_with_playwright(chapter_info):
    """Scrape a single chapter using Playwright"""
    num = chapter_info['num']
    url = chapter_info['url']
    title = chapter_info['title']

    print(f"\nChapter {num}: {title}")
    print(f"  URL: {url}")

    try:
        with sync_playwright() as p:
            print(f"  Launching browser...")
            browser = p.chromium.launch(
                headless=True,
                args=['--ignore-certificate-errors']
            )
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                ignore_https_errors=True
            )
            page = context.new_page()

            print(f"  Loading page...")
            page.goto(url, wait_until='networkidle', timeout=60000)

            # Wait for content to load
            time.sleep(3)

            print(f"  Extracting content...")
            html_content = page.content()

            browser.close()

        # Convert to Markdown
        print(f"  Converting to Markdown...")
        base_url = '/'.join(url.split('/')[:3])
        md_content = html_to_markdown(html_content, base_url)

        # Save to file
        filename = f"chapter{num}.md"
        filepath = os.path.join('faiss', filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"# Chapter {num}: {title}\n\n")
            f.write(f"Source: {url}\n\n")
            f.write("---\n\n")
            f.write(md_content)

        print(f"  ✓ Saved to {filepath}")
        return True

    except Exception as e:
        print(f"  ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main scraping function"""
    print("=" * 60)
    print("Scraping FAISS Series from Pinecone (Playwright)")
    print("=" * 60)

    # Create output directory
    os.makedirs('faiss', exist_ok=True)

    success_count = 0
    failed_chapters = []

    for chapter in CHAPTERS:
        if scrape_with_playwright(chapter):
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
