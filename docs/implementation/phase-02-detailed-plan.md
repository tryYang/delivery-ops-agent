# Phase 2 详细实施计划

本文档是 Phase 2 编码前的详细实施计划。阶段概览见 [phase-02-bugfix-readonly-mvp.md](phase-02-bugfix-readonly-mvp.md)，目录设计见 [project-structure.md](../architecture/project-structure.md)。

## Scope

### 本阶段做什么

- 扩展 Bug Fix 领域模型与端口（`domain/bugfix.py`、`domain/ports.py`）。
- Fake Adapter：`bug_sources`、`prd`、`repo`。
- Application 服务：排序、证据构建、风险判断、工单编译。
- 替换 `graphs/bugfix/graph.py` 占位为 Python 编排器 + `BugFixState`。
- 扩展 `AgentReport` / `ReportPublisher` 输出结构化 Bug Fix 产物。
- 任务上下文：支持「分析第 N 个 bug」关联上一轮 Top 列表。
- 单元测试、契约测试、Bug Fix 只读集成测试。

### 本阶段不做什么

- 不引入 LangGraph runtime / checkpoint。
- 不接入真实 TAPD/Jira/PRD/Repo 平台。
- 不调用 Cursor SDK / Claude Code。
- 不修改代码、不创建分支/worktree。
- 不实现 Quality Gate、Hermes、FastAPI。
- 不扩展 Feature Graph（保持 Phase 1 占位）。

## Target Flow

```text
DirectInvocationAdapter
  -> IngressService
    -> IntentRouter -> WorkflowRouter
    -> BugFixGraph.run(intent, message)
         -> BugSourceAdapter / Ranker / Prd / Repo / Evidence / Risk / Compiler
    -> TaskStore + BugFixSession
    -> ReportPublisher (含 bugfix artifacts)
  -> AgentReport
```

## Target Directory

见 [phase-02-bugfix-readonly-mvp.md](phase-02-bugfix-readonly-mvp.md) 与 project-structure Phase 2 扩展节。

## Implementation Steps

1. 领域模型与 `AgentReport` 扩展。
2. Fake Adapters（Bug / PRD / Repo）。
3. `BugSeverityRanker`。
4. `BugRefParser` + `InMemoryBugFixSession`。
5. `BugEvidenceBuilder`。
6. `BugRiskJudge`。
7. `FixWorkOrderCompiler`。
8. `BugFixGraph` 编排器 + `BugFixState`。
9. `IngressService` / `ReportPublisher` / `conftest` 集成。
10. 测试与 `pytest -v` 验收。

## Acceptance Checklist

- [x] `domain/bugfix.py` 与端口扩展完成。
- [x] Fake Bug/PRD/Repo adapter 可用。
- [x] Top 3 严重 Bug 列表可返回。
- [x] 指定 Bug 可生成 `BugEvidencePacket`（含 unknowns/conflicts）。
- [x] 可输出 `FixWorkOrder` 八段结构。
- [x] 风险等级 `low/medium/high` 可判定。
- [x] 不产生任何代码修改。
- [x] Phase 1 测试仍通过。
- [x] Bug Fix 只读集成测试通过。

## Next Phase Handoff

Phase 3 复用 PRD/Repo 搜索与 Work Order 模式，为 Feature 新建独立模型与 `FeatureGraph`，不共享 Bug Fix 状态。
