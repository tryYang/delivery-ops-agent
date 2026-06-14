from __future__ import annotations

from delivery_ops.domain.features import FeatureDetail, FeaturePrdAnalysis

_PRD_CATALOG: dict[str, FeaturePrdAnalysis] = {
    "PRD-FEAT-001": FeaturePrdAnalysis(
        prd_id="PRD-FEAT-001",
        scope=["订单列表页增加导出配置", "CSV 列可勾选"],
        acceptance_criteria=["导出列与选择一致", "UTF-8 编码", "10万行 30s 内完成"],
        boundaries=["不修改订单核心状态机"],
        claims=["用户可保存导出模板"],
    ),
    "PRD-FEAT-002": FeaturePrdAnalysis(
        prd_id="PRD-FEAT-002",
        scope=["会员权益页", "三档等级展示"],
        acceptance_criteria=["权益与后台配置一致"],
        boundaries=["不涉及支付流程"],
        claims=["复用现有 TierCard 组件"],
    ),
    "PRD-FEAT-004": FeaturePrdAnalysis(
        prd_id="PRD-FEAT-004",
        scope=["收银台新增支付宝", "回调与对账"],
        acceptance_criteria=["支付成功率 >= 99%", "对账 T+1"],
        boundaries=["不改微信既有逻辑"],
        claims=["需支付平台审批"],
    ),
    "PRD-FEAT-005": FeaturePrdAnalysis(
        prd_id="PRD-FEAT-005",
        scope=["帮助中心搜索框", "搜索结果页"],
        acceptance_criteria=["搜索 P95 < 1s"],
        boundaries=["仅只读文档"],
        claims=["接入现有搜索服务"],
    ),
}


class FakeFeaturePrdReader:
    async def read_and_analyze(self, feature: FeatureDetail) -> FeaturePrdAnalysis | None:
        if feature.prd_id is None:
            return None
        return _PRD_CATALOG.get(feature.prd_id)
