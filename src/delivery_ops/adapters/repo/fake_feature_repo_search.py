from __future__ import annotations

from delivery_ops.domain.bugfix import CodeHit
from delivery_ops.domain.features import FeatureDetail

_MODULE_HITS: dict[str, list[CodeHit]] = {
    "order": [
        CodeHit(
            path="src/order/export.py",
            symbol="ExportService",
            line_hint=12,
            reason="现有导出服务可扩展",
        ),
        CodeHit(
            path="src/components/CheckboxGroup.vue",
            symbol="CheckboxGroup",
            line_hint=1,
            reason="列选择 UI 可复用",
        ),
    ],
    "membership": [
        CodeHit(
            path="src/membership/TierCard.vue",
            symbol="TierCard",
            line_hint=8,
            reason="等级卡片组件",
        ),
    ],
    "payment": [
        CodeHit(
            path="src/payment/channels/wechat.py",
            symbol="WechatChannel",
            line_hint=20,
            reason="支付渠道抽象",
        ),
    ],
    "notification": [
        CodeHit(
            path="src/notification/inbox.py",
            symbol="mark_all_read",
            line_hint=45,
            reason="消息列表批量操作入口",
        ),
    ],
    "cms": [
        CodeHit(
            path="src/cms/search.py",
            symbol="search_docs",
            line_hint=30,
            reason="文档搜索占位",
        ),
    ],
}


class FakeFeatureRepoSearch:
    async def search_reusable(self, feature: FeatureDetail) -> list[CodeHit]:
        return list(_MODULE_HITS.get(feature.module, []))
