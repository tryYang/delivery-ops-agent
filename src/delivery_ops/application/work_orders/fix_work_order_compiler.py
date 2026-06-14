from __future__ import annotations

from delivery_ops.domain.bugfix import BugEvidencePacket, BugRiskAssessment, BugRiskLevel, FixWorkOrder


class FixWorkOrderCompiler:
    async def compile(
        self,
        packet: BugEvidencePacket,
        risk: BugRiskAssessment,
    ) -> FixWorkOrder:
        evidence_text = "\n".join(
            [
                "## Bug Facts",
                *packet.bug_facts,
                "## PRD Claims",
                *(packet.prd_claims or ["(none)"]),
                "## Code Facts",
                *(packet.code_facts or ["(none)"]),
                "## Conflicts",
                *(packet.conflicts or ["(none)"]),
                "## Unknowns",
                *(packet.unknowns or ["(none)"]),
            ]
        )

        forbidden = ["无关重构", "修改数据库 schema", "扩大 diff 范围"]
        if risk.level == BugRiskLevel.HIGH:
            forbidden.append("自动执行修复（高风险仅出方案）")

        required_changes = [
            f"修复 {packet.bug_id} 根因，恢复 PRD 声明的预期行为。",
            "补充或更新回归测试覆盖复现路径。",
        ]
        if risk.level == BugRiskLevel.HIGH:
            required_changes = [
                "输出修复方案与影响分析，等待人工审批后再执行。",
                *required_changes,
            ]

        return FixWorkOrder(
            objective=f"修复 Bug {packet.bug_id}",
            evidence=evidence_text,
            allowed_scope=packet.suggested_scope,
            required_changes=required_changes,
            acceptance_criteria=[
                "复现步骤不再触发缺陷。",
                "相关单元/集成测试通过。",
                "diff 限定在 allowed_scope 内。",
            ],
            forbidden=forbidden,
            risk_level=risk.level,
            verification_notes=[
                f"Risk: {risk.level.value} — {'; '.join(risk.reasons)}",
                "执行后须经 Quality Gate 独立验收（Phase 5）。",
            ],
        )
