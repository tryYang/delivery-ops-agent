from __future__ import annotations

from delivery_ops.domain.features import (
    DependencyMap,
    FeatureDetail,
    FeatureEvidencePacket,
    FeaturePriority,
    FeatureRiskAssessment,
    FeatureRiskLevel,
)

_HIGH_RISK_MODULES: frozenset[str] = frozenset({"payment", "auth", "order"})
_HIGH_KEYWORDS: tuple[str, ...] = ("支付", "权限", "schema", "跨系统")


class FeatureRiskPlanner:
    def assess(
        self,
        feature: FeatureDetail,
        packet: FeatureEvidencePacket,
        dependencies: DependencyMap,
    ) -> FeatureRiskAssessment:
        reasons: list[str] = []
        splits: list[str] = []
        level = FeatureRiskLevel.LOW

        if feature.module in _HIGH_RISK_MODULES:
            level = FeatureRiskLevel.HIGH
            reasons.append(f"module={feature.module} 属于高风险域")

        text_blob = f"{feature.title} {feature.description}".lower()
        for kw in _HIGH_KEYWORDS:
            if kw.lower() in text_blob or kw in (feature.dependencies_hint or ""):
                level = FeatureRiskLevel.HIGH
                reasons.append(f"命中高风险关键词或依赖 '{kw}'")

        blocking = [d for d in dependencies.items if d.blocking]
        if blocking:
            if level == FeatureRiskLevel.LOW:
                level = FeatureRiskLevel.MEDIUM
            reasons.append(f"{len(blocking)} 个 blocking 依赖未闭合")

        if packet.conflicts:
            level = FeatureRiskLevel.HIGH
            reasons.append("PRD/Figma 存在冲突")

        if packet.open_questions and level == FeatureRiskLevel.LOW:
            level = FeatureRiskLevel.MEDIUM
            reasons.append("存在 open_questions")

        if feature.priority == FeaturePriority.P0 and level == FeatureRiskLevel.LOW:
            level = FeatureRiskLevel.MEDIUM
            reasons.append("P0 需求需人工复核范围")

        auto_executable = level != FeatureRiskLevel.HIGH
        if not auto_executable:
            reasons.append("高风险：仅输出方案与拆分建议")
            splits.append("阶段1: API/权限对接")
            splits.append("阶段2: UI 与集成")
            splits.append("阶段3: 验收与回归")

        return FeatureRiskAssessment(
            level=level,
            reasons=reasons,
            suggested_splits=splits,
            auto_executable=auto_executable,
        )
