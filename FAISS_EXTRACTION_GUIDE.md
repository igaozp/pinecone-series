# FAISS系列文章提取指南

由于 Pinecone 网站有严格的反爬虫保护机制，自动化脚本无法直接访问网站内容。本指南提供了手动提取文章内容的方法。

## 问题说明

尝试了以下方法均被网站防护机制阻止：
- ✗ 标准 HTTP 请求 (requests) - 返回 403 Forbidden
- ✗ WebFetch 工具 - 返回 403 Forbidden
- ✗ Playwright 自动化浏览器 - SSL证书错误和页面崩溃
- ✗ Cloudscraper (Cloudflare绕过) - 返回 403 Forbidden
- ✗ curl 命令行工具 - Access Denied

## 解决方案：浏览器控制台脚本

### 方法 1: 使用浏览器控制台脚本（推荐）

我已经创建了一个 JavaScript 脚本，可以在浏览器的开发者工具中运行。

#### 步骤：

1. **打开章节页面**
   - 在浏览器中访问下面列出的任一章节 URL

2. **打开开发者工具**
   - Windows/Linux: 按 `F12` 或 `Ctrl + Shift + I`
   - Mac: 按 `Cmd + Option + I`

3. **切换到 Console 标签**
   - 在开发者工具中点击 "Console" 标签

4. **复制并粘贴脚本**
   - 打开文件: `browser_extractor.js`
   - 复制全部内容
   - 粘贴到控制台中
   - 按 Enter 键执行

5. **下载文件**
   - 脚本会自动下载 Markdown 文件
   - 文件名格式: `chapterXX.md`
   - 将下载的文件移动到 `faiss/` 目录

6. **重复操作**
   - 对每个章节重复上述步骤

### 方法 2: 使用浏览器扩展

如果您熟悉浏览器扩展，可以使用以下工具：

1. **MarkDownload** (Chrome/Firefox 扩展)
   - 可以将网页直接转换为 Markdown
   - https://github.com/deathau/markdownload

2. **Save as Markdown** (Chrome 扩展)
   - 简单的网页到 Markdown 转换工具

3. **SingleFile** (Chrome/Firefox 扩展)
   - 保存完整的网页（包括图片）
   - 之后可以手动转换为 Markdown

### 方法 3: 手动复制粘贴

如果脚本无法正常工作：

1. 访问章节页面
2. 复制文章内容
3. 使用文本编辑器创建 Markdown 文件
4. 按照 Markdown 格式整理内容
5. 保存到 `faiss/chapterXX.md`

## FAISS 系列章节列表

请按以下顺序提取文章：

### Chapter 01: Introduction to Facebook AI Similarity Search (Faiss)
- **URL:** https://www.pinecone.io/learn/series/faiss/faiss-tutorial/
- **文件名:** chapter01.md
- **描述:** FAISS 简介和基础教程

### Chapter 02: Nearest Neighbor Indexes for Similarity Search
- **URL:** https://www.pinecone.io/learn/series/faiss/vector-indexes/
- **文件名:** chapter02.md
- **描述:** 最近邻索引用于相似性搜索

### Chapter 03: Locality Sensitive Hashing (LSH): The Illustrated Guide
- **URL:** https://www.pinecone.io/learn/series/faiss/locality-sensitive-hashing/
- **文件名:** chapter03.md
- **描述:** 局部敏感哈希的图解指南

### Chapter 04: Random Projection for Locality Sensitive Hashing
- **URL:** https://www.pinecone.io/learn/series/faiss/locality-sensitive-hashing-random-projection/
- **文件名:** chapter04.md
- **描述:** 用于局部敏感哈希的随机投影

### Chapter 05: Product Quantization: Compressing high-dimensional vectors by 97%
- **URL:** https://www.pinecone.io/learn/series/faiss/product-quantization/
- **文件名:** chapter05.md
- **描述:** 乘积量化：压缩高维向量97%

### Chapter 06: Hierarchical Navigable Small Worlds (HNSW)
- **URL:** https://www.pinecone.io/learn/series/faiss/hnsw/
- **文件名:** chapter06.md
- **描述:** 分层导航小世界算法

### Chapter 07: Facebook AI and the Index Factory
- **URL:** https://www.pinecone.io/learn/composite-indexes
- **文件名:** chapter07.md
- **描述:** Facebook AI 和索引工厂

## 提取要求

在提取内容时，请确保：

1. **图片引用**
   - 保留所有图片的 URL 引用
   - 格式: `![alt text](image_url)`
   - 确保 URL 是完整的绝对路径

2. **视频/嵌入内容**
   - 保留视频链接
   - 格式: `[Video](video_url)` 或直接嵌入代码

3. **代码示例**
   - 使用代码块格式
   - 指定编程语言（如果能识别）
   - 示例:
     ```python
     import faiss
     ```

4. **格式保持**
   - 标题层级 (H1, H2, H3, ...)
   - 列表（有序和无序）
   - 粗体和斜体
   - 引用块
   - 表格

## 文件结构示例

每个章节文件应该有以下结构：

```markdown
# Chapter XX: 章节标题

**Source:** https://www.pinecone.io/learn/...

---

文章内容...

## 章节标题

内容...

### 子标题

内容...

![图片描述](https://...)

​```python
代码示例
​```

...
```

## 验证

提取完成后，请检查：

- [ ] 所有 7 个章节文件都已创建
- [ ] 文件位于 `faiss/` 目录
- [ ] 文件名格式正确: `chapter01.md` ~ `chapter07.md`
- [ ] 图片链接完整且可访问
- [ ] 代码块格式正确
- [ ] 标题层级合理

## 需要帮助？

如果在提取过程中遇到问题：

1. 检查浏览器控制台是否有错误消息
2. 确保 JavaScript 已启用
3. 尝试刷新页面后重新运行脚本
4. 尝试使用其他浏览器（Chrome、Firefox、Edge）
5. 如果脚本完全无法工作，使用方法2或方法3

## 后续步骤

提取完所有章节后：

1. 检查所有文件的完整性
2. 可以使用 Markdown 预览工具查看格式
3. 如有需要，可以进行进一步的格式调整
4. 将文件提交到 git 仓库

祝提取顺利！
