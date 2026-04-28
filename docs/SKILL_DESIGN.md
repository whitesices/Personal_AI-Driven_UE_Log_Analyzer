# Skill Design

## 1. Skill 名称

`ue-log-analysis`

## 2. 触发场景

当 AI Agent 需要处理以下任务时使用：

- 分析 Unreal Engine 最新日志。
- 诊断构建失败、打包失败、运行时崩溃。
- 总结 Blueprint、插件、资源引用或 C++ 编译错误。
- 生成结构化 Markdown 日志报告。
- 判断提交前 UE 日志是否存在阻塞问题。

## 3. Skill 文件

Skill 位于：

```text
skills/ue-log-analysis/SKILL.md
```

## 4. 设计原则

- Skill 保持简短，只包含核心流程和安全规则。
- 具体实现由 Python 包提供，避免在 Skill 中重复代码。
- AI Agent 必须优先使用本地工具，而不是手动读取任意路径。
- Skill 强调证据优先，避免无日志依据的推测。

## 5. 工作流摘要

1. 确认 UE 项目根目录。
2. 查找 `Saved/Logs` 最新 `.log` 文件。
3. 读取尾部最多 20000 字符。
4. 检测并分类问题。
5. 输出结构化报告。
6. 修改代码后运行测试。
7. 提交前扫描最新日志。

