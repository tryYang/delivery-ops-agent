from __future__ import annotations

from delivery_ops.domain.features import FeatureDetail, FeaturePrdAnalysis
from delivery_ops.domain.ports import FeaturePrdReaderPort


class FeaturePrdAnalyzer:
    def __init__(self, reader: FeaturePrdReaderPort) -> None:
        self._reader = reader

    async def analyze(self, feature: FeatureDetail) -> FeaturePrdAnalysis | None:
        return await self._reader.read_and_analyze(feature)
