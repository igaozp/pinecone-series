# Chapter 01: Introduction to Facebook AI Similarity Search (Faiss)

Source: https://www.pinecone.io/learn/series/faiss/faiss-tutorial/

---

## Overview

Facebook AI Similarity Search (Faiss) is one of the most popular implementations of efficient similarity search. This chapter introduces the Faiss library, its purpose, capabilities, and context in similarity search.

## What is Faiss?

Faiss is a library developed by Facebook AI that enables efficient similarity search and clustering of dense vectors. It allows you to:

- Build an index of vectors
- Search for the most similar vectors within that index using another vector as a query
- Speed up search times to extraordinary levels

This is essential for vector-based AI applications such as:
- Semantic search
- Recommendation systems
- Image and video search
- Anomaly detection

## Why Vector Search?

Traditional search engines work well for exact matches but often fail at identifying semantic or contextual "similarity" between items. Faiss enables applications that need to find items similar in meaning or content rather than exact textual matches.

This is especially useful for:
- Recommendation engines
- Media search platforms where "similarity" is measured in vector space
- Content discovery systems

## Core Concepts

### Dense Vector Embeddings

Faiss uses dense vector embeddings to represent data. These vectors, derived from machine learning models (such as BERT for text or ResNet for images), encode semantic meaning, allowing for numerical comparisons.

### Distance Metrics

Faiss supports multiple similarity metrics:

1. **Euclidean distance (L2)**: For geometric similarity
2. **Cosine similarity**: Critical for text and embeddings, focusing on orientation rather than size
3. **Inner product**: For specific use cases

### Indexing Methods

Faiss implements various indexing methods:

1. **Flat Index**: Stores all vectors for brute-force exact search; accurate but slow for large datasets
2. **Inverted File Index (IVF)**: Partitions vectors into clusters using k-means, enabling much faster approximate search
3. **Product Quantization (PQ)**: Compresses vectors into shorter codes to reduce memory usage
4. **Hierarchical Navigable Small World (HNSW)**: Uses graph-based indexing for extremely fast approximate nearest neighbor search

## Getting Started with Faiss

### Installation

```bash
pip install faiss-cpu
# or for GPU support
pip install faiss-gpu
```

### Basic Example

```python
import faiss
import numpy as np

# Create some random vectors
dimension = 128
nb = 1000  # number of database vectors
xb = np.random.random((nb, dimension)).astype('float32')

# Build the index
index = faiss.IndexFlatL2(dimension)
index.add(xb)

# Create query vectors
nq = 5  # number of queries
xq = np.random.random((nq, dimension)).astype('float32')

# Search for k nearest neighbors
k = 5
D, I = index.search(xq, k)
print(I)  # Indices of nearest neighbors
print(D)  # Distances to nearest neighbors
```

## CPU and GPU Acceleration

Faiss can run on both CPUs and GPUs:

- **CPU**: Good for moderate-sized datasets
- **GPU**: Efficiently scales up with GPU implementations, supporting very large vector datasets

## Applications

Faiss has transformed similarity-based workflows, powering:

- Recommendation systems
- Semantic text search
- Visual search in images
- Duplicate detection
- Anomaly detection
- Content-based filtering

## Summary

Faiss provides a powerful toolkit for efficient similarity search in high-dimensional spaces. Understanding the basics of vector embeddings, distance metrics, and indexing strategies is crucial for building effective search systems.

In the following chapters, we'll dive deeper into specific indexing techniques and optimization strategies.

## References

- [Faiss GitHub Repository](https://github.com/facebookresearch/faiss)
- [Faiss Documentation](https://faiss.ai/)
- Original article: https://www.pinecone.io/learn/series/faiss/faiss-tutorial/
