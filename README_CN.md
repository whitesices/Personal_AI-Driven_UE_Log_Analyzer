# Personal_AI-Driven_UE_Log_Analyzer

[![CI](https://github.com/whitesices/Personal_AI-Driven_UE_Log_Analyzer/actions/workflows/ci.yml/badge.svg)](https://github.com/whitesices/Personal_AI-Driven_UE_Log_Analyzer/actions/workflows/ci.yml)

AI-Driven UE Log Analyzer 是一个本地运行、带安全边界的 Unreal Engine 日志分析工具，同时也是一个面向面试展示的 AI Agent 工程化实践项目。

它展示了一套完整闭环：

```text
UE Project Saved/Logs
        |
        v
Python Analyzer + UE Rule Library
        |
        +--> CLI Markdown Report
        +--> MCP stdio Server for AI Agents
        +--> Skill-guided UE triage workflow
        +--> Hooks for test and pre-commit checks
        +--> Tests / CI / Docs / Retrospective
```

## 为什么这个项目体现 AI 主导开发

这个项目不只是一个日志解析器。它的设计目标是展示 AI 如何主导一个小而完整的工程工作流：

- **Skill**：沉淀可复用的 UE 日志分析经验。
- **MCP**：为 AI 工具提供安全的 UE 项目上下文入口。
- **Hook**：在 AI 修改代码后、Git 提交前形成验证闭环。
- **Tests / CI**：保证行为可靠。
- **Docs / Retrospective**：沉淀 AI 主导开发过程，方便复盘和评审。

## 功能特性

- 自动查找 `<UE_PROJECT>/Saved/Logs` 下最新的 `.log` 文件。
- 只读取用户指定 UE 项目目录内部的文件。
- 默认只分析日志尾部内容，避免超大日志占用过多上下文。
- 检测 UE 专项问题，包括 LinkerSave、SavePackage、Assertion failed、AutomationTool、PackagingResults、Unknown Cook Failure、Blueprint 编译错误、资源缺失、插件/模块加载失败、C++ 编译错误、Shader/DDC、SDK、Pak 和 IoStore 问题。
- 生成结构化 Markdown 报告，包含：
  - category
  - severity
  - likely UE stage
  - risk level
  - possible causes
  - recommended fixes
  - verification steps
- 支持 CLI、MCP stdio server 和 Python API 三种使用方式。
- 提供 Hook、测试、CI、Skill 文档和面试展示材料。

## 安装

```bash
python -m pip install -e ".[dev]"
```

## CLI 使用

推荐使用显式 `--project` 参数：

```bash
python -m ue_log_analyzer --project "D:/UEProjects/MyProject"
```

将报告保存到 UE 项目目录内：

```bash
python -m ue_log_analyzer --project "D:/UEProjects/MyProject" --output "AIReports/latest_report.md"
```

兼容旧版命令行入口：

```bash
ue-log-analyzer "D:/UEProjects/MyProject"
```

分析 UE 项目内的指定日志：

```bash
python -m ue_log_analyzer --project "D:/UEProjects/MyProject" --log-path "Saved/Logs/MyProject.log"
```

安全说明：`--output` 和 `--log-path` 都会被限制在 UE 项目目录内。

## MCP Server 使用

运行真实的 stdio MCP server：

```bash
python -m ue_log_analyzer.mcp_stdio_server
```

Claude Desktop / Claude Code / Cursor 可参考如下 MCP 客户端配置：

```json
{
  "mcpServers": {
    "ue-log-analyzer": {
      "command": "python",
      "args": ["-m", "ue_log_analyzer.mcp_stdio_server"]
    }
  }
}
```

这是配置模板。本项目提供了真实的 stdio server adapter，但不同客户端可能需要结合具体环境做额外配置。

已注册工具：

- `get_latest_log_info`
- `analyze_latest_log`
- `generate_markdown_report`
- `scan_ue_project_structure`

详见 [MCP stdio server 设计](docs/08_MCP_STDIO_SERVER.md)。

## Hook 使用

AI 修改代码后运行测试：

```bash
python hooks/after_code_change.py
```

Git 提交前扫描最新 UE 日志：

```bash
python hooks/pre_commit_scan.py "D:/UEProjects/MyProject"
```

当发现 critical 或 high 严重度 UE 日志问题时，pre-commit scan 会返回非零退出码。

## Skill 使用

UE Log Analysis Skill 位于：

```text
skills/ue-log-analysis/SKILL.md
```

该 Skill 定义了一套可复用的 AI 工作流，用于：

- 选择最新日志。
- 强制执行项目目录内安全读取。
- 识别 UE Build / Cook / Package / Runtime 阶段。
- 解释可能根因。
- 推荐修复步骤。
- 在代码修改后进行验证。

## 测试与质量检查

```bash
python -m pytest
ruff check .
mypy src
python -m build
```

GitHub Actions CI 会执行：

- install
- pytest
- ruff
- mypy

## 示例报告

- [HotPatcher LinkerSave Assertion](examples/reports/hotpatcher_linkersave_assertion_report.md)
- [Packaging Failed](examples/reports/packaging_failed_report.md)
- [Blueprint Compile Error](examples/reports/blueprint_compile_error_report.md)

示例日志位于：

```text
examples/sample_ue_project/Saved/Logs/
```

## 安全边界

- 不调用外部 API。
- 不上传日志。
- 不启动 Unreal Editor。
- 不执行 UE 项目中的脚本。
- 输入日志路径必须位于 UE 项目目录内。
- CLI 输出路径必须位于 UE 项目目录内。
- MCP tools 复用同一套安全受限的业务函数。
- 长日志通过有界尾部读取进行分析。

## 文档地图

- [Original Prompt](docs/00_ORIGINAL_PROMPT.md)
- [Agent Task Breakdown](docs/01_AGENT_TASK_BREAKDOWN.md)
- [AI Development Log](docs/02_AI_DEVELOPMENT_LOG.md)
- [Human Review Notes](docs/03_HUMAN_REVIEW_NOTES.md)
- [AI Native Workflow](docs/09_AI_NATIVE_WORKFLOW.md)
- [PRD](docs/PRD.md)
- [Usage Guide](docs/USAGE_GUIDE.md)
- [Project Memory](docs/PROJECT_MEMORY.md)
- [Technical Design](docs/TECHNICAL_DESIGN.md)
- [AI Workflow](docs/AI_WORKFLOW.md)
- [MCP Design](docs/MCP_DESIGN.md)
- [MCP stdio Server](docs/08_MCP_STDIO_SERVER.md)
- [Skill Design](docs/SKILL_DESIGN.md)
- [Hook Design](docs/HOOK_DESIGN.md)
- [Test Report](docs/06_TEST_REPORT.md)
- [Retrospective](docs/07_RETROSPECTIVE.md)

## Autonomous AI Experiment

一个有边界的、不中途人工确认的 AI 自主开发实验记录在：

```text
experiments/ai_autonomous_run/
```

它将主项目中的“AI 主导 + 人类 Review”工作流，与一个更小范围的自主 AI 运行协议区分开。这样既方便面试讨论，也避免夸大项目的自动化程度。

## Roadmap

- 增加可配置 YAML UE 规则包。
- 增加 stdio MCP 集成 smoke test。
- 增加 HTML 和 SARIF 报告输出。
- 增加 Git Hook 安装辅助脚本。
- 增加多次构建日志的趋势分析。
- 增加更深入的 AutomationTool 和 Cook 阶段解析器。

