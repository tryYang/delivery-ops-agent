# Delivery Ops Work Order Skill

## Use When

Use this skill when generating or modifying Bug Evidence Packets, Feature Evidence Packets, Fix Work Orders, or Feature Work Orders.

## General Rules

- Build evidence before writing a work order.
- Evidence must separate facts, claims, conflicts, unknowns, and suggested scope.
- Do not hide unresolved product or design questions.
- Work orders must be executable by Cursor SDK or Claude Code without relying on hidden chat context.
- Work orders must include allowed scope and forbidden changes.
- Bug Fix and Feature Development use different templates.

## Bug Evidence Packet

Required sections:

- `Bug Facts`: source bug details, severity, reproduction, impact.
- `PRD Claims`: expected behavior from PRD or product docs.
- `Design Claims`: expected UI states from Figma when available.
- `Code Facts`: relevant files, functions, API calls, recent commits.
- `Conflicts`: PRD/Figma/code contradictions.
- `Unknowns`: missing facts that block confident execution.
- `Suggested Scope`: files or modules likely safe to inspect or change.

## Feature Evidence Packet

Required sections:

- `Requirement Facts`: requirement source, priority, target release, owner.
- `PRD Claims`: scope, acceptance criteria, boundaries, dependencies.
- `Figma Claims`: screens, states, components, annotations.
- `Code Facts`: reusable components, services, routes, tests.
- `Dependencies`: APIs, permissions, data contracts, cross-system dependencies.
- `Conflicts`: PRD/Figma/code contradictions.
- `Open Questions`: product or technical questions.
- `Suggested Scope`: modules likely safe to extend.

## Fix Work Order

Required sections:

- `Objective`
- `Evidence`
- `Allowed Scope`
- `Required Changes`
- `Acceptance Criteria`
- `Forbidden`
- `Risk Level`
- `Verification Notes`

Rules:

- Keep the diff focused on restoring expected behavior.
- Prefer regression tests that reproduce the bug.
- Do not include unrelated refactors.

## Feature Work Order

Required sections:

- `Objective`
- `Requirement Scope`
- `Design Scope`
- `Existing Code To Reuse`
- `Required Changes`
- `Acceptance Criteria`
- `Open Questions`
- `Forbidden`
- `Risk Level`

Rules:

- Reuse existing components and service patterns.
- Do not expand scope beyond PRD/Figma without marking an open question.
- If a dependency is missing, generate a blocked or partial work order instead of guessing.

## Output Constraints

- Use concrete file paths when known.
- Mark missing PRD/Figma/code context explicitly.
- Keep high-risk tasks as plans and decomposition only.
- Do not ask executors to modify auth, payment, order core state, database schema, or permissions unless explicitly allowed.
