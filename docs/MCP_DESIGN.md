# MCP Design

## 1. 目标

MCP Server 让 AI Agent 可以安全调用 UE 日志分析能力，而不是直接任意读取文件系统。

## 2. 工具函数

当前实现位于 `src/ue_log_analyzer/mcp_server.py`，采用 runtime 无关的 Python 函数：

| 工具 | 输入 | 输出 |
| --- | --- | --- |
| `get_latest_log_info` | `project_root` | 最新日志元信息 |
| `analyze_latest_log` | `project_root`, `read_limit_chars` | 结构化 JSON 分析结果 |
| `generate_markdown_report` | `project_root`, `read_limit_chars` | Markdown 报告和 JSON 分析结果 |

## 3. 安全边界

- 所有读取都限制在 `project_root` 下。
- 默认只读取最新日志尾部 20000 个字符。
- 工具函数返回普通 JSON，不执行日志内容。
- 错误以 `{ "ok": false, "error": "..." }` 返回，便于 Agent 处理。

## 4. 后续接入方式

可以将这些函数挂载到任意 MCP runtime：

1. stdio MCP server。
2. FastMCP。
3. Codex 本地工具适配器。
4. IDE Agent 插件。

适配层只需要将 MCP tool call 的 `arguments` 转发给 `dispatch_tool(name, arguments)`。

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

