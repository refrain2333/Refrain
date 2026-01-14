# Git 提交规范指引

当你需要执行 Git 提交时，请遵循以下 **Conventional Commits (约定式提交)** 规范。

## 1. 提交格式
```text
<type>(<scope>): <subject>

<body>

<footer>
```

## 2. 常用类型 (Type)
- **feat**: 新功能 (feature)
- **fix**: 修补 bug
- **docs**: 文档修改 (documentation)
- **style**: 格式修改 (不影响代码运行的变动)
- **refactor**: 重构 (即不是新增功能，也不是修改 bug 的代码变动)
- **test**: 增加测试
- **chore**: 构建过程或辅助工具的变动
- **perf**: 性能优化
- **ci**: CI 配置文件或脚本的变动

## 3. 规范要求
- **Subject**: 简短描述，不超过 50 个字符。结尾不加句号。建议使用中文。
- **Body**: 详细描述变动的原因和主要内容（可选）。
- **Footer**: 备注重大变更 (BREAKING CHANGE) 或关闭 Issue (如 `Closes #123`)。

## 4. 示例
- `feat(llm): 接入 DeepSeek-R1 思考链支持`
- `fix(cli): 修复配置文件不存在时启动崩溃的问题`
- `docs(arch): 更新系统架构图方案`

---
**使用建议**：在 Cursor Chat 中输入 `/git`，我会根据你当前的改动自动生成符合此规范的提交信息。
