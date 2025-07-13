import json
from typing import List
from .base import VendorMapping
from ..models.die import Die


class ASMLMapping(VendorMapping):
    """ASML vendor-specific coordinate transformation and export.
    
    ASML lithography tools typically use:
    - Center-origin coordinate system
    - Micrometer units
    - JSON format for modern tools
    - Specific field names (SiteX, SiteY)
    """
    
    def __init__(self, rotation_angle: float = 0.0, scale_factor: float = 1000.0, offset_x: float = 0.0, offset_y: float = 0.0):
        """Initialize ASML mapping with transformation parameters.
        
        Args:
            rotation_angle: Rotation in degrees (default: 0.0)
            scale_factor: Scale factor for coordinate conversion (default: 1000.0 for mm to μm)
            offset_x: X offset in target units (default: 0.0)
            offset_y: Y offset in target units (default: 0.0)
        """
        self.rotation_angle = rotation_angle
        self.scale_factor = scale_factor
        self.offset_x = offset_x
        self.offset_y = offset_y
    
    def transform(self, dies: List[Die]) -> List[Die]:
        """Transform die coordinates to ASML format.
        
        ASML transformation:
        1. Apply scaling (mm to μm conversion)
        2. Apply rotation if specified
        3. Apply coordinate system offset
        4. Convert to center-origin if needed
        """
        transformed_dies = []
        
        for die in dies:
            # Apply scaling
            x_scaled = die.x * self.scale_factor
            y_scaled = die.y * self.scale_factor
            
            # Apply rotation (if specified)
            if self.rotation_angle != 0.0:
                import math
                angle_rad = math.radians(self.rotation_angle)
                cos_a = math.cos(angle_rad)
                sin_a = math.sin(angle_rad)
                
                x_rotated = x_scaled * cos_a - y_scaled * sin_a
                y_rotated = x_scaled * sin_a + y_scaled * cos_a
            else:
                x_rotated = x_scaled
                y_rotated = y_scaled
            
            # Apply offset
            x_final = x_rotated + self.offset_x
            y_final = y_rotated + self.offset_y
            
            # Create transformed die
            transformed_die = Die(int(x_final), int(y_final), die.available)
            transformed_dies.append(transformed_die)
        
        return transformed_dies
    
    def get_output_format(self) -> str:
        """Return ASML's required output format."""
        return "JSON"
    
    def export_to_vendor_format(self, dies: List[Die]) -> str:
        """Export dies to ASML JSON format.
        
        ASML JSON structure typically includes:
        - Recipe metadata
        - Site coordinates with SiteX/SiteY fields
        - Tool-specific parameters
        """
        transformed_dies = self.transform(dies)
        
        # Build ASML-compatible JSON structure
        asml_data = {
            "RecipeType": "WaferSampling",
            "ToolModel": "ASML",
            "CoordinateSystem": "CenterOrigin",
            "Units": "Micrometers",
            "SamplingStrategy": {
                "TotalSites": len(transformed_dies),
                "Sites": [
                    {
                        "SiteID": i + 1,
                        "SiteX": die.x,
                        "SiteY": die.y,
                        "Enabled": die.available
                    }
                    for i, die in enumerate(transformed_dies)
                ]
            },
            "TransformationParameters": {
                "RotationAngle": self.rotation_angle,
                "ScaleFactor": self.scale_factor,
                "OffsetX": self.offset_x,
                "OffsetY": self.offset_y
            }
        }
        
        return json.dumps(asml_data, indent=2)