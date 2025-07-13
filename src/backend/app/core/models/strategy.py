from typing import List, Optional
from .rule import Rule
from .wafer_map import WaferMap
from ..vendor.base import VendorMapping

class GenericStrategy:
    def __init__(self, name: str, rules: List[Rule], mapping: Optional[VendorMapping] = None):
        self.name = name
        self.rules = rules
        self.mapping = mapping

    def apply(self, wafer_map: WaferMap):
        selected = []
        for rule in self.rules:
            selected.extend(rule.apply(wafer_map))
        if self.mapping:
            selected = self.mapping.transform(selected)
        return selected
