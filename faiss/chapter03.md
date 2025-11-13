# Chapter 03: Locality Sensitive Hashing (LSH): The Illustrated Guide

Source: https://www.pinecone.io/learn/series/faiss/locality-sensitive-hashing/

---

## Overview

Locality Sensitive Hashing (LSH) is a fundamental technique for approximate nearest neighbor search. This chapter explores how LSH works, why it's important for similarity search, and how it's implemented in Faiss.

## The Problem with Exact Search

For large datasets with millions or billions of vectors, exact nearest neighbor search becomes computationally prohibitive:

- **Brute force search**: O(n × d) complexity
- **Memory requirements**: Linear with dataset size
- **Query latency**: Unacceptable for real-time applications

LSH offers a solution by trading exactness for speed.

## What is Locality Sensitive Hashing?

LSH is a hashing technique where similar inputs are hashed to the same buckets with high probability. Unlike traditional hashing (which aims to minimize collisions), LSH encourages collisions for similar items.

### Key Principles

1. **Similar items → Similar hashes**: Items that are close in the original space should hash to the same bucket
2. **Different items → Different hashes**: Items that are far apart should hash to different buckets
3. **Probabilistic guarantee**: Works with high probability, not certainty

## How LSH Works

### Basic Algorithm

1. **Hash Function Design**: Create hash functions that preserve locality
2. **Multiple Hash Tables**: Use multiple hash tables to increase recall
3. **Bucketing**: Hash all vectors into buckets
4. **Query Time**: Hash the query vector and search only within matching buckets

### Hash Function Families

Different LSH families exist for different distance metrics:

1. **Random Hyperplane (for cosine similarity)**:
   - Use random hyperplanes to divide space
   - Hash bit = which side of the hyperplane the vector lies on

2. **p-stable distributions (for Euclidean distance)**:
   - Uses random projections with p-stable distributions
   - Preserves distance relationships

### Example: Random Hyperplane LSH

```python
import numpy as np

class RandomHyperplaneLSH:
    def __init__(self, num_bits, dimension):
        self.num_bits = num_bits
        # Generate random hyperplanes
        self.hyperplanes = np.random.randn(num_bits, dimension)
    
    def hash(self, vector):
        # Compute dot product with each hyperplane
        projections = np.dot(self.hyperplanes, vector)
        # Return binary hash code
        return (projections > 0).astype(int)
    
    def hash_to_int(self, vector):
        binary_hash = self.hash(vector)
        # Convert binary to integer
        return int(''.join(binary_hash.astype(str)), 2)

# Usage
lsh = RandomHyperplaneLSH(num_bits=8, dimension=128)
vector = np.random.randn(128)
hash_value = lsh.hash_to_int(vector)
print(f"Hash value: {hash_value}")
```

## LSH Parameters

### Key Parameters

1. **Number of hash functions (k)**:
   - More bits = more specific buckets
   - Fewer false positives but may miss neighbors
   
2. **Number of hash tables (L)**:
   - More tables = higher recall
   - More memory and computation

3. **Trade-offs**:
   - High k, low L: High precision, low recall
   - Low k, high L: High recall, lower precision

### Parameter Selection

```
Probability that neighbors are hashed to same bucket: p1 ≈ (1 - θ/180)^k
Probability that non-neighbors are hashed together: p2 ≈ (1 - θ'/180)^k

Where θ and θ' are angles between vectors
```

## LSH in Faiss

Faiss implements LSH through the `IndexLSH` class:

```python
import faiss

d = 128  # dimension
nbits = 2 * d  # number of bits in hash code

# Create LSH index
index = faiss.IndexLSH(d, nbits)

# Add vectors
index.add(vectors)

# Search
k = 5
D, I = index.search(query_vectors, k)
```

### Faiss LSH Features

- **Binary codes**: Compact representation
- **Fast Hamming distance**: Efficient similarity computation
- **Rotation**: Optional rotation for better distribution
- **Multi-probe**: Can probe multiple buckets

## Multi-Probe LSH

Instead of using many hash tables, multi-probe LSH:
- Uses fewer hash tables
- Probes multiple nearby buckets per table
- Reduces memory while maintaining recall

```python
# In Faiss, controlled by search parameters
index.nprobe = 10  # Number of buckets to probe
```

## Advantages of LSH

1. **Sub-linear query time**: O(n^ρ) where ρ < 1
2. **Memory efficient**: Can use compact hash codes
3. **Theoretical guarantees**: Probabilistic bounds on accuracy
4. **Simplicity**: Easy to implement and understand

## Limitations of LSH

1. **Parameter tuning**: Requires careful selection of k and L
2. **Dimension dependent**: Performance degrades in very high dimensions ("curse of dimensionality")
3. **Moderate accuracy**: Other methods (HNSW, IVF) often perform better
4. **Fixed structure**: Difficult to adapt to data distribution

## LSH vs Other Methods

| Method | Speed | Accuracy | Memory | Training |
|--------|-------|----------|--------|----------|
| LSH    | Fast  | Moderate | Low    | No       |
| IVF    | Fast  | High     | Medium | Yes      |
| HNSW   | Fastest| High    | High   | No       |
| PQ     | Fast  | Moderate | Very Low| Yes     |

## Practical Considerations

### When to Use LSH

- **High-dimensional sparse data**: Text, user-item interactions
- **Streaming data**: No training required
- **Memory constrained**: Binary codes are compact
- **Quick prototyping**: Simple to implement

### When to Use Alternatives

- **Dense embeddings**: HNSW or IVF often better
- **Highest accuracy needs**: Use HNSW
- **Very large scale**: Consider IVFPQ
- **Have training data**: IVF-based methods may outperform

## Advanced Topics

### Learned LSH

Modern approaches:
- Learn hash functions from data
- Use neural networks to generate hash codes
- Often outperform random LSH

### Cross-Polytope LSH

Recent improvement:
- Uses cross-polytope structure
- Better than random hyperplanes
- Implemented in some Faiss variants

## Summary

LSH is a foundational technique for approximate nearest neighbor search:

- Hashes similar items to the same buckets
- Trades exactness for speed
- Works well for certain data types
- Understanding LSH helps appreciate modern methods

While newer methods like HNSW often outperform LSH in practice, LSH remains important for:
- Understanding similarity search fundamentals
- Specific use cases (streaming, sparse data)
- Theoretical analysis

## References

- Original article: https://www.pinecone.io/learn/series/faiss/locality-sensitive-hashing/
- [LSH Tutorial by Andoni & Indyk](https://web.mit.edu/andoni/www/LSH/)
- [Faiss LSH Documentation](https://github.com/facebookresearch/faiss/wiki/Faiss-indexes#lsh)
