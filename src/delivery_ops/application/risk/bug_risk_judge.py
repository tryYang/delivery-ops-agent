from __future__ import annotations

from delivery_ops.domain.bugfix import (
    BugDetail,
    BugEvidencePacket,
    BugRiskAssessment,
    BugRiskLevel,
)

_HIGH_RISK_MODULES: frozenset[str] = frozenset({"payment", "auth", "order"})
_HIGH_RISK_KEYWORDS: tuple[str, ...] = ("schema", "数据库", "权限", "支付", "订单核心")


class BugRiskJudge:
    def assess(self, bug: BugDetail, packet: BugEvidencePacket) -> BugRiskAssessment:
        reasons: list[str] = []
        level = BugRiskLevel.LOW

        if bug.module in _HIGH_RISK_MODULES:
            level = BugRiskLevel.HIGH
            reasons.append(f"module={bug.module} 属于高风险域")

        title_and_desc = f"{bug.title} {bug.description}".lower()
        for keyword in _HIGH_RISK_KEYWORDS:
            if keyword.lower() in title_and_desc:
                level = BugRiskLevel.HIGH
                reasons.append(f"命中高风险关键词 '{keyword}'")

        if packet.conflicts:
            level = BugRiskLevel.HIGH
            reasons.append("证据包存在 PRD/代码冲突")

        if packet.unknowns and level == BugRiskLevel.LOW:
            level = BugRiskLevel.MEDIUM
            reasons.append("存在未决 unknowns，证据不完整")

        if bug.severity.value == "critical" and level == BugRiskLevel.LOW:
            level = BugRiskLevel.MEDIUM
            reasons.append("critical severity 需人工复核")

        auto_executable = level != BugRiskLevel.HIGH
        if not auto_executable:
            reasons.append("高风险：禁止自动执行，仅输出方案")

        return BugRiskAssessment(level=level, reasons=reasons, auto_executable=auto_executable)
