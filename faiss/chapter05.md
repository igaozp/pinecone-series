# Chapter 05: Product Quantization: Compressing High-Dimensional Vectors by 97%

Source: https://www.pinecone.io/learn/series/faiss/product-quantization/

---

## Overview

Product Quantization (PQ) is a vector compression technique that can reduce memory usage by up to 97% while maintaining reasonable search accuracy. This chapter explores how PQ works and how it's used in Faiss to enable billion-scale vector search.

## The Memory Problem

High-dimensional vectors consume enormous memory:

- **128-dimensional float32**: 512 bytes per vector
- **1 billion vectors**: 512 GB of memory
- **Loading time**: Several minutes to hours

Product Quantization solves this by compressing vectors dramatically.

## What is Product Quantization?

Product Quantization compresses vectors by:
1. **Splitting** vectors into sub-vectors
2. **Quantizing** each sub-vector independently
3. **Representing** each sub-vector by a centroid ID

### Key Idea

Instead of storing full vectors, store small integer codes that reference learned centroids.

## How Product Quantization Works

### Step-by-Step Process

#### 1. Split Vectors into Sub-vectors

Divide a d-dimensional vector into m sub-vectors:

```python
# Original vector: 128 dimensions
# Split into m=8 sub-vectors of 16 dimensions each

d = 128
m = 8  # number of sub-quantizers
d_sub = d // m  # 16 dimensions per sub-vector

vector = np.random.randn(128)
sub_vectors = vector.reshape(m, d_sub)
print(f"Sub-vectors shape: {sub_vectors.shape}")  # (8, 16)
```

#### 2. Learn Codebooks

For each sub-space, learn k centroids using k-means:

```python
def learn_codebooks(vectors, m, k):
    """
    Learn codebooks for product quantization.
    
    Args:
        vectors: (n, d) training vectors
        m: number of sub-quantizers
        k: codebook size (typically 256)
    
    Returns:
        codebooks: (m, k, d/m) array of centroids
    """
    n, d = vectors.shape
    d_sub = d // m
    codebooks = np.zeros((m, k, d_sub))
    
    for i in range(m):
        # Extract sub-vectors for this sub-space
        sub_vectors = vectors[:, i*d_sub:(i+1)*d_sub]
        
        # Run k-means
        from sklearn.cluster import KMeans
        kmeans = KMeans(n_clusters=k, random_state=0)
        kmeans.fit(sub_vectors)
        
        codebooks[i] = kmeans.cluster_centers_
    
    return codebooks
```

#### 3. Encode Vectors

Replace each sub-vector with its nearest centroid ID:

```python
def encode_vector(vector, codebooks):
    """
    Encode a vector using product quantization.
    
    Args:
        vector: (d,) array
        codebooks: (m, k, d/m) codebooks
    
    Returns:
        codes: (m,) array of centroid IDs
    """
    m, k, d_sub = codebooks.shape
    codes = np.zeros(m, dtype=np.uint8)
    
    for i in range(m):
        sub_vector = vector[i*d_sub:(i+1)*d_sub]
        # Find nearest centroid
        distances = np.sum((codebooks[i] - sub_vector)**2, axis=1)
        codes[i] = np.argmin(distances)
    
    return codes
```

### Complete Example

```python
import numpy as np
from sklearn.cluster import KMeans

class ProductQuantizer:
    def __init__(self, m, k):
        """
        Initialize Product Quantizer.
        
        Args:
            m: Number of sub-quantizers
            k: Codebook size (typically 256 for uint8)
        """
        self.m = m
        self.k = k
        self.codebooks = None
    
    def fit(self, X):
        """Learn codebooks from training data."""
        n, d = X.shape
        self.d = d
        self.d_sub = d // self.m
        
        assert d % self.m == 0, "d must be divisible by m"
        
        self.codebooks = np.zeros((self.m, self.k, self.d_sub))
        
        for i in range(self.m):
            sub_vectors = X[:, i*self.d_sub:(i+1)*self.d_sub]
            kmeans = KMeans(n_clusters=self.k, random_state=0, n_init=10)
            kmeans.fit(sub_vectors)
            self.codebooks[i] = kmeans.cluster_centers_
    
    def encode(self, X):
        """Encode vectors to PQ codes."""
        n = X.shape[0]
        codes = np.zeros((n, self.m), dtype=np.uint8)
        
        for i in range(self.m):
            sub_vectors = X[:, i*self.d_sub:(i+1)*self.d_sub]
            # Find nearest centroid for each vector
            for j in range(n):
                distances = np.sum((self.codebooks[i] - sub_vectors[j])**2, axis=1)
                codes[j, i] = np.argmin(distances)
        
        return codes
    
    def decode(self, codes):
        """Reconstruct approximate vectors from codes."""
        n = codes.shape[0]
        X_reconstructed = np.zeros((n, self.d))
        
        for i in range(self.m):
            X_reconstructed[:, i*self.d_sub:(i+1)*self.d_sub] = \
                self.codebooks[i][codes[:, i]]
        
        return X_reconstructed

# Example usage
X_train = np.random.randn(10000, 128)
pq = ProductQuantizer(m=8, k=256)
pq.fit(X_train)

# Encode test vectors
X_test = np.random.randn(100, 128)
codes = pq.encode(X_test)
print(f"Original size: {X_test.nbytes} bytes")
print(f"Compressed size: {codes.nbytes} bytes")
print(f"Compression ratio: {X_test.nbytes / codes.nbytes:.1f}x")
```

## Memory Savings

### Compression Ratio Calculation

**Original representation**:
- 128 dimensions × 4 bytes (float32) = 512 bytes

**PQ representation**:
- m=8 sub-quantizers × 1 byte (uint8) = 8 bytes

**Compression**: 512 / 8 = 64x = **98.4% reduction**!

For typical settings (m=8, k=256):
- **Memory**: ~96-98% reduction
- **Accuracy**: 90-95% recall maintained

## Asymmetric Distance Computation

For search, we use **Asymmetric Distance Computation** (ADC):

### Standard Approach (Symmetric)

Both query and database vectors are compressed:
- **Fast** but **less accurate**
- Not commonly used

### Asymmetric Approach

Only database vectors are compressed:
- Query remains full precision
- More accurate
- Standard in Faiss

```python
def compute_distance_table(query, codebooks):
    """
    Precompute distances from query to all centroids.
    
    Args:
        query: (d,) query vector
        codebooks: (m, k, d/m) codebooks
    
    Returns:
        distance_table: (m, k) distances
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
    Compute approximate distances using distance table.
    
    Args:
        codes: (n, m) PQ codes
        distance_table: (m, k) precomputed distances
    
    Returns:
        distances: (n,) approximate L2 distances
    """
    n, m = codes.shape
    distances = np.zeros(n)
    
    for i in range(m):
        distances += distance_table[i, codes[:, i]]
    
    return distances

# Usage
query = np.random.randn(128)
distance_table = compute_distance_table(query, pq.codebooks)
distances = compute_distances(codes, distance_table)
```

## Product Quantization in Faiss

### IndexPQ

Basic PQ index:

```python
import faiss

d = 128
m = 8  # number of sub-quantizers
nbits = 8  # bits per code (256 centroids)

# Create index
index = faiss.IndexPQ(d, m, nbits)

# Train the index
index.train(training_vectors)

# Add vectors
index.add(database_vectors)

# Search
k = 10
D, I = index.search(query_vectors, k)
```

### IndexIVFPQ

Combines IVF with PQ for better performance:

```python
nlist = 100  # number of clusters
m = 8
nbits = 8

# Create quantizer for IVF
quantizer = faiss.IndexFlatL2(d)

# Create IVFPQ index
index = faiss.IndexIVFPQ(quantizer, d, nlist, m, nbits)

# Train
index.train(training_vectors)

# Add vectors
index.add(database_vectors)

# Set search parameters
index.nprobe = 10

# Search
D, I = index.search(query_vectors, k)
```

## Parameter Selection

### Number of Sub-quantizers (m)

Trade-offs:
- **Larger m**: Better compression, slightly lower accuracy
- **Smaller m**: Less compression, better accuracy
- **Typical values**: 8, 16, 32, 64
- **Constraint**: d must be divisible by m

### Codebook Size (k)

Usually fixed:
- **k = 256**: Uses uint8 codes (most common)
- **k = 65536**: Uses uint16 codes (better accuracy, more memory)

### Number of IVF Clusters (nlist)

For IVFPQ:
- **Small datasets**: nlist = sqrt(n)
- **Large datasets**: nlist = 4 * sqrt(n)

## Accuracy vs Compression Trade-off

| Configuration | Compression | Accuracy | Use Case |
|--------------|-------------|----------|----------|
| m=4, k=256 | ~32x | High | Small datasets |
| m=8, k=256 | ~64x | Medium-High | General purpose |
| m=16, k=256 | ~128x | Medium | Large-scale |
| m=32, k=256 | ~256x | Lower | Massive scale |

## Optimizations

### Polysemous Codes

Faiss extension for better search:
- Uses Hamming distance on codes
- Filters candidates before full distance computation
- Significant speedup with minimal accuracy loss

```python
# Enable polysemous codes
index_pq.search_type = faiss.METRIC_INNER_PRODUCT
index_pq.polysemous_ht = 54  # Hamming threshold
```

### SIMD Optimization

Faiss uses SIMD instructions:
- Vectorized distance table lookup
- 4-8x speedup on modern CPUs
- Automatic in Faiss

## When to Use Product Quantization

✅ **Use PQ when**:
- Memory is limited
- Dataset is very large (> 1M vectors)
- Can accept ~5-10% accuracy loss
- Need fast search speeds

❌ **Avoid PQ when**:
- Need exact search
- Memory is abundant
- Dataset is small (< 100K vectors)
- Cannot tolerate any accuracy loss

## Practical Example: Billion-Scale Search

```python
import faiss
import numpy as np

# Parameters for billion-scale
d = 128
nlist = 65536  # ~sqrt(1B) * 4
m = 64  # aggressive compression
k_search = 100

# Create index
quantizer = faiss.IndexFlatL2(d)
index = faiss.IndexIVFPQ(quantizer, d, nlist, m, 8)

# Train on sample
training_size = 1_000_000
training_data = np.random.randn(training_size, d).astype('float32')
index.train(training_data)

# Add in batches
batch_size = 10_000_000
# for batch in batches:
#     index.add(batch)

# Configure search
index.nprobe = 64  # search 64 clusters

# Search
query = np.random.randn(1, d).astype('float32')
D, I = index.search(query, k_search)
```

## Summary

Product Quantization is essential for large-scale vector search:

- **Compression**: 96-98% memory reduction
- **Speed**: Fast distance computation via lookup tables
- **Scalability**: Enables billion-scale search
- **Trade-off**: Small accuracy loss for huge gains

Key concepts:
- Split vectors into sub-vectors
- Quantize each sub-vector independently
- Use asymmetric distance computation
- Combine with IVF for best results

PQ is a cornerstone technology in modern similarity search, making it possible to search billions of vectors on commodity hardware.

## References

- Original article: https://www.pinecone.io/learn/series/faiss/product-quantization/
- [Product Quantization Paper](https://lear.inrialpes.fr/pubs/2011/JDS11/jegou_searching_with_quantization.pdf)
- [Faiss PQ Documentation](https://github.com/facebookresearch/faiss/wiki/Faiss-indexes#pq)
