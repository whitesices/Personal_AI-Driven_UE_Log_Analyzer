# Agent Task Breakdown

本文记录 AI Agent 如何拆解并推进本项目。

## 1. 需求分析

AI 先将用户目标拆成三个层面：

- UE 日志分析能力：读取、检测、分类、报告。
- AI Agent 工程化能力：MCP、Skill、Hook。
- 面试展示能力：文档、测试、CI、复盘、示例报告。

## 2. 项目结构

AI 保留现有结构，并按职责扩展：

```text
src/ue_log_analyzer/     # 业务代码
tests/                   # pytest
docs/                    # 设计、流程、复盘、展示材料
hooks/                   # 自动测试和提交前扫描
skills/                  # UE 日志分析 Skill
examples/                # 样例日志和样例报告
.github/workflows/       # CI
```

## 3. MCP

第一版先实现 MCP-style 工具函数，确保业务能力可测试。

第二版新增 `mcp_stdio_server.py`：

- 使用 FastMCP 风格注册 stdio Server。
- tool 复用已有业务函数。
- 不复制日志分析逻辑。
- SDK 缺失时提供清晰 fallback。

## 4. Skill

Skill 用于固化 UE 日志分析经验：

- 如何选择最新日志。
- 如何限制读取范围。
- 如何按 UE 阶段判断问题。
- 如何给出修复和验证步骤。

## 5. Hook

Hook 用于让 AI 修改代码后形成闭环：

- `after_code_change.py`：运行 pytest。
- `pre_commit_scan.py`：提交前扫描最新 UE 日志，高风险问题阻塞提交。

## 6. 测试

测试覆盖从基础能力扩展到工程集成：

- reader 路径安全。
- analyzer 分类和规则匹配。
- CLI 输出路径限制。
- MCP dispatcher 和 stdio 注册。
- UE 项目结构扫描。
- HotPatcher/LinkerSave、Packaging、Blueprint、Missing Asset 样例。

## 7. 文档

文档不是附属品，而是 AI 主导开发的证据链：

- PRD 说明目标。
- Technical Design 说明架构。
- MCP/Skill/Hook 文档说明 Agent 工程化。
- Test Report 说明可靠性。
- Retrospective 说明经验沉淀。
- Project Memory 方便团队同步。

## 8. 复盘

复盘关注：

- AI 做得好的地方。
- AI 生成内容不足。
- 人类 reviewer 应介入的位置。
- 面试如何讲清工程价值。

