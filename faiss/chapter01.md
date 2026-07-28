# 第 01 章：Facebook AI 相似性搜索（Faiss）简介

原文：[Faiss 教程](https://www.pinecone.io/learn/series/faiss/faiss-tutorial/)

---

## 概览

Facebook AI Similarity Search（Faiss）是最流行的高效相似性搜索实现之一。本章将介绍 Faiss 库、它的用途与能力，以及它在相似性搜索领域中的定位。

## 什么是 Faiss？

Faiss 是 Facebook AI 开发的一个库，可用于对稠密向量进行高效的相似性搜索和聚类。使用它可以：

- 为向量构建索引；
- 用另一个向量作为查询，在索引中搜索与之最相似的向量；
- 将搜索速度提升到非常高的水平。

这些能力对于以下基于向量的 AI 应用至关重要：

- 语义搜索；
- 推荐系统；
- 图像和视频搜索；
- 异常检测。

## 为什么需要向量搜索？

传统搜索引擎擅长精确匹配，却往往难以识别项目在语义或上下文上的“相似”。Faiss 让应用能够按含义或内容寻找相似项目，而不是只匹配完全相同的文本。

它尤其适用于：

- 推荐引擎；
- 在向量空间中衡量“相似度”的媒体搜索平台；
- 内容发现系统。

## 核心概念

### 稠密向量嵌入

Faiss 使用稠密向量嵌入来表示数据。这些向量由机器学习模型生成（例如用于文本的 BERT 或用于图像的 ResNet），能够编码语义信息，从而允许我们用数值方式进行比较。

### 距离度量

Faiss 支持多种相似性度量：

1. **欧氏距离（L2）**：用于衡量几何上的相似性；
2. **余弦相似度**：对文本和嵌入尤为重要，它关注方向而非向量大小；
3. **内积**：适用于特定的使用场景。

### 索引方法

Faiss 实现了多种索引方法：

1. **Flat 索引**：保存全部向量并进行暴力精确搜索；结果准确，但在大型数据集上速度较慢；
2. **倒排文件索引（IVF）**：使用 k-means 将向量划分为多个聚类，从而实现快得多的近似搜索；
3. **乘积量化（PQ）**：把向量压缩成更短的编码，以降低内存占用；
4. **分层可导航小世界（HNSW）**：使用基于图的索引，完成速度极快的近似最近邻搜索。

## Faiss 快速入门

### 安装

```bash
pip install faiss-cpu
# 如需 GPU 支持
pip install faiss-gpu
```

### 基础示例

```python
import faiss
import numpy as np

# 创建一些随机向量
dimension = 128
nb = 1000  # 数据库向量的数量
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

## CPU 与 GPU 加速

Faiss 既能在 CPU 上运行，也能在 GPU 上运行：

- **CPU**：适合中等规模的数据集；
- **GPU**：借助 GPU 实现高效扩展，能够支持非常大的向量数据集。

## 应用场景

Faiss 改变了许多基于相似性的工作流程，常见用途包括：

- 推荐系统；
- 语义文本搜索；
- 图像视觉搜索；
- 重复内容检测；
- 异常检测；
- 基于内容的过滤。

## 小结

Faiss 为高维空间中的高效相似性搜索提供了一套强大的工具。理解向量嵌入、距离度量和索引策略等基础知识，是构建有效搜索系统的关键。

接下来的章节将深入讲解具体的索引技术和优化策略。

## 参考资料

- [Faiss GitHub 仓库](https://github.com/facebookresearch/faiss)
- [Faiss 文档](https://faiss.ai/)
- [英文原文](https://www.pinecone.io/learn/series/faiss/faiss-tutorial/)
