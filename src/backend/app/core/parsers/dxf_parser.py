"""
DXF format parser for CAD drawing files.

DXF (Drawing Exchange Format) is a CAD data file format used for 
2D and 3D design data and metadata. This parser extracts die boundaries
and coordinate information for wafer sampling strategy validation.
"""
import uuid
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path
import logging

try:
    import ezdxf
except ImportError:
    ezdxf = None

from ..models.schematic import (
    SchematicData, SchematicFormat, CoordinateSystem, DieBoundary, SchematicMetadata
)

logger = logging.getLogger(__name__)


class DXFParser:
    """Parser for DXF CAD files to extract die boundaries."""
    
    def __init__(self):
        if ezdxf is None:
            raise ImportError("ezdxf is required for DXF parsing. Install with: pip install ezdxf")
        
        # Configuration for die detection
        self.die_detection_config = {
            'min_die_size': 1.0,  # Minimum die dimension in drawing units
            'max_die_size': 100.0,  # Maximum die dimension in drawing units
            'target_layers': None,  # Auto-detect layers if None
            'entity_types': ['LWPOLYLINE', 'POLYLINE', 'RECTANGLE', 'CIRCLE', 'INSERT'],
            'text_layers': ['TEXT', 'MTEXT'],  # Text entity types for die IDs
        }
    
    def parse_file(self, file_path: str, **kwargs) -> SchematicData:
        """
        Parse a DXF file and extract die boundary information.
        
        Args:
            file_path: Path to the DXF file
            **kwargs: Additional parsing options:
                - die_size_filter: (min_size, max_size) tuple
                - target_layers: List of layer names to process
                - coordinate_scale: Scale factor for coordinates
                - layout_space: Expected layout space name
        
        Returns:
            SchematicData object with parsed die boundaries
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"DXF file not found: {file_path}")
        
        logger.info(f"Parsing DXF file: {file_path}")
        
        try:
            # Load DXF document
            doc = ezdxf.readfile(str(file_path))
            
            # Extract metadata
            metadata = self._extract_metadata(file_path, doc)
            
            # Get model space (main drawing area)
            msp = doc.modelspace()
            
            # Extract die boundaries
            die_boundaries = self._extract_die_boundaries(msp, doc, **kwargs)
            
            # Validate and process boundaries
            die_boundaries = self._process_boundaries(die_boundaries, **kwargs)
            
            logger.info(f"Extracted {len(die_boundaries)} die boundaries from DXF")
            
            return SchematicData(
                id=str(uuid.uuid4()),
                filename=file_path.name,
                format_type=SchematicFormat.DXF,
                upload_date=datetime.utcnow(),
                die_boundaries=die_boundaries,
                coordinate_system=CoordinateSystem.CAD_UNITS,
                wafer_size=self._estimate_wafer_size(die_boundaries),
                metadata=metadata
            )
            
        except Exception as e:
            logger.error(f"Error parsing DXF file {file_path}: {str(e)}")
            raise ValueError(f"Failed to parse DXF file: {str(e)}")
    
    def _extract_metadata(self, file_path: Path, doc: 'ezdxf.Document') -> SchematicMetadata:
        """Extract metadata from DXF file and document."""
        file_stats = file_path.stat()
        
        # Extract DXF header information
        header_info = {}
        try:
            header_info = {
                'dxf_version': doc.dxfversion,
                'acadver': doc.header.get('$ACADVER', 'Unknown'),
                'units': self._get_units_info(doc),
                'layers': [layer.dxf.name for layer in doc.layers][:20],  # First 20 layers
                'block_count': len(doc.blocks),
                'entity_count': len(list(doc.modelspace()))
            }
        except Exception as e:
            logger.warning(f"Could not extract full DXF header info: {e}")
        
        return SchematicMetadata(
            original_filename=file_path.name,
            file_size=file_stats.st_size,
            creation_date=datetime.fromtimestamp(file_stats.st_mtime),
            software_info=f"DXF {doc.dxfversion}",
            units=header_info.get('units', 'Unknown'),
            scale_factor=1.0,
            layer_info=header_info,
            custom_attributes={}
        )
    
    def _get_units_info(self, doc: 'ezdxf.Document') -> str:
        """Extract units information from DXF header."""
        try:
            units_code = doc.header.get('$INSUNITS', 0)
            units_map = {
                0: 'Unitless',
                1: 'Inches',
                2: 'Feet',
                3: 'Miles',
                4: 'Millimeters',
                5: 'Centimeters',
                6: 'Meters',
                7: 'Kilometers',
                8: 'Microinches',
                9: 'Mils',
                10: 'Yards',
                11: 'Angstroms',
                12: 'Nanometers',
                13: 'Microns',
                14: 'Decimeters',
                15: 'Decameters',
                16: 'Hectometers',
                17: 'Gigameters',
                18: 'Astronomical units',
                19: 'Light years',
                20: 'Parsecs'
            }
            return units_map.get(units_code, f'Unknown ({units_code})')
        except:
            return 'Unknown'
    
    def _extract_die_boundaries(self, msp: 'ezdxf.layouts.Modelspace', 
                               doc: 'ezdxf.Document', **kwargs) -> List[DieBoundary]:
        """Extract die boundaries from DXF model space."""
        die_boundaries = []
        coordinate_scale = kwargs.get('coordinate_scale', 1.0)
        target_layers = kwargs.get('target_layers', [])
        
        # Method 1: Extract from geometric entities (rectangles, polylines)
        boundaries_from_geometry = self._extract_from_geometry(msp, coordinate_scale, target_layers)
        die_boundaries.extend(boundaries_from_geometry)
        
        # Method 2: Extract from text entities that might indicate die positions
        boundaries_from_text = self._extract_from_text(msp, coordinate_scale, target_layers)
        die_boundaries.extend(boundaries_from_text)
        
        # Method 3: Extract from block inserts (repeated elements)
        boundaries_from_blocks = self._extract_from_blocks(msp, doc, coordinate_scale, target_layers)
        die_boundaries.extend(boundaries_from_blocks)
        
        return die_boundaries
    
    def _extract_from_geometry(self, msp: 'ezdxf.layouts.Modelspace', 
                              scale: float, target_layers: List[str]) -> List[DieBoundary]:
        """Extract die boundaries from geometric entities."""
        boundaries = []
        die_counter = 0
        
        # Process different entity types
        for entity_type in self.die_detection_config['entity_types']:
            for entity in msp.query(entity_type):
                # Filter by layer if specified
                if target_layers and entity.dxf.layer not in target_layers:
                    continue
                
                bbox = self._get_entity_bounding_box(entity)
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
                        die_id=f"die_{die_counter:03d}",
                        x_min=bbox[0][0] * scale,
                        y_min=bbox[0][1] * scale,
                        x_max=bbox[1][0] * scale,
                        y_max=bbox[1][1] * scale,
                        center_x=center_x,
                        center_y=center_y,
                        available=True,
                        metadata={
                            'layer': entity.dxf.layer,
                            'entity_type': entity.dxftype(),
                            'color': getattr(entity.dxf, 'color', None),
                            'source': 'geometry_detection'
                        }
                    )
                    boundaries.append(boundary)
        
        return boundaries
    
    def _extract_from_text(self, msp: 'ezdxf.layouts.Modelspace', 
                          scale: float, target_layers: List[str]) -> List[DieBoundary]:
        """Extract die positions from text entities."""
        boundaries = []
        
        for text_type in self.die_detection_config['text_layers']:
            for text_entity in msp.query(text_type):
                # Filter by layer if specified
                if target_layers and text_entity.dxf.layer not in target_layers:
                    continue
                
                try:
                    # Get text position and content
                    if hasattr(text_entity.dxf, 'insert'):
                        pos = text_entity.dxf.insert
                        text_content = getattr(text_entity.dxf, 'text', '')
                    elif hasattr(text_entity.dxf, 'x') and hasattr(text_entity.dxf, 'y'):
                        pos = (text_entity.dxf.x, text_entity.dxf.y, 0)
                        text_content = getattr(text_entity.dxf, 'text', '')
                    else:
                        continue
                    
                    pos_x, pos_y = pos[0] * scale, pos[1] * scale
                    
                    # Estimate die size based on text height or use default
                    text_height = getattr(text_entity.dxf, 'height', 1.0)
                    estimated_size = max(text_height * 10, 5.0) * scale
                    half_size = estimated_size / 2
                    
                    boundary = DieBoundary(
                        die_id=text_content or f"text_die_{len(boundaries)+1}",
                        x_min=pos_x - half_size,
                        y_min=pos_y - half_size,
                        x_max=pos_x + half_size,
                        y_max=pos_y + half_size,
                        center_x=pos_x,
                        center_y=pos_y,
                        available=True,
                        metadata={
                            'layer': text_entity.dxf.layer,
                            'source': 'text_detection',
                            'original_text': text_content,
                            'text_height': text_height
                        }
                    )
                    boundaries.append(boundary)
                    
                except Exception as e:
                    logger.warning(f"Error processing text entity: {e}")
                    continue
        
        return boundaries
    
    def _extract_from_blocks(self, msp: 'ezdxf.layouts.Modelspace', 
                            doc: 'ezdxf.Document', scale: float, 
                            target_layers: List[str]) -> List[DieBoundary]:
        """Extract die boundaries from block inserts (repeated elements)."""
        boundaries = []
        die_counter = 0
        
        for insert in msp.query('INSERT'):
            # Filter by layer if specified
            if target_layers and insert.dxf.layer not in target_layers:
                continue
            
            try:
                # Get block definition
                block_name = insert.dxf.name
                if block_name not in doc.blocks:
                    continue
                
                block = doc.blocks[block_name]
                
                # Calculate block bounding box
                block_bbox = self._get_block_bounding_box(block)
                if block_bbox is None:
                    continue
                
                # Apply insert transformation
                insert_point = insert.dxf.insert
                scale_factors = (
                    getattr(insert.dxf, 'xscale', 1.0),
                    getattr(insert.dxf, 'yscale', 1.0)
                )
                
                # Transform bounding box
                transformed_bbox = self._transform_bbox(
                    block_bbox, insert_point, scale_factors
                )
                
                width = (transformed_bbox[1][0] - transformed_bbox[0][0]) * scale
                height = (transformed_bbox[1][1] - transformed_bbox[0][1]) * scale
                
                # Filter by size
                if (self.die_detection_config['min_die_size'] <= width <= self.die_detection_config['max_die_size'] and
                    self.die_detection_config['min_die_size'] <= height <= self.die_detection_config['max_die_size']):
                    
                    die_counter += 1
                    center_x = (transformed_bbox[0][0] + transformed_bbox[1][0]) / 2 * scale
                    center_y = (transformed_bbox[0][1] + transformed_bbox[1][1]) / 2 * scale
                    
                    boundary = DieBoundary(
                        die_id=f"block_{die_counter:03d}_{block_name}",
                        x_min=transformed_bbox[0][0] * scale,
                        y_min=transformed_bbox[0][1] * scale,
                        x_max=transformed_bbox[1][0] * scale,
                        y_max=transformed_bbox[1][1] * scale,
                        center_x=center_x,
                        center_y=center_y,
                        available=True,
                        metadata={
                            'layer': insert.dxf.layer,
                            'source': 'block_insert',
                            'block_name': block_name,
                            'insert_point': insert_point,
                            'scale_factors': scale_factors
                        }
                    )
                    boundaries.append(boundary)
                    
            except Exception as e:
                logger.warning(f"Error processing block insert: {e}")
                continue
        
        return boundaries
    
    def _get_entity_bounding_box(self, entity) -> Optional[Tuple[Tuple[float, float], Tuple[float, float]]]:
        """Get bounding box for a DXF entity."""
        try:
            # Try to use ezdxf's bounding box calculation
            if hasattr(entity, 'bounding_box'):
                bbox = entity.bounding_box
                return ((bbox.extmin.x, bbox.extmin.y), (bbox.extmax.x, bbox.extmax.y))
            
            # Manual calculation for specific entity types
            entity_type = entity.dxftype()
            
            if entity_type in ['LWPOLYLINE', 'POLYLINE']:
                points = []
                if hasattr(entity, 'vertices'):
                    points = [(v.dxf.location.x, v.dxf.location.y) for v in entity.vertices]
                elif hasattr(entity, 'get_points'):
                    points = [(p[0], p[1]) for p in entity.get_points()]
                
                if points:
                    x_coords = [p[0] for p in points]
                    y_coords = [p[1] for p in points]
                    return ((min(x_coords), min(y_coords)), (max(x_coords), max(y_coords)))
            
            elif entity_type == 'CIRCLE':
                center = entity.dxf.center
                radius = entity.dxf.radius
                return ((center.x - radius, center.y - radius), 
                       (center.x + radius, center.y + radius))
            
            elif entity_type == 'RECTANGLE':
                # Rectangle entities have width and height
                insert = entity.dxf.insert
                width = getattr(entity.dxf, 'width', 0)
                height = getattr(entity.dxf, 'height', 0)
                return ((insert.x, insert.y), (insert.x + width, insert.y + height))
            
        except Exception as e:
            logger.warning(f"Error calculating bounding box for {entity.dxftype()}: {e}")
        
        return None
    
    def _get_block_bounding_box(self, block) -> Optional[Tuple[Tuple[float, float], Tuple[float, float]]]:
        """Calculate bounding box for a block definition."""
        try:
            x_coords, y_coords = [], []
            
            for entity in block:
                bbox = self._get_entity_bounding_box(entity)
                if bbox:
                    x_coords.extend([bbox[0][0], bbox[1][0]])
                    y_coords.extend([bbox[0][1], bbox[1][1]])
            
            if x_coords and y_coords:
                return ((min(x_coords), min(y_coords)), (max(x_coords), max(y_coords)))
            
        except Exception as e:
            logger.warning(f"Error calculating block bounding box: {e}")
        
        return None
    
    def _transform_bbox(self, bbox: Tuple[Tuple[float, float], Tuple[float, float]], 
                       insert_point: Tuple[float, float, float], 
                       scale_factors: Tuple[float, float]) -> Tuple[Tuple[float, float], Tuple[float, float]]:
        """Transform bounding box based on insert parameters."""
        # Apply scaling
        width = (bbox[1][0] - bbox[0][0]) * scale_factors[0]
        height = (bbox[1][1] - bbox[0][1]) * scale_factors[1]
        
        # Apply translation
        new_min_x = insert_point[0] + bbox[0][0] * scale_factors[0]
        new_min_y = insert_point[1] + bbox[0][1] * scale_factors[1]
        
        return ((new_min_x, new_min_y), (new_min_x + width, new_min_y + height))
    
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
        merge_threshold = 0.1  # Small threshold for DXF coordinates
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
            if not boundary.die_id.startswith('text_'):  # Preserve text-based IDs
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
        
        # Estimate wafer size based on layout diameter (assuming mm units)
        if layout_diameter < 50:
            return "100mm"
        elif layout_diameter < 100:
            return "150mm"
        elif layout_diameter < 150:
            return "200mm"
        elif layout_diameter < 300:
            return "300mm"
        else:
            return "300mm+"
    
    def get_supported_extensions(self) -> List[str]:
        """Return list of supported file extensions."""
        return ['.dxf']
    
    def validate_file(self, file_path: str) -> bool:
        """Validate if file is a valid DXF file."""
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                return False
            
            # Check file extension
            if file_path.suffix.lower() not in self.get_supported_extensions():
                return False
            
            # Try to load the file
            ezdxf.readfile(str(file_path))
            return True
            
        except Exception:
            return False