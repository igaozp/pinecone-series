# Pinecone Series 文章翻译

本仓库用于存储从 Pinecone Learn 网站提取的技术文章系列，特别关注 FAISS (Facebook AI Similarity Search) 相关内容。

## 📁 项目结构

```
pinecone-series/
├── faiss/                          # FAISS 系列文章 Markdown 文件
│   ├── README.md                   # FAISS 系列说明
│   ├── chapter01.md               # 待提取
│   ├── chapter02.md               # 待提取
│   ├── chapter03.md               # 待提取
│   ├── chapter04.md               # 待提取
│   ├── chapter05.md               # 待提取
│   ├── chapter06.md               # 待提取
│   └── chapter07.md               # 待提取
├── browser_extractor.js           # 浏览器控制台提取脚本
├── open_all_chapters.html         # 章节链接快速访问页面
├── FAISS_EXTRACTION_GUIDE.md      # 详细提取指南
├── scrape_faiss.py                # Python 抓取脚本（基础版）
├── scrape_faiss_cloudscraper.py   # Python 抓取脚本（Cloudscraper）
└── scrape_faiss_playwright.py     # Python 抓取脚本（Playwright）
```

## 🎯 FAISS 系列

### 关于 FAISS

FAISS (Facebook AI Similarity Search) 是由 Meta AI Research 开发的用于高效相似性搜索和密集向量聚类的库。它包含了多种搜索算法，可以处理任何大小的向量集合，甚至是无法完全载入内存的向量集。

### 系列内容

本系列包含 7 个章节，涵盖从基础到高级的 FAISS 使用知识：

1. **Introduction to FAISS** - FAISS 入门
2. **Vector Indexes** - 向量索引
3. **Locality Sensitive Hashing** - 局部敏感哈希
4. **Random Projection** - 随机投影
5. **Product Quantization** - 乘积量化
6. **HNSW** - 分层导航小世界
7. **Index Factory** - 索引工厂

## 🚀 快速开始

### 方法 1: 使用 HTML 快速访问页面（推荐）

1. 在浏览器中打开 `open_all_chapters.html`
2. 点击"打开所有章节"按钮或单独打开每个章节
3. 按照页面上的说明使用浏览器控制台脚本提取内容

### 方法 2: 使用浏览器控制台脚本

1. 访问任一章节 URL（见下方列表）
2. 按 `F12` 打开开发者工具
3. 切换到 Console 标签
4. 复制 `browser_extractor.js` 的内容并粘贴
5. 按 Enter 执行
6. 自动下载 Markdown 文件
7. 将文件移动到 `faiss/` 目录

### 方法 3: 使用 Python 脚本（已尝试，受限于网站防护）

由于网站的反爬虫保护机制，自动化 Python 脚本无法直接访问。已尝试的方法包括：
- 标准 HTTP 请求（requests）
- Cloudscraper（Cloudflare 绕过）
- Playwright（自动化浏览器）

所有方法均返回 403 Forbidden 或其他错误。

## 📚 章节链接

| 章节 | 标题 | URL |
|------|------|-----|
| 01 | Introduction to FAISS | https://www.pinecone.io/learn/series/faiss/faiss-tutorial/ |
| 02 | Vector Indexes | https://www.pinecone.io/learn/series/faiss/vector-indexes/ |
| 03 | Locality Sensitive Hashing | https://www.pinecone.io/learn/series/faiss/locality-sensitive-hashing/ |
| 04 | Random Projection | https://www.pinecone.io/learn/series/faiss/locality-sensitive-hashing-random-projection/ |
| 05 | Product Quantization | https://www.pinecone.io/learn/series/faiss/product-quantization/ |
| 06 | HNSW | https://www.pinecone.io/learn/series/faiss/hnsw/ |
| 07 | Index Factory | https://www.pinecone.io/learn/composite-indexes |

## 📋 提取要求

提取的 Markdown 文件应该包含：

- ✅ 完整的文章标题和内容
- ✅ 所有图片的完整 URL 引用
- ✅ 视频和嵌入内容的链接
- ✅ 格式正确的代码块（带语言标识）
- ✅ 保持原有的格式结构（标题、列表、表格等）

## 🔧 工具说明

### browser_extractor.js
浏览器控制台脚本，可以在网页上直接运行，自动提取内容并下载为 Markdown 文件。

### open_all_chapters.html
提供友好的界面，包含所有章节链接和使用说明。可以一键打开所有章节页面。

### Python 脚本
虽然无法绕过网站防护，但保留这些脚本作为参考：
- `scrape_faiss.py` - 基础 HTTP 请求
- `scrape_faiss_cloudscraper.py` - Cloudflare 绕过尝试
- `scrape_faiss_playwright.py` - 浏览器自动化尝试

## 📖 详细文档

查看 `FAISS_EXTRACTION_GUIDE.md` 获取：
- 详细的提取步骤
- 问题排查指南
- 替代方案说明
- 验证清单

## ⚠️ 重要说明

### 网站访问限制

Pinecone Learn 网站有严格的访问保护机制：
- 阻止自动化脚本访问
- 可能使用 Cloudflare 或类似的防护服务
- 需要真实浏览器环境才能访问

### 版权声明

所有文章内容版权归 Pinecone Systems Inc. 所有。本项目仅用于：
- 个人学习和研究
- 技术文档参考
- 非商业用途

如需商业使用，请联系 Pinecone 官方获取授权。

## 🤝 贡献

如果您成功提取了某个章节，欢迎提交 Pull Request：

1. Fork 本仓库
2. 创建特性分支
3. 添加提取的 Markdown 文件到 `faiss/` 目录
4. 提交更改
5. 创建 Pull Request

## 📞 帮助

如果在提取过程中遇到问题：

1. 查看 `FAISS_EXTRACTION_GUIDE.md` 的常见问题部分
2. 尝试不同的浏览器（Chrome、Firefox、Edge）
3. 确保 JavaScript 已启用
4. 检查浏览器控制台的错误消息

## 📝 待办事项

- [ ] 提取 Chapter 01
- [ ] 提取 Chapter 02
- [ ] 提取 Chapter 03
- [ ] 提取 Chapter 04
- [ ] 提取 Chapter 05
- [ ] 提取 Chapter 06
- [ ] 提取 Chapter 07
- [ ] 验证所有图片链接
- [ ] 检查代码格式
- [ ] 翻译成中文（可选）

## 🌟 相关资源

- [FAISS GitHub](https://github.com/facebookresearch/faiss)
- [Pinecone Learn](https://www.pinecone.io/learn/)
- [FAISS Documentation](https://faiss.ai/)

---

**最后更新:** 2025-11-13
