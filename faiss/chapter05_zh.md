# 第 05 章：乘积量化：将高维向量压缩 97%

来源：https://www.pinecone.io/learn/series/faiss/product-quantization/

---

## 概述

乘积量化 (PQ) 是一种向量压缩技术，可以将内存使用减少高达 97%，同时保持合理的搜索精度。本章探讨 PQ 的工作原理以及如何在 Faiss 中使用它来实现十亿级向量搜索。

## 内存问题

高维向量消耗大量内存：

- **128 维 float32**：每个向量 512 字节
- **10 亿个向量**：512 GB 内存
- **加载时间**：几分钟到几小时

乘积量化通过大幅压缩向量来解决这个问题。

## 什么是乘积量化？

乘积量化通过以下方式压缩向量：
1. **分割**向量为子向量
2. **独立量化**每个子向量
3. **用中心点 ID 表示**每个子向量

### 关键思想

不存储完整向量，而是存储引用学习到的中心点的小整数编码。

## 乘积量化工作原理

### 逐步过程

#### 1. 将向量分割为子向量

将 d 维向量分为 m 个子向量：

```python
# 原始向量：128 维
# 分割为 m=8 个子向量，每个 16 维

d = 128
m = 8  # 子量化器数量
d_sub = d // m  # 每个子向量 16 维

vector = np.random.randn(128)
sub_vectors = vector.reshape(m, d_sub)
print(f"子向量形状: {sub_vectors.shape}")  # (8, 16)
```

#### 2. 学习码本

对于每个子空间，使用 k-means 学习 k 个中心点：

```python
def learn_codebooks(vectors, m, k):
    """
    为乘积量化学习码本。
    
    参数：
        vectors: (n, d) 训练向量
        m: 子量化器数量
        k: 码本大小（通常为 256）
    
    返回：
        codebooks: (m, k, d/m) 中心点数组
    """
    n, d = vectors.shape
    d_sub = d // m
    codebooks = np.zeros((m, k, d_sub))
    
    for i in range(m):
        # 提取此子空间的子向量
        sub_vectors = vectors[:, i*d_sub:(i+1)*d_sub]
        
        # 运行 k-means
        from sklearn.cluster import KMeans
        kmeans = KMeans(n_clusters=k, random_state=0)
        kmeans.fit(sub_vectors)
        
        codebooks[i] = kmeans.cluster_centers_
    
    return codebooks
```

#### 3. 编码向量

将每个子向量替换为最近的中心点 ID：

```python
def encode_vector(vector, codebooks):
    """
    使用乘积量化编码向量。
    
    参数：
        vector: (d,) 数组
        codebooks: (m, k, d/m) 码本
    
    返回：
        codes: (m,) 中心点 ID 数组
    """
    m, k, d_sub = codebooks.shape
    codes = np.zeros(m, dtype=np.uint8)
    
    for i in range(m):
        sub_vector = vector[i*d_sub:(i+1)*d_sub]
        # 找到最近的中心点
        distances = np.sum((codebooks[i] - sub_vector)**2, axis=1)
        codes[i] = np.argmin(distances)
    
    return codes
```

### 完整示例

```python
import numpy as np
from sklearn.cluster import KMeans

class ProductQuantizer:
    def __init__(self, m, k):
        """
        初始化乘积量化器。
        
        参数：
            m: 子量化器数量
            k: 码本大小（通常为 256 用于 uint8）
        """
        self.m = m
        self.k = k
        self.codebooks = None
    
    def fit(self, X):
        """从训练数据学习码本。"""
        n, d = X.shape
        self.d = d
        self.d_sub = d // self.m
        
        assert d % self.m == 0, "d 必须能被 m 整除"
        
        self.codebooks = np.zeros((self.m, self.k, self.d_sub))
        
        for i in range(self.m):
            sub_vectors = X[:, i*self.d_sub:(i+1)*self.d_sub]
            kmeans = KMeans(n_clusters=self.k, random_state=0, n_init=10)
            kmeans.fit(sub_vectors)
            self.codebooks[i] = kmeans.cluster_centers_
    
    def encode(self, X):
        """将向量编码为 PQ 码。"""
        n = X.shape[0]
        codes = np.zeros((n, self.m), dtype=np.uint8)
        
        for i in range(self.m):
            sub_vectors = X[:, i*self.d_sub:(i+1)*self.d_sub]
            # 为每个向量找到最近的中心点
            for j in range(n):
                distances = np.sum((self.codebooks[i] - sub_vectors[j])**2, axis=1)
                codes[j, i] = np.argmin(distances)
        
        return codes
    
    def decode(self, codes):
        """从编码重建近似向量。"""
        n = codes.shape[0]
        X_reconstructed = np.zeros((n, self.d))
        
        for i in range(self.m):
            X_reconstructed[:, i*self.d_sub:(i+1)*self.d_sub] = \
                self.codebooks[i][codes[:, i]]
        
        return X_reconstructed

# 示例用法
X_train = np.random.randn(10000, 128)
pq = ProductQuantizer(m=8, k=256)
pq.fit(X_train)

# 编码测试向量
X_test = np.random.randn(100, 128)
codes = pq.encode(X_test)
print(f"原始大小: {X_test.nbytes} 字节")
print(f"压缩大小: {codes.nbytes} 字节")
print(f"压缩比: {X_test.nbytes / codes.nbytes:.1f}x")
```

## 内存节省

### 压缩比计算

**原始表示**：
- 128 维 × 4 字节 (float32) = 512 字节

**PQ 表示**：
- m=8 个子量化器 × 1 字节 (uint8) = 8 字节

**压缩**：512 / 8 = 64x = **减少 98.4%**！

对于典型设置（m=8, k=256）：
- **内存**：减少约 96-98%
- **精度**：保持 90-95% 召回率

## 非对称距离计算

对于搜索，我们使用**非对称距离计算** (ADC)：

### 标准方法（对称）

查询和数据库向量都被压缩：
- **快**但**不太准确**
- 不常用

### 非对称方法

仅数据库向量被压缩：
- 查询保持全精度
- 更准确
- Faiss 中的标准方法

```python
def compute_distance_table(query, codebooks):
    """
    预计算查询到所有中心点的距离。
    
    参数：
        query: (d,) 查询向量
        codebooks: (m, k, d/m) 码本
    
    返回：
        distance_table: (m, k) 距离
    """
    m, k, d_sub = codebooks.shape
    distance_table = np.zeros((m, k))
    
    for i in range(m):
        query_sub = query[i*d_sub:(i+1)*d_sub]
        for j in range(k):
            distance_table[i, j] = np.sum((query_sub - codebooks[i, j])**2)
    
    return distance_table

def compute_distances(codes, distance_table):
    """
    使用距离表计算近似距离。
    
    参数：
        codes: (n, m) PQ 编码
        distance_table: (m, k) 预计算距离
    
    返回：
        distances: (n,) 近似 L2 距离
    """
    n, m = codes.shape
    distances = np.zeros(n)
    
    for i in range(m):
        distances += distance_table[i, codes[:, i]]
    
    return distances

# 用法
query = np.random.randn(128)
distance_table = compute_distance_table(query, pq.codebooks)
distances = compute_distances(codes, distance_table)
```

## Faiss 中的乘积量化

### IndexPQ

基本 PQ 索引：

```python
import faiss

d = 128
m = 8  # 子量化器数量
nbits = 8  # 每个编码的位数（256 个中心点）

# 创建索引
index = faiss.IndexPQ(d, m, nbits)

# 训练索引
index.train(training_vectors)

# 添加向量
index.add(database_vectors)

# 搜索
k = 10
D, I = index.search(query_vectors, k)
```

### IndexIVFPQ

将 IVF 与 PQ 结合以获得更好的性能：

```python
nlist = 100  # 聚类数量
m = 8
nbits = 8

# 为 IVF 创建量化器
quantizer = faiss.IndexFlatL2(d)

# 创建 IVFPQ 索引
index = faiss.IndexIVFPQ(quantizer, d, nlist, m, nbits)

# 训练
index.train(training_vectors)

# 添加向量
index.add(database_vectors)

# 设置搜索参数
index.nprobe = 10

# 搜索
D, I = index.search(query_vectors, k)
```

## 参数选择

### 子量化器数量 (m)

权衡：
- **更大的 m**：更好的压缩，略低的精度
- **更小的 m**：较少的压缩，更好的精度
- **典型值**：8、16、32、64
- **约束**：d 必须能被 m 整除

### 码本大小 (k)

通常固定：
- **k = 256**：使用 uint8 编码（最常见）
- **k = 65536**：使用 uint16 编码（更好的精度，更多内存）

### IVF 聚类数量 (nlist)

对于 IVFPQ：
- **小数据集**：nlist = sqrt(n)
- **大数据集**：nlist = 4 * sqrt(n)

## 精度与压缩权衡

| 配置 | 压缩 | 精度 | 用例 |
|------|------|------|------|
| m=4, k=256 | ~32x | 高 | 小数据集 |
| m=8, k=256 | ~64x | 中高 | 通用 |
| m=16, k=256 | ~128x | 中等 | 大规模 |
| m=32, k=256 | ~256x | 较低 | 超大规模 |

## 优化

### 多义编码

Faiss 扩展以获得更好的搜索：
- 使用汉明距离进行编码
- 在完整距离计算前过滤候选
- 以最小精度损失获得显著加速

```python
# 启用多义编码
index_pq.search_type = faiss.METRIC_INNER_PRODUCT
index_pq.polysemous_ht = 54  # 汉明阈值
```

### SIMD 优化

Faiss 使用 SIMD 指令：
- 向量化的距离表查找
- 在现代 CPU 上加速 4-8 倍
- Faiss 中自动实现

## 何时使用乘积量化

✅ **在以下情况使用 PQ**：
- 内存有限
- 数据集非常大（> 1M 向量）
- 可以接受约 5-10% 的精度损失
- 需要快速搜索速度

❌ **在以下情况避免使用 PQ**：
- 需要精确搜索
- 内存充足
- 数据集小（< 100K 向量）
- 不能容忍任何精度损失

## 实际示例：十亿级搜索

```python
import faiss
import numpy as np

# 十亿级参数
d = 128
nlist = 65536  # ~sqrt(1B) * 4
m = 64  # 激进压缩
k_search = 100

# 创建索引
quantizer = faiss.IndexFlatL2(d)
index = faiss.IndexIVFPQ(quantizer, d, nlist, m, 8)

# 在样本上训练
training_size = 1_000_000
training_data = np.random.randn(training_size, d).astype('float32')
index.train(training_data)

# 批量添加
batch_size = 10_000_000
# for batch in batches:
#     index.add(batch)

# 配置搜索
index.nprobe = 64  # 搜索 64 个聚类

# 搜索
query = np.random.randn(1, d).astype('float32')
D, I = index.search(query, k_search)
```

## 总结

乘积量化对于大规模向量搜索至关重要：

- **压缩**：减少 96-98% 内存
- **速度**：通过查找表快速计算距离
- **可扩展性**：实现十亿级搜索
- **权衡**：以微小精度损失换取巨大收益

关键概念：
- 将向量分割为子向量
- 独立量化每个子向量
- 使用非对称距离计算
- 与 IVF 结合以获得最佳效果

PQ 是现代相似性搜索的基石技术，使得在普通硬件上搜索数十亿向量成为可能。

## 参考文献

- 原文：https://www.pinecone.io/learn/series/faiss/product-quantization/
- [乘积量化论文](https://lear.inrialpes.fr/pubs/2011/JDS11/jegou_searching_with_quantization.pdf)
- [Faiss PQ 文档](https://github.com/facebookresearch/faiss/wiki/Faiss-indexes#pq)
