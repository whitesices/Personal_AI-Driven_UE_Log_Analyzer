# Original Prompt

本项目的初始开发目标来自一次 AI 主导开发任务。核心提示词摘要如下：

```text
你现在是一个 AI Native 软件开发 Agent。

我要你主导完成一个项目：AI-Driven UE Log Analyzer。

我是 Unreal Engine 开发者，平时会遇到 UE 构建失败、打包失败、插件兼容、
Blueprint 编译错误、C++ 崩溃、Assertion failed 等问题。我希望构建一个 AI
辅助工具，让 AI 可以读取 UE 项目的 Saved/Logs 日志，并生成结构化分析报告。

项目目标：
1. 构建一个本地工具，用于读取 UE 项目最新日志。
2. 检测 Error、Warning、Fatal error、Assertion failed、PackagingResults Error 等关键词。
3. 分类问题类型：构建错误、打包错误、运行时崩溃、插件兼容、蓝图错误、资源引用错误、C++ 编译错误。
4. 生成 Markdown 格式分析报告。
5. 设计一个 MCP Server，让 AI Agent 可以调用工具读取 UE 项目上下文。
6. 设计一个 UE Log Analysis Skill，固化 UE 日志分析流程。
7. 设计 Hook，在 AI 修改代码后自动运行测试，在 Git 提交前自动扫描最新 UE 日志。
8. 生成完整文档、测试用例和项目复盘。

技术要求：
- 使用 Python 实现。
- 使用清晰的目录结构。
- 必须包含 pytest 测试。
- 必须包含 README。
- 读取文件时必须限制在用户指定的 UE 项目目录内。
- 日志内容过长时只读取最后 20000 字符。
- 输出报告必须结构化。
```

第二轮优化目标进一步要求：

- 将 MCP-style 工具函数升级为真正可运行的 MCP stdio Server。
- 增强 UE 专业规则库。
- 增强 CLI 安全边界和输出体验。
- 扩展测试体系。
- 加入 ruff、mypy、build 和 GitHub Actions CI。
- 增加面试展示文档、示例日志和示例报告。
- 将 README 升级为面试展示级别。

该文档用于说明：本项目不是普通日志分析器，而是一次 AI 主导工程闭环实践。

