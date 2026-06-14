from __future__ import annotations

from delivery_ops.domain.bugfix import BugDetail, BugEvidencePacket, CodeHit, PrdDocument


class BugEvidenceBuilder:
    async def build(
        self,
        bug: BugDetail,
        prd: PrdDocument | None,
        code_hits: list[CodeHit],
    ) -> BugEvidencePacket:
        bug_facts = [
            f"[{bug.bug_id}] {bug.title} (severity={bug.severity.value})",
            bug.description,
            f"Reproduction: {bug.reproduction}",
        ]
        if bug.comments:
            bug_facts.append(f"Comments: {'; '.join(bug.comments)}")

        prd_claims: list[str] = []
        unknowns: list[str] = []
        conflicts: list[str] = []

        if prd is not None:
            prd_claims = [f"PRD {prd.prd_id}: {claim}" for claim in prd.claims]
        else:
            unknowns.append("未关联 PRD，无法确认预期行为。")

        code_facts = [
            f"{hit.path}::{hit.symbol} (L{hit.line_hint}) — {hit.reason}"
            for hit in code_hits
        ]
        if not code_facts:
            unknowns.append("未检索到相关代码，修复范围不确定。")

        # 样例冲突：支付模块且 PRD 要求 5 秒内更新，用于演示 conflicts 字段。
        if bug.module == "payment" and prd is not None:
            conflicts.append("PRD 要求 5 秒内更新订单，需核实回调重试是否覆盖所有失败路径。")

        suggested_scope = [hit.path for hit in code_hits] or [f"src/{bug.module}/"]

        return BugEvidencePacket(
            bug_id=bug.bug_id,
            bug_facts=bug_facts,
            prd_claims=prd_claims,
            code_facts=code_facts,
            conflicts=conflicts,
            unknowns=unknowns,
            suggested_scope=suggested_scope,
        )
