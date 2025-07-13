"""
Schematic data models for wafer layout and die boundary management.
"""
import json
import uuid
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from .die import Die
from .wafer_map import WaferMap


class SchematicFormat(str, Enum):
    """Supported schematic file formats."""
    GDSII = "gdsii"
    DXF = "dxf"
    SVG = "svg"
    UNKNOWN = "unknown"


class CoordinateSystem(str, Enum):
    """Coordinate system types for schematic data."""
    CARTESIAN = "cartesian"
    POLAR = "polar"
    GDSII_UNITS = "gdsii_units"
    CAD_UNITS = "cad_units"
    NORMALIZED = "normalized"


class ValidationStatus(str, Enum):
    """Validation result status types."""
    PASS = "pass"
    WARNING = "warning"
    FAIL = "fail"
    NOT_VALIDATED = "not_validated"


@dataclass
class DieBoundary:
    """Represents a die boundary with coordinates and metadata."""
    die_id: str
    x_min: float
    y_min: float
    x_max: float
    y_max: float
    center_x: float
    center_y: float
    available: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def width(self) -> float:
        """Calculate die width."""
        return self.x_max - self.x_min
    
    @property
    def height(self) -> float:
        """Calculate die height."""
        return self.y_max - self.y_min
    
    @property
    def area(self) -> float:
        """Calculate die area."""
        return self.width * self.height
    
    def contains_point(self, x: float, y: float) -> bool:
        """Check if a point is within the die boundary."""
        return (self.x_min <= x <= self.x_max and 
                self.y_min <= y <= self.y_max)
    
    def to_die(self) -> Die:
        """Convert to a Die object for strategy processing."""
        return Die(
            x=int(self.center_x),
            y=int(self.center_y),
            available=self.available
        )


@dataclass
class SchematicMetadata:
    """Metadata extracted from schematic files."""
    original_filename: str
    file_size: int
    creation_date: Optional[datetime] = None
    software_info: Optional[str] = None
    units: Optional[str] = None
    scale_factor: float = 1.0
    layer_info: Dict[str, Any] = field(default_factory=dict)
    custom_attributes: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SchematicData:
    """Core schematic data model containing parsed layout information."""
    
    # Identity
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    filename: str = ""
    format_type: SchematicFormat = SchematicFormat.UNKNOWN
    upload_date: datetime = field(default_factory=datetime.utcnow)
    
    # Layout data
    die_boundaries: List[DieBoundary] = field(default_factory=list)
    coordinate_system: CoordinateSystem = CoordinateSystem.CARTESIAN
    wafer_size: Optional[str] = None
    
    # Metadata
    metadata: Optional[SchematicMetadata] = None
    
    # Computed properties
    _die_count: Optional[int] = None
    _layout_bounds: Optional[Tuple[float, float, float, float]] = None
    
    @property
    def die_count(self) -> int:
        """Get total number of dies in the schematic."""
        if self._die_count is None:
            self._die_count = len(self.die_boundaries)
        return self._die_count
    
    @property
    def available_die_count(self) -> int:
        """Get number of available dies."""
        return sum(1 for die in self.die_boundaries if die.available)
    
    @property
    def layout_bounds(self) -> Tuple[float, float, float, float]:
        """Get overall layout bounds (x_min, y_min, x_max, y_max)."""
        if self._layout_bounds is None and self.die_boundaries:
            x_coords = [die.x_min for die in self.die_boundaries] + [die.x_max for die in self.die_boundaries]
            y_coords = [die.y_min for die in self.die_boundaries] + [die.y_max for die in self.die_boundaries]
            self._layout_bounds = (min(x_coords), min(y_coords), max(x_coords), max(y_coords))
        return self._layout_bounds or (0, 0, 0, 0)
    
    def get_die_at_coordinates(self, x: float, y: float) -> Optional[DieBoundary]:
        """Find die boundary containing the given coordinates."""
        for die in self.die_boundaries:
            if die.contains_point(x, y):
                return die
        return None
    
    def to_wafer_map(self) -> WaferMap:
        """Convert schematic data to WaferMap for strategy processing."""
        dies = [die_boundary.to_die() for die_boundary in self.die_boundaries]
        return WaferMap(dies)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics about the schematic."""
        bounds = self.layout_bounds
        return {
            "die_count": self.die_count,
            "available_die_count": self.available_die_count,
            "layout_bounds": {
                "x_min": bounds[0],
                "y_min": bounds[1],
                "x_max": bounds[2],
                "y_max": bounds[3]
            },
            "layout_size": {
                "width": bounds[2] - bounds[0],
                "height": bounds[3] - bounds[1]
            },
            "coordinate_system": self.coordinate_system.value,
            "format_type": self.format_type.value,
            "wafer_size": self.wafer_size
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize schematic data to dictionary."""
        return {
            "id": self.id,
            "filename": self.filename,
            "format_type": self.format_type.value,
            "upload_date": self.upload_date.isoformat(),
            "die_boundaries": [
                {
                    "die_id": die.die_id,
                    "x_min": die.x_min,
                    "y_min": die.y_min,
                    "x_max": die.x_max,
                    "y_max": die.y_max,
                    "center_x": die.center_x,
                    "center_y": die.center_y,
                    "available": die.available,
                    "metadata": die.metadata
                }
                for die in self.die_boundaries
            ],
            "coordinate_system": self.coordinate_system.value,
            "wafer_size": self.wafer_size,
            "metadata": {
                "original_filename": self.metadata.original_filename,
                "file_size": self.metadata.file_size,
                "creation_date": self.metadata.creation_date.isoformat() if self.metadata.creation_date else None,
                "software_info": self.metadata.software_info,
                "units": self.metadata.units,
                "scale_factor": self.metadata.scale_factor,
                "layer_info": self.metadata.layer_info,
                "custom_attributes": self.metadata.custom_attributes
            } if self.metadata else None,
            "statistics": self.get_statistics()
        }


@dataclass
class ValidationConflict:
    """Represents a conflict between strategy and schematic data."""
    conflict_type: str  # "out_of_bounds", "misaligned", "unavailable_die"
    strategy_point: Tuple[float, float]
    description: str
    severity: str  # "error", "warning", "info"
    recommendation: Optional[str] = None
    affected_die_id: Optional[str] = None


@dataclass
class ValidationWarning:
    """Represents a warning during validation."""
    warning_type: str
    description: str
    affected_area: Optional[Tuple[float, float, float, float]] = None
    recommendation: Optional[str] = None


@dataclass
class SchematicValidationResult:
    """Results of validating a strategy against schematic data."""
    
    # Identity
    validation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    schematic_id: str = ""
    strategy_id: str = ""
    validation_date: datetime = field(default_factory=datetime.utcnow)
    
    # Results
    validation_status: ValidationStatus = ValidationStatus.NOT_VALIDATED
    conflicts: List[ValidationConflict] = field(default_factory=list)
    warnings: List[ValidationWarning] = field(default_factory=list)
    
    # Metrics
    alignment_score: float = 0.0  # 0.0 to 1.0
    coverage_percentage: float = 0.0
    total_strategy_points: int = 0
    valid_strategy_points: int = 0
    
    # Recommendations
    recommendations: List[str] = field(default_factory=list)
    
    @property
    def has_errors(self) -> bool:
        """Check if validation has any errors."""
        return any(conflict.severity == "error" for conflict in self.conflicts)
    
    @property
    def has_warnings(self) -> bool:
        """Check if validation has any warnings."""
        return len(self.warnings) > 0 or any(conflict.severity == "warning" for conflict in self.conflicts)
    
    @property
    def is_valid(self) -> bool:
        """Check if validation passed without errors."""
        return self.validation_status == ValidationStatus.PASS and not self.has_errors
    
    def add_conflict(self, conflict_type: str, strategy_point: Tuple[float, float], 
                    description: str, severity: str = "error", 
                    recommendation: str = None, affected_die_id: str = None):
        """Add a validation conflict."""
        conflict = ValidationConflict(
            conflict_type=conflict_type,
            strategy_point=strategy_point,
            description=description,
            severity=severity,
            recommendation=recommendation,
            affected_die_id=affected_die_id
        )
        self.conflicts.append(conflict)
    
    def add_warning(self, warning_type: str, description: str, 
                   affected_area: Tuple[float, float, float, float] = None,
                   recommendation: str = None):
        """Add a validation warning."""
        warning = ValidationWarning(
            warning_type=warning_type,
            description=description,
            affected_area=affected_area,
            recommendation=recommendation
        )
        self.warnings.append(warning)
    
    def calculate_alignment_score(self) -> float:
        """Calculate alignment score based on validation results."""
        if self.total_strategy_points == 0:
            return 0.0
        
        base_score = self.valid_strategy_points / self.total_strategy_points
        
        # Penalize for errors and warnings
        error_penalty = len([c for c in self.conflicts if c.severity == "error"]) * 0.1
        warning_penalty = len([c for c in self.conflicts if c.severity == "warning"]) * 0.05
        warning_penalty += len(self.warnings) * 0.05
        
        final_score = max(0.0, base_score - error_penalty - warning_penalty)
        self.alignment_score = round(final_score, 3)
        return self.alignment_score
    
    def get_summary(self) -> Dict[str, Any]:
        """Get validation summary for API responses."""
        return {
            "validation_id": self.validation_id,
            "schematic_id": self.schematic_id,
            "strategy_id": self.strategy_id,
            "validation_status": self.validation_status.value,
            "alignment_score": self.alignment_score,
            "coverage_percentage": self.coverage_percentage,
            "total_points": self.total_strategy_points,
            "valid_points": self.valid_strategy_points,
            "error_count": len([c for c in self.conflicts if c.severity == "error"]),
            "warning_count": len(self.warnings) + len([c for c in self.conflicts if c.severity == "warning"]),
            "is_valid": self.is_valid,
            "recommendations": self.recommendations
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize validation result to dictionary."""
        return {
            "validation_id": self.validation_id,
            "schematic_id": self.schematic_id,
            "strategy_id": self.strategy_id,
            "validation_date": self.validation_date.isoformat(),
            "validation_status": self.validation_status.value,
            "alignment_score": self.alignment_score,
            "coverage_percentage": self.coverage_percentage,
            "total_strategy_points": self.total_strategy_points,
            "valid_strategy_points": self.valid_strategy_points,
            "conflicts": [
                {
                    "conflict_type": conflict.conflict_type,
                    "strategy_point": conflict.strategy_point,
                    "description": conflict.description,
                    "severity": conflict.severity,
                    "recommendation": conflict.recommendation,
                    "affected_die_id": conflict.affected_die_id
                }
                for conflict in self.conflicts
            ],
            "warnings": [
                {
                    "warning_type": warning.warning_type,
                    "description": warning.description,
                    "affected_area": warning.affected_area,
                    "recommendation": warning.recommendation
                }
                for warning in self.warnings
            ],
            "recommendations": self.recommendations,
            "summary": self.get_summary()
        }