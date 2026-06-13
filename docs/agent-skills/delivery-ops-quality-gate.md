# Delivery Ops Quality Gate Skill

## Use When

Use this skill when designing or modifying execution verification, acceptance gates, quality reports, diff checks, or follow-up work orders.

## Core Rule

Executors do not judge their own work. Cursor SDK and Claude Code can produce code, diffs, logs, and test output. Quality Gate decides whether the task passed.

## Shared Checks

Every executed task must be checked for:

- lint/typecheck/test result.
- diff limited to allowed scope.
- forbidden files or modules not modified.
- acceptance criteria coverage.
- obvious regression risk.
- need for human review.

## Bug Verification Gate

Bug Fix verification must check:

- Original reproduction path no longer fails.
- Regression test exists or the missing-test reason is explicit.
- Behavior matches PRD, Figma, or historical expected behavior.
- The fix does not widen scope into unrelated modules.

## Feature Acceptance Gate

Feature acceptance must check:

- PRD acceptance criteria coverage.
- Figma screen/state coverage.
- API or data contract clarity.
- Open product questions captured.
- Required unit, component, integration, or E2E tests.
- Partial implementation clearly marked when dependencies are blocked.

## Status Values

Use only these quality statuses:

- `pass`: all required criteria are satisfied.
- `fail`: required criteria are not satisfied.
- `needs_human_review`: automated checks cannot confidently decide.
- `blocked`: verification cannot proceed because required inputs are missing.

## Quality Report

Required fields:

- `status`
- `failed_criteria`
- `scope_violations`
- `forbidden_changes`
- `changed_files`
- `test_summary`
- `review_notes`
- `follow_up_work_order`

## Follow-Up Rules

- Generate a follow-up work order when status is `fail`.
- Generate review notes when status is `needs_human_review`.
- Do not auto-execute follow-up work.
- Preserve all failed criteria for case library and evals.
