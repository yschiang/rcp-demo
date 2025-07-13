"""
GDSII format parser for IC layout files.

GDSII is a binary format used for describing planar geometric shapes,
text labels, and other information about integrated circuits.
This parser extracts die boundaries for wafer sampling strategy validation.
"""
import uuid
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path
import logging

try:
    import gdspy
except ImportError:
    gdspy = None

from ..models.schematic import (
    SchematicData, SchematicFormat, CoordinateSystem, DieBoundary, SchematicMetadata
)

logger = logging.getLogger(__name__)


class GDSIIParser:
    """Parser for GDSII layout files to extract die boundaries."""
    
    def __init__(self):
        if gdspy is None:
            raise ImportError("gdspy is required for GDSII parsing. Install with: pip install gdspy")
        
        # Configuration for die detection
        self.die_detection_config = {
            'min_die_size': 1000,  # Minimum die dimension in GDSII units
            'max_die_size': 50000,  # Maximum die dimension in GDSII units
            'boundary_layer': None,  # Auto-detect boundary layer if None
            'text_layers': [1, 2, 63],  # Common text layers for die IDs
            'merge_threshold': 100,  # Distance threshold for merging boundaries
        }
    
    def parse_file(self, file_path: str, **kwargs) -> SchematicData:
        """
        Parse a GDSII file and extract die boundary information.
        
        Args:
            file_path: Path to the GDSII file
            **kwargs: Additional parsing options:
                - die_size_filter: (min_size, max_size) tuple
                - target_cell: Name of specific cell to parse
                - coordinate_scale: Scale factor for coordinates
        
        Returns:
            SchematicData object with parsed die boundaries
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"GDSII file not found: {file_path}")
        
        logger.info(f"Parsing GDSII file: {file_path}")
        
        try:
            # Load GDSII library
            gdsii_lib = gdspy.GdsLibrary(infile=str(file_path))
            
            # Extract metadata
            metadata = self._extract_metadata(file_path, gdsii_lib)
            
            # Find the main cell (usually the top cell)
            target_cell = kwargs.get('target_cell')
            main_cell = self._find_main_cell(gdsii_lib, target_cell)
            
            if not main_cell:
                raise ValueError("No suitable cell found in GDSII file")
            
            logger.info(f"Processing cell: {main_cell.name}")
            
            # Extract die boundaries
            die_boundaries = self._extract_die_boundaries(main_cell, **kwargs)
            
            # Validate and process boundaries
            die_boundaries = self._process_boundaries(die_boundaries, **kwargs)
            
            logger.info(f"Extracted {len(die_boundaries)} die boundaries")
            
            return SchematicData(
                id=str(uuid.uuid4()),
                filename=file_path.name,
                format_type=SchematicFormat.GDSII,
                upload_date=datetime.utcnow(),
                die_boundaries=die_boundaries,
                coordinate_system=CoordinateSystem.GDSII_UNITS,
                wafer_size=self._estimate_wafer_size(die_boundaries),
                metadata=metadata
            )
            
        except Exception as e:
            logger.error(f"Error parsing GDSII file {file_path}: {str(e)}")
            raise ValueError(f"Failed to parse GDSII file: {str(e)}")
    
    def _extract_metadata(self, file_path: Path, gdsii_lib: 'gdspy.GdsLibrary') -> SchematicMetadata:
        """Extract metadata from GDSII file and library."""
        file_stats = file_path.stat()
        
        # Extract library information
        lib_info = {
            'library_name': getattr(gdsii_lib, 'name', 'Unknown'),
            'units': f"User units: {gdsii_lib.unit}, DB units: {gdsii_lib.precision}",
            'cell_count': len(gdsii_lib.cell_dict),
            'cell_names': list(gdsii_lib.cell_dict.keys())[:10]  # First 10 cells
        }
        
        return SchematicMetadata(
            original_filename=file_path.name,
            file_size=file_stats.st_size,
            creation_date=datetime.fromtimestamp(file_stats.st_mtime),
            software_info="GDSII Stream Format",
            units=f"{gdsii_lib.unit} user units, {gdsii_lib.precision} database units",
            scale_factor=gdsii_lib.unit,
            layer_info=lib_info,
            custom_attributes={}
        )
    
    def _find_main_cell(self, gdsii_lib: 'gdspy.GdsLibrary', target_cell: Optional[str] = None) -> Optional['gdspy.Cell']:
        """Find the main cell to process (top cell or specified cell)."""
        if target_cell:
            return gdsii_lib.cell_dict.get(target_cell)
        
        # Find top cells (cells not referenced by others)
        all_cells = set(gdsii_lib.cell_dict.keys())
        referenced_cells = set()
        
        for cell in gdsii_lib.cell_dict.values():
            for ref in cell.references:
                if hasattr(ref, 'ref_cell'):
                    referenced_cells.add(ref.ref_cell.name)
        
        top_cells = all_cells - referenced_cells
        
        if not top_cells:
            # If no clear top cell, use the first cell
            return next(iter(gdsii_lib.cell_dict.values()))
        
        # Return the first top cell
        return gdsii_lib.cell_dict[next(iter(top_cells))]
    
    def _extract_die_boundaries(self, cell: 'gdspy.Cell', **kwargs) -> List[DieBoundary]:
        """Extract die boundaries from a GDSII cell."""
        die_boundaries = []
        coordinate_scale = kwargs.get('coordinate_scale', 1.0)
        
        # Method 1: Look for rectangular boundaries on specific layers
        boundaries_from_shapes = self._extract_from_shapes(cell, coordinate_scale)
        die_boundaries.extend(boundaries_from_shapes)
        
        # Method 2: Look for text labels that might indicate die positions
        boundaries_from_text = self._extract_from_text_labels(cell, coordinate_scale)
        die_boundaries.extend(boundaries_from_text)
        
        # Method 3: If no explicit boundaries found, try to infer from cell references
        if not die_boundaries:
            boundaries_from_refs = self._extract_from_references(cell, coordinate_scale)
            die_boundaries.extend(boundaries_from_refs)
        
        return die_boundaries
    
    def _extract_from_shapes(self, cell: 'gdspy.Cell', scale: float) -> List[DieBoundary]:
        """Extract die boundaries from rectangular shapes."""
        boundaries = []
        die_counter = 0
        
        # Process polygons
        for polygon in cell.polygons:
            bbox = polygon.get_bounding_box()
            if bbox is None:
                continue
            
            width = (bbox[1][0] - bbox[0][0]) * scale
            height = (bbox[1][1] - bbox[0][1]) * scale
            
            # Filter by size to identify likely die boundaries
            if (self.die_detection_config['min_die_size'] <= width <= self.die_detection_config['max_die_size'] and
                self.die_detection_config['min_die_size'] <= height <= self.die_detection_config['max_die_size']):
                
                die_counter += 1
                center_x = (bbox[0][0] + bbox[1][0]) / 2 * scale
                center_y = (bbox[0][1] + bbox[1][1]) / 2 * scale
                
                boundary = DieBoundary(
                    die_id=f"die_{die_counter}",
                    x_min=bbox[0][0] * scale,
                    y_min=bbox[0][1] * scale,
                    x_max=bbox[1][0] * scale,
                    y_max=bbox[1][1] * scale,
                    center_x=center_x,
                    center_y=center_y,
                    available=True,
                    metadata={
                        'layer': polygon.layer,
                        'datatype': polygon.datatype,
                        'source': 'shape_detection'
                    }
                )
                boundaries.append(boundary)
        
        return boundaries
    
    def _extract_from_text_labels(self, cell: 'gdspy.Cell', scale: float) -> List[DieBoundary]:
        """Extract die positions from text labels."""
        boundaries = []
        
        for label in cell.labels:
            if hasattr(label, 'position') and hasattr(label, 'text'):
                # Assume text represents die ID and position represents center
                pos_x, pos_y = label.position[0] * scale, label.position[1] * scale
                
                # Estimate die size (could be made configurable)
                estimated_size = 5000 * scale  # Default die size
                half_size = estimated_size / 2
                
                boundary = DieBoundary(
                    die_id=label.text,
                    x_min=pos_x - half_size,
                    y_min=pos_y - half_size,
                    x_max=pos_x + half_size,
                    y_max=pos_y + half_size,
                    center_x=pos_x,
                    center_y=pos_y,
                    available=True,
                    metadata={
                        'layer': label.layer,
                        'source': 'text_label',
                        'original_text': label.text
                    }
                )
                boundaries.append(boundary)
        
        return boundaries
    
    def _extract_from_references(self, cell: 'gdspy.Cell', scale: float) -> List[DieBoundary]:
        """Extract die boundaries from cell references (instances)."""
        boundaries = []
        die_counter = 0
        
        for ref in cell.references:
            if hasattr(ref, 'ref_cell') and hasattr(ref, 'origin'):
                bbox = ref.get_bounding_box()
                if bbox is None:
                    continue
                
                die_counter += 1
                center_x = (bbox[0][0] + bbox[1][0]) / 2 * scale
                center_y = (bbox[0][1] + bbox[1][1]) / 2 * scale
                
                boundary = DieBoundary(
                    die_id=f"ref_{die_counter}_{ref.ref_cell.name}",
                    x_min=bbox[0][0] * scale,
                    y_min=bbox[0][1] * scale,
                    x_max=bbox[1][0] * scale,
                    y_max=bbox[1][1] * scale,
                    center_x=center_x,
                    center_y=center_y,
                    available=True,
                    metadata={
                        'source': 'cell_reference',
                        'ref_cell': ref.ref_cell.name,
                        'origin': ref.origin,
                        'rotation': getattr(ref, 'rotation', 0),
                        'magnification': getattr(ref, 'magnification', 1)
                    }
                )
                boundaries.append(boundary)
        
        return boundaries
    
    def _process_boundaries(self, boundaries: List[DieBoundary], **kwargs) -> List[DieBoundary]:
        """Process and validate extracted boundaries."""
        if not boundaries:
            return boundaries
        
        # Apply size filtering if specified
        die_size_filter = kwargs.get('die_size_filter')
        if die_size_filter:
            min_size, max_size = die_size_filter
            boundaries = [
                b for b in boundaries 
                if min_size <= b.width <= max_size and min_size <= b.height <= max_size
            ]
        
        # Remove duplicates based on position
        merge_threshold = self.die_detection_config['merge_threshold']
        unique_boundaries = []
        
        for boundary in boundaries:
            is_duplicate = False
            for existing in unique_boundaries:
                distance = ((boundary.center_x - existing.center_x)**2 + 
                           (boundary.center_y - existing.center_y)**2)**0.5
                if distance < merge_threshold:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_boundaries.append(boundary)
        
        # Sort by position for consistent ordering
        unique_boundaries.sort(key=lambda b: (b.center_y, b.center_x))
        
        # Reassign die IDs for consistency
        for i, boundary in enumerate(unique_boundaries):
            boundary.die_id = f"die_{i+1:03d}"
        
        return unique_boundaries
    
    def _estimate_wafer_size(self, boundaries: List[DieBoundary]) -> Optional[str]:
        """Estimate wafer size based on die layout bounds."""
        if not boundaries:
            return None
        
        # Calculate overall layout dimensions
        x_coords = [b.center_x for b in boundaries]
        y_coords = [b.center_y for b in boundaries]
        
        layout_width = max(x_coords) - min(x_coords)
        layout_height = max(y_coords) - min(y_coords)
        layout_diameter = max(layout_width, layout_height)
        
        # Estimate wafer size based on layout diameter (in mm, assuming typical scaling)
        # This is a rough estimation and should be calibrated for specific processes
        if layout_diameter < 50000:
            return "100mm"
        elif layout_diameter < 100000:
            return "150mm"
        elif layout_diameter < 150000:
            return "200mm"
        elif layout_diameter < 200000:
            return "300mm"
        else:
            return "300mm+"
    
    def get_supported_extensions(self) -> List[str]:
        """Return list of supported file extensions."""
        return ['.gds', '.gdsii']
    
    def validate_file(self, file_path: str) -> bool:
        """Validate if file is a valid GDSII file."""
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                return False
            
            # Check file extension
            if file_path.suffix.lower() not in self.get_supported_extensions():
                return False
            
            # Try to load the file header
            gdspy.GdsLibrary(infile=str(file_path))
            return True
            
        except Exception:
            return False