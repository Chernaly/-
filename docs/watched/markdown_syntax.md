# Markdown语法快速参考

Markdown是一种轻量级标记语言，使用简单的语法来格式化文本。

## 标题

使用#号表示标题级别：

```markdown
# 一级标题
## 二级标题
### 三级标题
#### 四级标题
##### 五级标题
###### 六级标题
```

## 段落和换行

- 段落之间用空行分隔
- 换行：行末加两个空格或使用`<br>`

## 文本样式

```markdown
**粗体文本**
*斜体文本*
***粗斜体文本***
~~删除线~~
`行内代码`
```

**效果：**
**粗体文本**
*斜体文本*
***粗斜体文本***
~~删除线~~
`行内代码`

## 列表

### 无序列表

```markdown
- 项目1
- 项目2
  - 子项目2.1
  - 子项目2.2
- 项目3
```

或使用星号：

```markdown
* 项目1
* 项目2
```

### 有序列表

```markdown
1. 第一项
2. 第二项
   1. 子项2.1
   2. 子项2.2
3. 第三项
```

### 任务列表

```markdown
- [x] 已完成任务
- [ ] 未完成任务
- [ ] 待办事项
```

## 链接和图片

### 链接

```markdown
[链接文本](https://www.example.com)
[带标题的链接](https://www.example.com "链接标题")
```

### 图片

```markdown
![替代文本](image.png)
![带标题的图片](image.png "图片标题")
```

### 引用式链接

```markdown
[链接文本][ref]

[ref]: https://www.example.com "可选标题"
```

## 代码

### 行内代码

```markdown
使用`printf()`函数输出文本
```

### 代码块

```markdown
```python
def hello():
    print("Hello, World!")
```
```

支持语法高亮的语言：
- python
- javascript
- java
- cpp
- bash
- json
- yaml
- 等等...

## 引用

```markdown
> 这是一段引用文本
>
> 可以包含多个段落
```

> 这是一段引用文本
>
> 可以包含多个段落

## 表格

```markdown
| 列1 | 列2 | 列3 |
|-----|-----|-----|
| 数据1 | 数据2 | 数据3 |
| 数据4 | 数据5 | 数据6 |
```

| 列1 | 列2 | 列3 |
|-----|-----|-----|
| 数据1 | 数据2 | 数据3 |
| 数据4 | 数据5 | 数据6 |

### 对齐方式

```markdown
| 左对齐 | 居中 | 右对齐 |
|:-------|:----:|-------:|
| 内容   | 内容 | 内容   |
```

| 左对齐 | 居中 | 右对齐 |
|:-------|:----:|-------:|
| 内容   | 内容 | 内容   |

## 分隔线

使用三个或更多的连字符、星号或下划线：

```markdown
---
***
___
```

## 转义字符

使用反斜杠转义特殊字符：

```markdown
\* 不是斜体 \*
\# 不是标题
\[ 不是链接
```

## 脚注

```markdown
这是一段文本[^1]

[^1]: 这是脚注内容
```

## 缩写

```markdown
HTML是一种标记语言

*[HTML]: Hyper Text Markup Language
```

## 高亮（部分支持）

```markdown
==高亮文本==
```

## 数学公式

### 行内公式

```markdown
$E = mc^2$
```

### 块级公式

```markdown
$$
\frac{-b \pm \sqrt{b^2-4ac}}{2a}
$$
```

## HTML标签

Markdown支持内嵌HTML：

```html
<div align="center">
  <strong>居中的粗体文本</strong>
</div>

<details>
<summary>点击展开</summary>

隐藏的内容

</details>
```

## 组合使用

```markdown
### **粗体标题**

1. **第一项** - 描述
2. **第二项** - 描述

> **注意**：重要提示

| 功能 | 快捷键 | 说明 |
|------|--------|------|
| 保存 | `Ctrl+S` | 保存文件 |
| 打开 | `Ctrl+O` | 打开文件 |

```javascript
// 示例代码
const message = "Hello, Markdown!";
console.log(message);
```

![示例图片](https://example.com/image.png)

[了解更多](https://example.com)
```

## 最佳实践

### 1. 保持简洁

- 一行不超过80个字符
- 使用空行分隔段落

### 2. 层级清晰

- 标题层级不要跳跃
- 列表嵌套不超过3层

### 3. 链接管理

- 使用引用式链接提高可读性
- 为图片提供替代文本

### 4. 代码规范

- 指定代码语言以启用语法高亮
- 保持代码缩进一致

## 工具推荐

### 编辑器

- **Typora**: 所见即所得
- **VS Code**: 功能强大，插件丰富
- **Obsidian**: 笔记管理
- **MarkText**: 开源免费

### 在线工具

- **Dillinger**: 在线编辑器
- **StackEdit**: 浏览器中的Markdown编辑器
- **Markdown Tables Generator**: 表格生成器

## 学习资源

- [Markdown官方教程](https://www.markdownguide.org/)
- [GitHub Flavored Markdown](https://github.github.com/gfm/)
- [CommonMark规范](https://commonmark.org/)

## 总结

Markdown语法简单易学，是写文档、博客、笔记的理想选择。掌握这些基本语法，你就可以开始高效地编写格式化的文档了。
