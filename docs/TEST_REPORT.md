# Test Report

## 1. 测试日期

2026-04-28

## 2. 测试环境

- OS：Windows
- Shell：PowerShell
- Python：本地 Anaconda Python
- Test runner：pytest

## 3. 执行命令

```bash
python -m pytest
```

## 4. 最终结果

```text
25 passed in 0.87s
```

## 5. 覆盖范围

测试覆盖以下能力：

- 最新日志发现。
- 日志尾部读取限制。
- 越权路径读取拦截。
- 无日志时的错误处理。
- UE 常见失败类型分类。
- 空日志或干净日志处理。
- Markdown 报告必要章节。
- MCP-style 工具函数 JSON 输出。
- MCP dispatcher 未知工具错误。
- Hook 命令构造。
- pre-commit 扫描阻塞与非阻塞退出码。
- MCP stdio adapter 注册工具列表。
- MCP stdio Server 对象创建。
- UE 专业规则库匹配。
- CLI 输出路径越权拦截。
- UE 项目结构扫描。
- HotPatcher / LinkerSave / InSaver、Packaging、Blueprint、Missing Asset 样例。

## 6. Hook 验证

执行：

```bash
python hooks/after_code_change.py
```

结果：

```text
25 passed in 0.87s
```

执行：

```bash
python hooks/pre_commit_scan.py examples/sample_ue_project
```

结果：

```text
UE log scan: 1 issue(s), blocking=0
```

## 7. 发现并修复的问题

### 7.1 pytest 默认临时目录不可访问

首次执行 pytest 时，当前环境拒绝访问系统默认 pytest 临时目录：

```text
PermissionError: [WinError 5] Access denied
```

处理方式：

- 避免测试依赖 pytest `tmp_path`。
- 新增 `tests/conftest.py`，使用仓库内 `test_workspace/<uuid>` 作为测试工作目录。
- 在 `pyproject.toml` 中关闭 pytest cache provider，避免在受限环境中创建 cache 文件失败。

### 7.2 README 原始内容编码异常

仓库原始 README 存在乱码。已重写为完整中文 README。

## 8. 剩余风险

- MCP stdio Server 已实现；仍建议在目标客户端中做一次端到端连接验证。
- 分类规则采用启发式规则，后续可以引入更细粒度 UE 日志模式库。
- Hook 目前不自动安装到 `.git/hooks`，需要用户按项目策略接入。
