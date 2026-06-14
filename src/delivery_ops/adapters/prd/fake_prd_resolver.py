from __future__ import annotations

from delivery_ops.domain.bugfix import BugDetail, PrdDocument, PrdRef

_PRD_CATALOG: dict[str, PrdDocument] = {
    "PRD-PAY-001": PrdDocument(
        prd_id="PRD-PAY-001",
        claims=[
            "支付成功后订单状态必须在 5 秒内更新为已支付。",
            "回调失败需重试最多 3 次。",
        ],
    ),
    "PRD-AUTH-002": PrdDocument(
        prd_id="PRD-AUTH-002",
        claims=["登录页必须展示图形验证码。", "验证码刷新后应立即可见。"],
    ),
    "PRD-PROFILE-001": PrdDocument(
        prd_id="PRD-PROFILE-001",
        claims=["支持 PNG/JPEG 头像上传，单文件不超过 5MB。"],
    ),
    "PRD-ORDER-003": PrdDocument(
        prd_id="PRD-ORDER-003",
        claims=["订单导出 CSV 使用 UTF-8 编码。"],
    ),
}


class FakePrdResolver:
    async def resolve(self, bug: BugDetail) -> tuple[PrdRef | None, PrdDocument | None]:
        if bug.prd_hint is None:
            return None, None
        document = _PRD_CATALOG.get(bug.prd_hint)
        if document is None:
            return None, None
        ref = PrdRef(
            prd_id=document.prd_id,
            title=f"PRD {document.prd_id}",
            url=f"https://docs.example.com/prd/{document.prd_id}",
            found_via="bug.prd_hint",
        )
        return ref, document
