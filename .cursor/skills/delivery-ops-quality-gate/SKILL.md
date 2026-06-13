---
name: delivery-ops-quality-gate
description: Applies Delivery Ops independent verification rules. Use when designing or modifying quality gates, verification reports, diff scope checks, acceptance checks, or follow-up work orders.
---

# Delivery Ops Quality Gate

Read `docs/agent-skills/delivery-ops-quality-gate.md` before designing or modifying verification, acceptance, or quality-report logic.

Key constraints:

- Executors must not judge their own work.
- Bug Fix uses Bug Verification Gate.
- Feature Development uses Feature Acceptance Gate.
- Check diff scope, forbidden changes, tests, and acceptance criteria.
- Use only `pass`, `fail`, `needs_human_review`, or `blocked`.
