# MCP Design

## 1. 目标

MCP Server 让 AI Agent 可以安全调用 UE 日志分析能力，而不是直接任意读取文件系统。

## 2. 工具函数

当前实现分为两层：

- `src/ue_log_analyzer/mcp_server.py`：runtime 无关的 Python 工具函数。
- `src/ue_log_analyzer/mcp_stdio_server.py`：FastMCP 风格 stdio MCP Server 适配层。

MCP tools：

| 工具 | 输入 | 输出 |
| --- | --- | --- |
| `get_latest_log_info` | `project_root` | 最新日志元信息 |
| `analyze_latest_log` | `project_root`, `read_limit_chars` | 结构化 JSON 分析结果 |
| `generate_markdown_report` | `project_root`, `read_limit_chars` | Markdown 报告和 JSON 分析结果 |
| `scan_ue_project_structure` | `project_root` | UE 项目结构摘要 |

## 3. 安全边界

- 所有读取都限制在 `project_root` 下。
- 默认只读取最新日志尾部 20000 个字符。
- 工具函数返回普通 JSON，不执行日志内容。
- 错误以 `{ "ok": false, "error": "..." }` 返回，便于 Agent 处理。

## 4. 后续接入方式

stdio Server 可通过以下方式运行：

```bash
python -m ue_log_analyzer.mcp_stdio_server
```

Claude Desktop / Claude Code / Cursor 可参考 `docs/08_MCP_STDIO_SERVER.md` 中的配置示例。
其他 Agent runtime 也可以直接复用 `dispatch_tool(name, arguments)`。

## 5. 示例响应

```json
{
  "ok": true,
  "analysis": {
    "summary": {
      "total_issues": 2,
      "has_blocking_issue": true
    }
  }
}
```
