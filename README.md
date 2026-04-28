# AI-Driven UE Log Analyzer

本项目是一个本地 Python 工具，用于读取 Unreal Engine 项目 `Saved/Logs` 下的最新日志，检测常见错误信号，分类问题类型，并生成结构化 Markdown 分析报告。它也提供 MCP-style 工具函数、UE Log Analysis Skill 和 Hook 脚本，方便接入 AI Native 开发流程。

## 功能

- 自动查找 UE 项目最新 `.log` 文件。
- 只读取用户指定 UE 项目目录内的日志文件。
- 日志过长时默认只读取最后 20000 字符。
- 检测 `Error`、`Warning`、`Fatal error`、`Assertion failed`、`PackagingResults: Error` 等信号。
- 分类为构建错误、打包错误、运行时崩溃、插件兼容、蓝图错误、资源引用错误、C++ 编译错误或未知问题。
- 输出结构化 Markdown 报告。
- 提供 MCP-style Python 工具函数。
- 提供 AI 工作流 Skill 和 Hook 脚本。
- 包含 pytest 测试。

## 目录结构

```text
.
├── docs/
├── hooks/
├── skills/
│   └── ue-log-analysis/
├── src/
│   └── ue_log_analyzer/
├── tests/
├── pyproject.toml
└── README.md
```

## 安装

```bash
python -m pip install -e ".[dev]"
```

如果不安装，也可以在仓库中直接运行 pytest；`pyproject.toml` 已配置 `pythonpath = ["src"]`。

## 使用 CLI

```bash
ue-log-analyzer <UE_PROJECT_ROOT>
```

或：

```bash
python -m ue_log_analyzer.cli <UE_PROJECT_ROOT>
```

写入报告文件：

```bash
ue-log-analyzer <UE_PROJECT_ROOT> --output <UE_PROJECT_ROOT>/Saved/Logs/AI_Log_Report.md
```

## MCP-style 工具函数

核心函数位于 `src/ue_log_analyzer/mcp_server.py`：

```python
from ue_log_analyzer.mcp_server import generate_markdown_report

result = generate_markdown_report("D:/UnrealProjects/MyGame")
print(result["report"])
```

可用工具：

- `get_latest_log_info(project_root)`
- `analyze_latest_log(project_root, read_limit_chars=20000)`
- `generate_markdown_report(project_root, read_limit_chars=20000)`
- `dispatch_tool(name, arguments)`

## Hook

代码修改后运行测试：

```bash
python hooks/after_code_change.py
```

提交前扫描最新 UE 日志：

```bash
python hooks/pre_commit_scan.py <UE_PROJECT_ROOT>
```

或：

```bash
UE_PROJECT_ROOT=<UE_PROJECT_ROOT> python hooks/pre_commit_scan.py
```

如果发现 `critical` 或 `high` 严重度问题，`pre_commit_scan.py` 返回 `1`。

## 测试

```bash
python -m pytest
```

当前测试结果：

```text
15 passed
```

## 文档

- [PRD](docs/PRD.md)
- [Usage Guide](docs/USAGE_GUIDE.md)
- [Project Memory](docs/PROJECT_MEMORY.md)
- [Technical Design](docs/TECHNICAL_DESIGN.md)
- [AI Workflow](docs/AI_WORKFLOW.md)
- [MCP Design](docs/MCP_DESIGN.md)
- [Skill Design](docs/SKILL_DESIGN.md)
- [Hook Design](docs/HOOK_DESIGN.md)
- [Test Report](docs/TEST_REPORT.md)
- [Retrospective](docs/RETROSPECTIVE.md)

## 安全边界

- 读取文件时必须位于用户指定的 UE 项目目录内。
- 默认最多分析日志末尾 20000 字符。
- 不执行日志内容。
- 不启动 Unreal Editor。
- 不删除、不重置、不修改 UE 项目文件。
