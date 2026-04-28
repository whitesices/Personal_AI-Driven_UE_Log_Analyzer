# AI-Driven UE Log Analyzer PRD

## 1. 背景

Unreal Engine 项目在日常开发、构建、打包和运行阶段会生成大量日志。开发者经常需要从 `Saved/Logs` 中定位构建失败、打包失败、插件兼容、Blueprint 编译、C++ 编译、资源引用、运行时崩溃和断言失败等问题。手动排查日志耗时，且容易遗漏最关键的上下文。

本项目目标是构建一个本地优先的 UE 日志分析工具，为 AI Agent 提供安全、结构化、可测试的日志读取和分析能力。

## 2. 目标

1. 从用户指定的 UE 项目目录中读取最新日志。
2. 只允许访问 UE 项目目录内部文件，避免越权读取。
3. 当日志过长时，只分析最后 20000 个字符。
4. 检测 UE 常见问题关键词，包括 Error、Warning、Fatal error、Assertion failed、PackagingResults Error。
5. 将问题分类为构建错误、打包错误、运行时崩溃、插件兼容、蓝图错误、资源引用错误、C++ 编译错误或未知问题。
6. 输出结构化 Markdown 分析报告。
7. 提供 MCP Server 工具函数，供 AI Agent 获取 UE 项目上下文和日志报告。
8. 提供 UE Log Analysis Skill 文档，固化 AI 排查流程。
9. 提供 Hook 脚本，在代码修改后运行测试，在 Git 提交前扫描最新 UE 日志。
10. 提供 pytest 测试、README 和完整项目文档。

## 3. 非目标

1. 不直接修改 UE 项目文件。
2. 不启动 Unreal Editor 或执行构建命令。
3. 不上传日志到远端服务。
4. 不依赖外部 AI API。
5. 不尝试完整解析 UE 所有日志格式，只做本地启发式分析和结构化摘要。

## 4. 用户故事

### 4.1 快速定位最新日志问题

作为 UE 开发者，我希望工具自动找到 `Saved/Logs` 下最新的 `.log` 文件，并生成错误摘要，方便我快速判断失败原因。

### 4.2 安全地交给 AI Agent 使用

作为项目维护者，我希望 AI Agent 只能读取我指定的 UE 项目目录内的日志，不能读取任意系统文件。

### 4.3 提交前阻止明显问题

作为开发者，我希望在 Git 提交前自动扫描最新 UE 日志。如果日志中存在高严重度问题，Hook 可以返回非零退出码提醒我。

### 4.4 AI 修改代码后自动验证

作为 AI Native 工作流使用者，我希望 AI 修改代码后自动运行 pytest，并将结果写入报告，形成闭环。

## 5. 功能需求

### 5.1 日志发现

- 输入：UE 项目根目录。
- 默认日志目录：`<UE_PROJECT>/Saved/Logs`。
- 支持只查找 `.log` 文件。
- 选择最后修改时间最新的日志文件。
- 如果日志目录不存在或没有日志文件，应返回可解释错误。

### 5.2 安全读取

- 所有文件读取必须经过路径归一化。
- 目标路径必须位于用户指定的 UE 项目目录内部。
- 读取日志时最多保留最后 20000 个字符。
- 不执行日志中的任何内容。

### 5.3 问题检测

工具需要检测以下信号：

- `Error`
- `Warning`
- `Fatal error`
- `Assertion failed`
- `PackagingResults: Error`
- `LogBlueprint`
- `LogPluginManager`
- `LogLinker`
- `LogCompile`
- C++ 编译器风格错误，例如 `error C2143`

### 5.4 问题分类

分类结果包括：

- `build_error`
- `packaging_error`
- `runtime_crash`
- `plugin_compatibility`
- `blueprint_error`
- `asset_reference_error`
- `cpp_compile_error`
- `unknown`

每条问题应包含：

- 分类
- 严重度
- 匹配关键词
- 原始日志行
- 行号
- 简短解释

### 5.5 Markdown 报告

报告必须包含：

- 标题
- 分析时间
- UE 项目路径
- 日志文件路径
- 日志读取范围说明
- 总览统计
- 高优先级问题
- 分类问题列表
- 原始证据片段
- 建议下一步

### 5.6 MCP Server 工具函数

MCP 能力应覆盖：

- 获取最新日志元信息。
- 分析最新日志并返回结构化 JSON。
- 生成 Markdown 报告。

第一阶段实现为可被 MCP 适配器调用的 Python 工具函数，避免绑定具体运行时。

### 5.7 Hook

Hook 脚本包括：

- `after_code_change.py`：运行 pytest 并输出简要结果。
- `pre_commit_scan.py`：扫描最新 UE 日志，发现高严重度问题时返回非零退出码。

## 6. 质量要求

- Python 3.10+。
- 包含 pytest 测试。
- 核心逻辑应可单元测试。
- 错误信息应清晰。
- 不使用危险 shell 命令。
- 默认不访问网络。

## 7. 交付物

- Python 源码。
- MCP Server 工具函数。
- UE Log Analysis Skill 文档。
- Hook 脚本。
- pytest 测试。
- README。
- `docs/PRD.md`
- `docs/AI_WORKFLOW.md`
- `docs/MCP_DESIGN.md`
- `docs/SKILL_DESIGN.md`
- `docs/HOOK_DESIGN.md`
- `docs/TEST_REPORT.md`
- `docs/RETROSPECTIVE.md`
- `docs/TECHNICAL_DESIGN.md`

