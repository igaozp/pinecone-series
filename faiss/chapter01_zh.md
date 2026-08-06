# 第 01 章：Facebook AI 相似性搜索 (Faiss) 简介

来源：https://www.pinecone.io/learn/series/faiss/faiss-tutorial/

---

## 概述

Facebook AI 相似性搜索 (Faiss) 是最流行的高效相似性搜索实现之一。本章介绍 Faiss 库、其用途、功能以及在相似性搜索中的背景。

## 什么是 Faiss？

Faiss 是由 Facebook AI 开发的库，能够对稠密向量进行高效的相似性搜索和聚类。它允许你：

- 构建向量索引
- 使用另一个向量作为查询，在该索引中搜索最相似的向量
- 将搜索时间加速到非凡的水平

这对于基于向量的 AI 应用至关重要，例如：
- 语义搜索
- 推荐系统
- 图像和视频搜索
- 异常检测

## 为什么需要向量搜索？

传统搜索引擎在精确匹配方面表现良好，但往往无法识别项目之间的语义或上下文"相似性"。Faiss 使应用程序能够找到在含义或内容上相似的项目，而不是精确的文本匹配。

这对于以下场景特别有用：
- 推荐引擎
- 在向量空间中测量"相似性"的媒体搜索平台
- 内容发现系统

## 核心概念

### 稠密向量嵌入

Faiss 使用稠密向量嵌入来表示数据。这些向量来自机器学习模型（如用于文本的 BERT 或用于图像的 ResNet），编码语义信息，允许进行数值比较。

### 距离度量

Faiss 支持多种相似性度量：

1. **欧氏距离 (L2)**：用于几何相似性
2. **余弦相似度**：对文本和嵌入至关重要，关注方向而非大小
3. **内积**：用于特定用例

### 索引方法

Faiss 实现了多种索引方法：

1. **Flat 索引**：存储所有向量用于暴力精确搜索；准确但对大数据集较慢
2. **倒排文件索引 (IVF)**：使用 k-means 将向量分区到聚类中，实现更快的近似搜索
3. **乘积量化 (PQ)**：将向量压缩为更短的编码以减少内存使用
4. **分层可导航小世界 (HNSW)**：使用基于图的索引实现极快的近似最近邻搜索

## Faiss 入门

### 安装

```bash
pip install faiss-cpu
# 或者 GPU 支持
pip install faiss-gpu
```

### 基本示例

```python
import faiss
import numpy as np

# 创建一些随机向量
dimension = 128
nb = 1000  # 数据库向量数量
xb = np.random.random((nb, dimension)).astype('float32')

# 构建索引
index = faiss.IndexFlatL2(dimension)
index.add(xb)

# 创建查询向量
nq = 5  # 查询数量
xq = np.random.random((nq, dimension)).astype('float32')

# 搜索 k 个最近邻
k = 5
D, I = index.search(xq, k)
print(I)  # 最近邻的索引
print(D)  # 到最近邻的距离
```

## CPU 和 GPU 加速

Faiss 可以在 CPU 和 GPU 上运行：

- **CPU**：适合中等规模的数据集
- **GPU**：通过 GPU 实现高效扩展，支持非常大的向量数据集

## 应用

Faiss 改变了基于相似性的工作流程，支持：

- 推荐系统
- 语义文本搜索
- 图像中的视觉搜索
- 重复检测
- 异常检测
- 基于内容的过滤

## 总结

Faiss 为高维空间中的高效相似性搜索提供了强大的工具包。理解向量嵌入、距离度量和索引策略的基础知识对于构建有效的搜索系统至关重要。

在接下来的章节中，我们将深入探讨特定的索引技术和优化策略。

## 参考文献

- [Faiss GitHub 仓库](https://github.com/facebookresearch/faiss)
- [Faiss 文档](https://faiss.ai/)
- 原文：https://www.pinecone.io/learn/series/faiss/faiss-tutorial/
