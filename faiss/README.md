# Pinecone Faiss 系列教程

本目录收录 Pinecone Faiss 系列教程的 Markdown 中文版。

## 章节目录

1. [第 01 章：Facebook AI 相似性搜索（Faiss）简介](chapter01.md)
   - Faiss 库概览
   - 核心概念：向量嵌入、距离度量与索引方法
   - 基础用法示例

2. [第 02 章：用于相似性搜索的最近邻索引](chapter02.md)
   - Flat、IVF、PQ 与 HNSW 索引
   - 如何选择合适的索引
   - 性能取舍

3. [第 03 章：局部敏感哈希（LSH）图解指南](chapter03.md)
   - LSH 基础
   - 哈希函数族
   - 多探测 LSH

4. [第 04 章：用于局部敏感哈希的随机投影](chapter04.md)
   - Johnson–Lindenstrauss 引理
   - 随机投影技术
   - 用于 LSH 的随机超平面

5. [第 05 章：乘积量化——将高维向量压缩 97%](chapter05.md)
   - PQ 压缩技术
   - 非对称距离计算
   - 内存节省与精度取舍

6. [第 06 章：分层可导航小世界（HNSW）](chapter06.md)
   - 基于图的索引
   - 多层结构
   - 业界领先的性能

7. [第 07 章：复合索引与 Faiss 索引工厂](chapter07.md)
   - 索引工厂语法
   - 组合多种技术
   - 参数选择指南

## 原始系列

这些文章基于 [Pinecone Faiss 英文系列教程](https://www.pinecone.io/learn/series/faiss/) 翻译整理。

## 关于本项目

这是一个面向 Pinecone 系列文章的中文翻译与文档整理项目。示例代码、API 名称和数学符号保留原文形式，便于读者直接运行并对照官方资料。
