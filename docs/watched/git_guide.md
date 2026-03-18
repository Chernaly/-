# Git版本控制完全指南

Git是一个分布式版本控制系统，用于跟踪文件的更改并协调多人协作开发。

## 什么是版本控制？

版本控制是一种记录文件变化的系统，允许你：

- 追踪文件的历史修改
- 回退到之前的版本
- 比较不同版本的差异
- 多人协作开发

## Git基础概念

### 仓库（Repository）

仓库是Git的核心概念，包含：
- 项目文件
- 修改历史
- 分支信息

### 提交（Commit）

提交是Git的基本操作单位，每次提交包含：
- 修改的内容
- 提交信息
- 作者信息
- 时间戳

### 分支（Branch）

分支允许你在不影响主代码的情况下开发新功能：

```bash
# 创建新分支
git branch feature-login

# 切换分支
git checkout feature-login

# 或者一步完成
git checkout -b feature-login
```

## 常用命令

### 初始化配置

```bash
# 设置用户名
git config --global user.name "Your Name"

# 设置邮箱
git config --global user.email "your.email@example.com"

# 查看配置
git config --list
```

### 基本操作

```bash
# 初始化仓库
git init

# 添加文件到暂存区
git add filename.txt
git add .  # 添加所有文件

# 提交更改
git commit -m "Add new feature"

# 查看状态
git status

# 查看历史
git log
git log --oneline
```

### 远程操作

```bash
# 克隆远程仓库
git clone https://github.com/user/repo.git

# 添加远程仓库
git remote add origin https://github.com/user/repo.git

# 推送到远程
git push origin main

# 从远程拉取
git pull origin main
```

### 分支管理

```bash
# 查看分支
git branch

# 创建分支
git branch new-feature

# 切换分支
git checkout new-feature

# 合并分支
git merge new-feature

# 删除分支
git branch -d new-feature
```

## Git工作流程

### 基本流程

1. **工作区（Working Directory）**: 编辑文件
2. **暂存区（Staging Area）**: `git add`
3. **本地仓库（Local Repository）**: `git commit`
4. **远程仓库（Remote Repository）**: `git push`

### Feature Branch工作流

1. 从main分支创建feature分支
2. 在feature分支上开发
3. 完成后合并回main
4. 删除feature分支

```bash
# 1. 创建feature分支
git checkout -b feature-user-auth

# 2. 开发并提交
git add .
git commit -m "Add user authentication"

# 3. 切回main分支
git checkout main

# 4. 合并feature分支
git merge feature-user-auth

# 5. 删除feature分支
git branch -d feature-user-auth
```

## 解决冲突

当多人修改同一文件时可能产生冲突：

```bash
# 尝试合并
git merge feature-branch

# 如果有冲突，Git会标记冲突文件
# 手动编辑文件解决冲突

# 标记为已解决
git add resolved-file.txt

# 完成合并
git commit
```

## 最佳实践

### 提交信息规范

使用清晰、有意义的提交信息：

```
feat: 添加用户登录功能
fix: 修复登录验证bug
docs: 更新README文档
style: 格式化代码
refactor: 重构用户模块
test: 添加单元测试
```

### .gitignore文件

忽略不需要跟踪的文件：

```
# Python
__pycache__/
*.py[cod]
*.so
.Python
venv/

# IDE
.vscode/
.idea/
*.swp

# 操作系统
.DS_Store
Thumbs.db
```

## 高级技巧

### 储藏（Stash）

临时保存未提交的更改：

```bash
# 储藏当前更改
git stash

# 查看储藏列表
git stash list

# 恢复储藏
git stash pop
```

### 撤销操作

```bash
# 撤销工作区的修改
git checkout -- filename.txt

# 撤销暂存区的修改
git reset HEAD filename.txt

# 撤销最后一次提交（保留修改）
git reset --soft HEAD^

# 撤销最后一次提交（丢弃修改）
git reset --hard HEAD^
```

### 查看差异

```bash
# 查看工作区差异
git diff

# 查看暂存区差异
git diff --staged

# 比较两个提交
git diff commit1 commit2
```

## Git Flow工作流

Git Flow是一种流行的分支管理策略：

- **main**: 生产环境代码
- **develop**: 开发分支
- **feature**: 新功能分支
- **release**: 发布分支
- **hotfix**: 紧急修复分支

## 常见问题

### 如何撤销已推送的提交？

```bash
# 创建一个反向提交
git revert <commit-hash>
git push origin main
```

### 如何修改最后一次提交信息？

```bash
git commit --amend -m "New commit message"
```

### 如何同步fork的仓库？

```bash
# 添加上游仓库
git remote add upstream https://github.com/original/repo.git

# 拉取上游更新
git fetch upstream

# 合并到本地
git merge upstream/main
```

## 学习资源

- 官方文档: https://git-scm.com/doc
- Pro Git书籍: https://git-scm.com/book
- 交互式教程: https://learngitbranching.js.org/

## 总结

Git是现代软件开发不可或缺的工具。掌握Git不仅能够提高个人开发效率，更是团队协作的基础。通过不断实践，你会发现Git的强大之处。
