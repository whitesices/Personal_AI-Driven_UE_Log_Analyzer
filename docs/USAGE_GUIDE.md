# Usage Guide

本文说明如何使用 AI-Driven UE Log Analyzer 分析一个 Unreal Engine 项目。

## 1. 准备 UE 项目路径

你需要提供 UE 项目根目录，也就是包含 `Saved/Logs` 的目录。

示例：

```text
D:\UnrealProjects\MyGame
```

工具会自动查找：

```text
D:\UnrealProjects\MyGame\Saved\Logs\*.log
```

并选择最后修改时间最新的 `.log` 文件进行分析。

## 2. 安装工具

进入本工具项目目录：

```powershell
cd C:\ML\Personal_AI-Driven_UE_Log_Analyzer
```

安装为本地可编辑包：

```powershell
python -m pip install -e ".[dev]"
```

安装后可以使用命令：

```powershell
ue-log-analyzer --help
```

## 3. 分析最新 UE 日志

运行：

```powershell
ue-log-analyzer "D:\UnrealProjects\MyGame"
```

工具会输出 Markdown 格式报告，包含：

- 分析时间
- UE 项目路径
- 最新日志路径
- 读取范围
- 问题总览
- 高优先级问题
- 分类问题列表
- 原始证据片段
- 建议下一步

## 4. 保存分析报告

将报告保存到 UE 项目日志目录：

```powershell
ue-log-analyzer "D:\UnrealProjects\MyGame" --output "D:\UnrealProjects\MyGame\Saved\Logs\AI_Log_Report.md"
```

报告是普通 Markdown 文件，可以直接交给 AI Agent、IDE、代码评审或团队成员查看。

## 5. 指定某个日志文件

默认会分析最新日志。如果你想分析指定日志，可以传入 `--log-path`。

推荐使用相对 UE 项目根目录的路径：

```powershell
ue-log-analyzer "D:\UnrealProjects\MyGame" --log-path "Saved\Logs\MyGame.log"
```

安全限制：

- `--log-path` 必须位于 UE 项目目录内。
- 工具会拒绝读取 UE 项目目录外的文件。

## 6. 调整读取长度

默认只读取日志最后 20000 个字符。

如果你想缩小分析范围：

```powershell
ue-log-analyzer "D:\UnrealProjects\MyGame" --read-limit-chars 8000
```

如果日志尾部上下文不足，可以提高限制：

```powershell
ue-log-analyzer "D:\UnrealProjects\MyGame" --read-limit-chars 50000
```

## 7. 启用高级诊断 Agent

插件兼容性检查：

```powershell
python -m ue_log_analyzer --project "D:\UnrealProjects\MyGame" --plugin-check
```

Blueprint 错误专项分析：

```powershell
python -m ue_log_analyzer --project "D:\UnrealProjects\MyGame" --blueprint-analysis
```

生成只读自动修复建议计划：

```powershell
python -m ue_log_analyzer --project "D:\UnrealProjects\MyGame" --fix-plan
```

一次性启用全部高级诊断：

```powershell
python -m ue_log_analyzer --project "D:\UnrealProjects\MyGame" --full-diagnostics
```

这些能力仍然遵守项目目录安全边界，不会执行 UE 项目脚本，也不会自动修改 UE 项目文件。

## 8. 不安装时直接运行

如果暂时不想安装包，可以在工具项目目录中运行：

```powershell
cd C:\ML\Personal_AI-Driven_UE_Log_Analyzer
$env:PYTHONPATH="$PWD\src"
python -m ue_log_analyzer.cli "D:\UnrealProjects\MyGame"
```

保存报告：

```powershell
$env:PYTHONPATH="$PWD\src"
python -m ue_log_analyzer.cli "D:\UnrealProjects\MyGame" --output "D:\UnrealProjects\MyGame\Saved\Logs\AI_Log_Report.md"
```

## 9. 提交前扫描 UE 日志

使用 Hook 脚本扫描最新 UE 日志：

```powershell
python hooks\pre_commit_scan.py "D:\UnrealProjects\MyGame"
```

如果日志中存在阻塞问题，脚本会返回非零退出码。

阻塞问题包括：

- `critical`：`Fatal error`、`Assertion failed`、`Unhandled Exception`
- `high`：`PackagingResults: Error`、C++ 编译错误、构建失败

也可以使用环境变量：

```powershell
$env:UE_PROJECT_ROOT="D:\UnrealProjects\MyGame"
python hooks\pre_commit_scan.py
```

## 10. AI 修改代码后运行测试

在本工具项目中运行：

```powershell
python hooks\after_code_change.py
```

该脚本会执行：

```powershell
python -m pytest
```

并返回 pytest 的退出码。

## 11. 在 Python 中调用

生成 Markdown 报告：

```python
from ue_log_analyzer.mcp_server import generate_markdown_report

result = generate_markdown_report("D:/UnrealProjects/MyGame")
if result["ok"]:
    print(result["report"])
else:
    print(result["error"])
```

获取结构化 JSON：

```python
from ue_log_analyzer.mcp_server import analyze_latest_log

result = analyze_latest_log("D:/UnrealProjects/MyGame")
print(result["analysis"]["summary"])
```

高级诊断函数：

```python
from ue_log_analyzer import (
    analyze_blueprint_errors,
    check_plugin_compatibility,
    generate_auto_fix_plan,
)

plugin_report = check_plugin_compatibility("D:/UnrealProjects/MyGame")
blueprint_report = analyze_blueprint_errors("D:/UnrealProjects/MyGame")
fix_plan = generate_auto_fix_plan("D:/UnrealProjects/MyGame")
```

## 12. 示例项目验证

本仓库包含一个最小示例：

```powershell
ue-log-analyzer "C:\ML\Personal_AI-Driven_UE_Log_Analyzer\examples\sample_ue_project"
```

也可以运行提交前扫描：

```powershell
python hooks\pre_commit_scan.py examples\sample_ue_project
```

预期结果：

```text
UE log scan: 1 issue(s), blocking=0
```

## 13. 常见问题

### 找不到日志目录

确认传入的是 UE 项目根目录，而不是 `Saved/Logs` 目录本身。

正确：

```powershell
ue-log-analyzer "D:\UnrealProjects\MyGame"
```

错误：

```powershell
ue-log-analyzer "D:\UnrealProjects\MyGame\Saved\Logs"
```

### 没有发现 `.log` 文件

确认 UE 项目运行、构建或打包后已经生成日志。通常日志位于：

```text
<UE_PROJECT_ROOT>\Saved\Logs
```

### 报告没有发现错误，但 UE 仍失败

可能原因：

- 分析的不是最新失败对应的日志。
- 失败信息位于更早的日志部分。
- 当前读取长度太小。

可以增加读取长度：

```powershell
ue-log-analyzer "D:\UnrealProjects\MyGame" --read-limit-chars 50000
```

### 指定日志被拒绝读取

工具只允许读取 UE 项目目录内的文件。请使用项目内相对路径，例如：

```powershell
ue-log-analyzer "D:\UnrealProjects\MyGame" --log-path "Saved\Logs\MyGame.log"
```
