from __future__ import annotations

from delivery_ops.domain.bugfix import CodeHit
from delivery_ops.domain.features import (
    DependencyMap,
    DesignContext,
    FeatureDetail,
    FeatureEvidencePacket,
    FeaturePrdAnalysis,
)


class FeatureEvidenceBuilder:
    async def build(
        self,
        feature: FeatureDetail,
        prd: FeaturePrdAnalysis | None,
        design: DesignContext | None,
        code_hits: list[CodeHit],
        dependencies: DependencyMap,
    ) -> FeatureEvidencePacket:
        requirement_facts = [
            f"[{feature.feature_id}] {feature.title} (priority={feature.priority.value})",
            feature.description,
            f"Target release: {feature.target_release}, owner: {feature.owner}",
        ]
        if feature.acceptance_hint:
            requirement_facts.append(f"Acceptance hint: {feature.acceptance_hint}")

        prd_claims: list[str] = []
        open_questions: list[str] = []
        conflicts: list[str] = []

        if prd is not None:
            prd_claims = [f"PRD {prd.prd_id}: {c}" for c in prd.claims]
            prd_claims.extend(f"Scope: {s}" for s in prd.scope)
            prd_claims.extend(f"AC: {ac}" for ac in prd.acceptance_criteria)
        else:
            open_questions.append("未关联 PRD，验收标准不明确。")

        figma_claims: list[str] = []
        if design is not None:
            figma_claims = [
                f"Screens: {', '.join(design.screens)}",
                f"Components: {', '.join(design.components)}",
                f"States: {', '.join(design.states)}",
            ]
            if design.annotations:
                figma_claims.extend(f"Note: {a}" for a in design.annotations)
        elif feature.figma_url is None:
            open_questions.append("无 Figma 链接，UI 实现依据不足。")

        if prd is not None and design is not None and feature.module == "payment":
            conflicts.append("PRD 要求支付成功率指标，需与 Figma 收银台状态流转对齐验证。")

        code_facts = [
            f"{hit.path}::{hit.symbol} (L{hit.line_hint}) — {hit.reason}" for hit in code_hits
        ]
        if not code_facts:
            open_questions.append("未找到可复用代码，实现路径不确定。")

        dep_lines = [
            f"{item.kind}:{item.name} blocking={item.blocking} — {item.description}"
            for item in dependencies.items
        ]

        suggested_scope = [hit.path for hit in code_hits] or [f"src/{feature.module}/"]

        return FeatureEvidencePacket(
            feature_id=feature.feature_id,
            requirement_facts=requirement_facts,
            prd_claims=prd_claims,
            figma_claims=figma_claims,
            code_facts=code_facts,
            dependencies=dep_lines,
            conflicts=conflicts,
            open_questions=open_questions,
            suggested_scope=suggested_scope,
        )
