# MCP Stdio Server

## 1. Why The First Version Was MCP-style

The first version implemented MCP-style Python functions in `mcp_server.py`.

That was intentional:

- Business logic could be tested without depending on a specific MCP runtime.
- The project could validate path safety, JSON output, and report generation first.
- AI Agent tools could reuse the functions later without duplicating logic.

## 2. Second-round Upgrade

The second version adds:

```text
src/ue_log_analyzer/mcp_stdio_server.py
```

This module uses the official MCP Python SDK FastMCP style when the `mcp` package is installed.
It registers stdio MCP tools and delegates to existing functions in `mcp_server.py`.

If the MCP SDK is missing, the module raises a clear runtime error explaining how to install it.
The code structure remains in place so CI and users can install the dependency later.

## 3. MCP Tools

| Tool | Purpose |
| --- | --- |
| `get_latest_log_info` | Return metadata for the newest UE log under `Saved/Logs` |
| `analyze_latest_log` | Return structured UE log analysis JSON |
| `generate_markdown_report` | Return a Markdown analysis report |
| `scan_ue_project_structure` | Return high-level UE project structure and latest log path |

## 4. Safety Boundary

- All reads are constrained to the user-provided UE project directory.
- Logs are read with a bounded tail limit.
- MCP tools do not execute log content.
- MCP tools do not run UE project scripts.
- `generate_markdown_report` returns Markdown and does not write files.
- Structure scanning lists high-level paths only.

## 5. Running The Server

Install the project:

```bash
python -m pip install -e ".[dev]"
```

Run the stdio server:

```bash
python -m ue_log_analyzer.mcp_stdio_server
```

## 6. Client Configuration Example

Claude Desktop / Claude Code / Cursor can use a similar MCP configuration:

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

This is a configuration template. Actual client setup may differ by tool and environment.

## 7. Future Work

- Add an integration smoke test that starts the stdio server when MCP SDK is available.
- Add richer project context tools for `.uproject`, `.uplugin`, and `Build.cs` summaries.
- Add per-tool schemas once the selected MCP client workflow is finalized.

