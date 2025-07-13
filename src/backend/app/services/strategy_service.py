"""
Strategy Service - Business logic layer for strategy operations.
"""
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime

from ..core.strategy.definition import StrategyDefinition, StrategyType, StrategyLifecycle
from ..core.strategy.repository import StrategyManager, InMemoryStrategyRepository, StrategyVersion
from ..core.strategy.compilation import StrategyCompiler, ExecutionContext
from ..core.models.wafer_map import WaferMap
from ..core.models.die import Die


class StrategyService:
    """High-level service for strategy management and execution."""
    
    def __init__(self, 
                 repository=None,
                 compiler=None):
        # Use dependency injection in production
        self.repository = repository or InMemoryStrategyRepository()
        self.manager = StrategyManager(self.repository)
        self.compiler = compiler or StrategyCompiler(None)  # Will need rule factory
    
    def create_strategy(self,
                       name: str,
                       description: str,
                       process_step: str,
                       tool_type: str,
                       strategy_type: StrategyType,
                       author: str) -> StrategyDefinition:
        """Create a new strategy definition."""
        definition = StrategyDefinition(
            name=name,
            description=description,
            strategy_type=strategy_type,
            process_step=process_step,
            tool_type=tool_type,
            author=author,
            lifecycle_state=StrategyLifecycle.DRAFT
        )
        
        # Validate before saving
        errors = definition.validate()
        if errors:
            raise ValueError(f"Strategy validation failed: {', '.join(errors)}")
        
        self.repository.save(definition)
        return definition
    
    def get_strategy(self, strategy_id: str, version: Optional[str] = None) -> Optional[StrategyDefinition]:
        """Get strategy by ID and optional version."""
        return self.repository.get_by_id(strategy_id, version)
    
    def list_strategies(self,
                       process_step: Optional[str] = None,
                       tool_type: Optional[str] = None,
                       lifecycle_state: Optional[StrategyLifecycle] = None) -> List[StrategyDefinition]:
        """List strategies with optional filters."""
        return self.repository.list_strategies(process_step, tool_type, lifecycle_state)
    
    def update_strategy(self, strategy_id: str, updates: Dict[str, Any]) -> Optional[StrategyDefinition]:
        """Update strategy definition."""
        definition = self.repository.get_by_id(strategy_id)
        if definition is None:
            return None
        
        # Apply updates
        if 'name' in updates:
            definition.name = updates['name']
        if 'description' in updates:
            definition.description = updates['description']
        if 'rules' in updates:
            # Convert rule dictionaries to RuleConfig objects
            # This would need proper implementation
            pass
        if 'conditions' in updates:
            # Update conditional logic
            pass
        if 'transformations' in updates:
            # Update transformation config
            pass
        
        definition.modified_at = datetime.now()
        
        # Validate and save
        errors = definition.validate()
        if errors:
            raise ValueError(f"Strategy validation failed: {', '.join(errors)}")
        
        self.repository.save(definition)
        return definition
    
    def clone_strategy(self, source_id: str, new_name: str, author: str) -> Optional[StrategyDefinition]:
        """Clone an existing strategy."""
        return self.manager.clone_strategy(source_id, new_name, author)
    
    def promote_strategy(self, strategy_id: str, user: str) -> bool:
        """Promote strategy through lifecycle states."""
        return self.manager.promote_strategy(strategy_id, user)
    
    def delete_strategy(self, strategy_id: str) -> bool:
        """Delete (deprecate) a strategy."""
        return self.repository.delete(strategy_id)
    
    def get_strategy_versions(self, strategy_id: str) -> List[StrategyVersion]:
        """Get all versions of a strategy."""
        return self.repository.get_versions(strategy_id)
    
    def simulate_strategy(self,
                         strategy_id: str,
                         wafer_map_data: Dict[str, Any],
                         process_parameters: Dict[str, Any],
                         tool_constraints: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate strategy execution and return detailed results."""
        # Get strategy definition
        definition = self.repository.get_by_id(strategy_id)
        if definition is None:
            raise ValueError("Strategy not found")
        
        # Create wafer map from data
        wafer_map = self._create_wafer_map_from_data(wafer_map_data)
        
        # Create execution context
        context = ExecutionContext(
            wafer_map=wafer_map,
            process_parameters=process_parameters,
            tool_constraints=tool_constraints,
            execution_id=str(uuid.uuid4()),
            timestamp=datetime.now().isoformat(),
            wafer_size=process_parameters.get('wafer_size'),
            product_type=process_parameters.get('product_type'),
            process_layer=process_parameters.get('process_layer')
        )
        
        try:
            # Compile strategy
            compiled_strategy = self.compiler.compile(definition)
            
            # Execute simulation
            selected_dies = compiled_strategy.execute(context)
            
            # Calculate coverage statistics
            coverage_stats = self._calculate_coverage_stats(wafer_map, selected_dies)
            
            # Get performance metrics
            performance_metrics = compiled_strategy.performance_estimate
            
            return {
                "selected_points": [
                    {"x": die.x, "y": die.y, "available": die.available}
                    for die in selected_dies
                ],
                "coverage_stats": coverage_stats,
                "performance_metrics": performance_metrics,
                "warnings": []  # Would include any warnings from execution
            }
        
        except Exception as e:
            return {
                "selected_points": [],
                "coverage_stats": {},
                "performance_metrics": {},
                "warnings": [f"Simulation failed: {str(e)}"]
            }
    
    def _create_wafer_map_from_data(self, wafer_map_data: Dict[str, Any]) -> WaferMap:
        """Create WaferMap object from data dictionary."""
        dies = []
        
        # Handle different input formats
        if 'dies' in wafer_map_data:
            for die_data in wafer_map_data['dies']:
                die = Die(
                    x=die_data['x'],
                    y=die_data['y'],
                    available=die_data.get('available', True)
                )
                dies.append(die)
        elif 'grid_size' in wafer_map_data:
            # Generate grid-based wafer map
            size = wafer_map_data['grid_size']
            for x in range(size):
                for y in range(size):
                    dies.append(Die(x, y, True))
        else:
            # Default 5x5 grid
            for x in range(5):
                for y in range(5):
                    dies.append(Die(x, y, True))
        
        return WaferMap(dies)
    
    def _calculate_coverage_stats(self, wafer_map: WaferMap, selected_dies: List[Die]) -> Dict[str, Any]:
        """Calculate coverage statistics for simulation results."""
        total_dies = len(wafer_map.dies)
        available_dies = len(wafer_map.get_available_dies())
        selected_count = len(selected_dies)
        
        coverage_percentage = (selected_count / available_dies * 100) if available_dies > 0 else 0
        
        # Calculate distribution statistics
        if selected_dies:
            x_coords = [die.x for die in selected_dies]
            y_coords = [die.y for die in selected_dies]
            
            distribution = {
                "x_range": {"min": min(x_coords), "max": max(x_coords)},
                "y_range": {"min": min(y_coords), "max": max(y_coords)},
                "center_of_mass": {
                    "x": sum(x_coords) / len(x_coords),
                    "y": sum(y_coords) / len(y_coords)
                }
            }
        else:
            distribution = {}
        
        return {
            "total_dies": total_dies,
            "available_dies": available_dies,
            "selected_count": selected_count,
            "coverage_percentage": round(coverage_percentage, 2),
            "distribution": distribution
        }