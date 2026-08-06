# 第 06 章：分层可导航小世界 (HNSW)

来源：https://www.pinecone.io/learn/series/faiss/hnsw/

---

## 概述

分层可导航小世界 (HNSW) 是一种基于图的索引，为近似最近邻搜索提供最先进的性能。本章探讨 HNSW 的工作原理、为什么它如此有效，以及如何在 Faiss 中使用它。

## HNSW 的演进

### 小世界网络

小世界网络有两个关键属性：
1. **高聚类性**：节点倾向于聚在一起
2. **短路径**：任何两个节点都通过短路径连接

著名的例子："六度分隔"

### 可导航小世界 (NSW)

NSW 将小世界属性应用于向量搜索：
- 向量是节点
- 边连接相似的向量
- 贪心搜索在图中导航

问题：搜索可能陷入局部最小值。

### 分层 NSW (HNSW)

HNSW 用分层结构解决了 NSW 的问题：
- 多层图
- 较高层更稀疏（用于长跳跃）
- 较低层更密集（用于精度）
- 对数搜索复杂度

## HNSW 工作原理

### 图结构

HNSW 由多层组成：

```
第 2 层：○───────○         （稀疏，长连接）
         │       │
第 1 层：○───○───○───○     （中等密度）
         │   │   │   │
第 0 层：○─○─○─○─○─○─○─○   （密集，所有点）
```

- **第 0 层**：包含所有向量，完全连接
- **较高层**：包含逐渐减少的向量
- **指数衰减**：每层大约有下一层 1/M 的点数

### 构建算法

#### 1. 为新元素分配层

```python
import numpy as np

def select_layer(max_layer, ml=1.0/np.log(2)):
    """
    为新元素选择随机层。
    
    参数：
        max_layer: 当前最大层
        ml: 归一化因子
    
    返回：
        layer: 随机层号
    """
    return min(int(-np.log(np.random.uniform()) * ml), max_layer)
```

#### 2. 找到入口点

从顶层开始：
```python
def search_layer(query, entry_point, layer, ef=1):
    """
    在一层中搜索最近邻。
    
    参数：
        query: 查询向量
        entry_point: 起始节点
        layer: 搜索层
        ef: 动态候选列表大小
    
    返回：
        nearest_neighbors: ef 个最近邻
    """
    visited = set()
    candidates = [(distance(query, entry_point), entry_point)]
    best = candidates[0]
    
    while candidates:
        current_dist, current = heappop(candidates)
        
        if current_dist > best[0]:
            break
        
        for neighbor in get_neighbors(current, layer):
            if neighbor not in visited:
                visited.add(neighbor)
                d = distance(query, neighbor)
                
                if d < best[0]:
                    heappush(candidates, (d, neighbor))
                    best = (d, neighbor)
    
    return get_top_ef(visited, query, ef)
```

#### 3. 插入并连接

```python
def insert(element, layer):
    """
    插入元素并创建连接。
    
    参数：
        element: 要插入的新向量
        layer: 要插入的层
    
    返回：
        None
    """
    neighbors = find_nearest(element, M)
    
    for neighbor in neighbors:
        # 添加双向链接
        add_edge(element, neighbor)
        add_edge(neighbor, element)
        
        # 如果需要则修剪连接
        if len(get_neighbors(neighbor)) > M_max:
            prune_connections(neighbor, M_max)
```

### 搜索算法

多层贪心搜索：

```python
def search_hnsw(query, ef, k):
    """
    搜索 HNSW 索引以找到 k 个最近邻。
    
    参数：
        query: 查询向量
        ef: 动态候选列表大小（ef >= k）
        k: 要返回的邻居数量
    
    返回：
        k_nearest: k 个最近邻
    """
    # 从顶层开始
    current_nearest = entry_point
    
    # 在各层中导航
    for layer in range(top_layer, 0, -1):
        current_nearest = search_layer(
            query, current_nearest, layer, ef=1
        )[0]
    
    # 在第 0 层进行最终搜索
    candidates = search_layer(
        query, current_nearest, layer=0, ef=ef
    )
    
    # 返回前 k 个
    return sorted(candidates, key=lambda x: x[0])[:k]
```

## HNSW 参数

### 构建参数

#### 1. M（连接数）

- **定义**：每层每个元素的最大连接数
- **权衡**：
  - 更高的 M：更好的精度，更多内存，更慢的构建
  - 更低的 M：更少内存，更快的构建，较低的精度
- **典型值**：16-64
- **经验法则**：从 M=16 开始，增加以获得更好的精度

#### 2. efConstruction

- **定义**：构建期间动态候选列表的大小
- **权衡**：
  - 更高的 efConstruction：更好的图质量，更慢的构建
  - 更低的 efConstruction：更快的构建，较低的质量
- **典型值**：100-500
- **建议**：efConstruction >= 2 * M

### 搜索参数

#### efSearch

- **定义**：搜索期间动态候选列表的大小
- **权衡**：
  - 更高的 efSearch：更好的召回率，更慢的搜索
  - 更低的 efSearch：更快的搜索，较低的召回率
- **典型值**：100-500
- **重要**：efSearch >= k（结果数量）

## Faiss 中的 HNSW

### 基本用法

```python
import faiss
import numpy as np

d = 128  # 维度
M = 32   # 连接数

# 创建 HNSW 索引
index = faiss.IndexHNSWFlat(d, M)

# 设置构建参数
index.hnsw.efConstruction = 40

# 添加向量（不需要训练！）
vectors = np.random.randn(100000, d).astype('float32')
index.add(vectors)

# 设置搜索参数
index.hnsw.efSearch = 16

# 搜索
k = 10
query = np.random.randn(1, d).astype('float32')
D, I = index.search(query, k)
```

### 高级配置

```python
# 创建带自定义参数的索引
index = faiss.IndexHNSWFlat(d, M=32)

# 构建参数
index.hnsw.efConstruction = 200  # 更高以获得更好的质量
index.hnsw.max_level = 6         # 最大层数

# 带进度添加
batch_size = 10000
for i in range(0, len(vectors), batch_size):
    batch = vectors[i:i+batch_size]
    index.add(batch)
    print(f"已添加 {i+len(batch)} 个向量")

# 动态搜索参数调优
for ef in [16, 32, 64, 128]:
    index.hnsw.efSearch = ef
    D, I = index.search(query, k)
    print(f"efSearch={ef}, 召回率=...")
```

## 性能特征

### 时间复杂度

- **构建**：O(n log n × M × efConstruction × d)
- **搜索**：O(log n × efSearch × d)
- **内存**：O(n × M × d)

### 与其他方法的比较

| 方法 | 构建 | 搜索 | 内存 | 精度 |
|------|------|------|------|------|
| Flat | O(1) | O(n) | O(nd) | 100% |
| IVF | O(n log k) | O(√n) | O(nd) | 95-99% |
| HNSW | O(n log n) | O(log n) | O(nM) | 95-99% |
| LSH | O(n) | O(n^ρ) | O(n) | 80-90% |

## HNSW 的优势

1. **最佳查询性能**：对数搜索时间
2. **高精度**：可达 95-99% 召回率
3. **不需要训练**：不像 IVF 或 PQ
4. **动态更新**：易于添加新向量
5. **健壮性**：在不同数据类型上表现良好

## 局限性

1. **内存密集**：存储完整向量 + 图
2. **构建时间**：比 IVF 更慢
3. **无压缩**：在 Faiss 中不能轻松与 PQ 结合
4. **参数调优**：需要仔细选择 M 和 ef

## 优化技术

### 1. 启发式邻居选择

不使用简单的最近邻：
- 多样化连接
- 避免冗余边
- 改善可导航性

### 2. 动态修剪

在构建期间：
```python
def prune_connections(node, M_max):
    """
    修剪连接以保留最佳的 M_max 条边。
    
    启发式：保留多样化、连接良好的邻居
    """
    neighbors = get_neighbors(node)
    if len(neighbors) <= M_max:
        return
    
    # 按距离排序
    neighbors.sort(key=lambda n: distance(node, n))
    
    # 保留 M_max 个最佳
    keep = neighbors[:M_max]
    remove = neighbors[M_max:]
    
    for neighbor in remove:
        remove_edge(node, neighbor)
```

### 3. 层选择策略

最优的 ml 参数：
```python
ml = 1.0 / np.log(2.0)  # Faiss 中的默认值
```

这会创建层大小的指数衰减。

## 实际指南

### 选择参数

**高精度**：
```python
M = 64
efConstruction = 200
efSearch = 128
```

**平衡性能**：
```python
M = 32
efConstruction = 100
efSearch = 64
```

**快速搜索**：
```python
M = 16
efConstruction = 40
efSearch = 16
```

### 内存估算

```python
def estimate_memory(n_vectors, d, M):
    """
    估算 HNSW 内存使用。
    
    参数：
        n_vectors: 向量数量
        d: 维度
        M: 连接数
    
    返回：
        memory_gb: 估计内存（GB）
    """
    # 向量存储 (float32)
    vector_mem = n_vectors * d * 4
    
    # 图存储（近似）
    # 平均每个向量 2*M 个连接
    graph_mem = n_vectors * 2 * M * 4  # 每个 ID 4 字节
    
    total_bytes = vector_mem + graph_mem
    return total_bytes / (1024**3)

# 示例
memory_gb = estimate_memory(1_000_000, 128, 32)
print(f"估计内存: {memory_gb:.2f} GB")
```

## 用例

### 何时使用 HNSW

✅ **适用于**：
- 需要最高查询性能
- 能够负担完整向量的内存
- 实时应用
- 动态数据集（频繁更新）
- 高精度要求

❌ **不适用于**：
- 内存受限环境
- 十亿级数据集（使用 IVFPQ）
- 批处理（IVF 可能足够）
- 当有训练数据可用时（IVF 可以利用）

## 与其他技术结合

### HNSW + 量化（在 Faiss 中有限）

理论上：
- 使用 HNSW 构建图结构
- 应用 PQ 进行压缩
- 两全其美

实践中：
- 在 Faiss 中支持不佳
- 需要自定义实现
- 使用专门的库（Hnswlib、Milvus）

### HNSW + IVF 路由

混合方法：
- IVF 用于粗过滤
- 每个聚类内使用 HNSW
- 平衡内存和性能

## 高级主题

### 近似删除

HNSW 支持软删除：
```python
# 标记为删除（实现特定）
index.mark_deleted(vector_id)

# 定期重建以回收空间
if deleted_fraction > 0.1:
    index = rebuild_index(index)
```

### 并行构建

加速索引构建：
- 批量添加向量
- 使用多线程
- Faiss 支持并行添加

### 图质量指标

评估索引质量：
- **平均度**：应接近 2M
- **直径**：小世界属性
- **聚类系数**：高聚类性

## 总结

HNSW 代表了近似最近邻搜索的最先进水平：

- **基于图**：使用分层可导航小世界图
- **快速**：对数搜索复杂度
- **准确**：可达 95-99% 召回率
- **无需训练**：在任何数据上立即工作
- **权衡**：更高的内存使用

关键参数：
- **M**：控制精度和内存（16-64）
- **efConstruction**：控制索引质量（100-500）
- **efSearch**：控制查询精度（16-500）

当查询性能和精度是首要考虑因素且内存可用时，HNSW 是首选。

## 参考文献

- 原文：https://www.pinecone.io/learn/series/faiss/hnsw/
- [HNSW 论文](https://arxiv.org/abs/1603.09320)
- [Hnswlib 库](https://github.com/nmslib/hnswlib)
- [Faiss HNSW 文档](https://github.com/facebookresearch/faiss/wiki/Faiss-indexes#hnsw)
