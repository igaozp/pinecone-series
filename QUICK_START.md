# 快速开始 - 下载 FAISS 文章

由于 Docker 环境的限制，请在您的**本地计算机**上运行以下命令。

## 🚀 方法 1: 使用 Bash 脚本（推荐）

```bash
# 1. 克隆或拉取仓库到本地
git clone <repository-url>
cd pinecone-series

# 2. 赋予脚本执行权限
chmod +x download_all_chapters.sh

# 3. 运行脚本（自动下载所有章节）
./download_all_chapters.sh

# 4. 查看下载的文件
ls -lh faiss/chapter*.md

# 5. 提交到 Git
git add faiss/
git commit -m "Add FAISS chapters downloaded via Jina AI"
git push
```

## 🐍 方法 2: 使用 Python 脚本

```bash
# 1. 确保已安装 requests
pip install requests

# 2. 运行下载脚本
python3 download_all_chapters.py

# 3. 提交到 Git
git add faiss/
git commit -m "Add FAISS chapters downloaded via Jina AI"
git push
```

## 📝 方法 3: 手动下载单个章节

如果您只想下载某个特定章节：

```bash
# 下载 Chapter 01
curl "https://r.jina.ai/https://www.pinecone.io/learn/series/faiss/faiss-tutorial/" \
  -H "Authorization: Bearer jina_ccf592ec8f8e470185afa074e7076614WpvRgv0U8B8R0yI8Dqte51xyw-Wi" \
  -o faiss/chapter01.md

# 下载 Chapter 02
curl "https://r.jina.ai/https://www.pinecone.io/learn/series/faiss/vector-indexes/" \
  -H "Authorization: Bearer jina_ccf592ec8f8e470185afa074e7076614WpvRgv0U8B8R0yI8Dqte51xyw-Wi" \
  -o faiss/chapter02.md

# ... 其他章节类似
```

## ✅ 验证下载

下载完成后，检查文件：

```bash
# 查看所有章节文件
ls -lh faiss/

# 检查文件内容（查看前 50 行）
head -50 faiss/chapter01.md

# 统计字符数
wc -m faiss/chapter*.md
```

每个章节文件应该：
- 大小 > 10 KB
- 包含完整的 Markdown 格式内容
- 有标题、章节内容、代码块、图片链接等

## 🔧 故障排查

### 问题：下载的文件为空或很小

```bash
# 检查文件大小
ls -lh faiss/chapter01.md

# 查看文件内容
cat faiss/chapter01.md
```

如果看到 "Access denied"，可能原因：
- API 密钥过期
- 网络连接问题
- IP 被限制

解决方案：
1. 等待几分钟后重试
2. 更换网络环境
3. 使用浏览器方法（见 `FAISS_EXTRACTION_GUIDE.md`）

### 问题：curl 命令报错

如果使用 Windows，建议：
- 使用 Git Bash
- 或者使用 Python 脚本
- 或者使用 WSL (Windows Subsystem for Linux)

### 问题：Python 脚本报错

```bash
# 安装依赖
pip install requests

# 检查 Python 版本（需要 3.6+）
python3 --version
```

## 📊 预期结果

成功下载后，您应该看到：

```
faiss/
├── README.md
├── chapter01.md  (~20-50 KB)
├── chapter02.md  (~20-50 KB)
├── chapter03.md  (~20-50 KB)
├── chapter04.md  (~20-50 KB)
├── chapter05.md  (~20-50 KB)
├── chapter06.md  (~20-50 KB)
└── chapter07.md  (~20-50 KB)
```

## 🎯 下一步

下载完成后：

1. **审查内容**
   - 打开几个文件确认格式正确
   - 检查图片链接是否完整
   - 确认代码块格式正确

2. **提交到 Git**
   ```bash
   git add faiss/
   git commit -m "Add all FAISS chapters via Jina AI"
   git push
   ```

3. **（可选）翻译成中文**
   - 可以使用 AI 工具辅助翻译
   - 保留原始英文版本作为参考

## 💡 提示

- **批量下载**: 两个脚本都会自动添加 2 秒延迟，避免 API 限流
- **断点续传**: 如果下载中断，重新运行脚本会覆盖已有文件
- **文件编码**: 所有文件使用 UTF-8 编码
- **保留元数据**: 脚本会在文件开头添加源链接等元信息

## 🆘 需要帮助？

如果遇到问题：
1. 查看 `USE_JINA_AI.md` 获取详细的 Jina AI 使用说明
2. 查看 `FAISS_EXTRACTION_GUIDE.md` 获取其他提取方法
3. 使用浏览器方法作为备选方案

---

**重要**: 确保在本地计算机（非 Docker 容器）上运行这些命令！
