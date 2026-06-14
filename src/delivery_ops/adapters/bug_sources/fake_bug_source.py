from __future__ import annotations

from datetime import UTC, datetime, timedelta

from delivery_ops.domain.bugfix import BugDetail, BugSeverity, BugSummary


def _days_ago(days: int) -> datetime:
    return datetime.now(UTC) - timedelta(days=days)


# 固定样例：覆盖 severity、PRD hint、module 组合，供契约与集成测试复现。
_SAMPLE_BUGS: tuple[BugDetail, ...] = (
    BugDetail(
        bug_id="BUG-001",
        title="支付回调失败导致订单状态未更新",
        severity=BugSeverity.CRITICAL,
        status="open",
        module="payment",
        updated_at=_days_ago(1),
        description="用户支付成功后订单仍显示待支付。",
        reproduction="1. 下单 2. 微信支付 3. 查看订单列表",
        comments=["影响生产环境", "需优先处理"],
        prd_hint="PRD-PAY-001",
    ),
    BugDetail(
        bug_id="BUG-002",
        title="登录页验证码偶发不显示",
        severity=BugSeverity.HIGH,
        status="open",
        module="auth",
        updated_at=_days_ago(3),
        description="刷新页面后验证码图片空白。",
        reproduction="多次刷新登录页",
        comments=[],
        prd_hint="PRD-AUTH-002",
    ),
    BugDetail(
        bug_id="BUG-003",
        title="商品列表分页参数错误",
        severity=BugSeverity.HIGH,
        status="open",
        module="catalog",
        updated_at=_days_ago(5),
        description="第二页返回重复数据。",
        reproduction="访问商品列表第2页",
        comments=["仅 staging 复现"],
        prd_hint=None,
    ),
    BugDetail(
        bug_id="BUG-004",
        title="用户头像上传格式校验过严",
        severity=BugSeverity.MEDIUM,
        status="open",
        module="profile",
        updated_at=_days_ago(10),
        description="合法 PNG 被拒绝。",
        reproduction="上传 2MB PNG 头像",
        comments=[],
        prd_hint="PRD-PROFILE-001",
    ),
    BugDetail(
        bug_id="BUG-005",
        title="帮助中心链接404",
        severity=BugSeverity.LOW,
        status="open",
        module="cms",
        updated_at=_days_ago(20),
        description="页脚帮助链接失效。",
        reproduction="点击页脚帮助中心",
        comments=[],
        prd_hint=None,
    ),
    BugDetail(
        bug_id="BUG-006",
        title="订单导出 CSV 中文乱码",
        severity=BugSeverity.MEDIUM,
        status="open",
        module="order",
        updated_at=_days_ago(7),
        description="导出文件编码非 UTF-8。",
        reproduction="导出订单 CSV",
        comments=[],
        prd_hint="PRD-ORDER-003",
    ),
)


class FakeBugSourceAdapter:
    async def list_open_bugs(self) -> list[BugSummary]:
        return [BugSummary.model_validate(b.model_dump()) for b in _SAMPLE_BUGS]

    async def get_bug_detail(self, bug_id: str) -> BugDetail | None:
        for bug in _SAMPLE_BUGS:
            if bug.bug_id == bug_id:
                return bug
        return None
