# Delivery Ops Architecture Skill

## Use When

Use this skill when designing or modifying Delivery Ops Agent architecture, workflow routing, adapters, task state, or executor boundaries.

## Core Decisions

- Bug Fix and Feature Development must be separate LangGraph subgraphs.
- Shared infrastructure is allowed only for adapters, storage, execution, reporting, and audit logs.
- Bug Fix and Feature Development must not share task state, evidence models, work order templates, risk policies, or acceptance gates.
- The core graph must depend on `IngressPort`, not Hermes, WeChat, DingTalk, Feishu, or any concrete gateway.
- Phase 1 entry is `DirectInvocationAdapter` plus `IngressPort`.
- `HermesAdapter` is a later message-channel adapter.
- `FutureGatewayAdapter` is only a placeholder until a real self-hosted gateway is justified.
- Cursor SDK and Claude Code are executors only. They must not decide whether the task passed.
- Quality Gate is the independent judge after execution.

## Required Architecture Shape

```text
DirectInvocationAdapter -> IngressPort -> IntentRouter -> WorkflowRouter
WorkflowRouter -> BugFixGraph | FeatureDevelopmentGraph
WorkOrder -> HumanApproval -> ExecutorRouter -> CursorOrClaude
ExecutionResult -> QualityGate -> CaseLibrary
```

## Implementation Rules

- Use Python `Protocol` for adapter boundaries.
- Keep platform-specific payloads out of domain models.
- Prefer explicit Pydantic models for state and external payload normalization.
- Keep async I/O behind adapters and service interfaces.
- Persist task snapshots and audit events before any long-running operation.
- Add human approval checkpoints before medium-risk execution.
- Never auto-execute high-risk tasks.

## Risk Boundaries

Bug Fix high-risk indicators:

- Auth, payment, order core state, database schema, or unclear PRD/Figma conflict.

Feature high-risk indicators:

- Cross-system process, permission model, payment/order state, database schema, or new architecture abstraction.

High-risk tasks should generate plans, decomposition, and open questions only.
