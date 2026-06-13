---
name: delivery-ops-architecture
description: Applies Delivery Ops Agent architecture rules. Use when designing or modifying workflow routing, LangGraph subgraphs, adapters, task state, ingress strategy, executor boundaries, or risk policies.
---

# Delivery Ops Architecture

Read `docs/agent-skills/delivery-ops-architecture.md` before making architecture, workflow, adapter, executor, or risk-policy changes.

Key constraints:

- Keep Bug Fix and Feature Development as separate graphs.
- Use `DirectInvocationAdapter` and `IngressPort` for the first implementation.
- Treat Hermes as a later adapter and Gateway as a placeholder.
- Treat Cursor SDK and Claude Code as executors only.
- Let Quality Gate judge execution results.
