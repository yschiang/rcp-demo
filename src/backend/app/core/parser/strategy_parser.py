from typing import Dict
from ..models.rule import FixedPointRule
from ..models.strategy import GenericStrategy
from ..vendor.asml import ASMLMapping
from ..vendor.kla import KLAMapping

class StrategyParser:
    def __init__(self):
        self.plugin_registry: Dict[str, object] = {
            "ASML": ASMLMapping(),
            "KLA": KLAMapping()
        }

    def parse(self, config: dict) -> GenericStrategy:
        rule_objs = []
        for rule_cfg in config["rules"]:
            if rule_cfg["type"] == "FixedPoint":
                rule_objs.append(FixedPointRule(rule_cfg["points"]))

        mapping = self.plugin_registry.get(config.get("tool_model"))
        return GenericStrategy(config["name"], rule_objs, mapping)
