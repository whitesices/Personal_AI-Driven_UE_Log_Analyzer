# Technical Design

## 1. 架构概览

项目采用本地 Python 包结构，核心分析逻辑与 CLI、Hook、MCP 工具函数解耦。

```text
UE Project
└── Saved/Logs/*.log
        |
        v
ue_log_analyzer.reader
        |
        v
ue_log_analyzer.detector
        |
        v
ue_log_analyzer.classifier
        |
        v
ue_log_analyzer.report
        |
        +--> CLI
        +--> Hooks
        +--> MCP tool functions
        +--> Diagnostic Agents
```

## 2. 目录结构

```text
.
├── docs/
├── examples/
├── hooks/
├── skills/
│   └── ue-log-analysis/
├── src/
│   └── ue_log_analyzer/
└── tests/
```

## 3. 核心模块

### 3.1 `models.py`

定义数据结构：

- `LogFileInfo`
- `LogIssue`
- `AnalysisSummary`
- `AnalysisResult`

### 3.2 `reader.py`

职责：

- 校验 UE 项目目录。
- 查找 `Saved/Logs` 下最新 `.log` 文件。
- 安全读取日志末尾最多 20000 个字符。
- 阻止路径越界。

### 3.3 `detector.py`

职责：

- 将日志文本拆分为带行号的记录。
- 根据关键词和正则表达式找出候选问题行。
- 保留匹配关键词。

### 3.4 `classifier.py`

职责：

- 根据日志行和匹配关键词分类。
- 计算严重度。
- 生成简短解释。

### 3.5 `analyzer.py`

职责：

- 编排读取、检测、分类、统计。
- 对外提供 `analyze_project()` 高层 API。

### 3.6 `report.py`

职责：

- 将结构化分析结果渲染为 Markdown。
- 输出稳定、可读、便于 AI 继续处理的报告。

### 3.7 `mcp_server.py`

职责：

- 提供纯 Python MCP 工具函数。
- 返回 JSON 可序列化结构。
- 后续可以挂载到 FastMCP 或其他 MCP runtime。

### 3.8 `cli.py`

职责：

- 提供命令行入口。
- 支持输出 Markdown 报告到 stdout 或文件。
- 支持 `--plugin-check`、`--blueprint-analysis`、`--fix-plan` 和 `--full-diagnostics`。

### 3.9 `plugin_checker.py`

职责：

- 读取 `.uproject` 与项目内 `.uplugin` 描述文件。
- 检查插件引擎版本、模块 Source/Binaries 和启用状态风险。
- 保持只读，不加载或执行插件代码。

### 3.10 `blueprint_analyzer.py`

职责：

- 从日志尾部提取 Blueprint 编译和运行时错误。
- 识别缺失函数、缺失属性、`Accessed None` 和 K2 节点问题。
- 输出可验证的修复建议。

### 3.11 `auto_fix_agent.py`

职责：

- 汇总核心日志分析、插件检查和 Blueprint 分析。
- 生成优先级排序的修复建议计划。
- 保持 advisory-only，不修改 UE 项目文件。

## 4. 安全设计

### 4.1 路径限制

所有日志文件路径必须满足：

```python
candidate.resolve().is_relative_to(project_root.resolve())
```

为兼容 Python 3.10，实际实现会提供兼容函数。

### 4.2 读取限制

默认最多读取最后 20000 个字符。实现上从文件末尾读取有界字节窗口，再解码并截取尾部字符，避免把超大日志整文件读入内存，也避免把过长内容送入 AI 上下文。

### 4.3 执行限制

工具只读取文本和生成报告，不执行 UE 日志中的内容，不启动编辑器，不删除文件。

## 5. 分类规则

分类采用可解释的启发式规则：

| 分类 | 触发条件 |
| --- | --- |
| `packaging_error` | 包含 `PackagingResults: Error`、`AutomationTool`、`UATHelper` |
| `runtime_crash` | 包含 `Fatal error`、`Assertion failed`、`Unhandled Exception` |
| `plugin_compatibility` | 包含 `LogPluginManager`、`plugin`、`module could not be loaded` |
| `blueprint_error` | 包含 `LogBlueprint`、`Blueprint Runtime Error`、`K2Node` |
| `asset_reference_error` | 包含 `LogLinker`、`Can't find file`、`Failed to load`、`Missing` |
| `cpp_compile_error` | 包含 `error C####`、`CompilerResultsLog`、`.cpp(`、`.h(` |
| `build_error` | 包含 `LogCompile`、`Build failed`、`UBT` |
| `unknown` | 只匹配通用 Error/Warning，未命中特定分类 |

## 6. 严重度规则

- `critical`：`Fatal error`、`Assertion failed`、`Unhandled Exception`。
- `high`：`PackagingResults: Error`、C++ 编译错误、构建失败。
- `medium`：普通 `Error`、插件、蓝图、资源引用问题。
- `low`：`Warning`。

## 7. 测试策略

测试覆盖：

- 最新日志发现。
- 路径越界拦截。
- 超长日志截断。
- 关键词检测。
- 问题分类。
- Markdown 报告结构。
- MCP 工具函数 JSON 输出。
- Hook 脚本入口行为。
