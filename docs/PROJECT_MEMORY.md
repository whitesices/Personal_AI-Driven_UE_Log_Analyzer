# Project Memory

本文是 AI-Driven UE Log Analyzer 的项目同步记忆，供项目组成员、后续 AI Agent 和新接手同事快速了解当前状态。

## 1. 项目定位

AI-Driven UE Log Analyzer 是一个本地 Python 工具，用于分析 Unreal Engine 项目 `Saved/Logs` 下的最新日志，并生成结构化 Markdown 报告。

核心目标：

- 帮 UE 开发者快速定位构建失败、打包失败、插件兼容、Blueprint 编译错误、C++ 编译错误、运行时崩溃和断言失败。
- 为 AI Agent 提供安全、结构化、可测试的 UE 日志上下文读取能力。
- 形成 AI Native 开发闭环：读日志、分析、生成报告、修改后测试、提交前扫描。

## 2. 当前状态

当前版本已完成第一版完整闭环：

- Python 包结构已建立。
- 核心日志分析能力已实现。
- MCP-style 工具函数已实现。
- MCP stdio Server 适配层已实现。
- UE Log Analysis Skill 已编写。
- Hook 脚本已实现。
- README 和 docs 文档已补齐。
- pytest 测试已通过。

最新验证结果：

```text
python -m pytest
25 passed

python hooks\after_code_change.py
25 passed

python hooks\pre_commit_scan.py examples\sample_ue_project
UE log scan: 1 issue(s), blocking=0
```

## 3. 重要目录

```text
.
├── src/ue_log_analyzer/          # 核心 Python 包
├── tests/                        # pytest 测试
├── docs/                         # 项目文档
├── hooks/                        # AI 修改后测试、提交前日志扫描脚本
├── skills/ue-log-analysis/       # UE 日志分析 Skill
├── examples/sample_ue_project/   # 最小示例 UE 项目日志
├── pyproject.toml                # Python 项目配置
└── README.md                     # 项目入口文档
```

## 4. 核心模块

| 模块 | 职责 |
| --- | --- |
| `models.py` | 定义日志信息、问题、分析结果等数据结构 |
| `reader.py` | 安全定位和读取 UE 日志 |
| `detector.py` | 检测 Error、Warning、Fatal、Assertion 等日志信号 |
| `classifier.py` | 将问题分类并计算严重度 |
| `analyzer.py` | 编排读取、检测、分类和统计 |
| `report.py` | 生成结构化 Markdown 报告 |
| `mcp_server.py` | 提供 MCP-style 工具函数和 dispatcher |
| `mcp_stdio_server.py` | 提供真实 MCP stdio Server 适配层 |
| `cli.py` | 命令行入口 |

## 5. 安全边界

这些约束是项目的硬性要求，后续修改不能破坏：

- 只能读取用户指定 UE 项目目录内的文件。
- 默认只分析日志最后 20000 个字符。
- 不执行日志内容。
- 不启动 Unreal Editor。
- 不删除、不重置、不修改 UE 项目文件。
- Hook 不使用 shell 字符串拼接执行命令。
- 显式 `--log-path` 可以使用项目内相对路径，但必须仍然位于 UE 项目根目录内。

## 6. 分类规则

当前分类为启发式规则：

| 分类 | 典型触发信号 |
| --- | --- |
| `runtime_crash` | `Fatal error`、`Assertion failed`、`Unhandled Exception` |
| `packaging_error` | `PackagingResults: Error`、`UATHelper`、`AutomationTool` |
| `cpp_compile_error` | `error C####`、`CompilerResultsLog`、`.cpp(line)`、`.h(line)` |
| `build_error` | `LogCompile`、`Build failed`、`UnrealBuildTool`、`UBT` |
| `plugin_compatibility` | `LogPluginManager`、`plugin`、module load failure |
| `blueprint_error` | `LogBlueprint`、`Blueprint Runtime Error`、`K2Node` |
| `asset_reference_error` | `LogLinker`、`Can't find file`、`Failed to load`、`Missing` |
| `unknown` | 只匹配通用 Error/Warning，无法归入具体类别 |

严重度规则：

- `critical`：崩溃、断言、未处理异常。
- `high`：打包错误、C++ 编译错误、构建失败。
- `medium`：插件、蓝图、资源引用和普通错误。
- `low`：普通 Warning。

## 7. 常用命令

安装：

```powershell
python -m pip install -e ".[dev]"
```

分析 UE 项目：

```powershell
ue-log-analyzer "D:\UnrealProjects\MyGame"
```

保存报告：

```powershell
ue-log-analyzer "D:\UnrealProjects\MyGame" --output "D:\UnrealProjects\MyGame\Saved\Logs\AI_Log_Report.md"
```

指定日志：

```powershell
ue-log-analyzer "D:\UnrealProjects\MyGame" --log-path "Saved\Logs\MyGame.log"
```

运行测试：

```powershell
python -m pytest
```

AI 修改代码后验证：

```powershell
python hooks\after_code_change.py
```

提交前扫描：

```powershell
python hooks\pre_commit_scan.py "D:\UnrealProjects\MyGame"
```

## 8. MCP 调用

当前 MCP 分为两层：

- `mcp_server.py`：runtime 无关的 Python 工具函数，方便测试和复用。
- `mcp_stdio_server.py`：真实 stdio MCP Server 适配层，供 Claude Desktop / Claude Code / Cursor 等客户端参考接入。

工具函数位置：

```text
src/ue_log_analyzer/mcp_server.py
```

可用函数：

- `get_latest_log_info(project_root)`
- `analyze_latest_log(project_root, read_limit_chars=20000)`
- `generate_markdown_report(project_root, read_limit_chars=20000)`
- `dispatch_tool(name, arguments)`
- `scan_ue_project_structure(project_root)`

stdio Server：

```powershell
python -m ue_log_analyzer.mcp_stdio_server
```

示例：

```python
from ue_log_analyzer.mcp_server import generate_markdown_report

result = generate_markdown_report("D:/UnrealProjects/MyGame")
if result["ok"]:
    print(result["report"])
else:
    print(result["error"])
```

## 9. 已知环境注意事项

在当前 Windows 沙箱环境中，pytest 默认临时目录和 cache 目录可能出现权限问题。

当前处理方式：

- 测试不依赖 pytest `tmp_path`。
- `tests/conftest.py` 使用仓库内 `test_workspace/<uuid>` 作为测试目录。
- `pyproject.toml` 关闭 pytest cache provider。
- `.gitignore` 已忽略 `test_workspace/`、`test_tmp/`、`.tmp/` 和 `pytest-cache-files-*/`。

## 10. 文档地图

| 文档 | 用途 |
| --- | --- |
| `README.md` | 项目入口 |
| `docs/USAGE_GUIDE.md` | 使用指南 |
| `docs/PRD.md` | 产品需求 |
| `docs/TECHNICAL_DESIGN.md` | 技术方案 |
| `docs/AI_WORKFLOW.md` | AI 工作流 |
| `docs/MCP_DESIGN.md` | MCP 设计 |
| `docs/SKILL_DESIGN.md` | Skill 设计 |
| `docs/HOOK_DESIGN.md` | Hook 设计 |
| `docs/06_TEST_REPORT.md` | 第二轮测试报告 |
| `docs/07_RETROSPECTIVE.md` | 第二轮项目复盘 |
| `docs/08_MCP_STDIO_SERVER.md` | MCP stdio Server 说明 |
| `docs/PROJECT_MEMORY.md` | 项目同步记忆 |

## 11. 后续建议

建议下一阶段按优先级推进：

1. 增加可配置规则文件，例如 `rules/ue_patterns.yml`。
2. 增加 Git Hook 自动安装脚本。
3. 增加 HTML 或 SARIF 报告输出。
4. 对 Cook、AutomationTool、Blueprint Compiler 增加更细分类。
5. 支持分析多个日志文件并生成趋势摘要。

## 12. 交接提醒

后续开发前请先确认：

- 是否改动了 `reader.py` 的路径安全逻辑。
- 是否改动了默认读取限制。
- 是否新增了会访问网络、启动 UE、删除文件或执行 shell 的行为。
- 是否更新了测试和 `docs/06_TEST_REPORT.md`。
- 是否同步更新了本文件。
