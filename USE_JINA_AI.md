# 使用 Jina AI 提取 FAISS 文章

虽然在当前的 Docker 环境中 Jina AI 也被阻止（返回 403），但您可以在本地计算机上使用 Jina AI Reader 来提取文章内容。

## 方法 1: 使用 curl（本地命令行）

在您的本地计算机上运行以下命令：

```bash
# 使用您的 API 密钥
export JINA_API_KEY="jina_ccf592ec8f8e470185afa074e7076614WpvRgv0U8B8R0yI8Dqte51xyw-Wi"

# 提取 Chapter 01
curl -H "Authorization: Bearer $JINA_API_KEY" \
  "https://r.jina.ai/https://www.pinecone.io/learn/series/faiss/faiss-tutorial/" \
  > faiss/chapter01.md

# 提取 Chapter 02
curl -H "Authorization: Bearer $JINA_API_KEY" \
  "https://r.jina.ai/https://www.pinecone.io/learn/series/faiss/vector-indexes/" \
  > faiss/chapter02.md

# 提取 Chapter 03
curl -H "Authorization: Bearer $JINA_API_KEY" \
  "https://r.jina.ai/https://www.pinecone.io/learn/series/faiss/locality-sensitive-hashing/" \
  > faiss/chapter03.md

# 提取 Chapter 04
curl -H "Authorization: Bearer $JINA_API_KEY" \
  "https://r.jina.ai/https://www.pinecone.io/learn/series/faiss/locality-sensitive-hashing-random-projection/" \
  > faiss/chapter04.md

# 提取 Chapter 05
curl -H "Authorization: Bearer $JINA_API_KEY" \
  "https://r.jina.ai/https://www.pinecone.io/learn/series/faiss/product-quantization/" \
  > faiss/chapter05.md

# 提取 Chapter 06
curl -H "Authorization: Bearer $JINA_API_KEY" \
  "https://r.jina.ai/https://www.pinecone.io/learn/series/faiss/hnsw/" \
  > faiss/chapter06.md

# 提取 Chapter 07
curl -H "Authorization: Bearer $JINA_API_KEY" \
  "https://r.jina.ai/https://www.pinecone.io/learn/composite-indexes" \
  > faiss/chapter07.md
```

## 方法 2: 使用 Python 脚本（本地运行）

保存以下脚本为 `local_jina_scraper.py` 并在本地运行：

```python
#!/usr/bin/env python3
import requests
import time

API_KEY = "jina_ccf592ec8f8e470185afa074e7076614WpvRgv0U8B8R0yI8Dqte51xyw-Wi"

CHAPTERS = [
    ('01', 'https://www.pinecone.io/learn/series/faiss/faiss-tutorial/', 'Introduction to FAISS'),
    ('02', 'https://www.pinecone.io/learn/series/faiss/vector-indexes/', 'Vector Indexes'),
    ('03', 'https://www.pinecone.io/learn/series/faiss/locality-sensitive-hashing/', 'LSH'),
    ('04', 'https://www.pinecone.io/learn/series/faiss/locality-sensitive-hashing-random-projection/', 'Random Projection'),
    ('05', 'https://www.pinecone.io/learn/series/faiss/product-quantization/', 'Product Quantization'),
    ('06', 'https://www.pinecone.io/learn/series/faiss/hnsw/', 'HNSW'),
    ('07', 'https://www.pinecone.io/learn/composite-indexes', 'Index Factory'),
]

headers = {
    'Authorization': f'Bearer {API_KEY}',
    'X-Return-Format': 'markdown',
}

for num, url, title in CHAPTERS:
    print(f"Fetching Chapter {num}: {title}...")
    try:
        response = requests.get(f"https://r.jina.ai/{url}", headers=headers, timeout=60)
        if response.status_code == 200:
            with open(f'faiss/chapter{num}.md', 'w', encoding='utf-8') as f:
                f.write(f"# Chapter {num}: {title}\n\n")
                f.write(f"**Source:** {url}\n\n---\n\n")
                f.write(response.text)
            print(f"  ✓ Saved chapter{num}.md")
        else:
            print(f"  ✗ Error {response.status_code}: {response.text[:100]}")
    except Exception as e:
        print(f"  ✗ Exception: {e}")

    time.sleep(2)  # Be polite

print("\nDone!")
```

然后运行：

```bash
python3 local_jina_scraper.py
```

## 方法 3: 使用浏览器和 Jina AI

1. 在浏览器中访问：`https://r.jina.ai/https://www.pinecone.io/learn/series/faiss/faiss-tutorial/`
2. 您可能需要先在 Jina AI 网站登录并使用您的 API 密钥
3. 保存返回的 Markdown 内容到对应的文件

## 方法 4: 一键批处理脚本（Bash）

创建 `download_all_jina.sh`:

```bash
#!/bin/bash

API_KEY="jina_ccf592ec8f8e470185afa074e7076614WpvRgv0U8B8R0yI8Dqte51xyw-Wi"

declare -A chapters=(
    ["01"]="https://www.pinecone.io/learn/series/faiss/faiss-tutorial/"
    ["02"]="https://www.pinecone.io/learn/series/faiss/vector-indexes/"
    ["03"]="https://www.pinecone.io/learn/series/faiss/locality-sensitive-hashing/"
    ["04"]="https://www.pinecone.io/learn/series/faiss/locality-sensitive-hashing-random-projection/"
    ["05"]="https://www.pinecone.io/learn/series/faiss/product-quantization/"
    ["06"]="https://www.pinecone.io/learn/series/faiss/hnsw/"
    ["07"]="https://www.pinecone.io/learn/composite-indexes"
)

mkdir -p faiss

for num in "${!chapters[@]}"; do
    url="${chapters[$num]}"
    echo "Downloading Chapter $num..."

    curl -s -H "Authorization: Bearer $API_KEY" \
         -H "X-Return-Format: markdown" \
         "https://r.jina.ai/$url" \
         -o "faiss/chapter$num.md"

    if [ $? -eq 0 ]; then
        echo "  ✓ Chapter $num saved"
    else
        echo "  ✗ Chapter $num failed"
    fi

    sleep 2
done

echo "All done!"
```

赋予执行权限并运行：

```bash
chmod +x download_all_jina.sh
./download_all_jina.sh
```

## 环境限制说明

在当前的 Docker/容器环境中，即使使用 Jina AI 也无法访问，可能原因：

1. **容器 IP 被阻止**: Docker 容器的 IP 可能被 Jina AI 或 Pinecone 列入黑名单
2. **网络限制**: 容器网络配置可能有限制
3. **自动化检测**: 服务可能检测到这是自动化环境

因此，**强烈建议在本地计算机上运行这些脚本**，成功率会高很多。

## Jina AI 优势

- ✅ 自动转换为 Markdown 格式
- ✅ 保留图片和链接
- ✅ 清理不必要的 HTML 元素
- ✅ 生成 LLM 友好的文本
- ✅ 支持大多数网站（如果没有特殊限制）

## 故障排查

如果在本地仍然遇到问题：

1. **检查 API 密钥是否有效**
   ```bash
   curl -H "Authorization: Bearer YOUR_KEY" https://r.jina.ai/https://example.com
   ```

2. **检查 API 配额**
   - 登录 Jina AI 控制台查看剩余配额

3. **尝试不使用认证**（如果有免费配额）
   ```bash
   curl "https://r.jina.ai/https://example.com"
   ```

4. **检查网络连接**
   ```bash
   ping r.jina.ai
   ```

## 备选方案

如果 Jina AI 也不能工作，请使用：
- `browser_extractor.js` - 浏览器控制台脚本
- `open_all_chapters.html` - 可视化界面
- 手动复制粘贴（见 `FAISS_EXTRACTION_GUIDE.md`）

---

**提示**: 建议先用一个章节测试，确认能正常工作后再批量下载所有章节。
