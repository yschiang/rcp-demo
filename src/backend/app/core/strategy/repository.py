"""
Strategy Repository - Handles persistence, versioning, and lifecycle management.
"""
from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
import json

from .definition import StrategyDefinition, StrategyLifecycle


@dataclass
class StrategyVersion:
    """Represents a specific version of a strategy."""
    strategy_id: str
    version: str
    definition: StrategyDefinition
    created_at: datetime
    created_by: str
    changelog: str = ""
    is_active: bool = False


class StrategyRepository(ABC):
    """Abstract repository for strategy persistence and versioning."""
    
    @abstractmethod
    def save(self, definition: StrategyDefinition) -> StrategyVersion:
        """Save a strategy definition and return version info."""
        pass
    
    @abstractmethod
    def get_by_id(self, strategy_id: str, version: Optional[str] = None) -> Optional[StrategyDefinition]:
        """Get strategy by ID, optionally specific version."""
        pass
    
    @abstractmethod
    def list_strategies(self, 
                       process_step: Optional[str] = None,
                       tool_type: Optional[str] = None,
                       lifecycle_state: Optional[StrategyLifecycle] = None) -> List[StrategyDefinition]:
        """List strategies with optional filters."""
        pass
    
    @abstractmethod
    def get_versions(self, strategy_id: str) -> List[StrategyVersion]:
        """Get all versions of a strategy."""
        pass
    
    @abstractmethod
    def update_lifecycle_state(self, strategy_id: str, new_state: StrategyLifecycle, user: str) -> bool:
        """Update strategy lifecycle state."""
        pass
    
    @abstractmethod
    def delete(self, strategy_id: str) -> bool:
        """Delete a strategy (soft delete)."""
        pass


class InMemoryStrategyRepository(StrategyRepository):
    """In-memory implementation for development and testing."""
    
    def __init__(self):
        self._strategies: Dict[str, Dict[str, StrategyDefinition]] = {}
        self._versions: Dict[str, List[StrategyVersion]] = {}
        self._active_versions: Dict[str, str] = {}
    
    def save(self, definition: StrategyDefinition) -> StrategyVersion:
        """Save strategy definition."""
        strategy_id = definition.id
        
        # Initialize storage for new strategy
        if strategy_id not in self._strategies:
            self._strategies[strategy_id] = {}
            self._versions[strategy_id] = []
        
        # Store definition
        self._strategies[strategy_id][definition.version] = definition
        
        # Create version record
        version = StrategyVersion(
            strategy_id=strategy_id,
            version=definition.version,
            definition=definition,
            created_at=datetime.now(),
            created_by=definition.author,
            is_active=(definition.lifecycle_state == StrategyLifecycle.ACTIVE)
        )
        
        self._versions[strategy_id].append(version)
        
        # Update active version if this is active
        if definition.lifecycle_state == StrategyLifecycle.ACTIVE:
            self._active_versions[strategy_id] = definition.version
        
        return version
    
    def get_by_id(self, strategy_id: str, version: Optional[str] = None) -> Optional[StrategyDefinition]:
        """Get strategy by ID."""
        if strategy_id not in self._strategies:
            return None
        
        if version is None:
            # Get active version or latest
            version = self._active_versions.get(strategy_id)
            if version is None:
                versions = sorted(self._strategies[strategy_id].keys(), reverse=True)
                version = versions[0] if versions else None
        
        return self._strategies[strategy_id].get(version) if version else None
    
    def list_strategies(self, 
                       process_step: Optional[str] = None,
                       tool_type: Optional[str] = None,
                       lifecycle_state: Optional[StrategyLifecycle] = None) -> List[StrategyDefinition]:
        """List strategies with filters."""
        results = []
        
        for strategy_id in self._strategies:
            # Get latest version of each strategy
            definition = self.get_by_id(strategy_id)
            if definition is None:
                continue
            
            # Apply filters
            if process_step and definition.process_step != process_step:
                continue
            if tool_type and definition.tool_type != tool_type:
                continue
            if lifecycle_state and definition.lifecycle_state != lifecycle_state:
                continue
            
            results.append(definition)
        
        return results
    
    def get_versions(self, strategy_id: str) -> List[StrategyVersion]:
        """Get all versions of a strategy."""
        return self._versions.get(strategy_id, [])
    
    def update_lifecycle_state(self, strategy_id: str, new_state: StrategyLifecycle, user: str) -> bool:
        """Update strategy lifecycle state."""
        definition = self.get_by_id(strategy_id)
        if definition is None:
            return False
        
        definition.lifecycle_state = new_state
        definition.modified_at = datetime.now()
        
        # Update active version tracking
        if new_state == StrategyLifecycle.ACTIVE:
            self._active_versions[strategy_id] = definition.version
        elif strategy_id in self._active_versions and self._active_versions[strategy_id] == definition.version:
            del self._active_versions[strategy_id]
        
        return True
    
    def delete(self, strategy_id: str) -> bool:
        """Soft delete strategy."""
        definition = self.get_by_id(strategy_id)
        if definition is None:
            return False
        
        definition.lifecycle_state = StrategyLifecycle.DEPRECATED
        return True


class FileSystemStrategyRepository(StrategyRepository):
    """File system-based repository implementation."""
    
    def __init__(self, storage_path: str):
        self.storage_path = storage_path
        # Implementation would handle file-based persistence
    
    def save(self, definition: StrategyDefinition) -> StrategyVersion:
        """Save to file system."""
        # Implementation for file persistence
        pass
    
    # ... other methods would be implemented


class StrategyManager:
    """High-level interface for strategy management operations."""
    
    def __init__(self, repository: StrategyRepository):
        self.repository = repository
    
    def create_strategy(self, 
                       name: str,
                       process_step: str,
                       tool_type: str,
                       author: str) -> StrategyDefinition:
        """Create a new strategy definition."""
        definition = StrategyDefinition(
            name=name,
            process_step=process_step,
            tool_type=tool_type,
            author=author
        )
        
        self.repository.save(definition)
        return definition
    
    def clone_strategy(self, source_id: str, new_name: str, author: str) -> Optional[StrategyDefinition]:
        """Clone an existing strategy."""
        source = self.repository.get_by_id(source_id)
        if source is None:
            return None
        
        # Create new definition based on source
        cloned = StrategyDefinition(
            name=new_name,
            description=f"Cloned from {source.name}",
            strategy_type=source.strategy_type,
            process_step=source.process_step,
            tool_type=source.tool_type,
            rules=source.rules.copy(),
            conditions=source.conditions,
            transformations=source.transformations,
            author=author,
            lifecycle_state=StrategyLifecycle.DRAFT
        )
        
        self.repository.save(cloned)
        return cloned
    
    def promote_strategy(self, strategy_id: str, user: str) -> bool:
        """Promote strategy through lifecycle states."""
        definition = self.repository.get_by_id(strategy_id)
        if definition is None:
            return False
        
        # Define promotion path
        promotion_path = {
            StrategyLifecycle.DRAFT: StrategyLifecycle.REVIEW,
            StrategyLifecycle.REVIEW: StrategyLifecycle.APPROVED,
            StrategyLifecycle.APPROVED: StrategyLifecycle.ACTIVE
        }
        
        next_state = promotion_path.get(definition.lifecycle_state)
        if next_state is None:
            return False
        
        return self.repository.update_lifecycle_state(strategy_id, next_state, user)