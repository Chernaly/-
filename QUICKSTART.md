# 快速开始指南

## 系统已安装并测试通过！

恭喜！智能知识管理系统已经成功安装并通过所有测试。

## 下一步操作

### 1. 配置Claude API（可选但推荐）

要启用AI功能，需要配置Claude API密钥：

```bash
# 编辑 .env 文件
# 将 ANTHROPIC_API_KEY=sk-ant-test-placeholder
# 替换为你的实际API密钥
ANTHROPIC_API_KEY=your_actual_api_key_here
```

### 2. 测试系统状态

```bash
python main.py status
```

### 3. 处理现有文档

批量处理 `docs/watched/` 目录中的所有文档：

```bash
python main.py process --dir ./docs/watched
```

### 4. 启动文件监控

自动监控文档变化并处理：

```bash
python main.py watch --dir ./docs/watched
```

### 5. 搜索文档

使用关键词搜索：

```bash
python main.py search -q "Python" --method keyword
```

使用语义搜索（需要向量数据库）：

```bash
python main.py search -q "如何学习编程" --method semantic
```

混合搜索（推荐）：

```bash
python main.py search -q "Git使用" --method hybrid
```

### 6. 问答系统

向系统提问：

```bash
python main.py ask -q "Python有哪些应用领域?"
```

## 测试文档

系统中已经包含了3个示例文档：

1. `python_basics.md` - Python编程入门指南
2. `git_guide.md` - Git版本控制完全指南
3. `markdown_syntax.md` - Markdown语法快速参考

你可以用这些文档来测试搜索和问答功能。

## 功能演示

### 示例1：搜索Python相关内容

```bash
python main.py search -q "Python" -l 5
```

### 示例2：搜索Git相关内容

```bash
python main.py search -q "版本控制"
```

### 示例3：提问

```bash
python main.py ask -q "什么是Git?"
```

### 示例4：按标签搜索

```bash
python main.py search -q "教程" --tags python
```

## 工作流程

1. **添加新文档**: 在 `docs/watched/` 目录中创建或复制markdown文件
2. **自动处理**: 如果启动了watch模式，系统会自动检测并处理新文件
3. **AI分析**: 使用Claude API生成摘要和标签（如果配置了API密钥）
4. **更新文档**: 自动在文档顶部添加frontmatter元数据
5. **索引建立**: 将文档添加到数据库和向量存储
6. **搜索问答**: 使用搜索和问答功能查询知识库

## 不使用API密钥的注意事项

如果没有配置Claude API密钥：

- 文档仍会被索引和存储
- 关键词搜索功能正常工作
- 语义搜索功能正常工作（使用ChromaDB默认嵌入）
- 不会生成摘要和标签
- 问答功能会返回基本答案（基于文档摘要）

## 日志文件

系统日志保存在 `knowledge_system.log` 文件中，可以查看详细运行信息。

## 数据库位置

- SQLite数据库: `data/db/knowledge.db`
- 向量数据库: `data/vectors/chroma/`

## 下一步

1. 添加你自己的markdown笔记到 `docs/watched/` 目录
2. 使用搜索功能查找信息
3. 尝试问答功能
4. 根据需要调整配置文件 `config/default.yaml`

## 需要帮助？

查看完整的README.md文档获取更多信息。
