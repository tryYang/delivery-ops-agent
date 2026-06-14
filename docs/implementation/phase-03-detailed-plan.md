# Phase 3 详细实施计划

本文档是 Phase 3 编码前的详细实施计划。阶段概览见 [phase-03-feature-readonly-mvp.md](phase-03-feature-readonly-mvp.md)，目录设计见 [project-structure.md](../architecture/project-structure.md)。

## Scope

### 本阶段做什么

- 新增 `domain/features.py` 与端口扩展。
- Fake Adapter：requirements、design、feature PRD/Repo 读路径。
- Application 服务：排序、PRD/设计、依赖、证据、风险、工单编译。
- 替换 `graphs/feature/graph.py` 为 Python 编排器 + `FeatureState`。
- 扩展 `AgentReport.feature`；`InMemoryFeatureSession`。
- 修正 `IntentRouter` Feature/Bug 分析意图冲突。
- 单元、契约、集成测试。

### 本阶段不做什么

- LangGraph、真实平台、执行器、代码修改、Quality Gate、Hermes、FastAPI。
- 不修改 Bug Fix 链路。

## Target Flow

```text
DirectInvocationAdapter -> IngressService -> FeatureGraph.run()
  -> RequirementAdapter / Ranker / PRD / Design / Repo / Evidence / Risk / Compiler
  -> TaskStore + FeatureSession -> ReportPublisher -> AgentReport
```

## Implementation Steps

1. 领域模型与 `AgentReport` 扩展。
2. Fake Adapters。
3. `FeatureReadinessRanker`。
4. `FeatureRefParser` + `InMemoryFeatureSession`。
5. PRD/Design/Dependency 服务。
6. `FeatureEvidenceBuilder`。
7. `FeatureRiskPlanner`。
8. `FeatureWorkOrderCompiler`。
9. `FeatureGraph` + `FeatureState`。
10. Ingress / Report / IntentRouter / wiring。
11. 测试与 `pytest -v`。

## Acceptance Checklist

- [x] `domain/features.py` 与端口扩展完成
- [x] Fake Requirement/Design/PRD/Repo adapter 可用
- [x] Top 待开发需求可列出
- [x] `FeatureEvidencePacket` 可生成
- [x] `FeatureWorkOrder` 可输出
- [x] 风险等级与拆分建议可输出
- [x] Phase 1/2 测试仍通过
- [x] Feature 只读集成测试通过

## Next Phase Handoff

Phase 4 复用 Feature/Fix Work Order，接入执行器与人工审批。
