from __future__ import annotations

from datetime import UTC, datetime, timedelta

from delivery_ops.domain.features import FeatureDetail, FeaturePriority

_SAMPLE_FEATURES: tuple[FeatureDetail, ...] = (
    FeatureDetail(
        feature_id="FEAT-001",
        title="订单导出支持自定义列",
        priority=FeaturePriority.P0,
        status="pending",
        target_release="2026-Q3",
        owner="pm-alice",
        module="order",
        updated_at=datetime.now(UTC) - timedelta(days=2),
        description="用户可选择导出 CSV 列字段。",
        acceptance_hint="导出文件包含所选列且编码 UTF-8",
        prd_id="PRD-FEAT-001",
        figma_url="https://figma.example.com/feat-001",
        dependencies_hint="订单 API、导出服务",
    ),
    FeatureDetail(
        feature_id="FEAT-002",
        title="会员等级权益页",
        priority=FeaturePriority.P1,
        status="pending",
        target_release="2026-Q3",
        owner="pm-bob",
        module="membership",
        updated_at=datetime.now(UTC) - timedelta(days=5),
        description="展示会员等级与权益说明。",
        acceptance_hint="三档会员权益展示完整",
        prd_id="PRD-FEAT-002",
        figma_url="https://figma.example.com/feat-002",
        dependencies_hint="会员中心 API",
    ),
    FeatureDetail(
        feature_id="FEAT-003",
        title="消息中心批量已读",
        priority=FeaturePriority.P1,
        status="pending",
        target_release="2026-Q4",
        owner="pm-carol",
        module="notification",
        updated_at=datetime.now(UTC) - timedelta(days=8),
        description="支持一键标记全部已读。",
        acceptance_hint=None,
        prd_id=None,
        figma_url=None,
        dependencies_hint="消息列表 API",
    ),
    FeatureDetail(
        feature_id="FEAT-004",
        title="支付渠道扩展-支付宝",
        priority=FeaturePriority.P0,
        status="pending",
        target_release="2026-Q3",
        owner="pm-alice",
        module="payment",
        updated_at=datetime.now(UTC) - timedelta(days=1),
        description="新增支付宝支付渠道。",
        acceptance_hint="支付成功率与微信持平",
        prd_id="PRD-FEAT-004",
        figma_url="https://figma.example.com/feat-004",
        dependencies_hint="支付网关、权限系统",
    ),
    FeatureDetail(
        feature_id="FEAT-005",
        title="帮助中心搜索",
        priority=FeaturePriority.P2,
        status="pending",
        target_release="2026-Q4",
        owner="pm-bob",
        module="cms",
        updated_at=datetime.now(UTC) - timedelta(days=15),
        description="帮助文档全文搜索。",
        acceptance_hint="搜索响应 < 1s",
        prd_id="PRD-FEAT-005",
        figma_url=None,
        dependencies_hint="搜索索引服务",
    ),
)


class FakeRequirementSourceAdapter:
    async def list_pending_features(self) -> list[FeatureDetail]:
        return [FeatureDetail.model_validate(f.model_dump()) for f in _SAMPLE_FEATURES]

    async def get_feature_detail(self, feature_id: str) -> FeatureDetail | None:
        for feature in _SAMPLE_FEATURES:
            if feature.feature_id == feature_id:
                return feature
        return None
