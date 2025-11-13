# Chapter 07: Composite Indexes and the Faiss Index Factory

Source: https://www.pinecone.io/learn/series/faiss/faiss-index-factory/

---

## Overview

The Faiss Index Factory allows you to create complex, composite indexes by combining multiple indexing techniques. This chapter explores how to use the Index Factory to build optimized indexes with simple configuration strings.

## The Need for Composite Indexes

Real-world applications often need to combine multiple techniques:

- **IVF + PQ**: Fast search with compression
- **IVF + PQ + Refinement**: Better accuracy with two-stage search
- **Preprocessing + Index**: Dimensionality reduction before indexing
- **Multiple quantizers**: Residual quantization for better compression

The Index Factory makes it easy to create these combinations.

## Index Factory Basics

### Simple Example

```python
import faiss

d = 128  # dimension
index = faiss.index_factory(d, "Flat")

# Equivalent to:
# index = faiss.IndexFlatL2(d)
```

### Factory String Syntax

Basic format: `"Preprocessing,Coarse,Fine,Refinement"`

Components:
1. **Preprocessing** (optional): Dimension reduction, normalization
2. **Coarse** (optional): Coarse quantization (IVF, IMI)
3. **Fine** (required): Fine quantization or storage
4. **Refinement** (optional): Re-ranking with better metric

## Common Index Types

### 1. Flat Index

```python
# Exhaustive search (exact)
index = faiss.index_factory(d, "Flat")
```

**Use case**: Small datasets, baselines

### 2. IVF Indexes

```python
# IVF with flat storage
index = faiss.index_factory(d, "IVF100,Flat")

# IVF with PQ compression
index = faiss.index_factory(d, "IVF100,PQ8")

# Training required
index.train(training_data)
```

**Parameters**:
- `IVF100`: 100 Voronoi cells
- `PQ8`: Product quantization with 8 segments

### 3. HNSW Index

```python
# HNSW with 32 connections
index = faiss.index_factory(d, "HNSW32")

# No training needed
index.add(vectors)
```

### 4. Product Quantization

```python
# Pure PQ index
index = faiss.index_factory(d, "PQ16")

# Needs training
index.train(training_data)
```

## Advanced Composite Indexes

### IVF with PQ

Combines speed and compression:

```python
# 4096 clusters, 64 segments PQ
index = faiss.index_factory(d, "IVF4096,PQ64")

# Train on representative data
training_data = sample_data[:100000]
index.train(training_data)

# Add database
index.add(database_vectors)

# Search parameters
index.nprobe = 16  # Number of clusters to search
```

**Configuration**:
- `IVF4096`: Good for 1M-100M vectors
- `PQ64`: 64x compression for 128-dim vectors
- `nprobe=16`: Balance of speed and accuracy

### IVF with PQ and Refinement

Two-stage search for better accuracy:

```python
# IVFنسخة,PQ with k-factor refinement
index = faiss.index_factory(d, "IVF4096,PQ64,Refine(Flat)")

index.train(training_data)
index.add(database_vectors)

# First stage: Fast PQ search
# Second stage: Exact distance refinement
k = 10
k_factor = 3  # Retrieve 3k in first stage
index.k_factor = k_factor

D, I = index.search(query, k)
```

**How it works**:
1. Retrieve k×k_factor candidates using PQ
2. Re-rank using exact distances
3. Return top k

### Inverted Multi-Index (IMI)

Alternative to IVF for very large datasets:

```python
# IMI with 2^14 clusters, PQ encoding
index = faiss.index_factory(d, "IMI2x7,PQ32")

# IMI2x7 creates 2^14 = 16384 clusters
# Using multi-index structure
```

**Advantages**:
- More clusters without overhead
- Better for > 100M vectors
- Requires more training data

## Preprocessing Options

### PCA Reduction

Reduce dimensionality before indexing:

```python
# Reduce 128D to 64D, then IVF+PQ
index = faiss.index_factory(128, "PCA64,IVF100,PQ16")

# PCA learned during training
index.train(training_data)
```

**Benefits**:
- Faster search in lower dimensions
- Less memory for non-compressed indexes
- May improve accuracy for noisy data

### OPQ (Optimized Product Quantization)

Learns rotation for better PQ:

```python
# OPQ rotation before PQ
index = faiss.index_factory(d, "IVF4096,PQ64x8")

# PQx8 applies OPQ with 8-bit codes
```

**Improvement**: 5-15% better accuracy than plain PQ

### Normalization

For cosine similarity:

```python
# L2 normalize vectors
faiss.normalize_L2(vectors)

# Use inner product index
index = faiss.index_factory(d, "IVF100,Flat", faiss.METRIC_INNER_PRODUCT)
```

## Metric Types

Specify distance metric:

```python
# L2 distance (default)
index = faiss.index_factory(d, "IVF100,Flat", faiss.METRIC_L2)

# Inner product (for cosine with normalized vectors)
index = faiss.index_factory(d, "IVF100,Flat", faiss.METRIC_INNER_PRODUCT)
```

## Complete Examples

### Example 1: Million-Scale Search

```python
import faiss
import numpy as np

# Dataset parameters
n = 1_000_000
d = 128
nq = 100

# Generate data
database = np.random.randn(n, d).astype('float32')
queries = np.random.randn(nq, d).astype('float32')

# Create index
index = faiss.index_factory(d, "IVF4096,PQ32")

# Train
training_size = 100_000
training_data = database[:training_size]
index.train(training_data)

# Add vectors
index.add(database)

# Search
index.nprobe = 32
k = 10
D, I = index.search(queries, k)

print(f"Search completed")
print(f"Index size: {index.ntotal} vectors")
```

### Example 2: Billion-Scale with IMI

```python
# For 1 billion vectors
d = 256
index = faiss.index_factory(d, "IMI2x12,PQ128")

# IMI2x12 = 2^24 = 16M clusters
# PQ128 = 128 segments (256/128 = 2 dims per segment)

# Training on 10M samples
training_data = sample_data[:10_000_000]
index.train(training_data)

# Add in batches
batch_size = 10_000_000
for batch in batches:
    index.add(batch)

# Configure search
index.nprobe = 128  # Search more clusters for accuracy
```

### Example 3: High-Accuracy Search

```python
# HNSW for best accuracy
index = faiss.index_factory(d, "HNSW64")
index.hnsw.efConstruction = 200

# Add vectors
index.add(database)

# High accuracy search
index.hnsw.efSearch = 128
D, I = index.search(queries, k)
```

### Example 4: With Dimensionality Reduction

```python
# Reduce 512D to 128D
original_d = 512
reduced_d = 128

index = faiss.index_factory(
    original_d,
    f"PCA{reduced_d},IVF4096,PQ32"
)

# Train (learns PCA + IVF + PQ)
index.train(training_data)
index.add(database)

# Search automatically applies PCA
D, I = index.search(queries, k)
```

## Parameter Selection Guidelines

### By Dataset Size

| Size | Recommended Index | Config String |
|------|------------------|---------------|
| < 10K | Flat | `"Flat"` |
| 10K-100K | IVF | `"IVF256,Flat"` |
| 100K-1M | IVF+PQ | `"IVF1024,PQ32"` |
| 1M-10M | IVF+PQ | `"IVF4096,PQ64"` |
| 10M-100M | IVF+PQ | `"IVF16384,PQ96"` |
| 100M-1B | IMI+PQ | `"IMI2x12,PQ128"` |
| > 1B | IMI+PQ+Sharding | Multiple indexes |

### By Accuracy Requirement

**Exact search**:
```python
index = faiss.index_factory(d, "Flat")
```

**High accuracy (95-99%)**:
```python
index = faiss.index_factory(d, "HNSW32")
# or
index = faiss.index_factory(d, "IVF4096,Flat")
index.nprobe = 64
```

**Moderate accuracy (90-95%)**:
```python
index = faiss.index_factory(d, "IVF4096,PQ64")
index.nprobe = 32
```

**Fast search (85-90%)**:
```python
index = faiss.index_factory(d, "IVF4096,PQ64")
index.nprobe = 8
```

### By Memory Constraint

**No constraint**:
```python
index = faiss.index_factory(d, "HNSW32")
```

**Medium memory**:
```python
index = faiss.index_factory(d, "IVF4096,Flat")
```

**Low memory**:
```python
index = faiss.index_factory(d, "IVF4096,PQ32")
```

**Very low memory**:
```python
index = faiss.index_factory(d, "IVF16384,PQ16")
```

## Performance Tuning

### Search-Time Parameters

```python
# IVF: Number of cells to search
index.nprobe = 16  # More = slower, more accurate

# HNSW: Candidate list size
index.hnsw.efSearch = 64  # More = slower, more accurate

# Refinement: Expansion factor
index.k_factor = 3  # Retrieve 3x, return 1x
```

### Memory-Accuracy Trade-off

```python
# Measure actual memory
import sys
size_bytes = sys.getsizeof(index)

# For vectors in index
vector_memory = index.ntotal * d * 4  # float32

# For compressed indexes
compressed_memory = index.ntotal * (d // m)  # for PQm
```

## Advanced Factory Strings

### Complete Syntax

```
[Preprocessing][,Coarse][,Fine][,Refine]
```

**Examples**:

```python
# PCA + rotation + IVF + OPQ + refinement
"PCA64,IVF4096,PQ32x8,Refine(Flat)"

# Multiple preprocessing
"PCA64,OPQ32,IVF1024,PQ32"

# Cosine similarity with normalization
"IVF100,Flat"  # with faiss.METRIC_INNER_PRODUCT
```

## Common Patterns

### Pattern 1: Speed-Optimized

```python
index = faiss.index_factory(d, "IVF16384,PQ64")
index.nprobe = 8
# Fast but moderate accuracy
```

### Pattern 2: Accuracy-Optimized

```python
index = faiss.index_factory(d, "IVF4096,Flat,Refine(SQ8)")
index.nprobe = 64
# Higher accuracy with refinement
```

### Pattern 3: Memory-Optimized

```python
index = faiss.index_factory(d, "PCA64,IVF16384,PQ16")
# Reduce dimension + aggressive compression
```

### Pattern 4: Balanced

```python
index = faiss.index_factory(d, "IVF4096,PQ32")
index.nprobe = 16
# Good balance of all factors
```

## Best Practices

1. **Always train on representative data**: Use at least 100K-1M samples
2. **Start simple**: Begin with `"IVF1024,Flat"`, then optimize
3. **Measure performance**: Track both speed and accuracy
4. **Use refinement for critical accuracy**: Small overhead, big gain
5. **Scale parameters with data**: More data → more clusters
6. **Consider GPU**: Use `faiss.index_cpu_to_gpu()` for large searches

## GPU Acceleration

```python
import faiss

# Create index
index = faiss.index_factory(d, "IVF4096,PQ64")
index.train(training_data)

# Move to GPU
res = faiss.StandardGpuResources()
gpu_index = faiss.index_cpu_to_gpu(res, 0, index)

# Add and search on GPU
gpu_index.add(database)
D, I = gpu_index.search(queries, k)
```

## Summary

The Faiss Index Factory is a powerful tool for creating optimized similarity search indexes:

- **Simple syntax**: Create complex indexes with strings
- **Composable**: Combine preprocessing, quantization, and refinement
- **Flexible**: Adjust for accuracy, speed, or memory
- **Production-ready**: Used in large-scale systems

Key takeaways:
- Start with simple configurations and measure
- Use IVF+PQ for most applications
- Add preprocessing (PCA, OPQ) when beneficial
- Use refinement to boost accuracy
- Scale parameters with dataset size

The Index Factory makes it easy to experiment and find the optimal configuration for your specific use case.

## Reference Table

| String | Description | Use Case |
|--------|-------------|----------|
| `Flat` | Exact search | Baseline, small data |
| `IVFn,Flat` | IVF with full vectors | High accuracy, medium data |
| `IVFn,PQm` | IVF with PQ | Large-scale, balanced |
| `HNSWn` | Graph-based | Highest performance |
| `PCAk,IVFn,PQm` | With dimension reduction | High-dim data |
| `IVFn,PQm,Refine(Flat)` | With refinement | High accuracy needed |
| `IMI2xn,PQm` | Multi-index | Billion-scale |

## References

- Original article: https://www.pinecone.io/learn/series/faiss/faiss-index-factory/
- [Faiss Index Factory Guide](https://github.com/facebookresearch/faiss/wiki/The-index-factory)
- [Faiss Wiki](https://github.com/facebookresearch/faiss/wiki)
