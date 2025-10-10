# 贡献指南 / Contributing Guide

感谢你考虑为本项目做出贡献！/ Thank you for considering contributing to this project!

## 如何贡献 / How to Contribute

### 报告 Bug / Reporting Bugs

如果你发现了 bug，请：
1. 检查 [Issues](../../issues) 确认问题是否已被报告
2. 如果没有，创建一个新的 Issue
3. 提供详细的问题描述、复现步骤和环境信息

If you find a bug:
1. Check [Issues](../../issues) to see if it's already reported
2. If not, create a new Issue
3. Provide detailed description, reproduction steps, and environment info

### 提出新功能 / Suggesting Features

如果你有新功能的想法：
1. 在 [Discussions](../../discussions) 中讨论你的想法
2. 如果得到积极反馈，创建一个 Feature Request Issue

If you have an idea for a new feature:
1. Discuss your idea in [Discussions](../../discussions)
2. If it receives positive feedback, create a Feature Request Issue

### 提交代码 / Submitting Code

1. Fork 本仓库 / Fork the repository
2. 创建你的特性分支 / Create your feature branch
   ```bash
   git checkout -b feature/AmazingFeature
   ```
3. 提交你的修改 / Commit your changes
   ```bash
   git commit -m 'Add some AmazingFeature'
   ```
4. 推送到分支 / Push to the branch
   ```bash
   git push origin feature/AmazingFeature
   ```
5. 创建 Pull Request / Create a Pull Request

### 代码规范 / Code Style

- 使用有意义的变量名和函数名 / Use meaningful variable and function names
- 添加必要的注释 / Add necessary comments
- 保持代码简洁清晰 / Keep code clean and simple
- 遵循 PEP 8 规范（Python）/ Follow PEP 8 style guide (Python)

### 提交信息规范 / Commit Message Guidelines

使用清晰的提交信息：/ Use clear commit messages:

```
类型: 简短描述

详细描述（可选）

Type: Brief description

Detailed description (optional)
```

类型 / Types:
- `feat`: 新功能 / New feature
- `fix`: Bug 修复 / Bug fix
- `docs`: 文档更新 / Documentation update
- `style`: 代码格式调整 / Code style changes
- `refactor`: 代码重构 / Code refactoring
- `test`: 测试相关 / Test related
- `chore`: 构建/工具相关 / Build/tool related

示例 / Examples:
```
feat: 添加批量导出功能
fix: 修复预览卡顿问题
docs: 更新 README 安装说明
```

## 开发环境设置 / Development Setup

1. 克隆仓库 / Clone the repository
   ```bash
   git clone https://github.com/yourusername/video-frame-processor.git
   cd video-frame-processor
   ```

2. 安装依赖 / Install dependencies
   ```bash
   pip install pillow
   ```

3. 安装外部工具 / Install external tools
   - FFmpeg
   - ImageMagick
   - Adobe Photoshop (optional)

4. 运行程序 / Run the program
   ```bash
   python main.py
   ```

## 测试 / Testing

在提交 PR 之前，请确保：/ Before submitting a PR, ensure:
- 代码能正常运行 / Code runs without errors
- 新功能已经过测试 / New features are tested
- 没有破坏现有功能 / Existing features still work

## 问题和讨论 / Questions and Discussions

- 使用 [Issues](../../issues) 报告 bug 和请求功能
- 使用 [Discussions](../../discussions) 进行一般性讨论

- Use [Issues](../../issues) for bug reports and feature requests
- Use [Discussions](../../discussions) for general discussions

## 行为准则 / Code of Conduct

- 尊重所有贡献者 / Respect all contributors
- 保持友好和专业 / Be friendly and professional
- 接受建设性的批评 / Accept constructive criticism
- 关注项目的最佳利益 / Focus on what's best for the project

---

再次感谢你的贡献！🎉 / Thank you again for your contribution! 🎉
