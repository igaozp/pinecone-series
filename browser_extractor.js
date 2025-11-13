/**
 * FAISS Series Article Extractor for Browser Console
 *
 * Instructions:
 * 1. Open https://www.pinecone.io/learn/series/faiss/faiss-tutorial/ in your browser
 * 2. Open Developer Tools (F12 or Cmd+Option+I on Mac)
 * 3. Go to the Console tab
 * 4. Paste this entire script and press Enter
 * 5. The script will extract the content and download it as a Markdown file
 * 6. Repeat for each chapter URL
 */

(function() {
    'use strict';

    // Get the current page URL to determine chapter number
    const url = window.location.href;
    let chapterNum = '00';
    let chapterTitle = 'Unknown';

    // Map URLs to chapter numbers
    const chapterMap = {
        'faiss-tutorial': { num: '01', title: 'Introduction to Facebook AI Similarity Search (Faiss)' },
        'vector-indexes': { num: '02', title: 'Nearest Neighbor Indexes for Similarity Search' },
        'locality-sensitive-hashing/': { num: '03', title: 'Locality Sensitive Hashing (LSH): The Illustrated Guide' },
        'locality-sensitive-hashing-random-projection': { num: '04', title: 'Random Projection for Locality Sensitive Hashing' },
        'product-quantization': { num: '05', title: 'Product Quantization: Compressing high-dimensional vectors by 97%' },
        'hnsw': { num: '06', title: 'Hierarchical Navigable Small Worlds (HNSW)' },
        'composite-indexes': { num: '07', title: 'Facebook AI and the Index Factory' }
    };

    // Detect chapter from URL
    for (const [key, value] of Object.entries(chapterMap)) {
        if (url.includes(key)) {
            chapterNum = value.num;
            chapterTitle = value.title;
            break;
        }
    }

    console.log(`Extracting Chapter ${chapterNum}: ${chapterTitle}`);

    // Function to convert HTML element to Markdown
    function elementToMarkdown(element, indent = 0) {
        if (!element) return '';

        const indentStr = '  '.repeat(indent);
        let result = '';

        // Text nodes
        if (element.nodeType === Node.TEXT_NODE) {
            const text = element.textContent.trim();
            return text ? text + ' ' : '';
        }

        // Element nodes
        if (element.nodeType === Node.ELEMENT_NODE) {
            const tagName = element.tagName.toLowerCase();

            switch (tagName) {
                case 'h1':
                    result = `\n# ${element.textContent.trim()}\n\n`;
                    break;

                case 'h2':
                    result = `\n## ${element.textContent.trim()}\n\n`;
                    break;

                case 'h3':
                    result = `\n### ${element.textContent.trim()}\n\n`;
                    break;

                case 'h4':
                    result = `\n#### ${element.textContent.trim()}\n\n`;
                    break;

                case 'h5':
                    result = `\n##### ${element.textContent.trim()}\n\n`;
                    break;

                case 'h6':
                    result = `\n###### ${element.textContent.trim()}\n\n`;
                    break;

                case 'p':
                    let pContent = '';
                    for (const child of element.childNodes) {
                        pContent += elementToMarkdown(child, indent);
                    }
                    result = `\n${pContent.trim()}\n\n`;
                    break;

                case 'pre':
                    const code = element.querySelector('code');
                    if (code) {
                        const lang = Array.from(code.classList)
                            .find(cls => cls.startsWith('language-'))
                            ?.replace('language-', '') || '';
                        result = `\n\`\`\`${lang}\n${code.textContent}\n\`\`\`\n\n`;
                    } else {
                        result = `\n\`\`\`\n${element.textContent}\n\`\`\`\n\n`;
                    }
                    break;

                case 'code':
                    if (element.parentElement.tagName.toLowerCase() !== 'pre') {
                        result = `\`${element.textContent}\``;
                    }
                    break;

                case 'a':
                    const href = element.getAttribute('href') || '';
                    const text = element.textContent.trim();
                    if (href) {
                        const fullHref = href.startsWith('http') ? href :
                                       href.startsWith('/') ? window.location.origin + href : href;
                        result = `[${text}](${fullHref})`;
                    } else {
                        result = text;
                    }
                    break;

                case 'img':
                    const src = element.getAttribute('src') || '';
                    const alt = element.getAttribute('alt') || 'image';
                    const fullSrc = src.startsWith('http') ? src :
                                  src.startsWith('//') ? 'https:' + src :
                                  src.startsWith('/') ? window.location.origin + src : src;
                    result = `\n![${alt}](${fullSrc})\n\n`;
                    break;

                case 'ul':
                    result = '\n';
                    for (const li of element.children) {
                        if (li.tagName.toLowerCase() === 'li') {
                            let liContent = '';
                            for (const child of li.childNodes) {
                                liContent += elementToMarkdown(child, indent + 1);
                            }
                            result += `${indentStr}- ${liContent.trim()}\n`;
                        }
                    }
                    result += '\n';
                    break;

                case 'ol':
                    result = '\n';
                    Array.from(element.children).forEach((li, index) => {
                        if (li.tagName.toLowerCase() === 'li') {
                            let liContent = '';
                            for (const child of li.childNodes) {
                                liContent += elementToMarkdown(child, indent + 1);
                            }
                            result += `${indentStr}${index + 1}. ${liContent.trim()}\n`;
                        }
                    });
                    result += '\n';
                    break;

                case 'blockquote':
                    const lines = element.textContent.trim().split('\n');
                    result = '\n' + lines.map(line => `> ${line}`).join('\n') + '\n\n';
                    break;

                case 'strong':
                case 'b':
                    result = `**${element.textContent}**`;
                    break;

                case 'em':
                case 'i':
                    result = `*${element.textContent}*`;
                    break;

                case 'br':
                    result = '  \n';
                    break;

                case 'hr':
                    result = '\n---\n\n';
                    break;

                case 'table':
                    result = '\n' + tableToMarkdown(element) + '\n\n';
                    break;

                case 'video':
                case 'iframe':
                    const videoSrc = element.getAttribute('src') || '';
                    if (videoSrc) {
                        const fullVideoSrc = videoSrc.startsWith('http') ? videoSrc :
                                           videoSrc.startsWith('//') ? 'https:' + videoSrc :
                                           videoSrc.startsWith('/') ? window.location.origin + videoSrc : videoSrc;
                        result = `\n**[Video/Embed](${fullVideoSrc})**\n\n`;
                    }
                    break;

                case 'script':
                case 'style':
                case 'nav':
                case 'header':
                case 'footer':
                    // Skip these elements
                    break;

                default:
                    // For other elements, process children
                    for (const child of element.childNodes) {
                        result += elementToMarkdown(child, indent);
                    }
                    break;
            }
        }

        return result;
    }

    function tableToMarkdown(table) {
        let md = '';
        const rows = Array.from(table.querySelectorAll('tr'));
        let headerFound = false;

        rows.forEach((row, rowIndex) => {
            const cells = Array.from(row.querySelectorAll('th, td'));
            const isHeader = row.querySelector('th') !== null;

            if (cells.length > 0) {
                const cellContents = cells.map(cell => cell.textContent.trim());
                md += '| ' + cellContents.join(' | ') + ' |\n';

                if (isHeader && !headerFound) {
                    md += '| ' + cellContents.map(() => '---').join(' | ') + ' |\n';
                    headerFound = true;
                }
            }
        });

        return md;
    }

    // Find the main article content
    const article = document.querySelector('article') ||
                   document.querySelector('main') ||
                   document.querySelector('[role="main"]') ||
                   document.querySelector('.article-content') ||
                   document.querySelector('.post-content');

    if (!article) {
        console.error('Could not find article content on the page');
        alert('Could not find article content. Please check the page structure.');
        return;
    }

    console.log('Converting to Markdown...');
    let markdown = elementToMarkdown(article);

    // Clean up excessive newlines
    markdown = markdown.replace(/\n{3,}/g, '\n\n').trim();

    // Add header
    const fullMarkdown = `# Chapter ${chapterNum}: ${chapterTitle}\n\n**Source:** ${url}\n\n---\n\n${markdown}`;

    console.log('Markdown generated, length:', fullMarkdown.length);

    // Download the file
    const blob = new Blob([fullMarkdown], { type: 'text/markdown' });
    const downloadUrl = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = downloadUrl;
    a.download = `chapter${chapterNum}.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(downloadUrl);

    console.log(`✓ Downloaded chapter${chapterNum}.md`);
    alert(`Chapter ${chapterNum} has been downloaded successfully!`);

})();
