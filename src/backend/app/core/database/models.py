"""
SQLAlchemy database models for strategy persistence.
"""
import json
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy import Column, String, Text, DateTime, Integer, Boolean, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import create_engine, ForeignKey

from ..strategy.definition import StrategyDefinition, StrategyType, StrategyLifecycle, RuleConfig, ConditionalLogic, TransformationConfig
from ..models.schematic import SchematicData, SchematicValidationResult, SchematicFormat, CoordinateSystem, ValidationStatus, DieBoundary, SchematicMetadata

Base = declarative_base()


class StrategyModel(Base):
    """SQLAlchemy model for strategy persistence."""
    __tablename__ = "strategies"
    
    # Primary identification
    id = Column(String(36), primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, default="")
    
    # Classification
    strategy_type = Column(String(50), nullable=False)
    process_step = Column(String(100), nullable=False)
    tool_type = Column(String(100), nullable=False)
    
    # Configuration (stored as JSON)
    rules_json = Column(Text, default="[]")
    conditions_json = Column(Text, nullable=True)
    transformations_json = Column(Text, nullable=True)
    
    # Vendor targeting
    target_vendor = Column(String(100), nullable=True)
    vendor_specific_params_json = Column(Text, default="{}")
    
    # Metadata
    version = Column(String(20), default="1.0.0")
    author = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    modified_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    lifecycle_state = Column(String(20), default="draft")
    
    # Validation
    schema_version = Column(String(10), default="1.0")
    
    # Indexes for performance
    __table_args__ = (
        Index('ix_strategies_process_step', 'process_step'),
        Index('ix_strategies_tool_type', 'tool_type'),
        Index('ix_strategies_lifecycle_state', 'lifecycle_state'),
        Index('ix_strategies_author', 'author'),
        Index('ix_strategies_created_at', 'created_at'),
    )
    
    def to_strategy_definition(self) -> StrategyDefinition:
        """Convert database model to StrategyDefinition domain object."""
        # Parse JSON fields
        rules_data = json.loads(self.rules_json) if self.rules_json else []
        conditions_data = json.loads(self.conditions_json) if self.conditions_json else None
        transformations_data = json.loads(self.transformations_json) if self.transformations_json else None
        vendor_params = json.loads(self.vendor_specific_params_json) if self.vendor_specific_params_json else {}
        
        # Convert rules
        rules = []
        for rule_data in rules_data:
            rule = RuleConfig(
                rule_type=rule_data.get('rule_type', 'fixed_point'),
                parameters=rule_data.get('parameters', {}),
                weight=rule_data.get('weight', 1.0),
                enabled=rule_data.get('enabled', True),
                conditions=ConditionalLogic(**rule_data['conditions']) if rule_data.get('conditions') else None
            )
            rules.append(rule)
        
        # Convert conditions
        conditions = ConditionalLogic(**conditions_data) if conditions_data else None
        
        # Convert transformations
        transformations = TransformationConfig(**transformations_data) if transformations_data else None
        
        return StrategyDefinition(
            id=self.id,
            name=self.name,
            description=self.description,
            strategy_type=StrategyType(self.strategy_type),
            process_step=self.process_step,
            tool_type=self.tool_type,
            rules=rules,
            conditions=conditions,
            transformations=transformations,
            target_vendor=self.target_vendor,
            vendor_specific_params=vendor_params,
            version=self.version,
            author=self.author,
            created_at=self.created_at,
            modified_at=self.modified_at,
            lifecycle_state=StrategyLifecycle(self.lifecycle_state),
            schema_version=self.schema_version
        )
    
    @classmethod
    def from_strategy_definition(cls, definition: StrategyDefinition) -> 'StrategyModel':
        """Create database model from StrategyDefinition domain object."""
        # Serialize rules
        rules_data = []
        for rule in definition.rules:
            rule_dict = {
                'rule_type': rule.rule_type,
                'parameters': rule.parameters,
                'weight': rule.weight,
                'enabled': rule.enabled
            }
            if rule.conditions:
                rule_dict['conditions'] = rule.conditions.__dict__
            rules_data.append(rule_dict)
        
        # Serialize conditions
        conditions_json = None
        if definition.conditions:
            conditions_json = json.dumps(definition.conditions.__dict__)
        
        # Serialize transformations
        transformations_json = None
        if definition.transformations:
            transformations_json = json.dumps(definition.transformations.__dict__)
        
        return cls(
            id=definition.id,
            name=definition.name,
            description=definition.description,
            strategy_type=definition.strategy_type.value,
            process_step=definition.process_step,
            tool_type=definition.tool_type,
            rules_json=json.dumps(rules_data),
            conditions_json=conditions_json,
            transformations_json=transformations_json,
            target_vendor=definition.target_vendor,
            vendor_specific_params_json=json.dumps(definition.vendor_specific_params),
            version=definition.version,
            author=definition.author,
            created_at=definition.created_at,
            modified_at=definition.modified_at,
            lifecycle_state=definition.lifecycle_state.value,
            schema_version=definition.schema_version
        )


class StrategyVersionModel(Base):
    """SQLAlchemy model for strategy version tracking."""
    __tablename__ = "strategy_versions"
    
    # Composite primary key
    strategy_id = Column(String(36), primary_key=True)
    version = Column(String(20), primary_key=True)
    
    # Version metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(100), nullable=False)
    changelog = Column(Text, default="")
    is_active = Column(Boolean, default=False)
    
    # Strategy snapshot (full definition at time of version)
    strategy_snapshot_json = Column(Text, nullable=False)
    
    # Indexes
    __table_args__ = (
        Index('ix_strategy_versions_strategy_id', 'strategy_id'),
        Index('ix_strategy_versions_created_at', 'created_at'),
        Index('ix_strategy_versions_is_active', 'is_active'),
    )


# Database connection and session management
class DatabaseManager:
    """Manages database connection and session lifecycle."""
    
    def __init__(self, database_url: str = "sqlite:///./strategy_system.db"):
        self.database_url = database_url
        self.engine = create_engine(
            database_url,
            connect_args={"check_same_thread": False} if database_url.startswith("sqlite") else {}
        )
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def create_tables(self):
        """Create all database tables."""
        Base.metadata.create_all(bind=self.engine)
    
    def get_session(self):
        """Get a database session."""
        return self.SessionLocal()
    
    def drop_tables(self):
        """Drop all database tables (for testing)."""
        Base.metadata.drop_all(bind=self.engine)


class SchematicModel(Base):
    """SQLAlchemy model for schematic data persistence."""
    __tablename__ = "schematics"
    
    # Primary identification
    id = Column(String(36), primary_key=True)
    filename = Column(String(255), nullable=False)
    format_type = Column(String(20), nullable=False)
    upload_date = Column(DateTime, default=datetime.utcnow)
    
    # Layout configuration
    coordinate_system = Column(String(50), default="cartesian")
    wafer_size = Column(String(20), nullable=True)
    
    # Die boundaries (stored as JSON)
    die_boundaries_json = Column(Text, nullable=False)
    
    # Metadata (stored as JSON)
    metadata_json = Column(Text, nullable=True)
    
    # Computed statistics (cached for performance)
    die_count = Column(Integer, default=0)
    available_die_count = Column(Integer, default=0)
    layout_bounds_json = Column(Text, nullable=True)  # [x_min, y_min, x_max, y_max]
    
    # Tracking
    created_by = Column(String(100), nullable=False)
    last_validated = Column(DateTime, nullable=True)
    
    # Indexes for performance
    __table_args__ = (
        Index('ix_schematics_filename', 'filename'),
        Index('ix_schematics_format_type', 'format_type'),
        Index('ix_schematics_upload_date', 'upload_date'),
        Index('ix_schematics_created_by', 'created_by'),
    )
    
    def to_schematic_data(self) -> SchematicData:
        """Convert database model to SchematicData domain object."""
        # Parse die boundaries
        die_boundaries_data = json.loads(self.die_boundaries_json)
        die_boundaries = []
        for die_data in die_boundaries_data:
            die_boundary = DieBoundary(
                die_id=die_data['die_id'],
                x_min=die_data['x_min'],
                y_min=die_data['y_min'],
                x_max=die_data['x_max'],
                y_max=die_data['y_max'],
                center_x=die_data['center_x'],
                center_y=die_data['center_y'],
                available=die_data.get('available', True),
                metadata=die_data.get('metadata', {})
            )
            die_boundaries.append(die_boundary)
        
        # Parse metadata
        metadata = None
        if self.metadata_json:
            metadata_data = json.loads(self.metadata_json)
            metadata = SchematicMetadata(
                original_filename=metadata_data['original_filename'],
                file_size=metadata_data['file_size'],
                creation_date=datetime.fromisoformat(metadata_data['creation_date']) if metadata_data.get('creation_date') else None,
                software_info=metadata_data.get('software_info'),
                units=metadata_data.get('units'),
                scale_factor=metadata_data.get('scale_factor', 1.0),
                layer_info=metadata_data.get('layer_info', {}),
                custom_attributes=metadata_data.get('custom_attributes', {})
            )
        
        return SchematicData(
            id=self.id,
            filename=self.filename,
            format_type=SchematicFormat(self.format_type),
            upload_date=self.upload_date,
            die_boundaries=die_boundaries,
            coordinate_system=CoordinateSystem(self.coordinate_system),
            wafer_size=self.wafer_size,
            metadata=metadata
        )
    
    @classmethod
    def from_schematic_data(cls, data: SchematicData, created_by: str) -> 'SchematicModel':
        """Create database model from SchematicData domain object."""
        # Serialize die boundaries
        die_boundaries_data = []
        for die in data.die_boundaries:
            die_dict = {
                'die_id': die.die_id,
                'x_min': die.x_min,
                'y_min': die.y_min,
                'x_max': die.x_max,
                'y_max': die.y_max,
                'center_x': die.center_x,
                'center_y': die.center_y,
                'available': die.available,
                'metadata': die.metadata
            }
            die_boundaries_data.append(die_dict)
        
        # Serialize metadata
        metadata_json = None
        if data.metadata:
            metadata_dict = {
                'original_filename': data.metadata.original_filename,
                'file_size': data.metadata.file_size,
                'creation_date': data.metadata.creation_date.isoformat() if data.metadata.creation_date else None,
                'software_info': data.metadata.software_info,
                'units': data.metadata.units,
                'scale_factor': data.metadata.scale_factor,
                'layer_info': data.metadata.layer_info,
                'custom_attributes': data.metadata.custom_attributes
            }
            metadata_json = json.dumps(metadata_dict)
        
        # Serialize layout bounds
        bounds = data.layout_bounds
        layout_bounds_json = json.dumps([bounds[0], bounds[1], bounds[2], bounds[3]])
        
        return cls(
            id=data.id,
            filename=data.filename,
            format_type=data.format_type.value,
            upload_date=data.upload_date,
            coordinate_system=data.coordinate_system.value,
            wafer_size=data.wafer_size,
            die_boundaries_json=json.dumps(die_boundaries_data),
            metadata_json=metadata_json,
            die_count=data.die_count,
            available_die_count=data.available_die_count,
            layout_bounds_json=layout_bounds_json,
            created_by=created_by
        )


class SchematicValidationModel(Base):
    """SQLAlchemy model for schematic validation results."""
    __tablename__ = "schematic_validations"
    
    # Primary identification
    validation_id = Column(String(36), primary_key=True)
    schematic_id = Column(String(36), ForeignKey('schematics.id'), nullable=False)
    strategy_id = Column(String(36), ForeignKey('strategies.id'), nullable=False)
    validation_date = Column(DateTime, default=datetime.utcnow)
    
    # Validation results
    validation_status = Column(String(20), nullable=False)
    alignment_score = Column(Integer, default=0)  # Store as percentage (0-100)
    coverage_percentage = Column(Integer, default=0)  # Store as percentage (0-100)
    total_strategy_points = Column(Integer, default=0)
    valid_strategy_points = Column(Integer, default=0)
    
    # Detailed results (stored as JSON)
    conflicts_json = Column(Text, default="[]")
    warnings_json = Column(Text, default="[]")
    recommendations_json = Column(Text, default="[]")
    
    # Tracking
    validated_by = Column(String(100), nullable=False)
    
    # Relationships
    schematic = relationship("SchematicModel", backref="validations")
    strategy = relationship("StrategyModel", backref="schematic_validations")
    
    # Indexes for performance
    __table_args__ = (
        Index('ix_schematic_validations_schematic_id', 'schematic_id'),
        Index('ix_schematic_validations_strategy_id', 'strategy_id'),
        Index('ix_schematic_validations_validation_date', 'validation_date'),
        Index('ix_schematic_validations_status', 'validation_status'),
    )
    
    def to_validation_result(self) -> SchematicValidationResult:
        """Convert database model to SchematicValidationResult domain object."""
        from ..models.schematic import ValidationConflict, ValidationWarning
        
        # Parse conflicts
        conflicts_data = json.loads(self.conflicts_json)
        conflicts = []
        for conflict_data in conflicts_data:
            conflict = ValidationConflict(
                conflict_type=conflict_data['conflict_type'],
                strategy_point=tuple(conflict_data['strategy_point']),
                description=conflict_data['description'],
                severity=conflict_data['severity'],
                recommendation=conflict_data.get('recommendation'),
                affected_die_id=conflict_data.get('affected_die_id')
            )
            conflicts.append(conflict)
        
        # Parse warnings
        warnings_data = json.loads(self.warnings_json)
        warnings = []
        for warning_data in warnings_data:
            warning = ValidationWarning(
                warning_type=warning_data['warning_type'],
                description=warning_data['description'],
                affected_area=tuple(warning_data['affected_area']) if warning_data.get('affected_area') else None,
                recommendation=warning_data.get('recommendation')
            )
            warnings.append(warning)
        
        # Parse recommendations
        recommendations = json.loads(self.recommendations_json)
        
        return SchematicValidationResult(
            validation_id=self.validation_id,
            schematic_id=self.schematic_id,
            strategy_id=self.strategy_id,
            validation_date=self.validation_date,
            validation_status=ValidationStatus(self.validation_status),
            conflicts=conflicts,
            warnings=warnings,
            alignment_score=self.alignment_score / 100.0,  # Convert back to 0.0-1.0
            coverage_percentage=self.coverage_percentage,
            total_strategy_points=self.total_strategy_points,
            valid_strategy_points=self.valid_strategy_points,
            recommendations=recommendations
        )
    
    @classmethod
    def from_validation_result(cls, result: SchematicValidationResult, validated_by: str) -> 'SchematicValidationModel':
        """Create database model from SchematicValidationResult domain object."""
        # Serialize conflicts
        conflicts_data = []
        for conflict in result.conflicts:
            conflict_dict = {
                'conflict_type': conflict.conflict_type,
                'strategy_point': list(conflict.strategy_point),
                'description': conflict.description,
                'severity': conflict.severity,
                'recommendation': conflict.recommendation,
                'affected_die_id': conflict.affected_die_id
            }
            conflicts_data.append(conflict_dict)
        
        # Serialize warnings
        warnings_data = []
        for warning in result.warnings:
            warning_dict = {
                'warning_type': warning.warning_type,
                'description': warning.description,
                'affected_area': list(warning.affected_area) if warning.affected_area else None,
                'recommendation': warning.recommendation
            }
            warnings_data.append(warning_dict)
        
        return cls(
            validation_id=result.validation_id,
            schematic_id=result.schematic_id,
            strategy_id=result.strategy_id,
            validation_date=result.validation_date,
            validation_status=result.validation_status.value,
            alignment_score=int(result.alignment_score * 100),  # Convert to percentage
            coverage_percentage=int(result.coverage_percentage),
            total_strategy_points=result.total_strategy_points,
            valid_strategy_points=result.valid_strategy_points,
            conflicts_json=json.dumps(conflicts_data),
            warnings_json=json.dumps(warnings_data),
            recommendations_json=json.dumps(result.recommendations),
            validated_by=validated_by
        )


# Global database manager instance
db_manager = DatabaseManager()