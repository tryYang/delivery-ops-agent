from __future__ import annotations

from delivery_ops.domain.features import DesignContext, FeatureDetail
from delivery_ops.domain.ports import DesignAdapter


class DesignContextService:
    def __init__(self, design_adapter: DesignAdapter) -> None:
        self._design_adapter = design_adapter

    async def load(self, feature: FeatureDetail) -> DesignContext | None:
        design_ref = await self._design_adapter.resolve_design(feature)
        if design_ref is None:
            return None
        return await self._design_adapter.read_design_context(design_ref)
