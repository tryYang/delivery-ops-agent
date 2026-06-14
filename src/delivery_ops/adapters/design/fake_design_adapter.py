from __future__ import annotations

from delivery_ops.domain.features import DesignContext, DesignRef, FeatureDetail

_DESIGN_CONTEXTS: dict[str, DesignContext] = {
    "FEAT-001": DesignContext(
        screens=["OrderExportModal", "ColumnPicker"],
        components=["ExportButton", "CheckboxGroup"],
        states=["default", "loading", "success"],
        annotations=["列选择最多 20 项"],
    ),
    "FEAT-002": DesignContext(
        screens=["MembershipBenefitsPage"],
        components=["TierCard", "BenefitList"],
        states=["guest", "silver", "gold"],
        annotations=["移动端与 Web 双端"],
    ),
    "FEAT-004": DesignContext(
        screens=["PaymentMethodSelector"],
        components=["AlipayOption"],
        states=["selected", "disabled"],
        annotations=["与微信支付互斥选择"],
    ),
}


class FakeDesignAdapter:
    async def resolve_design(self, feature: FeatureDetail) -> DesignRef | None:
        if feature.figma_url is None:
            return None
        return DesignRef(
            file_key=f"file-{feature.feature_id}",
            node_id=f"node-{feature.feature_id}",
            title=f"Design for {feature.title}",
            url=feature.figma_url,
        )

    async def read_design_context(self, design_ref: DesignRef) -> DesignContext:
        feature_id = design_ref.file_key.removeprefix("file-")
        return _DESIGN_CONTEXTS.get(
            feature_id,
            DesignContext(
                screens=["PlaceholderScreen"],
                components=[],
                states=["default"],
                annotations=[],
            ),
        )
