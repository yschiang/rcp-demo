"""
Rule Plugin System - Pluggable sampling rules.
"""
from typing import Dict, List, Any
from abc import abstractmethod
import logging

from .registry import Plugin, PluginMetadata, register_plugin
from ..strategy.compilation import ExecutableRule, ExecutionContext
from ..models.die import Die
from ..models.wafer_map import WaferMap

logger = logging.getLogger(__name__)


class RulePlugin(Plugin, ExecutableRule):
    """Base class for rule plugins."""
    
    def __init__(self):
        self._config: Dict[str, Any] = {}
        self._initialized = False
    
    def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize rule with configuration."""
        self._config = config
        self._initialized = True
        return True
    
    def cleanup(self) -> None:
        """Cleanup rule resources."""
        self._initialized = False
    
    @abstractmethod
    def apply(self, wafer_map: WaferMap, context: ExecutionContext) -> List[Die]:
        """Apply rule to wafer map with context."""
        pass
    
    def estimate_performance(self, wafer_map: WaferMap) -> Dict[str, Any]:
        """Estimate execution performance."""
        return {
            "estimated_time_ms": len(wafer_map.dies) * 0.1,
            "memory_usage": "low",
            "complexity": "O(n)"
        }


@register_plugin("rule", "fixed_point")
class FixedPointRulePlugin(RulePlugin):
    """Fixed point sampling rule plugin."""
    
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="FixedPointRule",
            version="1.0.0",
            description="Selects dies at specific fixed coordinates",
            author="System",
            plugin_type="rule",
            dependencies=[]
        )
    
    def apply(self, wafer_map: WaferMap, context: ExecutionContext) -> List[Die]:
        """Apply fixed point rule."""
        if not self._initialized:
            logger.error("Rule not initialized")
            return []
        
        points = self._config.get("points", [])
        if not points:
            logger.warning("No points specified for FixedPointRule")
            return []
        
        selected = []
        for die in wafer_map.dies:
            if (die.x, die.y) in points and die.available:
                selected.append(die)
        
        logger.debug(f"FixedPointRule selected {len(selected)} dies")
        return selected


@register_plugin("rule", "center_edge")
class CenterEdgeRulePlugin(RulePlugin):
    """Center-edge sampling rule plugin."""
    
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="CenterEdgeRule",
            version="1.0.0",
            description="Selects dies at center and edge positions",
            author="System",
            plugin_type="rule",
            dependencies=[]
        )
    
    def apply(self, wafer_map: WaferMap, context: ExecutionContext) -> List[Die]:
        """Apply center-edge rule."""
        if not self._initialized:
            return []
        
        center_count = self._config.get("center_count", 1)
        edge_count = self._config.get("edge_count", 4)
        edge_margin = self._config.get("edge_margin", 1)
        
        if not wafer_map.dies:
            return []
        
        # Calculate wafer bounds
        x_coords = [die.x for die in wafer_map.dies]
        y_coords = [die.y for die in wafer_map.dies]
        min_x, max_x = min(x_coords), max(x_coords)
        min_y, max_y = min(y_coords), max(y_coords)
        
        selected = []
        
        # Select center dies
        center_x = (min_x + max_x) // 2
        center_y = (min_y + max_y) // 2
        
        center_candidates = [
            die for die in wafer_map.dies 
            if abs(die.x - center_x) <= 1 and abs(die.y - center_y) <= 1 and die.available
        ]
        selected.extend(center_candidates[:center_count])
        
        # Select edge dies
        edge_candidates = [
            die for die in wafer_map.dies
            if (die.x <= min_x + edge_margin or die.x >= max_x - edge_margin or
                die.y <= min_y + edge_margin or die.y >= max_y - edge_margin) and die.available
        ]
        
        # Remove any that were already selected as center
        edge_candidates = [die for die in edge_candidates if die not in selected]
        selected.extend(edge_candidates[:edge_count])
        
        logger.debug(f"CenterEdgeRule selected {len(selected)} dies")
        return selected


@register_plugin("rule", "uniform_grid")
class UniformGridRulePlugin(RulePlugin):
    """Uniform grid sampling rule plugin."""
    
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="UniformGridRule",
            version="1.0.0",
            description="Selects dies in a uniform grid pattern",
            author="System",
            plugin_type="rule",
            dependencies=[]
        )
    
    def apply(self, wafer_map: WaferMap, context: ExecutionContext) -> List[Die]:
        """Apply uniform grid rule."""
        if not self._initialized:
            return []
        
        spacing_x = self._config.get("spacing_x", 2)
        spacing_y = self._config.get("spacing_y", 2)
        offset_x = self._config.get("offset_x", 0)
        offset_y = self._config.get("offset_y", 0)
        
        if not wafer_map.dies:
            return []
        
        # Calculate starting position
        x_coords = [die.x for die in wafer_map.dies]
        y_coords = [die.y for die in wafer_map.dies]
        min_x, min_y = min(x_coords), min(y_coords)
        
        start_x = min_x + offset_x
        start_y = min_y + offset_y
        
        selected = []
        for die in wafer_map.dies:
            if (die.available and 
                (die.x - start_x) % spacing_x == 0 and 
                (die.y - start_y) % spacing_y == 0):
                selected.append(die)
        
        logger.debug(f"UniformGridRule selected {len(selected)} dies")
        return selected


@register_plugin("rule", "random_sampling")
class RandomSamplingRulePlugin(RulePlugin):
    """Random sampling rule plugin."""
    
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="RandomSamplingRule",
            version="1.0.0",
            description="Randomly selects dies from available dies",
            author="System",
            plugin_type="rule",
            dependencies=[]
        )
    
    def apply(self, wafer_map: WaferMap, context: ExecutionContext) -> List[Die]:
        """Apply random sampling rule."""
        if not self._initialized:
            return []
        
        import random
        
        sample_count = self._config.get("sample_count", 10)
        seed = self._config.get("seed")
        
        if seed is not None:
            random.seed(seed)
        
        available_dies = [die for die in wafer_map.dies if die.available]
        
        if len(available_dies) <= sample_count:
            selected = available_dies
        else:
            selected = random.sample(available_dies, sample_count)
        
        logger.debug(f"RandomSamplingRule selected {len(selected)} dies")
        return selected


class RulePluginFactory:
    """Factory for creating rule plugins."""
    
    def __init__(self, registry):
        self.registry = registry
        # Ensure rule plugin type is registered
        self.registry.register_plugin_type("rule")
    
    def create_rule(self, rule_type: str, parameters: Dict[str, Any]) -> ExecutableRule:
        """Create a rule plugin instance."""
        plugin = self.registry.create_plugin("rule", rule_type, parameters)
        if plugin is None:
            raise ValueError(f"Failed to create rule plugin: {rule_type}")
        return plugin
    
    def get_available_rule_types(self) -> List[str]:
        """Get list of available rule types."""
        return self.registry.list_plugins("rule")
    
    def get_rule_metadata(self, rule_type: str) -> PluginMetadata:
        """Get metadata for a rule type."""
        return self.registry.get_plugin_metadata("rule", rule_type)