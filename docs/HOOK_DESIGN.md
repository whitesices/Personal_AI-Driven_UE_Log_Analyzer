# Hook Design

## 1. Hook 目标

Hook 用于把 AI Native 开发流程变成可验证闭环：

- AI 修改代码后自动运行测试。
- Git 提交前自动扫描最新 UE 日志。

## 2. 脚本

| 脚本 | 用途 |
| --- | --- |
| `hooks/after_code_change.py` | 运行 pytest，并返回测试退出码 |
| `hooks/pre_commit_scan.py` | 分析最新 UE 日志，发现阻塞问题时返回 1 |

## 3. after_code_change

执行：

```bash
python hooks/after_code_change.py
```

行为：

- 在当前仓库根目录运行 `python -m pytest`。
- 不通过 shell 执行。
- 保留 pytest 原始退出码。

## 4. pre_commit_scan

执行：

```bash
python hooks/pre_commit_scan.py <UE_PROJECT_ROOT>
```

或使用环境变量：

```bash
UE_PROJECT_ROOT=<UE_PROJECT_ROOT> python hooks/pre_commit_scan.py
```

行为：

- 调用核心分析器读取最新 UE 日志。
- 如果存在 `critical` 或 `high` 严重度问题，返回 1。
- 否则返回 0。

## 5. 安全性

- Hook 只读取指定 UE 项目目录内日志。
- Hook 不删除、不重置、不修改 UE 项目文件。
- 执行测试时使用 Python 参数列表，不拼接 shell 字符串。

