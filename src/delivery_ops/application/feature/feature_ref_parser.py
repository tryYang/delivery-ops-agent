from __future__ import annotations

import re

from delivery_ops.domain.features import FeatureSummary

_INDEX_PATTERN = re.compile(r"第\s*(\d+)\s*个")
_HASH_FEAT_PATTERN = re.compile(r"#(FEAT-[\w-]+)", re.IGNORECASE)
_PLAIN_FEAT_PATTERN = re.compile(r"\b(FEAT-[\w-]+)\b", re.IGNORECASE)


class FeatureRefParseError(ValueError):
    pass


class FeatureRefParser:
    def parse(self, text: str, ranked_features: list[FeatureSummary] | None) -> str:
        normalized = text.strip()
        index_match = _INDEX_PATTERN.search(normalized)
        if index_match is not None:
            return self._resolve_by_index(int(index_match.group(1)), ranked_features)

        hash_match = _HASH_FEAT_PATTERN.search(normalized)
        if hash_match is not None:
            return hash_match.group(1).upper()

        plain_match = _PLAIN_FEAT_PATTERN.search(normalized)
        if plain_match is not None:
            return plain_match.group(1).upper()

        msg = "无法从文本解析 Feature 引用，请使用 #FEAT-001 或「第 N 个」。"
        raise FeatureRefParseError(msg)

    @staticmethod
    def _resolve_by_index(index: int, ranked_features: list[FeatureSummary] | None) -> str:
        if ranked_features is None or not ranked_features:
            msg = "无可用排序列表，请先查询功能任务。"
            raise FeatureRefParseError(msg)
        if index < 1 or index > len(ranked_features):
            msg = f"序号 {index} 超出范围（1-{len(ranked_features)}）。"
            raise FeatureRefParseError(msg)
        return ranked_features[index - 1].feature_id
