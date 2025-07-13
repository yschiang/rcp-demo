from abc import ABC, abstractmethod
from typing import List
from ..models.die import Die


class VendorMapping(ABC):
    """Abstract base class for vendor-specific coordinate transformations."""
    
    @abstractmethod
    def transform(self, dies: List[Die]) -> List[Die]:
        """Transform die coordinates to vendor-specific format.
        
        Args:
            dies: List of selected dies to transform
            
        Returns:
            List of dies with vendor-specific coordinate transformations applied
        """
        pass
    
    @abstractmethod
    def get_output_format(self) -> str:
        """Return the vendor's required output format (JSON, XML, CSV, etc.)."""
        pass
    
    @abstractmethod
    def export_to_vendor_format(self, dies: List[Die]) -> str:
        """Export dies to vendor-specific file format.
        
        Args:
            dies: List of dies to export
            
        Returns:
            String representation in vendor's required format
        """
        pass