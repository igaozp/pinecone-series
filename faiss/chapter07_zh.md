# 第 07 章：复合索引和 Faiss 索引工厂

来源：https://www.pinecone.io/learn/series/faiss/faiss-index-factory/

---

## 概述

Faiss 索引工厂允许你通过组合多种索引技术来创建复杂的复合索引。本章探讨如何使用索引工厂通过简单的配置字符串构建优化的索引。

## 复合索引的需求

实际应用通常需要组合多种技术：

- **IVF + PQ**：带压缩的快速搜索
- **IVF + PQ + 精炼**：通过两阶段搜索获得更好的精度
- **预处理 + 索引**：索引前降维
- **多个量化器**：残差量化以获得更好的压缩

索引工厂使创建这些组合变得简单。

## 索引工厂基础

### 简单示例

```python
import faiss

d = 128  # 维度
index = faiss.index_factory(d, "Flat")

# 等同于：
# index = faiss.IndexFlatL2(d)
```

### 工厂字符串语法

基本格式：`"预处理,粗量化,细量化,精炼"`

组件：
1. **预处理**（可选）：降维、归一化
2. **粗量化**（可选）：粗量化（IVF、IMI）
3. **细量化**（必需）：细量化或存储
4. **精炼**（可选）：使用更好度量重新排序

## 常见索引类型

### 1. Flat 索引

```python
# 穷举搜索（精确）
index = faiss.index_factory(d, "Flat")
```

**用例**：小数据集、基准

### 2. IVF 索引

```python
# 带 flat 存储的 IVF
index = faiss.index_factory(d, "IVF100,Flat")

# 带 PQ 压缩的 IVF
index = faiss.index_factory(d, "IVF100,PQ8")

# 需要训练
index.train(training_data)
```

**参数**：
- `IVF100`：100 个 Voronoi 单元
- `PQ8`：8 段的乘积量化

### 3. HNSW 索引

```python
# 32 个连接的 HNSW
index = faiss.index_factory(d, "HNSW32")

# 不需要训练
index.add(vectors)
```

### 4. 乘积量化

```python
# 纯 PQ 索引
index = faiss.index_factory(d, "PQ16")

# 需要训练
index.train(training_data)
```

## 高级复合索引

### IVF 与 PQ

结合速度和压缩：

```python
# 4096 个聚类，64 段 PQ
index = faiss.index_factory(d, "IVF4096,PQ64")

# 在代表性数据上训练
training_data = sample_data[:100000]
index.train(training_data)

# 添加数据库
index.add(database_vectors)

# 搜索参数
index.nprobe = 16  # 搜索的聚类数量
```

**配置**：
- `IVF4096`：适用于 1M-100M 向量
- `PQ64`：128 维向量的 64 倍压缩
- `nprobe=16`：速度和精度的平衡

### IVF 与 PQ 及精炼

两阶段搜索以获得更好的精度：

```python
# IVF4096,PQ 带 k 因子精炼
index = faiss.index_factory(d, "IVF4096,PQ64,Refine(Flat)")

index.train(training_data)
index.add(database_vectors)

# 第一阶段：快速 PQ 搜索
# 第二阶段：精确距离精炼
k = 10
k_factor = 3  # 第一阶段检索 3k
index.k_factor = k_factor

D, I = index.search(query, k)
```

**工作原理**：
1. 使用 PQ 检索 k×k_factor 个候选
2. 使用精确距离重新排序
3. 返回前 k 个

### 倒排多索引 (IMI)

IVF 的替代方案，适用于非常大的数据集：

```python
# 2^14 个聚类的 IMI，PQ 编码
index = faiss.index_factory(d, "IMI2x7,PQ32")

# IMI2x7 创建 2^14 = 16384 个聚类
# 使用多索引结构
```

**优势**：
- 更多聚类而无开销
- 更适合 > 100M 向量
- 需要更多训练数据

## 预处理选项

### PCA 降维

索引前降维：

```python
# 将 128D 降到 64D，然后 IVF+PQ
index = faiss.index_factory(128, "PCA64,IVF100,PQ16")

# PCA 在训练期间学习
index.train(training_data)
```

**好处**：
- 在低维中搜索更快
- 非压缩索引的内存更少
- 可能提高噪声数据的精度

### OPQ（优化乘积量化）

学习旋转以获得更好的 PQ：

```python
# PQ 前的 OPQ 旋转
index = faiss.index_factory(d, "IVF4096,PQ64x8")

# PQx8 应用 8 位编码的 OPQ
```

**改进**：比普通 PQ 精度提高 5-15%

### 归一化

用于余弦相似度：

```python
# L2 归一化向量
faiss.normalize_L2(vectors)

# 使用内积索引
index = faiss.index_factory(d, "IVF100,Flat", faiss.METRIC_INNER_PRODUCT)
```

## 度量类型

指定距离度量：

```python
# L2 距离（默认）
index = faiss.index_factory(d, "IVF100,Flat", faiss.METRIC_L2)

# 内积（用于归一化向量的余弦相似度）
index = faiss.index_factory(d, "IVF100,Flat", faiss.METRIC_INNER_PRODUCT)
```

## 完整示例

### 示例 1：百万级搜索

```python
import faiss
import numpy as np

# 数据集参数
n = 1_000_000
d = 128
nq = 100

# 生成数据
database = np.random.randn(n, d).astype('float32')
queries = np.random.randn(nq, d).astype('float32')

# 创建索引
index = faiss.index_factory(d, "IVF4096,PQ32")

# 训练
training_size = 100_000
training_data = database[:training_size]
index.train(training_data)

# 添加向量
index.add(database)

# 搜索
index.nprobe = 32
k = 10
D, I = index.search(queries, k)

print(f"搜索完成")
print(f"索引大小: {index.ntotal} 个向量")
```

### 示例 2：十亿级使用 IMI

```python
# 用于 10 亿向量
d = 256
index = faiss.index_factory(d, "IMI2x12,PQ128")

# IMI2x12 = 2^24 = 16M 聚类
# PQ128 = 128 段（256/128 = 每段 2 维）

# 在 1000 万样本上训练
training_data = sample_data[:10_000_000]
index.train(training_data)

# 批量添加
batch_size = 10_000_000
for batch in batches:
    index.add(batch)

# 配置搜索
index.nprobe = 128  # 搜索更多聚类以提高精度
```

### 示例 3：高精度搜索

```python
# HNSW 获得最佳精度
index = faiss.index_factory(d, "HNSW64")
index.hnsw.efConstruction = 200

# 添加向量
index.add(database)

# 高精度搜索
index.hnsw.efSearch = 128
D, I = index.search(queries, k)
```

### 示例 4：带降维

```python
# 将 512D 降到 128D
original_d = 512
reduced_d = 128

index = faiss.index_factory(
    original_d,
    f"PCA{reduced_d},IVF4096,PQ32"
)

# 训练（学习 PCA + IVF + PQ）
index.train(training_data)
index.add(database)

# 搜索自动应用 PCA
D, I = index.search(queries, k)
```

## 参数选择指南

### 按数据集大小

| 大小 | 推荐索引 | 配置字符串 |
|------|---------|-----------|
| < 10K | Flat | `"Flat"` |
| 10K-100K | IVF | `"IVF256,Flat"` |
| 100K-1M | IVF+PQ | `"IVF1024,PQ32"` |
| 1M-10M | IVF+PQ | `"IVF4096,PQ64"` |
| 10M-100M | IVF+PQ | `"IVF16384,PQ96"` |
| 100M-1B | IMI+PQ | `"IMI2x12,PQ128"` |
| > 1B | IMI+PQ+分片 | 多个索引 |

### 按精度要求

**精确搜索**：
```python
index = faiss.index_factory(d, "Flat")
```

**高精度（95-99%）**：
```python
index = faiss.index_factory(d, "HNSW32")
# 或
index = faiss.index_factory(d, "IVF4096,Flat")
index.nprobe = 64
```

**中等精度（90-95%）**：
```python
index = faiss.index_factory(d, "IVF4096,PQ64")
index.nprobe = 32
```

**快速搜索（85-90%）**：
```python
index = faiss.index_factory(d, "IVF4096,PQ64")
index.nprobe = 8
```

### 按内存限制

**无限制**：
```python
index = faiss.index_factory(d, "HNSW32")
```

**中等内存**：
```python
index = faiss.index_factory(d, "IVF4096,Flat")
```

**低内存**：
```python
index = faiss.index_factory(d, "IVF4096,PQ32")
```

**极低内存**：
```python
index = faiss.index_factory(d, "IVF16384,PQ16")
```

## 性能调优

### 搜索时参数

```python
# IVF：搜索的单元数
index.nprobe = 16  # 更多 = 更慢，更准确

# HNSW：候选列表大小
index.hnsw.efSearch = 64  # 更多 = 更慢，更准确

# 精炼：扩展因子
index.k_factor = 3  # 检索 3 倍，返回 1 倍
```

### 内存-精度权衡

```python
# 测量实际内存
import sys
size_bytes = sys.getsizeof(index)

# 对于索引中的向量
vector_memory = index.ntotal * d * 4  # float32

# 对于压缩索引
compressed_memory = index.ntotal * (d // m)  # 用于 PQm
```

## 高级工厂字符串

### 完整语法

```
[预处理][,粗量化][,细量化][,精炼]
```

**示例**：

```python
# PCA + 旋转 + IVF + OPQ + 精炼
"PCA64,IVF4096,PQ32x8,Refine(Flat)"

# 多重预处理
"PCA64,OPQ32,IVF1024,PQ32"

# 带归一化的余弦相似度
"IVF100,Flat"  # 配合 faiss.METRIC_INNER_PRODUCT
```

## 常见模式

### 模式 1：速度优化

```python
index = faiss.index_factory(d, "IVF16384,PQ64")
index.nprobe = 8
# 快但精度中等
```

### 模式 2：精度优化

```python
index = faiss.index_factory(d, "IVF4096,Flat,Refine(SQ8)")
index.nprobe = 64
# 通过精炼获得更高精度
```

### 模式 3：内存优化

```python
index = faiss.index_factory(d, "PCA64,IVF16384,PQ16")
# 降维 + 激进压缩
```

### 模式 4：平衡

```python
index = faiss.index_factory(d, "IVF4096,PQ32")
index.nprobe = 16
# 所有因素的良好平衡
```

## 最佳实践

1. **始终在代表性数据上训练**：使用至少 100K-1M 样本
2. **从简单开始**：从 `"IVF1024,Flat"` 开始，然后优化
3. **测量性能**：同时跟踪速度和精度
4. **对关键精度使用精炼**：开销小，收益大
5. **随数据规模调整参数**：更多数据 → 更多聚类
6. **考虑 GPU**：对大规模搜索使用 `faiss.index_cpu_to_gpu()`

## GPU 加速

```python
import faiss

# 创建索引
index = faiss.index_factory(d, "IVF4096,PQ64")
index.train(training_data)

# 移动到 GPU
res = faiss.StandardGpuResources()
gpu_index = faiss.index_cpu_to_gpu(res, 0, index)

# 在 GPU 上添加和搜索
gpu_index.add(database)
D, I = gpu_index.search(queries, k)
```

## 总结

Faiss 索引工厂是创建优化相似性搜索索引的强大工具：

- **简单语法**：用字符串创建复杂索引
- **可组合**：组合预处理、量化和精炼
- **灵活**：针对精度、速度或内存进行调整
- **生产就绪**：用于大规模系统

关键要点：
- 从简单配置开始并测量
- 对大多数应用使用 IVF+PQ
- 在有益时添加预处理（PCA、OPQ）
- 使用精炼提升精度
- 随数据集大小调整参数

索引工厂使实验和找到适合你特定用例的优化配置变得容易。

## 参考表

| 字符串 | 描述 | 用例 |
|--------|------|------|
| `Flat` | 精确搜索 | 基准、小数据 |
| `IVFn,Flat` | 带完整向量的 IVF | 高精度、中等数据 |
| `IVFn,PQm` | 带 PQ 的 IVF | 大规模、平衡 |
| `HNSWn` | 基于图 | 最高性能 |
| `PCAk,IVFn,PQm` | 带降维 | 高维数据 |
| `IVFn,PQm,Refine(Flat)` | 带精炼 | 需要高精度 |
| `IMI2xn,PQm` | 多索引 | 十亿级 |

## 参考文献

- 原文：https://www.pinecone.io/learn/series/faiss/faiss-index-factory/
- [Faiss 索引工厂指南](https://github.com/facebookresearch/faiss/wiki/The-index-factory)
- [Faiss Wiki](https://github.com/facebookresearch/faiss/wiki)
