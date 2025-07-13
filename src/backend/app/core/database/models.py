"""
SQLAlchemy database models for strategy persistence.
"""
import json
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy import Column, String, Text, DateTime, Integer, Boolean, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from ..strategy.definition import StrategyDefinition, StrategyType, StrategyLifecycle, RuleConfig, ConditionalLogic, TransformationConfig

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


# Global database manager instance
db_manager = DatabaseManager()