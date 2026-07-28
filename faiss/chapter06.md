# Chapter 06: Hierarchical Navigable Small Worlds (HNSW)

Source: https://www.pinecone.io/learn/series/faiss/hnsw/

---

## Overview

Hierarchical Navigable Small World (HNSW) is a graph-based index that offers state-of-the-art performance for approximate nearest neighbor search. This chapter explores how HNSW works, why it's so effective, and how to use it in Faiss.

## The Evolution to HNSW

### Small World Networks

Small world networks have two key properties:
1. **High clustering**: Nodes tend to cluster together
2. **Short paths**: Any two nodes are connected by a short path

Famous example: "Six degrees of separation"

### Navigable Small Worlds (NSW)

NSW applies small world properties to vector search:
- Vectors are nodes
- Edges connect similar vectors
- Greedy search navigates the graph

Problem: Search can get trapped in local minima.

### Hierarchical NSW (HNSW)

HNSW solves NSW's problem with a hierarchical structure:
- Multiple layers of graphs
- Higher layers are sparser (for long jumps)
- Lower layers are denser (for precision)
- Logarithmic search complexity

## How HNSW Works

### Graph Structure

HNSW consists of multiple layers:

```
Layer 2: ○───────○         (sparse, long connections)
         │       │
Layer 1: ○───○───○───○     (medium density)
         │   │   │   │
Layer 0: ○─○─○─○─○─○─○─○   (dense, all points)
```

- **Layer 0**: Contains all vectors with full connectivity
- **Higher layers**: Contain progressively fewer vectors
- **Exponential decay**: Each layer has ~1/M points of the layer below

### Construction Algorithm

#### 1. Assign Layer for New Element

```python
import numpy as np

def select_layer(max_layer, ml=1.0/np.log(2)):
    """
    Select random layer for new element.
    
    Args:
        max_layer: Current maximum layer
        ml: Normalization factor
    
    Returns:
        layer: Random layer number
    """
    return min(int(-np.log(np.random.uniform()) * ml), max_layer)
```

#### 2. Find Entry Point

Start from the top layer:
```python
def search_layer(query, entry_point, layer, ef=1):
    """
    Search for nearest neighbors in one layer.
    
    Args:
        query: Query vector
        entry_point: Starting node
        layer: Layer to search
        ef: Size of dynamic candidate list
    
    Returns:
        nearest_neighbors: ef nearest neighbors
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

#### 3. Insert and Connect

```python
def insert(element, layer):
    """
    Insert element and create connections.
    
    Args:
        element: New vector to insert
        layer: Layer to insert into
    
    Returns:
        None
    """
    neighbors = find_nearest(element, M)
    
    for neighbor in neighbors:
        # Add bidirectional link
        add_edge(element, neighbor)
        add_edge(neighbor, element)
        
        # Prune connections if needed
        if len(get_neighbors(neighbor)) > M_max:
            prune_connections(neighbor, M_max)
```

### Search Algorithm

Multi-layer greedy search:

```python
def search_hnsw(query, ef, k):
    """
    Search HNSW index for k nearest neighbors.
    
    Args:
        query: Query vector
        ef: Size of dynamic candidate list (ef >= k)
        k: Number of neighbors to return
    
    Returns:
        k_nearest: k nearest neighbors
    """
    # Start from top layer
    current_nearest = entry_point
    
    # Navigate through layers
    for layer in range(top_layer, 0, -1):
        current_nearest = search_layer(
            query, current_nearest, layer, ef=1
        )[0]
    
    # Final search in layer 0
    candidates = search_layer(
        query, current_nearest, layer=0, ef=ef
    )
    
    # Return top k
    return sorted(candidates, key=lambda x: x[0])[:k]
```

## HNSW Parameters

### Construction Parameters

#### 1. M (Number of Connections)

- **Definition**: Maximum number of connections per element per layer
- **Trade-off**:
  - Higher M: Better accuracy, more memory, slower construction
  - Lower M: Less memory, faster construction, lower accuracy
- **Typical values**: 16-64
- **Rule of thumb**: Start with M=16, increase for better accuracy

#### 2. efConstruction

- **Definition**: Size of dynamic candidate list during construction
- **Trade-off**:
  - Higher efConstruction: Better graph quality, slower construction
  - Lower efConstruction: Faster construction, lower quality
- **Typical values**: 100-500
- **Recommendation**: efConstruction >= 2 * M

### Search Parameters

#### efSearch

- **Definition**: Size of dynamic candidate list during search
- **Trade-off**:
  - Higher efSearch: Better recall, slower search
  - Lower efSearch: Faster search, lower recall
- **Typical values**: 100-500
- **Important**: efSearch >= k (number of results)

## HNSW in Faiss

### Basic Usage

```python
import faiss
import numpy as np

d = 128  # dimension
M = 32   # number of connections

# Create HNSW index
index = faiss.IndexHNSWFlat(d, M)

# Set construction parameter
index.hnsw.efConstruction = 40

# Add vectors (no training needed!)
vectors = np.random.randn(100000, d).astype('float32')
index.add(vectors)

# Set search parameter
index.hnsw.efSearch = 16

# Search
k = 10
query = np.random.randn(1, d).astype('float32')
D, I = index.search(query, k)
```

### Advanced Configuration

```python
# Create index with custom parameters
index = faiss.IndexHNSWFlat(d, M=32)

# Construction parameters
index.hnsw.efConstruction = 200  # Higher for better quality
index.hnsw.max_level = 6         # Maximum layer

# Add with progress
batch_size = 10000
for i in range(0, len(vectors), batch_size):
    batch = vectors[i:i+batch_size]
    index.add(batch)
    print(f"Added {i+len(batch)} vectors")

# Dynamic search parameter tuning
for ef in [16, 32, 64, 128]:
    index.hnsw.efSearch = ef
    D, I = index.search(query, k)
    print(f"efSearch={ef}, recall=...")
```

## Performance Characteristics

### Time Complexity

- **Construction**: O(n log n × M × efConstruction × d)
- **Search**: O(log n × efSearch × d)
- **Memory**: O(n × M × d)

### Comparison with Other Methods

| Method | Construction | Search | Memory | Accuracy |
|--------|-------------|--------|--------|----------|
| Flat   | O(1)        | O(n)   | O(nd)  | 100%     |
| IVF    | O(n log k)  | O(√n)  | O(nd)  | 95-99%   |
| HNSW   | O(n log n)  | O(log n)| O(nM) | 95-99%   |
| LSH    | O(n)        | O(n^ρ) | O(n)   | 80-90%   |

## Advantages of HNSW

1. **Best query performance**: Logarithmic search time
2. **High accuracy**: 95-99% recall achievable
3. **No training required**: Unlike IVF or PQ
4. **Dynamic updates**: Easy to add new vectors
5. **Robust**: Works well across different data types

## Limitations

1. **Memory intensive**: Stores full vectors + graph
2. **Construction time**: Slower to build than IVF
3. **No compression**: Cannot combine easily with PQ in Faiss
4. **Parameter tuning**: Requires careful selection of M and ef

## Optimization Techniques

### 1. Heuristic Neighbor Selection

Instead of simple nearest neighbors:
- Diversify connections
- Avoid redundant edges
- Improve navigability

### 2. Dynamic Pruning

During construction:
```python
def prune_connections(node, M_max):
    """
    Prune connections to keep best M_max edges.
    
    Heuristic: Keep diverse, well-connected neighbors
    """
    neighbors = get_neighbors(node)
    if len(neighbors) <= M_max:
        return
    
    # Sort by distance
    neighbors.sort(key=lambda n: distance(node, n))
    
    # Keep M_max best
    keep = neighbors[:M_max]
    remove = neighbors[M_max:]
    
    for neighbor in remove:
        remove_edge(node, neighbor)
```

### 3. Layer Selection Strategy

Optimal ml parameter:
```python
ml = 1.0 / np.log(2.0)  # Default in Faiss
```

This creates exponential decay in layer populations.

## Practical Guidelines

### Choosing Parameters

For **high accuracy**:
```python
M = 64
efConstruction = 200
efSearch = 128
```

For **balanced performance**:
```python
M = 32
efConstruction = 100
efSearch = 64
```

For **fast search**:
```python
M = 16
efConstruction = 40
efSearch = 16
```

### Memory Estimation

```python
def estimate_memory(n_vectors, d, M):
    """
    Estimate HNSW memory usage.
    
    Args:
        n_vectors: Number of vectors
        d: Dimensionality
        M: Number of connections
    
    Returns:
        memory_gb: Estimated memory in GB
    """
    # Vector storage (float32)
    vector_mem = n_vectors * d * 4
    
    # Graph storage (approximate)
    # Average 2*M connections per vector
    graph_mem = n_vectors * 2 * M * 4  # 4 bytes per ID
    
    total_bytes = vector_mem + graph_mem
    return total_bytes / (1024**3)

# Example
memory_gb = estimate_memory(1_000_000, 128, 32)
print(f"Estimated memory: {memory_gb:.2f} GB")
```

## Use Cases

### When to Use HNSW

✅ **Ideal for**:
- Need highest query performance
- Can afford memory for full vectors
- Real-time applications
- Dynamic datasets (frequent updates)
- High accuracy requirements

❌ **Not ideal for**:
- Memory-constrained environments
- Billion-scale datasets (use IVFPQ)
- Batch processing (IVF may suffice)
- When training data is available (IVF can leverage it)

## Combining with Other Techniques

### HNSW + Quantization (Limited in Faiss)

In theory:
- Use HNSW for graph structure
- Apply PQ for compression
- Best of both worlds

In practice:
- Not well-supported in Faiss
- Custom implementation needed
- Use specialized libraries (Hnswlib, Milvus)

### HNSW + IVF Routing

Hybrid approach:
- IVF for coarse filtering
- HNSW within each cluster
- Balances memory and performance

## Advanced Topics

### Approximate Deletes

HNSW supports soft deletes:
```python
# Mark as deleted (implementation-specific)
index.mark_deleted(vector_id)

# Rebuild periodically to reclaim space
if deleted_fraction > 0.1:
    index = rebuild_index(index)
```

### Parallel Construction

Speed up index building:
- Add vectors in batches
- Use multiple threads
- Faiss supports parallel adds

### Graph Quality Metrics

Evaluate index quality:
- **Average degree**: Should be close to 2M
- **Diameter**: Small world property
- **Clustering coefficient**: High clustering

## Summary

HNSW represents the state-of-the-art in approximate nearest neighbor search:

- **Graph-based**: Uses hierarchical navigable small world graphs
- **Fast**: Logarithmic search complexity
- **Accurate**: Achieves 95-99% recall
- **No training**: Works immediately on any data
- **Trade-off**: Higher memory usage

Key parameters:
- **M**: Controls accuracy and memory (16-64)
- **efConstruction**: Controls index quality (100-500)
- **efSearch**: Controls query accuracy (16-500)

HNSW is the go-to choice when query performance and accuracy are top priorities and memory is available.

## References

- Original article: https://www.pinecone.io/learn/series/faiss/hnsw/
- [HNSW Paper](https://arxiv.org/abs/1603.09320)
- [Hnswlib Library](https://github.com/nmslib/hnswlib)
- [Faiss HNSW Documentation](https://github.com/facebookresearch/faiss/wiki/Faiss-indexes#hnsw)
