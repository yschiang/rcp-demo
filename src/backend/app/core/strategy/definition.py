"""
Strategy Definition Layer - User-created templates that are serializable and versionable.
"""
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid


class StrategyType(Enum):
    """Supported strategy types."""
    FIXED_POINT = "fixed_point"
    CENTER_EDGE = "center_edge"  
    UNIFORM_GRID = "uniform_grid"
    HOTSPOT_PRIORITY = "hotspot_priority"
    ADAPTIVE = "adaptive"
    CUSTOM = "custom"


class StrategyLifecycle(Enum):
    """Strategy lifecycle states."""
    DRAFT = "draft"
    REVIEW = "review"
    APPROVED = "approved"
    ACTIVE = "active"
    DEPRECATED = "deprecated"


@dataclass
class ConditionalLogic:
    """Defines conditions that affect strategy execution."""
    wafer_size: Optional[str] = None  # e.g., "300mm", "200mm"
    product_type: Optional[str] = None  # e.g., "memory", "logic"
    process_layer: Optional[str] = None  # e.g., "metal1", "poly"
    defect_density_threshold: Optional[float] = None
    custom_conditions: Dict[str, Any] = field(default_factory=dict)
    
    def evaluate(self, context: Dict[str, Any]) -> bool:
        """Evaluate conditions against execution context."""
        # Implementation will be in the execution engine
        return True


@dataclass
class TransformationConfig:
    """Coordinate transformation parameters."""
    rotation_angle: float = 0.0
    scale_factor: float = 1.0
    offset_x: float = 0.0
    offset_y: float = 0.0
    flip_x: bool = False
    flip_y: bool = False
    custom_transforms: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class RuleConfig:
    """Configuration for a specific rule within a strategy."""
    rule_type: str
    parameters: Dict[str, Any]
    weight: float = 1.0
    conditions: Optional[ConditionalLogic] = None
    enabled: bool = True


@dataclass
class StrategyDefinition:
    """
    User-created strategy template - the source of truth for strategy configuration.
    This is what gets stored, versioned, and edited by users.
    """
    # Identity
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    
    # Classification
    strategy_type: StrategyType = StrategyType.CUSTOM
    process_step: str = ""
    tool_type: str = ""
    
    # Configuration
    rules: List[RuleConfig] = field(default_factory=list)
    conditions: Optional[ConditionalLogic] = None
    transformations: Optional[TransformationConfig] = None
    
    # Vendor targeting (optional at definition time)
    target_vendor: Optional[str] = None
    vendor_specific_params: Dict[str, Any] = field(default_factory=dict)
    
    # Metadata
    version: str = "1.0.0"
    author: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    modified_at: datetime = field(default_factory=datetime.now)
    lifecycle_state: StrategyLifecycle = StrategyLifecycle.DRAFT
    
    # Validation
    schema_version: str = "1.0"
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary for storage/transmission."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "strategy_type": self.strategy_type.value,
            "process_step": self.process_step,
            "tool_type": self.tool_type,
            "rules": [
                {
                    "rule_type": rule.rule_type,
                    "parameters": rule.parameters,
                    "weight": rule.weight,
                    "enabled": rule.enabled,
                    "conditions": rule.conditions.__dict__ if rule.conditions else None
                }
                for rule in self.rules
            ],
            "conditions": self.conditions.__dict__ if self.conditions else None,
            "transformations": self.transformations.__dict__ if self.transformations else None,
            "target_vendor": self.target_vendor,
            "vendor_specific_params": self.vendor_specific_params,
            "version": self.version,
            "author": self.author,
            "created_at": self.created_at.isoformat(),
            "modified_at": self.modified_at.isoformat(),
            "lifecycle_state": self.lifecycle_state.value,
            "schema_version": self.schema_version
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StrategyDefinition':
        """Deserialize from dictionary."""
        # Implementation for creating StrategyDefinition from dict
        # This will include proper type conversion and validation
        pass
    
    def validate(self, require_rules: bool = True) -> List[str]:
        """Validate strategy definition and return list of errors."""
        errors = []
        
        if not self.name.strip():
            errors.append("Strategy name is required")
        
        if not self.process_step.strip():
            errors.append("Process step is required")
            
        if not self.tool_type.strip():
            errors.append("Tool type is required")
            
        # Only require rules if explicitly requested (for execution vs creation)
        if require_rules and not self.rules:
            errors.append("At least one rule is required")
            
        return errors