# Chapter 04: Random Projection for Locality Sensitive Hashing

Source: https://www.pinecone.io/learn/series/faiss/random-projection/

---

## Overview

Random projection is a powerful dimensionality reduction technique that preserves distances between points. This chapter explores how random projections are used in LSH and how they enable efficient similarity search for high-dimensional data.

## The Johnson-Lindenstrauss Lemma

The theoretical foundation for random projection comes from the Johnson-Lindenstrauss (JL) lemma:

### JL Lemma Statement

For any set of n points in high-dimensional space, there exists a mapping to a lower-dimensional space (O(log n) dimensions) that approximately preserves pairwise distances.

**Key insight**: We can reduce dimensionality dramatically while maintaining distance relationships!

### Mathematical Formulation

Given:
- Original dimension: d
- Target dimension: k
- Distortion parameter: ε

Then for k ≥ 4(ε²/2 - ε³/3)⁻¹ log(n), there exists a mapping that preserves all pairwise distances within a factor of (1±ε).

## Random Projection Basics

### How It Works

1. **Generate random matrix**: Create a random k×d projection matrix
2. **Project vectors**: Multiply original vectors by this matrix
3. **Result**: Lower-dimensional vectors with preserved distances

### Simple Example

```python
import numpy as np

def random_projection(X, target_dim):
    """
    Project X to lower dimensional space.
    
    Args:
        X: (n, d) array of n vectors in d dimensions
        target_dim: Target dimensionality k
    
    Returns:
        (n, k) array of projected vectors
    """
    n, d = X.shape
    # Generate random projection matrix
    R = np.random.randn(d, target_dim) / np.sqrt(target_dim)
    # Project
    return np.dot(X, R)

# Example usage
X = np.random.randn(1000, 128)  # 1000 vectors in 128 dimensions
X_projected = random_projection(X, 32)  # Project to 32 dimensions
print(f"Original shape: {X.shape}")
print(f"Projected shape: {X_projected.shape}")
```

## Types of Random Projections

### 1. Gaussian Random Projection

Most common approach:
- Matrix entries drawn from N(0, 1/k)
- Satisfies JL lemma
- Easy to implement

```python
def gaussian_projection(d, k):
    return np.random.randn(d, k) / np.sqrt(k)
```

### 2. Sparse Random Projection

More efficient:
- Most entries are zero
- Faster computation
- Less memory

```python
def sparse_projection(d, k, density=0.1):
    """
    Create sparse random projection matrix.
    
    density: Fraction of non-zero entries
    """
    from scipy import sparse
    nnz = int(d * k * density)
    data = np.random.randn(nnz)
    rows = np.random.randint(0, d, nnz)
    cols = np.random.randint(0, k, nnz)
    return sparse.coo_matrix((data, (rows, cols)), shape=(d, k))
```

### 3. Structured Random Projection

Uses structured matrices for efficiency:
- Fast Hadamard Transform
- Circulant matrices
- O(d log k) computation instead of O(dk)

## Random Hyperplanes for LSH

Random hyperplanes are a special application of random projection for binary hashing.

### Algorithm

For each hash bit:
1. Generate a random hyperplane (random d-dimensional vector)
2. Compute dot product with input vector
3. Bit = 1 if positive, 0 if negative

```python
class RandomHyperplaneLSH:
    def __init__(self, input_dim, num_bits):
        self.input_dim = input_dim
        self.num_bits = num_bits
        # Random hyperplanes
        self.hyperplanes = np.random.randn(num_bits, input_dim)
        # Normalize
        norms = np.linalg.norm(self.hyperplanes, axis=1, keepdims=True)
        self.hyperplanes = self.hyperplanes / norms
    
    def hash(self, vectors):
        """
        Hash vectors to binary codes.
        
        Args:
            vectors: (n, d) array
        
        Returns:
            (n, num_bits) binary array
        """
        projections = np.dot(vectors, self.hyperplanes.T)
        return (projections > 0).astype(np.int8)
    
    def hamming_distance(self, hash1, hash2):
        """Compute Hamming distance between hash codes."""
        return np.sum(hash1 != hash2, axis=-1)

# Example
lsh = RandomHyperplaneLSH(input_dim=128, num_bits=64)
vectors = np.random.randn(1000, 128)
hash_codes = lsh.hash(vectors)
print(f"Hash codes shape: {hash_codes.shape}")
```

### Properties

- **Preserves angular distance**: Similar angles → similar hash codes
- **Efficient**: Fast dot product computation
- **Probabilistic guarantee**: Probability of same bit ∝ similarity

### Hash Collision Probability

For two vectors with angle θ:

```
P(hash_bit_match) = 1 - θ/π
```

For k bits:
```
P(k_bits_match) = (1 - θ/π)^k
```

## Applications in Similarity Search

### Building an LSH Index

```python
class LSHIndex:
    def __init__(self, input_dim, num_tables, num_bits):
        self.num_tables = num_tables
        # Create multiple hash tables
        self.lsh_functions = [
            RandomHyperplaneLSH(input_dim, num_bits)
            for _ in range(num_tables)
        ]
        self.tables = [dict() for _ in range(num_tables)]
    
    def add(self, vectors, ids):
        """Add vectors to the index."""
        for table_idx, lsh in enumerate(self.lsh_functions):
            hashes = lsh.hash(vectors)
            for vec_id, hash_code in zip(ids, hashes):
                # Convert to tuple for dictionary key
                key = tuple(hash_code)
                if key not in self.tables[table_idx]:
                    self.tables[table_idx][key] = []
                self.tables[table_idx][key].append(vec_id)
    
    def search(self, query, k=10):
        """Search for k nearest neighbors."""
        candidates = set()
        for table_idx, lsh in enumerate(self.lsh_functions):
            query_hash = tuple(lsh.hash(query.reshape(1, -1))[0])
            if query_hash in self.tables[table_idx]:
                candidates.update(self.tables[table_idx][query_hash])
        return list(candidates)[:k]
```

## Optimization Techniques

### 1. Adaptive Number of Bits

- More bits for large datasets
- Rule of thumb: num_bits ≈ log₂(n)

### 2. Data-Dependent Projections

Instead of pure random:
- PCA-based projections
- Learn projections from data
- Often better than random

### 3. Rotation Before Projection

For better distribution:
```python
# Apply random rotation before projection
rotation = scipy.stats.special_ortho_group.rvs(d)
X_rotated = np.dot(X, rotation)
X_projected = random_projection(X_rotated, k)
```

## Random Projection in Faiss

Faiss uses random projections in several indexes:

### IndexLSH

```python
import faiss

d = 128
nbits = 64

# Create index with random hyperplane LSH
index = faiss.IndexLSH(d, nbits)

# Optionally rotate before hashing
index.rotate_data = True

# Add vectors
index.add(vectors)

# Search
D, I = index.search(queries, k=10)
```

### Combination with Other Methods

Random projection can be combined with:
- **IVF**: Project before clustering
- **PQ**: Reduce dimension before quantization
- **HNSW**: Pre-process for faster graph construction

## Theoretical Guarantees

### Distance Preservation

For random projection from d to k dimensions:

```
E[||RP(x) - RP(y)||²] = ||x - y||²
```

The projection preserves expected distances exactly!

### Concentration Bounds

With high probability (1 - δ):

```
(1 - ε)||x - y||² ≤ ||RP(x) - RP(y)||² ≤ (1 + ε)||x - y||²
```

For k = O(log(n)/ε²)

## Practical Considerations

### When to Use Random Projection

✅ **Good for**:
- High-dimensional data (d > 1000)
- Need for dimensionality reduction
- Memory constraints
- Preprocessing step for other methods

❌ **Not ideal for**:
- Low-dimensional data (d < 100)
- When exact distances are critical
- Already have efficient indexes

### Parameter Selection

1. **Target dimension k**:
   - k = O(log n) for JL lemma
   - k = 32-128 often works well in practice

2. **Number of bits for LSH**:
   - Start with d/2 to d
   - Increase for larger datasets

3. **Number of tables**:
   - 10-50 tables typical
   - More tables = higher recall, more memory

## Comparison with Other Dimensionality Reduction

| Method | Speed | Preserves | Training | Use Case |
|--------|-------|-----------|----------|----------|
| Random Projection | Fast | Distances | No | Quick reduction |
| PCA | Medium | Variance | Yes | Statistical analysis |
| Autoencoders | Slow | Semantic | Yes | Deep learning |
| t-SNE | Very Slow | Local structure | No | Visualization |

## Summary

Random projection is a powerful technique that:

- Reduces dimensionality while preserving distances
- Provides theoretical guarantees (JL lemma)
- Enables efficient LSH through random hyperplanes
- Works well as preprocessing for similarity search

Key takeaways:
- Simple to implement
- Computationally efficient
- Theoretically grounded
- Practical for real-world applications

Understanding random projection helps build better similarity search systems and appreciate the mathematical foundations of modern indexing methods.

## References

- Original article: https://www.pinecone.io/learn/series/faiss/random-projection/
- [Johnson-Lindenstrauss Lemma](https://en.wikipedia.org/wiki/Johnson%E2%80%93Lindenstrauss_lemma)
- [Random Projection Tutorial](https://scikit-learn.org/stable/modules/random_projection.html)
- [Faiss Random Rotation](https://github.com/facebookresearch/faiss/wiki/Faiss-indexes#lsh)
