"""
Strategy Compilation Layer - Converts definitions into validated, executable forms.
"""
from typing import Dict, List, Optional, Any, Protocol
from dataclasses import dataclass
from abc import ABC, abstractmethod

from .definition import StrategyDefinition, RuleConfig
from ..models.wafer_map import WaferMap
from ..models.die import Die


class ExecutableRule(ABC):
    """Interface for compiled, executable rules."""
    
    @abstractmethod
    def apply(self, wafer_map: WaferMap, context: 'ExecutionContext') -> List[Die]:
        """Apply rule to wafer map with given context."""
        pass
    
    @abstractmethod
    def estimate_performance(self, wafer_map: WaferMap) -> Dict[str, Any]:
        """Estimate execution time and resource usage."""
        pass


@dataclass
class ExecutionContext:
    """Runtime context for strategy execution."""
    wafer_map: WaferMap
    process_parameters: Dict[str, Any]
    tool_constraints: Dict[str, Any]
    execution_id: str
    timestamp: str
    
    # Environment context
    wafer_size: Optional[str] = None
    product_type: Optional[str] = None
    process_layer: Optional[str] = None
    defect_density: Optional[float] = None
    
    def get_context_dict(self) -> Dict[str, Any]:
        """Get context as dictionary for condition evaluation."""
        return {
            "wafer_size": self.wafer_size,
            "product_type": self.product_type,
            "process_layer": self.process_layer,
            "defect_density": self.defect_density,
            **self.process_parameters,
            **self.tool_constraints
        }


@dataclass 
class CompiledStrategy:
    """
    Resolved, validated, executable form of a strategy.
    This is what actually gets executed against wafer maps.
    """
    definition_id: str
    name: str
    compiled_rules: List[ExecutableRule]
    execution_metadata: Dict[str, Any]
    validation_results: Dict[str, Any]
    performance_estimate: Dict[str, Any]
    
    def execute(self, context: ExecutionContext) -> List[Die]:
        """Execute strategy against execution context."""
        selected_dies = []
        
        # Apply each compiled rule
        for rule in self.compiled_rules:
            rule_result = rule.apply(context.wafer_map, context)
            selected_dies.extend(rule_result)
        
        # Remove duplicates while preserving order
        unique_dies = []
        seen_coordinates = set()
        for die in selected_dies:
            coord = (die.x, die.y)
            if coord not in seen_coordinates:
                unique_dies.append(die)
                seen_coordinates.add(coord)
        
        return unique_dies
    
    def validate_execution_context(self, context: ExecutionContext) -> List[str]:
        """Validate that context meets strategy requirements."""
        errors = []
        
        # Check if required context parameters are present
        # This will be expanded based on strategy requirements
        
        return errors


class StrategyCompiler:
    """
    Compiles StrategyDefinitions into executable CompiledStrategy objects.
    Handles dependency resolution, validation, and optimization.
    """
    
    def __init__(self, rule_factory: 'RuleFactory'):
        self.rule_factory = rule_factory
        self._compilation_cache: Dict[str, CompiledStrategy] = {}
    
    def compile(self, definition: StrategyDefinition) -> CompiledStrategy:
        """Compile strategy definition into executable form."""
        # Check cache first
        cache_key = f"{definition.id}:{definition.version}"
        if cache_key in self._compilation_cache:
            return self._compilation_cache[cache_key]
        
        # Validate definition
        validation_errors = definition.validate()
        if validation_errors:
            raise CompilationError(f"Strategy validation failed: {validation_errors}")
        
        # Compile rules
        compiled_rules = []
        for rule_config in definition.rules:
            if rule_config.enabled:
                executable_rule = self.rule_factory.create_rule(rule_config)
                compiled_rules.append(executable_rule)
        
        # Create compiled strategy
        compiled = CompiledStrategy(
            definition_id=definition.id,
            name=definition.name,
            compiled_rules=compiled_rules,
            execution_metadata={
                "compilation_timestamp": "2025-01-13",  # Will use datetime
                "schema_version": definition.schema_version,
                "compiler_version": "1.0.0"
            },
            validation_results={"errors": [], "warnings": []},
            performance_estimate=self._estimate_performance(compiled_rules)
        )
        
        # Cache compiled strategy
        self._compilation_cache[cache_key] = compiled
        
        return compiled
    
    def _estimate_performance(self, rules: List[ExecutableRule]) -> Dict[str, Any]:
        """Estimate performance characteristics of compiled strategy."""
        return {
            "estimated_execution_time_ms": len(rules) * 10,  # Placeholder
            "memory_usage_estimate": "low",
            "complexity_score": len(rules)
        }


class CompilationError(Exception):
    """Raised when strategy compilation fails."""
    pass


class RuleFactory:
    """Factory for creating executable rules from rule configurations."""
    
    def __init__(self):
        self._rule_registry: Dict[str, type] = {}
    
    def register_rule_type(self, rule_type: str, rule_class: type):
        """Register a rule implementation."""
        self._rule_registry[rule_type] = rule_class
    
    def create_rule(self, rule_config: RuleConfig) -> ExecutableRule:
        """Create executable rule from configuration."""
        rule_class = self._rule_registry.get(rule_config.rule_type)
        if not rule_class:
            raise CompilationError(f"Unknown rule type: {rule_config.rule_type}")
        
        return rule_class(rule_config.parameters)
    
    def get_available_rule_types(self) -> List[str]:
        """Get list of available rule types."""
        return list(self._rule_registry.keys())