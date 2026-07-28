# Chapter 02: Nearest Neighbor Indexes for Similarity Search

Source: https://www.pinecone.io/learn/series/faiss/vector-indexes/

---

## Overview

This chapter explores the various index types available in Faiss and how to choose the right one for your specific use case. Different indexes offer different trade-offs between accuracy, memory usage, and query speed.

## Understanding Nearest Neighbor Search

Nearest neighbor (NN) search is the problem of finding the most similar items to a query item in a dataset. In the context of vectors:

- **Exact search**: Guarantees finding the true nearest neighbors
- **Approximate search**: Trades some accuracy for speed

## Types of Indexes in Faiss

### 1. Flat Indexes

**IndexFlatL2** and **IndexFlatIP**

- Stores all vectors without compression
- Performs exhaustive search (brute force)
- Most accurate but slowest for large datasets
- Good baseline for comparison
- Memory usage: O(n × d) where n is number of vectors and d is dimensionality

```python
import faiss
d = 128
index = faiss.IndexFlatL2(d)
```

**Use cases**:
- Small datasets (< 10,000 vectors)
- When accuracy is critical
- As a baseline for comparison

### 2. IVF (Inverted File) Indexes

**IndexIVFFlat**

- Partitions the vector space into Voronoi cells
- Uses k-means clustering to create cells
- Searches only the nearest cells during query time
- Significantly faster than flat indexes with minimal accuracy loss

```python
nlist = 100  # number of clusters
quantizer = faiss.IndexFlatL2(d)
index = faiss.IndexIVFFlat(quantizer, d, nlist)
index.train(xb)  # IVF requires training
index.add(xb)
index.nprobe = 10  # number of cells to search
```

**Parameters**:
- `nlist`: Number of clusters (typically sqrt(n) to 4*sqrt(n))
- `nprobe`: Number of clusters to search (higher = more accurate but slower)

**Use cases**:
- Medium to large datasets (10K - 10M vectors)
- When you can tolerate some accuracy loss
- Good balance of speed and accuracy

### 3. Product Quantization (PQ) Indexes

**IndexIVFPQ**

- Compresses vectors using product quantization
- Dramatically reduces memory usage (often by 97%)
- Combines IVF with PQ for both speed and compression
- Some accuracy loss due to quantization

```python
m = 8  # number of subquantizers
nlist = 100
index = faiss.IndexIVFPQ(quantizer, d, nlist, m, 8)
```

**Parameters**:
- `m`: Number of subquantizers (d must be divisible by m)
- `nbits`: Bits per subquantizer (typically 8)

**Use cases**:
- Very large datasets (> 10M vectors)
- When memory is limited
- Acceptable accuracy loss

### 4. HNSW (Hierarchical Navigable Small World)

**IndexHNSWFlat**

- Graph-based index
- Excellent query performance
- Higher memory usage than IVF
- No training required

```python
M = 32  # number of connections per layer
index = faiss.IndexHNSWFlat(d, M)
index.hnsw.efConstruction = 40
index.hnsw.efSearch = 16
```

**Parameters**:
- `M`: Number of connections per element (higher = better accuracy, more memory)
- `efConstruction`: Size of dynamic candidate list during construction
- `efSearch`: Size of dynamic candidate list during search

**Use cases**:
- High-performance requirements
- When memory is not a constraint
- Need for high recall with fast queries

## Choosing the Right Index

### Decision Factors

1. **Dataset Size**:
   - < 10K: Flat
   - 10K - 1M: IVF
   - > 1M: IVFPQ or HNSW

2. **Memory Constraints**:
   - Limited: IVFPQ
   - Abundant: HNSW or Flat

3. **Accuracy Requirements**:
   - Exact: Flat
   - High: HNSW or IVF with high nprobe
   - Moderate: IVF or IVFPQ

4. **Query Speed**:
   - Fastest: HNSW
   - Fast: IVF or IVFPQ
   - Slower: Flat

### Index Comparison Table

| Index Type | Speed | Accuracy | Memory | Training Required |
|-----------|-------|----------|--------|------------------|
| Flat      | Slow  | Exact    | High   | No               |
| IVF       | Fast  | High     | High   | Yes              |
| IVFPQ     | Fast  | Medium   | Low    | Yes              |
| HNSW      | Fastest| High    | Medium | No               |

## Index Training

Some indexes require training:

```python
# Training an IVF index
index.train(training_vectors)
index.is_trained  # Should be True
index.add(vectors)
```

Training learns the structure of your data:
- IVF learns cluster centroids
- PQ learns quantization codebooks

## Performance Tuning

### For IVF Indexes:

```python
# More clusters = faster but needs more training data
nlist = int(np.sqrt(n))

# More probes = more accurate but slower
index.nprobe = 10  # Start here and adjust
```

### For HNSW Indexes:

```python
# Higher M = better accuracy but more memory
M = 32

# Higher efSearch = better accuracy but slower
index.hnsw.efSearch = 16
```

## Summary

Choosing the right index type is crucial for building an efficient similarity search system. Consider your specific requirements for:

- Dataset size
- Memory constraints
- Accuracy needs
- Query speed requirements

In the next chapters, we'll explore specific indexing techniques in more detail, starting with Locality Sensitive Hashing.

## References

- Original article: https://www.pinecone.io/learn/series/faiss/vector-indexes/
- [Faiss Index Documentation](https://github.com/facebookresearch/faiss/wiki)
