# 第 02 章：用于相似性搜索的最近邻索引

来源：https://www.pinecone.io/learn/series/faiss/vector-indexes/

---

## 概述

本章探讨 Faiss 中可用的各种索引类型，以及如何为你的特定用例选择合适的索引。不同的索引在精度、内存使用和查询速度之间提供不同的权衡。

## 理解最近邻搜索

最近邻 (NN) 搜索是在数据集中找到与查询项目最相似的项目的问题。在向量的背景下：

- **精确搜索**：保证找到真正的最近邻
- **近似搜索**：以牺牲一些精度换取速度

## Faiss 中的索引类型

### 1. Flat 索引

**IndexFlatL2** 和 **IndexFlatIP**

- 存储所有向量，不进行压缩
- 执行穷举搜索（暴力搜索）
- 最准确但对大数据集最慢
- 作为比较的良好基准
- 内存使用：O(n × d)，其中 n 是向量数量，d 是维度

```python
import faiss
d = 128
index = faiss.IndexFlatL2(d)
```

**用例**：
- 小数据集（< 10,000 个向量）
- 当精度至关重要时
- 作为比较的基准

### 2. IVF（倒排文件）索引

**IndexIVFFlat**

- 将向量空间划分为 Voronoi 单元
- 使用 k-means 聚类创建单元
- 在查询时仅搜索单元
- 比 flat 索引显著更快，精度损失最小

```python
nlist = 100  # 聚类数量
quantizer = faiss.IndexFlatL2(d)
index = faiss.IndexIVFFlat(quantizer, d, nlist)
index.train(xb)  # IVF 需要训练
index.add(xb)
index.nprobe = 10  # 搜索的单元数量
```

**参数**：
- `nlist`：聚类数量（通常为 sqrt(n) 到 4*sqrt(n)）
- `nprobe`：搜索的聚类数量（越高 = 越准确但越慢）

**用例**：
- 中到大数据集（10K - 10M 向量）
- 当你可以容忍一些精度损失时
- 速度和精度的良好平衡

### 3. 乘积量化 (PQ) 索引

**IndexIVFPQ**

- 使用乘积量化压缩向量
- 大幅减少内存使用（通常减少 97%）
- 将 IVF 与 PQ 结合以获得速度和压缩
- 由于量化会有一些精度损失

```python
m = 8  # 子量化器数量
nlist = 100
index = faiss.IndexIVFPQ(quantizer, d, nlist, m, 8)
```

**参数**：
- `m`：子量化器数量（d 必须能被 m 整除）
- `nbits`：每个子量化器的位数（通常为 8）

**用例**：
- 非常大的数据集（> 10M 向量）
- 当内存有限时
- 可接受的精度损失

### 4. HNSW（分层可导航小世界）

**IndexHNSWFlat**

- 基于图的索引
- 出色的查询性能
- 比 IVF 更高的内存使用
- 不需要训练

```python
M = 32  # 每层连接数
index = faiss.IndexHNSWFlat(d, M)
index.hnsw.efConstruction = 40
index.hnsw.efSearch = 16
```

**参数**：
- `M`：每个元素的连接数（越高 = 精度越好，内存越多）
- `efConstruction`：构建期间动态候选列表的大小
- `efSearch`：搜索期间动态候选列表的大小

**用例**：
- 高性能要求
- 当内存不是限制时
- 需要高召回率和快速查询

## 选择合适的索引

### 决策因素

1. **数据集大小**：
   - < 10K：Flat
   - 10K - 1M：IVF
   - > 1M：IVFPQ 或 HNSW

2. **内存限制**：
   - 有限：IVFPQ
   - 充足：HNSW 或 Flat

3. **精度要求**：
   - 精确：Flat
   - 高：HNSW 或高 nprobe 的 IVF
   - 中等：IVF 或 IVFPQ

4. **查询速度**：
   - 最快：HNSW
   - 快：IVF 或 IVFPQ
   - 较慢：Flat

### 索引比较表

| 索引类型 | 速度 | 精度 | 内存 | 是否需要训练 |
|---------|------|------|------|-------------|
| Flat | 慢 | 精确 | 高 | 否 |
| IVF | 快 | 高 | 高 | 是 |
| IVFPQ | 快 | 中等 | 低 | 是 |
| HNSW | 最快 | 高 | 中等 | 否 |

## 索引训练

某些索引需要训练：

```python
# 训练 IVF 索引
index.train(training_vectors)
index.is_trained  # 应为 True
index.add(vectors)
```

训练学习数据的结构：
- IVF 学习聚类中心
- PQ 学习量化码本

## 性能调优

### 对于 IVF 索引：

```python
# 更多聚类 = 更快但需要更多训练数据
nlist = int(np.sqrt(n))

# 更多探测 = 更准确但更慢
index.nprobe = 10  # 从这里开始调整
```

### 对于 HNSW 索引：

```python
# 更高的 M = 更好的精度但更多内存
M = 32

# 更高的 efSearch = 更好的精度但更慢
index.hnsw.efSearch = 16
```

## 总结

选择合适的索引类型对于构建高效的相似性搜索系统至关重要。考虑你的具体要求：

- 数据集大小
- 内存限制
- 精度需求
- 查询速度要求

在接下来的章节中，我们将更详细地探讨特定的索引技术，从局部敏感哈希开始。

## 参考文献

- 原文：https://www.pinecone.io/learn/series/faiss/vector-indexes/
- [Faiss 索引文档](https://github.com/facebookresearch/faiss/wiki)
