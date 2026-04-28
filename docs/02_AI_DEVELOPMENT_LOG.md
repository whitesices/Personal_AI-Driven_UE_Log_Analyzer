# AI Development Log

本文记录项目开发过程，强调 AI 主导开发如何形成工程闭环。

## 1. AI 生成的模块

AI 生成并迭代了以下模块：

- `reader.py`：安全读取 UE 项目最新日志。
- `detector.py`：检测 UE 日志信号。
- `rules.py`：UE 专业规则库。
- `classifier.py`：分类、严重度、阶段、风险、修复建议。
- `analyzer.py`：分析编排和统计。
- `report.py`：Markdown 报告生成。
- `mcp_server.py`：MCP-style 工具函数。
- `mcp_stdio_server.py`：真实 MCP stdio Server 适配层。
- `cli.py` / `__main__.py`：命令行入口。
- `hooks/`：测试 Hook 和提交前扫描 Hook。
- `tests/`：pytest 测试体系。
- `docs/`：需求、设计、流程、测试、复盘、面试材料。

## 2. 人工验收点

人类 reviewer 应重点检查：

- 路径越权防护是否完整。
- MCP 是否只是文档描述，还是有可运行 stdio Server。
- UE 规则是否体现真实 UE 工具链问题。
- 测试是否覆盖安全边界和典型 UE 样例。
- README 是否能用于面试讲解。

## 3. 测试发现的问题

第一轮测试发现当前 Windows 环境下 pytest 默认临时目录不可访问。

修复方式：

- 避免依赖系统临时目录。
- 使用仓库内 `test_workspace` fixture。
- fixture 结束后清理目录。
- 关闭 pytest cache provider。

第二轮测试重点补足：

- CLI 输出路径越权。
- MCP tool 注册。
- UE 规则匹配。
- HotPatcher/LinkerSave 专项样例。
- Project structure scan。

## 4. 修复策略

AI 修复时遵循：

- 不推翻已有结构。
- 先加测试，再改逻辑。
- 业务函数复用，不复制 MCP 逻辑。
- 所有新增路径处理复用 reader 安全函数。
- 文档与测试结果同步更新。

## 5. 当前验证

当前验证命令：

```bash
python -m pytest
ruff check .
mypy src
```

`ruff` 和 `mypy` 是第二轮新增质量门禁。

