from __future__ import annotations

from delivery_ops.domain.features import (
    DependencyItem,
    DependencyMap,
    DesignContext,
    FeatureDetail,
    FeaturePrdAnalysis,
)


class DependencyMapper:
    def map(
        self,
        feature: FeatureDetail,
        prd: FeaturePrdAnalysis | None,
        design: DesignContext | None,
    ) -> DependencyMap:
        items: list[DependencyItem] = []

        if feature.dependencies_hint:
            for part in feature.dependencies_hint.split("、"):
                part = part.strip()
                if part:
                    items.append(
                        DependencyItem(
                            kind="integration",
                            name=part,
                            description=f"需求声明依赖: {part}",
                            blocking=False,
                        )
                    )

        if prd is not None:
            for boundary in prd.boundaries:
                if "支付" in boundary or "权限" in boundary:
                    items.append(
                        DependencyItem(
                            kind="constraint",
                            name=boundary,
                            description="PRD 边界约束",
                            blocking=True,
                        )
                    )

        if design is None and feature.figma_url:
            items.append(
                DependencyItem(
                    kind="design",
                    name="figma_missing",
                    description="Figma URL 存在但设计上下文未加载",
                    blocking=True,
                )
            )

        if feature.module == "payment":
            items.append(
                DependencyItem(
                    kind="permission",
                    name="payment_gateway",
                    description="支付网关接入与审批",
                    blocking=True,
                )
            )

        return DependencyMap(items=items)
