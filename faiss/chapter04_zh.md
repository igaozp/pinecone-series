# 第 04 章：用于局部敏感哈希的随机投影

来源：https://www.pinecone.io/learn/series/faiss/random-projection/

---

## 概述

随机投影是一种强大的降维技术，能够保持点之间的距离。本章探讨随机投影如何用于 LSH，以及如何使高维数据的高效相似性搜索成为可能。

## Johnson-Lindenstrauss 引理

随机投影的理论基础来自 Johnson-Lindenstrauss (JL) 引理：

### JL 引理陈述

对于高维空间中的任意 n 个点的集合，存在一个映射到低维空间（O(log n) 维）的映射，该映射近似保持成对距离。

**关键见解**：我们可以大幅降低维度同时保持距离关系！

### 数学表述

给定：
- 原始维度：d
- 目标维度：k
- 失真参数：ε

那么对于 k ≥ 4(ε²/2 - ε³/3)⁻¹ log(n)，存在一个映射能够将所有成对距离保持在 (1±ε) 因子内。

## 随机投影基础

### 工作原理

1. **生成随机矩阵**：创建随机的 k×d 投影矩阵
2. **投影向量**：将原始向量乘以此矩阵
3. **结果**：具有保持距离的低维向量

### 简单示例

```python
import numpy as np

def random_projection(X, target_dim):
    """
    将 X 投影到低维空间。
    
    参数：
        X: (n, d) 数组，n 个 d 维向量
        target_dim: 目标维度 k
    
    返回：
        (n, k) 投影向量数组
    """
    n, d = X.shape
    # 生成随机投影矩阵
    R = np.random.randn(d, target_dim) / np.sqrt(target_dim)
    # 投影
    return np.dot(X, R)

# 示例用法
X = np.random.randn(1000, 128)  # 1000 个 128 维向量
X_projected = random_projection(X, 32)  # 投影到 32 维
print(f"原始形状: {X.shape}")
print(f"投影形状: {X_projected.shape}")
```

## 随机投影类型

### 1. 高斯随机投影

最常见的方法：
- 矩阵元素取自 N(0, 1/k)
- 满足 JL 引理
- 易于实现

```python
def gaussian_projection(d, k):
    return np.random.randn(d, k) / np.sqrt(k)
```

### 2. 稀疏随机投影

更高效：
- 大多数元素为零
- 计算更快
- 内存更少

```python
def sparse_projection(d, k, density=0.1):
    """
    创建稀疏随机投影矩阵。
    
    density: 非零元素的比例
    """
    from scipy import sparse
    nnz = int(d * k * density)
    data = np.random.randn(nnz)
    rows = np.random.randint(0, d, nnz)
    cols = np.random.randint(0, k, nnz)
    return sparse.coo_matrix((data, (rows, cols)), shape=(d, k))
```

### 3. 结构化随机投影

使用结构化矩阵提高效率：
- 快速哈达玛变换
- 循环矩阵
- O(d log k) 计算而非 O(dk)

## 用于 LSH 的随机超平面

随机超平面是随机投影在二进制哈希中的特殊应用。

### 算法

对于每个哈希位：
1. 生成随机超平面（随机 d 维向量）
2. 计算与输入向量的点积
3. 如果为正则位为 1，否则为 0

```python
class RandomHyperplaneLSH:
    def __init__(self, input_dim, num_bits):
        self.input_dim = input_dim
        self.num_bits = num_bits
        # 随机超平面
        self.hyperplanes = np.random.randn(num_bits, input_dim)
        # 归一化
        norms = np.linalg.norm(self.hyperplanes, axis=1, keepdims=True)
        self.hyperplanes = self.hyperplanes / norms
    
    def hash(self, vectors):
        """
        将向量哈希为二进制码。
        
        参数：
            vectors: (n, d) 数组
        
        返回：
            (n, num_bits) 二进制数组
        """
        projections = np.dot(vectors, self.hyperplanes.T)
        return (projections > 0).astype(np.int8)
    
    def hamming_distance(self, hash1, hash2):
        """计算哈希码之间的汉明距离。"""
        return np.sum(hash1 != hash2, axis=-1)

# 示例
lsh = RandomHyperplaneLSH(input_dim=128, num_bits=64)
vectors = np.random.randn(1000, 128)
hash_codes = lsh.hash(vectors)
print(f"哈希码形状: {hash_codes.shape}")
```

### 属性

- **保持角度距离**：相似角度 → 相似哈希码
- **高效**：快速点积计算
- **概率保证**：相同位的概率 ∝ 相似度

### 哈希冲突概率

对于角度为 θ 的两个向量：

```
P(hash_bit_match) = 1 - θ/π
```

对于 k 位：
```
P(k_bits_match) = (1 - θ/π)^k
```

## 相似性搜索中的应用

### 构建 LSH 索引

```python
class LSHIndex:
    def __init__(self, input_dim, num_tables, num_bits):
        self.num_tables = num_tables
        # 创建多个哈希表
        self.lsh_functions = [
            RandomHyperplaneLSH(input_dim, num_bits)
            for _ in range(num_tables)
        ]
        self.tables = [dict() for _ in range(num_tables)]
    
    def add(self, vectors, ids):
        """将向量添加到索引。"""
        for table_idx, lsh in enumerate(self.lsh_functions):
            hashes = lsh.hash(vectors)
            for vec_id, hash_code in zip(ids, hashes):
                # 转换为元组作为字典键
                key = tuple(hash_code)
                if key not in self.tables[table_idx]:
                    self.tables[table_idx][key] = []
                self.tables[table_idx][key].append(vec_id)
    
    def search(self, query, k=10):
        """搜索 k 个最近邻。"""
        candidates = set()
        for table_idx, lsh in enumerate(self.lsh_functions):
            query_hash = tuple(lsh.hash(query.reshape(1, -1))[0])
            if query_hash in self.tables[table_idx]:
                candidates.update(self.tables[table_idx][query_hash])
        return list(candidates)[:k]
```

## 优化技术

### 1. 自适应位数

- 大数据集使用更多位数
- 经验法则：num_bits ≈ log₂(n)

### 2. 数据相关投影

不使用纯随机：
- 基于 PCA 的投影
- 从数据学习投影
- 通常优于随机

### 3. 投影前旋转

为了更好的分布：
```python
# 投影前应用随机旋转
rotation = scipy.stats.special_ortho_group.rvs(d)
X_rotated = np.dot(X, rotation)
X_projected = random_projection(X_rotated, k)
```

## Faiss 中的随机投影

Faiss 在多个索引中使用随机投影：

### IndexLSH

```python
import faiss

d = 128
nbits = 64

# 创建使用随机超平面 LSH 的索引
index = faiss.IndexLSH(d, nbits)

# 可选地在哈希前旋转
index.rotate_data = True

# 添加向量
index.add(vectors)

# 搜索
D, I = index.search(queries, k=10)
```

### 与其他方法的组合

随机投影可以与以下方法组合：
- **IVF**：聚类前投影
- **PQ**：量化前降维
- **HNSW**：预处理以加快图构建

## 理论保证

### 距离保持

对于从 d 维到 k 维的随机投影：

```
E[||RP(x) - RP(y)||²] = ||x - y||²
```

投影精确保持期望距离！

### 浓度界限

以高概率 (1 - δ)：

```
(1 - ε)||x - y||² ≤ ||RP(x) - RP(y)||² ≤ (1 + ε)||x - y||²
```

对于 k = O(log(n)/ε²)

## 实际考虑

### 何时使用随机投影

✅ **适用于**：
- 高维数据（d > 1000）
- 需要降维
- 内存限制
- 作为其他方法的预处理步骤

❌ **不适用于**：
- 低维数据（d < 100）
- 当精确距离至关重要时
- 已经有高效索引时

### 参数选择

1. **目标维度 k**：
   - k = O(log n) 用于 JL 引理
   - k = 32-128 在实践中通常效果良好

2. **LSH 的位数**：
   - 从 d/2 到 d 开始
   - 对于更大的数据集增加

3. **表的数量**：
   - 通常 10-50 个表
   - 更多表 = 更高的召回率，更多内存

## 与其他降维方法的比较

| 方法 | 速度 | 保持 | 训练 | 用例 |
|------|------|------|------|------|
| 随机投影 | 快 | 距离 | 否 | 快速降维 |
| PCA | 中等 | 方差 | 是 | 统计分析 |
| 自编码器 | 慢 | 语义 | 是 | 深度学习 |
| t-SNE | 非常慢 | 局部结构 | 否 | 可视化 |

## 总结

随机投影是一种强大的技术：

- 在保持距离的同时降低维度
- 提供理论保证（JL 引理）
- 通过随机超平面实现高效的 LSH
- 作为相似性搜索的预处理效果良好

关键要点：
- 易于实现
- 计算高效
- 有理论依据
- 适用于实际应用

理解随机投影有助于构建更好的相似性搜索系统，并理解现代索引方法的数学基础。

## 参考文献

- 原文：https://www.pinecone.io/learn/series/faiss/random-projection/
- [Johnson-Lindenstrauss 引理](https://en.wikipedia.org/wiki/Johnson%E2%80%93Lindenstrauss_lemma)
- [随机投影教程](https://scikit-learn.org/stable/modules/random_projection.html)
- [Faiss 随机旋转](https://github.com/facebookresearch/faiss/wiki/Faiss-indexes#lsh)
