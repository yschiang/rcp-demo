"""
SQLAlchemy-based repository implementation for strategy persistence.
"""
import json
from typing import Dict, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from ..strategy.definition import StrategyDefinition, StrategyLifecycle
from ..strategy.repository import StrategyRepository, StrategyVersion
from .models import StrategyModel, StrategyVersionModel, db_manager


class SQLAlchemyStrategyRepository(StrategyRepository):
    """SQLAlchemy-based strategy repository implementation."""
    
    def __init__(self, session: Session = None):
        self.session = session
        self._owns_session = session is None
        if self._owns_session:
            self.session = db_manager.get_session()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._owns_session and self.session:
            self.session.close()
    
    def save(self, definition: StrategyDefinition) -> StrategyVersion:
        """Save a strategy definition and return version info."""
        try:
            # Check if strategy exists
            existing = self.session.query(StrategyModel).filter(
                StrategyModel.id == definition.id
            ).first()
            
            if existing:
                # Update existing strategy
                db_strategy = StrategyModel.from_strategy_definition(definition)
                for key, value in db_strategy.__dict__.items():
                    if not key.startswith('_') and key != 'id':
                        setattr(existing, key, value)
                existing.modified_at = datetime.utcnow()
                self.session.commit()
                strategy_model = existing
            else:
                # Create new strategy
                strategy_model = StrategyModel.from_strategy_definition(definition)
                self.session.add(strategy_model)
                self.session.commit()
            
            # Create version record
            version = StrategyVersion(
                strategy_id=definition.id,
                version=definition.version,
                definition=definition,
                created_at=datetime.utcnow(),
                created_by=definition.author,
                is_active=(definition.lifecycle_state == StrategyLifecycle.ACTIVE)
            )
            
            # Save version record to database
            version_model = StrategyVersionModel(
                strategy_id=definition.id,
                version=definition.version,
                created_at=version.created_at,
                created_by=version.created_by,
                changelog="",
                is_active=version.is_active,
                strategy_snapshot_json=json.dumps(definition.to_dict())
            )
            
            # Remove old active version if this is active
            if definition.lifecycle_state == StrategyLifecycle.ACTIVE:
                self.session.query(StrategyVersionModel).filter(
                    StrategyVersionModel.strategy_id == definition.id,
                    StrategyVersionModel.is_active == True
                ).update({StrategyVersionModel.is_active: False})
            
            self.session.add(version_model)
            self.session.commit()
            
            return version
            
        except SQLAlchemyError as e:
            self.session.rollback()
            raise Exception(f"Database error saving strategy: {str(e)}")
    
    def get_by_id(self, strategy_id: str, version: Optional[str] = None) -> Optional[StrategyDefinition]:
        """Get strategy by ID, optionally specific version."""
        try:
            if version is None:
                # Get latest version
                strategy_model = self.session.query(StrategyModel).filter(
                    StrategyModel.id == strategy_id
                ).first()
            else:
                # Get specific version from version table
                version_model = self.session.query(StrategyVersionModel).filter(
                    StrategyVersionModel.strategy_id == strategy_id,
                    StrategyVersionModel.version == version
                ).first()
                
                if version_model:
                    # Reconstruct from snapshot
                    snapshot_data = json.loads(version_model.strategy_snapshot_json)
                    return StrategyDefinition.from_dict(snapshot_data)
                else:
                    return None
            
            if strategy_model:
                return strategy_model.to_strategy_definition()
            else:
                return None
                
        except SQLAlchemyError as e:
            raise Exception(f"Database error retrieving strategy: {str(e)}")
    
    def list_strategies(self, 
                       process_step: Optional[str] = None,
                       tool_type: Optional[str] = None,
                       lifecycle_state: Optional[StrategyLifecycle] = None) -> List[StrategyDefinition]:
        """List strategies with optional filters."""
        try:
            query = self.session.query(StrategyModel)
            
            # Apply filters
            if process_step:
                query = query.filter(StrategyModel.process_step == process_step)
            if tool_type:
                query = query.filter(StrategyModel.tool_type == tool_type)
            if lifecycle_state:
                query = query.filter(StrategyModel.lifecycle_state == lifecycle_state.value)
            
            # Order by creation date (newest first)
            query = query.order_by(StrategyModel.created_at.desc())
            
            strategy_models = query.all()
            return [model.to_strategy_definition() for model in strategy_models]
            
        except SQLAlchemyError as e:
            raise Exception(f"Database error listing strategies: {str(e)}")
    
    def get_versions(self, strategy_id: str) -> List[StrategyVersion]:
        """Get all versions of a strategy."""
        try:
            version_models = self.session.query(StrategyVersionModel).filter(
                StrategyVersionModel.strategy_id == strategy_id
            ).order_by(StrategyVersionModel.created_at.desc()).all()
            
            versions = []
            for model in version_models:
                snapshot_data = json.loads(model.strategy_snapshot_json)
                definition = StrategyDefinition.from_dict(snapshot_data)
                
                version = StrategyVersion(
                    strategy_id=model.strategy_id,
                    version=model.version,
                    definition=definition,
                    created_at=model.created_at,
                    created_by=model.created_by,
                    changelog=model.changelog,
                    is_active=model.is_active
                )
                versions.append(version)
            
            return versions
            
        except SQLAlchemyError as e:
            raise Exception(f"Database error retrieving strategy versions: {str(e)}")
    
    def update_lifecycle_state(self, strategy_id: str, new_state: StrategyLifecycle, user: str) -> bool:
        """Update strategy lifecycle state."""
        try:
            strategy_model = self.session.query(StrategyModel).filter(
                StrategyModel.id == strategy_id
            ).first()
            
            if not strategy_model:
                return False
            
            strategy_model.lifecycle_state = new_state.value
            strategy_model.modified_at = datetime.utcnow()
            
            # Update active version tracking
            if new_state == StrategyLifecycle.ACTIVE:
                # Mark all versions as inactive first
                self.session.query(StrategyVersionModel).filter(
                    StrategyVersionModel.strategy_id == strategy_id
                ).update({StrategyVersionModel.is_active: False})
                
                # Mark current version as active
                self.session.query(StrategyVersionModel).filter(
                    StrategyVersionModel.strategy_id == strategy_id,
                    StrategyVersionModel.version == strategy_model.version
                ).update({StrategyVersionModel.is_active: True})
            
            self.session.commit()
            return True
            
        except SQLAlchemyError as e:
            self.session.rollback()
            raise Exception(f"Database error updating lifecycle state: {str(e)}")
    
    def delete(self, strategy_id: str) -> bool:
        """Soft delete strategy by setting to deprecated state."""
        try:
            strategy_model = self.session.query(StrategyModel).filter(
                StrategyModel.id == strategy_id
            ).first()
            
            if not strategy_model:
                return False
            
            strategy_model.lifecycle_state = StrategyLifecycle.DEPRECATED.value
            strategy_model.modified_at = datetime.utcnow()
            self.session.commit()
            return True
            
        except SQLAlchemyError as e:
            self.session.rollback()
            raise Exception(f"Database error deleting strategy: {str(e)}")


def get_database_repository() -> SQLAlchemyStrategyRepository:
    """Factory function to get database repository instance."""
    # Ensure database tables exist
    db_manager.create_tables()
    return SQLAlchemyStrategyRepository()