from __future__ import annotations

import re

from delivery_ops.domain.bugfix import BugSummary

_INDEX_PATTERN = re.compile(r"第\s*(\d+)\s*个")
_HASH_BUG_PATTERN = re.compile(r"#(BUG-[\w-]+)", re.IGNORECASE)
_PLAIN_BUG_PATTERN = re.compile(r"\b(BUG-[\w-]+)\b", re.IGNORECASE)


class BugRefParseError(ValueError):
    pass


class BugRefParser:
    def parse(self, text: str, ranked_bugs: list[BugSummary] | None) -> str:
        normalized = text.strip()
        index_match = _INDEX_PATTERN.search(normalized)
        if index_match is not None:
            return self._resolve_by_index(int(index_match.group(1)), ranked_bugs)

        hash_match = _HASH_BUG_PATTERN.search(normalized)
        if hash_match is not None:
            return hash_match.group(1).upper()

        plain_match = _PLAIN_BUG_PATTERN.search(normalized)
        if plain_match is not None:
            return plain_match.group(1).upper()

        msg = "无法从文本解析 Bug 引用，请使用 #BUG-001 或「第 N 个」。"
        raise BugRefParseError(msg)

    @staticmethod
    def _resolve_by_index(index: int, ranked_bugs: list[BugSummary] | None) -> str:
        if ranked_bugs is None or not ranked_bugs:
            msg = "无可用排序列表，请先查询严重 Bug。"
            raise BugRefParseError(msg)
        if index < 1 or index > len(ranked_bugs):
            msg = f"序号 {index} 超出范围（1-{len(ranked_bugs)}）。"
            raise BugRefParseError(msg)
        return ranked_bugs[index - 1].bug_id
