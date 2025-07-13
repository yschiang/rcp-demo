import xml.etree.ElementTree as ET
from typing import List
from .base import VendorMapping
from ..models.die import Die


class KLAMapping(VendorMapping):
    """KLA vendor-specific coordinate transformation and export.
    
    KLA inspection tools typically use:
    - Corner-origin coordinate system (bottom-left)
    - Millimeter units
    - XML format for recipe files
    - Specific field names (X_Position, Y_Position)
    """
    
    def __init__(self, coordinate_system: str = "CornerOrigin", units: str = "Millimeters", flip_y: bool = False):
        """Initialize KLA mapping with transformation parameters.
        
        Args:
            coordinate_system: Coordinate system type (default: "CornerOrigin")
            units: Unit system (default: "Millimeters")
            flip_y: Whether to flip Y coordinates (default: False)
        """
        self.coordinate_system = coordinate_system
        self.units = units
        self.flip_y = flip_y
    
    def transform(self, dies: List[Die]) -> List[Die]:
        """Transform die coordinates to KLA format.
        
        KLA transformation:
        1. Convert to corner-origin coordinate system
        2. Apply Y-flip if specified (some KLA tools expect inverted Y)
        3. Keep coordinates in millimeters (no scaling)
        4. Ensure non-negative coordinates
        """
        if not dies:
            return []
        
        transformed_dies = []
        
        # Find coordinate bounds for corner-origin conversion
        min_x = min(die.x for die in dies)
        min_y = min(die.y for die in dies)
        max_y = max(die.y for die in dies) if self.flip_y else 0
        
        for die in dies:
            # Convert to corner-origin (ensure non-negative coordinates)
            x_corner = die.x - min_x if min_x < 0 else die.x
            y_corner = die.y - min_y if min_y < 0 else die.y
            
            # Apply Y-flip if specified
            if self.flip_y:
                y_corner = max_y - y_corner
            
            # Create transformed die
            transformed_die = Die(int(x_corner), int(y_corner), die.available)
            transformed_dies.append(transformed_die)
        
        return transformed_dies
    
    def get_output_format(self) -> str:
        """Return KLA's required output format."""
        return "XML"
    
    def export_to_vendor_format(self, dies: List[Die]) -> str:
        """Export dies to KLA XML format.
        
        KLA XML structure typically includes:
        - Recipe header with tool information
        - Site definitions with X_Position/Y_Position
        - Inspection parameters
        """
        transformed_dies = self.transform(dies)
        
        # Build KLA-compatible XML structure
        root = ET.Element("KLA_InspectionRecipe")
        root.set("version", "1.0")
        
        # Header section
        header = ET.SubElement(root, "Header")
        ET.SubElement(header, "ToolType").text = "KLA"
        ET.SubElement(header, "CoordinateSystem").text = self.coordinate_system
        ET.SubElement(header, "Units").text = self.units
        ET.SubElement(header, "TotalSites").text = str(len(transformed_dies))
        
        # Recipe parameters
        recipe_params = ET.SubElement(root, "RecipeParameters")
        ET.SubElement(recipe_params, "SamplingMode").text = "UserDefined"
        ET.SubElement(recipe_params, "InspectionType").text = "Wafer"
        
        # Site definitions
        sites = ET.SubElement(root, "SiteDefinitions")
        
        for i, die in enumerate(transformed_dies):
            site = ET.SubElement(sites, "Site")
            site.set("ID", str(i + 1))
            
            ET.SubElement(site, "X_Position").text = str(die.x)
            ET.SubElement(site, "Y_Position").text = str(die.y)
            ET.SubElement(site, "Enabled").text = str(die.available).lower()
            ET.SubElement(site, "InspectionMode").text = "Standard"
        
        # Transformation metadata
        transform_info = ET.SubElement(root, "TransformationInfo")
        ET.SubElement(transform_info, "CoordinateSystem").text = self.coordinate_system
        ET.SubElement(transform_info, "Units").text = self.units
        ET.SubElement(transform_info, "YFlipped").text = str(self.flip_y).lower()
        
        # Convert to string with proper formatting
        rough_string = ET.tostring(root, encoding='unicode')
        
        # Add XML declaration and format
        xml_declaration = '<?xml version="1.0" encoding="UTF-8"?>\n'
        return xml_declaration + rough_string