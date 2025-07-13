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
    
    def parse_file(self, content: str, filename: str) -> GenericStrategy:
        """Parse strategy from file using format registry."""
        from ..parsers.format_parsers import format_registry
        result = format_registry.parse_strategy(content, filename)
        if not result.success:
            raise ValueError(f"Parsing failed: {', '.join(result.errors)}")
        return self.convert_definition_to_generic(result.data)
    
    def convert_definition_to_generic(self, definition) -> GenericStrategy:
        """Convert StrategyDefinition to GenericStrategy."""
        # Convert StrategyDefinition rules to legacy format
        config = {
            "name": definition.name,
            "tool_model": definition.target_vendor,
            "rules": [
                {
                    "type": "FixedPoint" if rule.rule_type == "fixed_point" else rule.rule_type,
                    "points": rule.parameters.get("points", [])
                }
                for rule in definition.rules
            ]
        }
        return self.parse(config)
