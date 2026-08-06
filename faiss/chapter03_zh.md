# 第 03 章：局部敏感哈希 (LSH)：图解指南

来源：https://www.pinecone.io/learn/series/faiss/locality-sensitive-hashing/

---

## 概述

局部敏感哈希 (LSH) 是近似最近邻搜索的基本技术。本章探讨 LSH 的工作原理、为什么它对相似性搜索很重要，以及如何在 Faiss 中实现它。

## 精确搜索的问题

对于拥有数百万或数十亿向量的大型数据集，精确最近邻搜索在计算上变得不可行：

- **暴力搜索**：O(n × d) 复杂度
- **内存需求**：与数据集大小线性相关
- **查询延迟**：对实时应用不可接受

LSH 通过牺牲精确性来换取速度，提供了解决方案。

## 什么是局部敏感哈希？

LSH 是一种哈希技术，其中相似的输入以高概率被哈希到相同的桶中。与传统哈希（旨在最小化冲突）不同，LSH 鼓励相似项目的冲突。

### 关键原则

1. **相似项目 → 相似哈希**：在原始空间中接近的项目应该哈希到相同的桶
2. **不同项目 → 不同哈希**：相距较远的项目应该哈希到不同的桶
3. **概率保证**：以高概率工作，而非确定性

## LSH 工作原理

### 基本算法

1. **哈希函数设计**：创建保持局部性的哈希函数
2. **多个哈希表**：使用多个哈希表以提高召回率
3. **分桶**：将所有向量哈希到桶中
4. **查询时间**：哈希查询向量，仅在匹配的桶内搜索

### 哈希函数族

针对不同的距离度量存在不同的 LSH 族：

1. **随机超平面（用于余弦相似度）**：
   - 使用随机超平面划分空间
   - 哈希位 = 向量位于超平面的哪一侧

2. **p 稳定分布（用于欧氏距离）**：
   - 使用具有 p 稳定分布的随机投影
   - 保持距离关系

### 示例：随机超平面 LSH

```python
import numpy as np

class RandomHyperplaneLSH:
    def __init__(self, num_bits, dimension):
        self.num_bits = num_bits
        # 生成随机超平面
        self.hyperplanes = np.random.randn(num_bits, dimension)
    
    def hash(self, vector):
        # 计算与每个超平面的点积
        projections = np.dot(self.hyperplanes, vector)
        # 返回二进制哈希码
        return (projections > 0).astype(int)
    
    def hash_to_int(self, vector):
        binary_hash = self.hash(vector)
        # 将二进制转换为整数
        return int(''.join(binary_hash.astype(str)), 2)

# 用法
lsh = RandomHyperplaneLSH(num_bits=8, dimension=128)
vector = np.random.randn(128)
hash_value = lsh.hash_to_int(vector)
print(f"哈希值: {hash_value}")
```

## LSH 参数

### 关键参数

1. **哈希函数数量 (k)**：
   - 更多位数 = 更具体的桶
   - 更少的假阳性，但可能错过邻居
   
2. **哈希表数量 (L)**：
   - 更多表 = 更高的召回率
   - 更多内存和计算

3. **权衡**：
   - 高 k，低 L：高精度，低召回率
   - 低 k，高 L：高召回率，较低精度

### 参数选择

```
邻居哈希到同一桶的概率：p1 ≈ (1 - θ/180)^k
非邻居哈希到一起的概率：p2 ≈ (1 - θ'/180)^k

其中 θ 和 θ' 是向量之间的角度
```

## Faiss 中的 LSH

Faiss 通过 `IndexLSH` 类实现 LSH：

```python
import faiss

d = 128  # 维度
nbits = 2 * d  # 哈希码中的位数

# 创建 LSH 索引
index = faiss.IndexLSH(d, nbits)

# 添加向量
index.add(vectors)

# 搜索
k = 5
D, I = index.search(query_vectors, k)
```

### Faiss LSH 特性

- **二进制码**：紧凑表示
- **快速汉明距离**：高效的相似性计算
- **旋转**：可选旋转以获得更好的分布
- **多探测**：可以探测多个桶

## 多探测 LSH

多探测 LSH 不使用很多哈希表，而是：
- 使用更少的哈希表
- 每个表探测多个附近的桶
- 在保持召回率的同时减少内存

```python
# 在 Faiss 中，由搜索参数控制
index.nprobe = 10  # 探测的桶数量
```

## LSH 的优势

1. **亚线性查询时间**：O(n^ρ)，其中 ρ < 1
2. **内存高效**：可以使用紧凑的哈希码
3. **理论保证**：精度的概率界限
4. **简单性**：易于实现和理解

## LSH 的局限性

1. **参数调优**：需要仔细选择 k 和 L
2. **维度相关**：在非常高维度下性能下降（"维度诅咒"）
3. **中等精度**：其他方法（HNSW、IVF）通常表现更好
4. **固定结构**：难以适应数据分布

## LSH 与其他方法的比较

| 方法 | 速度 | 精度 | 内存 | 训练 |
|------|------|------|------|------|
| LSH | 快 | 中等 | 低 | 否 |
| IVF | 快 | 高 | 中等 | 是 |
| HNSW | 最快 | 高 | 高 | 否 |
| PQ | 快 | 中等 | 非常低 | 是 |

## 实际考虑

### 何时使用 LSH

- **高维稀疏数据**：文本、用户-项目交互
- **流数据**：不需要训练
- **内存受限**：二进制码紧凑
- **快速原型设计**：实现简单

### 何时使用替代方案

- **稠密嵌入**：HNSW 或 IVF 通常更好
- **最高精度需求**：使用 HNSW
- **非常大的规模**：考虑 IVFPQ
- **有训练数据**：基于 IVF 的方法可能表现更好

## 高级主题

### 学习型 LSH

现代方法：
- 从数据学习哈希函数
- 使用神经网络生成哈希码
- 通常优于随机 LSH

### 交叉多面体 LSH

最近的改进：
- 使用交叉多面体结构
- 优于随机超平面
- 在某些 Faiss 变体中实现

## 总结

LSH 是近似最近邻搜索的基础技术：

- 将相似项目哈希到相同的桶
- 以精确性换取速度
- 对某些数据类型效果良好
- 理解 LSH 有助于理解现代方法

虽然像 HNSW 这样的新方法在实践中通常优于 LSH，但 LSH 在以下方面仍然重要：
- 理解相似性搜索基础
- 特定用例（流数据、稀疏数据）
- 理论分析

## 参考文献

- 原文：https://www.pinecone.io/learn/series/faiss/locality-sensitive-hashing/
- [LSH 教程 - Andoni & Indyk](https://web.mit.edu/andoni/www/LSH/)
- [Faiss LSH 文档](https://github.com/facebookresearch/faiss/wiki/Faiss-indexes#lsh)
