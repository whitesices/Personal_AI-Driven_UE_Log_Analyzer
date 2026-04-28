# Human Review Notes

本文模拟人类 reviewer 对项目的审查重点，便于面试时说明“AI 生成不等于无人验收”。

## 1. 安全边界

Reviewer 应确认：

- `project_root` 会被 resolve。
- 日志读取必须在 UE 项目目录内。
- `--log-path` 即使是绝对路径也不能越权。
- `--output` 不能默认写到项目目录外。
- MCP tools 不执行日志内容。
- Hook 不执行 UE 项目里的任意脚本。

当前状态：

- 读取路径由 `reader.ensure_within_project()` 约束。
- CLI output 路径已限制在 UE 项目目录内。
- MCP stdio tools 复用安全业务函数。

## 2. UE 专业规则

Reviewer 应确认规则不是简单关键词堆叠，而是包含：

- 阶段判断：Build / Cook / Stage / Package / Runtime。
- 可能根因。
- 修复步骤。
- 验证步骤。
- 风险等级。

当前状态：

- `rules.py` 覆盖 LinkerSave、Assertion、AutomationTool、PackagingResults、Unknown Cook Failure、Blueprint、Missing Asset、Plugin、C++、Shader/DDC、SDK、Pak/IoStore。

## 3. MCP 真实性

Reviewer 应区分：

- MCP-style：普通 Python 函数，适合测试。
- MCP stdio Server：可由 Claude Desktop / Claude Code / Cursor 通过 MCP 配置启动。

当前状态：

- `mcp_server.py` 保留 MCP-style 业务函数。
- `mcp_stdio_server.py` 使用 FastMCP 风格注册 stdio tools。
- README 和 `docs/08_MCP_STDIO_SERVER.md` 给出可接入配置示例。

## 4. 测试覆盖

Reviewer 应确认新增功能都有测试：

- rules。
- MCP adapter 注册。
- scan project structure。
- CLI output 越权。
- UE 典型日志样例。

当前状态：

- 测试数量已扩展到 24+。
- pytest 通过。

## 5. 面试展示价值

本项目可以展示：

- AI 主导任务拆解。
- Python 工程结构。
- UE 工具链理解。
- MCP / Skill / Hook 的 Agent 工程化。
- 测试和 CI 保障。
- 文档和复盘沉淀。

