from __future__ import annotations

from delivery_ops.domain.features import (
    FeatureEvidencePacket,
    FeatureRiskAssessment,
    FeatureRiskLevel,
    FeatureWorkOrder,
)


class FeatureWorkOrderCompiler:
    async def compile(
        self,
        packet: FeatureEvidencePacket,
        risk: FeatureRiskAssessment,
    ) -> FeatureWorkOrder:
        open_questions = list(packet.open_questions)
        required_changes = [
            f"实现 {packet.feature_id} 需求范围内功能。",
            "复用 existing_code_to_reuse 中组件与服务。",
        ]
        forbidden = ["无关重构", "超出 PRD/Figma 范围", "修改核心支付状态机"]
        if risk.level == FeatureRiskLevel.HIGH:
            forbidden.append("自动执行开发（高风险仅出方案）")
            required_changes = [
                "输出分阶段实施方案，等待人工审批。",
                *required_changes,
            ]

        return FeatureWorkOrder(
            objective=f"开发功能 {packet.feature_id}",
            requirement_scope=packet.prd_claims or packet.requirement_facts[:2],
            design_scope=packet.figma_claims,
            existing_code_to_reuse=packet.code_facts,
            required_changes=required_changes,
            acceptance_criteria=packet.prd_claims[-3:] if packet.prd_claims else ["满足需求验收标准"],
            open_questions=open_questions,
            forbidden=forbidden,
            risk_level=risk.level,
        )
