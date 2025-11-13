#!/bin/bash

# FAISS Series Downloader using Jina AI
# Run this script on your local machine (not in Docker)

API_KEY="jina_ccf592ec8f8e470185afa074e7076614WpvRgv0U8B8R0yI8Dqte51xyw-Wi"

# Create faiss directory if it doesn't exist
mkdir -p faiss

echo "=================================================="
echo "Downloading FAISS Series Articles via Jina AI"
echo "=================================================="
echo ""

# Chapter 01
echo "📥 Downloading Chapter 01: Introduction to FAISS..."
curl -s "https://r.jina.ai/https://www.pinecone.io/learn/series/faiss/faiss-tutorial/" \
  -H "Authorization: Bearer $API_KEY" \
  -o faiss/chapter01.md

if [ -s faiss/chapter01.md ]; then
    echo "✅ Chapter 01 downloaded ($(wc -c < faiss/chapter01.md) bytes)"
else
    echo "❌ Chapter 01 failed"
fi
sleep 2

# Chapter 02
echo "📥 Downloading Chapter 02: Vector Indexes..."
curl -s "https://r.jina.ai/https://www.pinecone.io/learn/series/faiss/vector-indexes/" \
  -H "Authorization: Bearer $API_KEY" \
  -o faiss/chapter02.md

if [ -s faiss/chapter02.md ]; then
    echo "✅ Chapter 02 downloaded ($(wc -c < faiss/chapter02.md) bytes)"
else
    echo "❌ Chapter 02 failed"
fi
sleep 2

# Chapter 03
echo "📥 Downloading Chapter 03: Locality Sensitive Hashing..."
curl -s "https://r.jina.ai/https://www.pinecone.io/learn/series/faiss/locality-sensitive-hashing/" \
  -H "Authorization: Bearer $API_KEY" \
  -o faiss/chapter03.md

if [ -s faiss/chapter03.md ]; then
    echo "✅ Chapter 03 downloaded ($(wc -c < faiss/chapter03.md) bytes)"
else
    echo "❌ Chapter 03 failed"
fi
sleep 2

# Chapter 04
echo "📥 Downloading Chapter 04: Random Projection..."
curl -s "https://r.jina.ai/https://www.pinecone.io/learn/series/faiss/locality-sensitive-hashing-random-projection/" \
  -H "Authorization: Bearer $API_KEY" \
  -o faiss/chapter04.md

if [ -s faiss/chapter04.md ]; then
    echo "✅ Chapter 04 downloaded ($(wc -c < faiss/chapter04.md) bytes)"
else
    echo "❌ Chapter 04 failed"
fi
sleep 2

# Chapter 05
echo "📥 Downloading Chapter 05: Product Quantization..."
curl -s "https://r.jina.ai/https://www.pinecone.io/learn/series/faiss/product-quantization/" \
  -H "Authorization: Bearer $API_KEY" \
  -o faiss/chapter05.md

if [ -s faiss/chapter05.md ]; then
    echo "✅ Chapter 05 downloaded ($(wc -c < faiss/chapter05.md) bytes)"
else
    echo "❌ Chapter 05 failed"
fi
sleep 2

# Chapter 06
echo "📥 Downloading Chapter 06: HNSW..."
curl -s "https://r.jina.ai/https://www.pinecone.io/learn/series/faiss/hnsw/" \
  -H "Authorization: Bearer $API_KEY" \
  -o faiss/chapter06.md

if [ -s faiss/chapter06.md ]; then
    echo "✅ Chapter 06 downloaded ($(wc -c < faiss/chapter06.md) bytes)"
else
    echo "❌ Chapter 06 failed"
fi
sleep 2

# Chapter 07
echo "📥 Downloading Chapter 07: Index Factory..."
curl -s "https://r.jina.ai/https://www.pinecone.io/learn/composite-indexes" \
  -H "Authorization: Bearer $API_KEY" \
  -o faiss/chapter07.md

if [ -s faiss/chapter07.md ]; then
    echo "✅ Chapter 07 downloaded ($(wc -c < faiss/chapter07.md) bytes)"
else
    echo "❌ Chapter 07 failed"
fi

echo ""
echo "=================================================="
echo "Download Complete!"
echo "=================================================="
echo ""
echo "Downloaded chapters:"
ls -lh faiss/chapter*.md 2>/dev/null | awk '{print $9, "-", $5}'
echo ""
echo "Total chapters: $(ls faiss/chapter*.md 2>/dev/null | wc -l)"
echo ""
echo "Next steps:"
echo "1. Review the downloaded files"
echo "2. Git add: git add faiss/"
echo "3. Git commit: git commit -m 'Add FAISS chapters downloaded via Jina AI'"
echo "4. Git push: git push"
