from __future__ import annotations

from typing import Any

from .mcp_server import (
    analyze_latest_log as core_analyze_latest_log,
)
from .mcp_server import (
    generate_markdown_report as core_generate_markdown_report,
)
from .mcp_server import (
    get_latest_log_info as core_get_latest_log_info,
)
from .mcp_server import (
    scan_ue_project_structure as core_scan_ue_project_structure,
)
from .reader import DEFAULT_READ_LIMIT_CHARS

_FastMCP: Any
try:
    from mcp.server.fastmcp import FastMCP as _ImportedFastMCP  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover - exercised only when SDK is missing at runtime.
    _FastMCP = None
else:
    _FastMCP = _ImportedFastMCP


MCP_SERVER_NAME = "ue-log-analyzer"
MCP_TOOL_NAMES = (
    "get_latest_log_info",
    "analyze_latest_log",
    "generate_markdown_report",
    "scan_ue_project_structure",
)


def registered_tool_names() -> tuple[str, ...]:
    """Return the MCP tools this stdio adapter registers."""
    return MCP_TOOL_NAMES


def create_server() -> Any:
    """Create a FastMCP stdio server that exposes UE log analysis tools.

    The server itself performs no business logic. Each tool delegates to the
    existing mcp_server functions, which enforce UE project path safety and
    bounded log reads.
    """
    if _FastMCP is None:
        raise RuntimeError(
            "The MCP Python SDK is not installed. Install the project with "
            '`python -m pip install -e ".[dev]"` or install package `mcp`.'
        )

    mcp = _FastMCP(MCP_SERVER_NAME)

    @mcp.tool()
    def get_latest_log_info(project_root: str) -> dict[str, Any]:
        """Return newest UE log metadata.

        Input:
            project_root: UE project root directory containing Saved/Logs.

        Output:
            JSON-serializable metadata for the latest .log file.

        Safety:
            Reads only under project_root and never executes log content.
        """
        return core_get_latest_log_info(project_root)

    @mcp.tool()
    def analyze_latest_log(
        project_root: str,
        read_limit_chars: int = DEFAULT_READ_LIMIT_CHARS,
    ) -> dict[str, Any]:
        """Analyze the newest UE log and return structured issue data.

        Input:
            project_root: UE project root directory containing Saved/Logs.
            read_limit_chars: Maximum trailing characters to analyze.

        Output:
            JSON-serializable analysis with categories, stages, risk levels,
            likely causes, fixes, and verification steps.

        Safety:
            Reads only the latest log under project_root/Saved/Logs and applies
            the configured tail limit.
        """
        return core_analyze_latest_log(project_root, read_limit_chars)

    @mcp.tool()
    def generate_markdown_report(
        project_root: str,
        read_limit_chars: int = DEFAULT_READ_LIMIT_CHARS,
    ) -> dict[str, Any]:
        """Generate a Markdown UE log analysis report.

        Input:
            project_root: UE project root directory containing Saved/Logs.
            read_limit_chars: Maximum trailing characters to analyze.

        Output:
            Markdown report plus the same structured analysis payload.

        Safety:
            Does not write files. The returned report is generated from a
            bounded read inside project_root.
        """
        return core_generate_markdown_report(project_root, read_limit_chars)

    @mcp.tool()
    def scan_ue_project_structure(project_root: str) -> dict[str, Any]:
        """Scan high-level UE project structure.

        Input:
            project_root: UE project root directory.

        Output:
            Presence of key UE folders, .uproject files, plugin descriptors,
            and latest log relative path when available.

        Safety:
            Lists only project_root-contained paths and does not read arbitrary
            source, asset, or config contents.
        """
        return core_scan_ue_project_structure(project_root)

    return mcp


def main() -> int:
    server = create_server()
    server.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
