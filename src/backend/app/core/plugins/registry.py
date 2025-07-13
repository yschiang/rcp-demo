"""
Plugin Registry - Central management for all pluggable components.
"""
from typing import Dict, Type, Any, List, Optional, Callable
from abc import ABC, abstractmethod
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class PluginMetadata:
    """Metadata about a plugin."""
    name: str
    version: str
    description: str
    author: str
    plugin_type: str
    dependencies: List[str]
    config_schema: Optional[Dict[str, Any]] = None


class Plugin(ABC):
    """Base class for all plugins."""
    
    @property
    @abstractmethod
    def metadata(self) -> PluginMetadata:
        """Return plugin metadata."""
        pass
    
    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize the plugin with configuration."""
        pass
    
    @abstractmethod
    def cleanup(self) -> None:
        """Cleanup plugin resources."""
        pass


class PluginRegistry:
    """Central registry for managing plugins of all types."""
    
    def __init__(self):
        self._plugins: Dict[str, Dict[str, Plugin]] = {}
        self._plugin_classes: Dict[str, Dict[str, Type[Plugin]]] = {}
        self._initializers: Dict[str, List[Callable]] = {}
        
    def register_plugin_type(self, plugin_type: str):
        """Register a new plugin type."""
        if plugin_type not in self._plugins:
            self._plugins[plugin_type] = {}
            self._plugin_classes[plugin_type] = {}
            self._initializers[plugin_type] = []
            logger.info(f"Registered plugin type: {plugin_type}")
    
    def register_plugin_class(self, plugin_type: str, name: str, plugin_class: Type[Plugin]):
        """Register a plugin class for a specific type."""
        if plugin_type not in self._plugin_classes:
            self.register_plugin_type(plugin_type)
        
        self._plugin_classes[plugin_type][name] = plugin_class
        logger.info(f"Registered plugin class: {plugin_type}.{name}")
    
    def create_plugin(self, plugin_type: str, name: str, config: Dict[str, Any] = None) -> Optional[Plugin]:
        """Create and initialize a plugin instance."""
        if plugin_type not in self._plugin_classes:
            logger.error(f"Unknown plugin type: {plugin_type}")
            return None
        
        if name not in self._plugin_classes[plugin_type]:
            logger.error(f"Unknown plugin: {plugin_type}.{name}")
            return None
        
        try:
            plugin_class = self._plugin_classes[plugin_type][name]
            plugin = plugin_class()
            
            # Initialize plugin
            if config is None:
                config = {}
            
            if plugin.initialize(config):
                self._plugins[plugin_type][name] = plugin
                logger.info(f"Created plugin: {plugin_type}.{name}")
                return plugin
            else:
                logger.error(f"Failed to initialize plugin: {plugin_type}.{name}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating plugin {plugin_type}.{name}: {e}")
            return None
    
    def get_plugin(self, plugin_type: str, name: str) -> Optional[Plugin]:
        """Get an existing plugin instance."""
        return self._plugins.get(plugin_type, {}).get(name)
    
    def list_plugin_types(self) -> List[str]:
        """List all registered plugin types."""
        return list(self._plugin_classes.keys())
    
    def list_plugins(self, plugin_type: str) -> List[str]:
        """List all available plugins for a type."""
        return list(self._plugin_classes.get(plugin_type, {}).keys())
    
    def list_active_plugins(self, plugin_type: str) -> List[str]:
        """List all active plugin instances for a type."""
        return list(self._plugins.get(plugin_type, {}).keys())
    
    def get_plugin_metadata(self, plugin_type: str, name: str) -> Optional[PluginMetadata]:
        """Get metadata for a plugin."""
        plugin_class = self._plugin_classes.get(plugin_type, {}).get(name)
        if plugin_class:
            temp_instance = plugin_class()
            return temp_instance.metadata
        return None
    
    def unload_plugin(self, plugin_type: str, name: str) -> bool:
        """Unload a plugin instance."""
        plugin = self._plugins.get(plugin_type, {}).get(name)
        if plugin:
            try:
                plugin.cleanup()
                del self._plugins[plugin_type][name]
                logger.info(f"Unloaded plugin: {plugin_type}.{name}")
                return True
            except Exception as e:
                logger.error(f"Error unloading plugin {plugin_type}.{name}: {e}")
                return False
        return False
    
    def shutdown(self):
        """Shutdown all plugins."""
        for plugin_type in self._plugins:
            for name in list(self._plugins[plugin_type].keys()):
                self.unload_plugin(plugin_type, name)


# Global registry instance
plugin_registry = PluginRegistry()


# Decorator for easy plugin registration
def register_plugin(plugin_type: str, name: str):
    """Decorator to register a plugin class."""
    def decorator(cls: Type[Plugin]):
        plugin_registry.register_plugin_class(plugin_type, name, cls)
        return cls
    return decorator