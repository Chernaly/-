# 智能知识管理助手 - 增强版

一个AI驱动的知识管理系统，具备Web界面、增强CLI和导出功能。

## ✨ 新功能特性

### 🌐 Web界面 (NEW!)
- 现代化的Web UI，支持浏览器访问
- REST API接口，完整的API文档
- 实时搜索和问答功能
- 文档上传和管理
- 可视化统计信息

### 🎨 增强CLI (NEW!)
- 基于Rich库的彩色终端界面
- 交互式菜单系统
- 进度条和加载动画
- 表格化数据显示
- 更友好的用户体验

### 📤 导出功能 (NEW!)
- 支持导出到Obsidian格式
- 支持导出到Notion格式
- 批量导出功能
- 保留元数据和标签

### 核心功能
- ✅ **自动监控**: 监视文件夹，自动处理新增或修改的markdown文件
- ✅ **AI分析**: 使用Claude API生成文档摘要和智能标签
- ✅ **混合搜索**: 支持关键词搜索、语义搜索和标签过滤
- ✅ **智能问答**: 用自然语言提问，基于知识库回答问题
- ✅ **关联发现**: 自动识别内容相似的文档

## 🚀 快速开始

### 1. 安装依赖

```bash
# 创建虚拟环境（推荐）
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

### 3. 启动系统

有多种方式启动和使用系统：

#### 🌐 Web界面（推荐）

```bash
# 使用新的启动脚本
python start.py web

# 或指定端口
python start.py web --port 8080

# 访问 http://localhost:8000
```

**Web界面功能：**
- 🏠 主页：系统概览和快速操作
- 🔍 搜索：混合搜索界面
- 💬 问答：智能问答系统
- 📤 上传：文档上传功能
- 📊 API文档：自动生成的API文档

#### 🎨 增强CLI（交互式）

```bash
# 启动交互式菜单
python start.py cli

# 或直接执行特定功能
python start.py cli search    # 搜索模式
python start.py cli qa        # 问答模式
python start.py cli status    # 系统状态
```

**CLI功能：**
- 📋 交互式菜单导航
- 🎨 彩色输出和图标
- 📊 表格化显示
- ⏳ 进度条动画
- 💡 智能提示

#### 💻 原始CLI（高级用户）

```bash
# 使用原始CLI
python start.py original --help
python start.py original watch --dir ./docs/watched
python start.py original process --dir ./docs/watched
python start.py original search -q "Python"
python start.py original ask -q "什么是Python?"
```

## 📖 详细使用指南

### Web界面使用

1. **启动Web服务器：**
   ```bash
   python start.py web --port 8000
   ```

2. **访问界面：**
   - 主页：http://localhost:8000
   - API文档：http://localhost:8000/docs
   - ReDoc：http://localhost:8000/redoc

3. **功能介绍：**
   - 📄 **文档管理**：查看、上传、管理文档
   - 🔍 **搜索**：使用关键词、语义或混合搜索
   - 💬 **问答**：自然语言问答
   - 📊 **统计**：实时统计信息

4. **API使用示例：**
   ```bash
   # 搜索文档
   curl -X POST "http://localhost:8000/api/search" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "query=Python&method=hybrid&limit=10"

   # 提问
   curl -X POST "http://localhost:8000/api/ask" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "question=什么是Python?"

   # 上传文档
   curl -X POST "http://localhost:8000/api/upload" \
        -F "file=@document.md"
   ```

### CLI使用

#### 交互式菜单模式
```bash
python start.py cli
```

功能选项：
1. 🔍 **搜索文档** - 交互式搜索
2. 💬 **智能问答** - 问答模式
3. 📄 **处理文档** - 批量处理
4. 📚 **查看文档** - 浏览列表
5. 📊 **系统状态** - 查看统计
6. 📤 **导出文档** - 导出功能

#### 直接命令模式
```bash
# 搜索
python start.py cli search

# 问答
python start.py cli qa

# 状态
python start.py cli status
```

### 导出功能

#### 导出到Obsidian
```bash
# 在CLI菜单中选择"导出文档" → "导出为Obsidian格式"
# 或使用API
python -c "from src.export.exporters import ObsidianExporter; \
           exporter = ObsidianExporter(); \
           print(exporter.export_all('./exports/obsidian'))"
```

**Obsidian导出特性：**
- ✅ 保留frontmatter元数据
- ✅ 标签转换为Obsidian格式
- ✅ Wikilinks支持
- ✅ 完整的markdown内容

#### 导出到Notion
```bash
# 在CLI菜单中选择"导出文档" → "导出为Notion CSV"
# 或使用API
python -c "from src.export.exporters import NotionExporter; \
           exporter = NotionExporter(); \
           print(exporter.export_all('./exports/notion'))"
```

**Notion导出特性：**
- ✅ CSV格式便于导入
- ✅ 保留标题、标签、摘要
- ✅ 日期和状态信息
- ✅ Markdown文件保留

#### 在Notion中导入
1. 导出为Notion格式
2. 在Notion中创建新数据库
3. 导入CSV文件
4. 完成！

## 🏗️ 项目结构

```
3.18.02/
├── web/                          # Web界面
│   ├── app.py                    # FastAPI应用
│   ├── templates/                # HTML模板
│   │   ├── base.html
│   │   ├── index.html
│   │   └── search.html
│   └── static/                   # 静态文件
│       ├── css/style.css
│       └── js/main.js
├── src/
│   ├── core/                     # 核心模块
│   ├── monitors/                 # 文件监控
│   ├── processors/               # 文档处理
│   ├── embeddings/               # 向量存储
│   ├── search/                   # 搜索引擎
│   ├── qa/                       # 问答系统
│   └── export/                   # 导出功能
│       ├── base.py
│       └── exporters/
│           ├── obsidian.py
│           └── notion.py
├── cli_enhanced.py               # 增强CLI
├── start.py                      # 统一启动入口
├── main.py                       # 原始CLI
└── requirements.txt              # 依赖
```

## 🔧 配置说明

编辑 `config/default.yaml`：

```yaml
# Web配置
web:
  host: "0.0.0.0"
  port: 8000
  debug: false

# CLI配置
cli:
  interactive: true
  color_output: true
  page_size: 20

# 导出配置
export:
  default_format: "obsidian"
  output_dir: "./exports"
  preserve_metadata: true
```

## 📚 API文档

### REST API端点

**文档管理：**
- `GET /api/documents` - 列出文档
- `GET /api/documents/{id}` - 获取文档详情
- `POST /api/upload` - 上传文档

**搜索：**
- `POST /api/search` - 搜索文档

**问答：**
- `POST /api/ask` - 智能问答

**系统：**
- `GET /api/stats` - 系统统计
- `GET /health` - 健康检查

完整API文档：http://localhost:8000/docs

## 💡 使用技巧

### 1. Web界面 + CLI组合使用
- 使用Web界面进行日常浏览和查询
- 使用CLI进行批量操作和管理任务
- 使用原始CLI进行脚本自动化

### 2. 高效搜索
- 使用混合搜索获得最佳结果
- 使用标签过滤缩小范围
- 语义搜索适合模糊查询

### 3. 导出最佳实践
- 定期导出备份到Obsidian
- 使用Notion进行团队协作
- 导出前确保所有文档已处理

### 4. 性能优化
- 批量处理大量文档
- 定期清理向量数据库
- 使用缓存减少API调用

## 🆘 常见问题

### Q: Web界面无法访问？
```bash
# 检查端口是否被占用
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# 使用其他端口
python start.py web --port 8080
```

### Q: CLI界面显示乱码？
- 确保终端支持UTF-8编码
- Windows用户使用Windows Terminal
- 更新Rich库：`pip install --upgrade rich`

### Q: 导出失败？
- 检查输出目录权限
- 确保文档已处理完成
- 查看日志文件了解详细错误

### Q: API调用超时？
- 增加请求超时时间
- 检查Claude API密钥是否有效
- 查看API使用限额

## 🔄 更新日志

### v2.0.0 (当前版本)
- ✨ 新增Web界面（FastAPI）
- ✨ 新增增强CLI（Rich）
- ✨ 新增导出功能（Obsidian/Notion）
- 🐛 修复向量搜索性能问题
- 📝 完善API文档
- 🎨 优化用户界面

### v1.0.0
- ✅ 基础文档管理
- ✅ AI分析和标签
- ✅ 混合搜索
- ✅ 智能问答
- ✅ 文件监控

## 📞 获取帮助

- 📖 [完整文档](./README.md)
- 🚀 [快速开始](./QUICKSTART.md)
- 🐛 [报告问题](https://github.com/Chernaly/-.git/issues)
- 💬 [API文档](http://localhost:8000/docs) (启动Web服务后)

## 📄 许可证

MIT License

---

**Made with ❤️ by Knowledge Management System**
