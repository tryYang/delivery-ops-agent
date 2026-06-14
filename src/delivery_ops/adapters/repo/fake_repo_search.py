from __future__ import annotations

from delivery_ops.domain.bugfix import BugDetail, CodeHit

_MODULE_HITS: dict[str, list[CodeHit]] = {
    "payment": [
        CodeHit(
            path="src/payment/callback_handler.py",
            symbol="handle_wechat_callback",
            line_hint=42,
            reason="支付回调处理入口",
        ),
        CodeHit(
            path="src/order/status_updater.py",
            symbol="mark_paid",
            line_hint=18,
            reason="订单状态更新",
        ),
    ],
    "auth": [
        CodeHit(
            path="src/auth/captcha.py",
            symbol="render_captcha",
            line_hint=27,
            reason="验证码渲染",
        ),
    ],
    "catalog": [
        CodeHit(
            path="src/catalog/pagination.py",
            symbol="paginate_products",
            line_hint=55,
            reason="商品分页",
        ),
    ],
    "profile": [
        CodeHit(
            path="src/profile/avatar_upload.py",
            symbol="validate_image",
            line_hint=12,
            reason="头像格式校验",
        ),
    ],
    "order": [
        CodeHit(
            path="src/order/export.py",
            symbol="export_csv",
            line_hint=88,
            reason="订单 CSV 导出",
        ),
    ],
    "cms": [
        CodeHit(
            path="src/cms/footer_links.py",
            symbol="help_center_url",
            line_hint=9,
            reason="帮助中心链接配置",
        ),
    ],
}


class FakeRepoSearch:
    async def search(self, bug: BugDetail) -> list[CodeHit]:
        hits = list(_MODULE_HITS.get(bug.module, []))
        if "支付" in bug.title or "payment" in bug.module:
            return hits
        return hits
