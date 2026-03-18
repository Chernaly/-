# 智能知识管理助手

一个AI驱动的知识管理系统，能够自动分类、索引和搜索markdown笔记，支持自然语言问答。

## 功能特性

- ✅ **自动监控**: 监视文件夹，自动处理新增或修改的markdown文件
- ✅ **AI分析**: 使用Claude API生成文档摘要和智能标签
- ✅ **混合搜索**: 支持关键词搜索、语义搜索和标签过滤
- ✅ **智能问答**: 用自然语言提问，基于知识库回答问题
- ✅ **关联发现**: 自动识别内容相似的文档

## 快速开始

### 1. 安装依赖

```bash
# 创建虚拟环境（可选）
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，添加你的 Claude API 密钥
# ANTHROPIC_API_KEY=your_actual_api_key_here
```

### 3. 运行系统

```bash
# 方式1: 启动文件监控（推荐）
python main.py watch --dir ./docs/watched

# 方式2: 批量处理现有文档
python main.py process --dir ./docs/watched

# 方式3: 搜索文档
python main.py search -q "Python" --method hybrid

# 方式4: 问答
python main.py ask -q "什么是Python?"

# 方式5: 查看系统状态
python main.py status
```

## 使用示例

### 1. 添加新文档

在 `docs/watched/` 目录下创建一个新的markdown文件：

```markdown
# Python编程入门

Python是一门优雅且强大的编程语言，适合初学者学习。

## 特点

- 语法简洁清晰
- 丰富的标准库
- 跨平台支持

## 应用领域

Python广泛应用于：
- Web开发
- 数据科学
- 人工智能
- 自动化脚本
```

系统会自动：
1. 检测新文件
2. 使用Claude API分析内容
3. 生成摘要和标签
4. 更新文档的frontmatter
5. 添加到向量数据库

处理后的文档会添加frontmatter：

```markdown
---
title: Python编程入门
summary: Python是一门优雅且强大的编程语言，适合初学者学习。具有语法简洁、标准库丰富、跨平台等特点，广泛应用于Web开发、数据科学、人工智能等领域。
tags:
- python
- programming
- tutorial
- beginners
date: 2024-01-15
---

# Python编程入门

...
```

### 2. 搜索文档

```bash
# 关键词搜索
python main.py search -q "机器学习" --method keyword

# 语义搜索
python main.py search -q "如何开始学习编程" --method semantic

# 混合搜索（默认）
python main.py search -q "Python应用" --method hybrid

# 按标签过滤
python main.py search -q "教程" --tags python beginners
```

### 3. 问答系统

```bash
python main.py ask -q "Python有哪些应用领域?"
```

输出示例：
```
Question: Python有哪些应用领域?

Answer:
根据知识库，Python有以下几个主要应用领域：

1. **Web开发** - 使用Django、Flask等框架
2. **数据科学** - 数据分析和可视化
3. **人工智能** - 机器学习和深度学习
4. **自动化脚本** - 提高工作效率

这些应用领域使Python成为一门多功能的编程语言。

Confidence: 85.3%
Based on 3 document(s)

Sources:
  1. Python编程入门
  2. Python应用领域介绍
  3. Python学习路径
```

## 项目结构

```
3.18.02/
├── src/
│   ├── core/
│   │   ├── config.py              # 配置管理
│   │   └── database.py            # SQLite数据库操作
│   ├── monitors/
│   │   ├── file_watcher.py        # 文件监控
│   │   └── event_handler.py       # 事件处理
│   ├── processors/
│   │   ├── document_processor.py  # 文档处理管道
│   │   └── ai_analyzer.py         # Claude API集成
│   ├── embeddings/
│   │   ├── embedder.py            # 文本分块
│   │   └── vector_store.py        # ChromaDB操作
│   ├── search/
│   │   └── search_engine.py       # 统一搜索接口
│   └── qa/
│       ├── query_engine.py        # 查询处理
│       └── answer_generator.py    # 答案生成
├── data/
│   ├── db/knowledge.db            # SQLite数据库
│   └── vectors/chroma/            # ChromaDB存储
├── docs/watched/                  # 默认监视文件夹
├── tests/                         # 测试文件
├── config/
│   └── default.yaml               # 默认配置
├── main.py                        # 主入口
├── requirements.txt               # Python依赖
├── .env.example                   # 环境变量模板
└── README.md                      # 本文档
```

## 配置说明

编辑 `config/default.yaml` 来自定义系统行为：

```yaml
# 文件监控配置
watcher:
  directories:
    - "./docs/watched"
  extensions: [".md", ".markdown"]

# Claude API配置
claude:
  api_key: "${ANTHROPIC_API_KEY}"
  model: "claude-3-5-sonnet-20241022"
  max_tokens: 1024
  temperature: 0.3

# 搜索配置
search:
  default_method: "hybrid"  # keyword, semantic, hybrid
  max_results: 20

# 其他配置请参考 config/default.yaml
```

## 数据库结构

系统使用SQLite存储元数据，包含以下表：

- `documents`: 文档元数据（路径、标题、摘要、时间戳）
- `tags`: 标签库
- `document_tags`: 文档-标签关联（含置信度分数）
- `document_relationships`: 文档间的关联关系
- `processing_log`: 处理日志

## 常见问题

### Q: 如何获取Claude API密钥？

访问 [Anthropic官网](https://www.anthropic.com/) 注册账号并获取API密钥。

### Q: 没有API密钥可以使用吗？

可以。系统会跳过AI分析，仅进行基本的文档索引和关键词搜索。

### Q: 支持哪些文件格式？

目前仅支持Markdown文件（.md, .markdown）。

### Q: 如何备份知识库？

备份以下两个目录：
- `data/db/` - SQLite数据库
- `data/vectors/` - 向量数据库

### Q: 搜索速度慢怎么办？

- 使用关键词搜索代替语义搜索
- 减少搜索结果数量（--limit参数）
- 检查向量数据库大小

## 开发计划

- [ ] Web界面（Flask/FastAPI）
- [ ] CLI增强（Rich终端界面）
- [ ] 导出功能（Obsidian、Notion格式）
- [ ] 多用户支持
- [ ] 文档版本控制

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！

## 联系方式

如有问题，请创建GitHub Issue。
