"""
SVG format parser for web-friendly schematic files.

SVG (Scalable Vector Graphics) is an XML-based vector image format
that can contain 2D graphics. This parser extracts die boundaries
from SVG representations of wafer layouts.
"""
import uuid
import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path
import logging
import re

try:
    from svglib.svglib import SvgShapeConverter
    from reportlab.graphics import renderPDF
except ImportError:
    SvgShapeConverter = None

from ..models.schematic import (
    SchematicData, SchematicFormat, CoordinateSystem, DieBoundary, SchematicMetadata
)

logger = logging.getLogger(__name__)


class SVGParser:
    """Parser for SVG files to extract die boundaries."""
    
    def __init__(self):
        # SVG namespace
        self.svg_ns = {'svg': 'http://www.w3.org/2000/svg'}
        
        # Configuration for die detection
        self.die_detection_config = {
            'min_die_size': 5.0,  # Minimum die dimension in SVG units
            'max_die_size': 200.0,  # Maximum die dimension in SVG units
            'target_shapes': ['rect', 'circle', 'ellipse', 'polygon', 'path'],
            'text_elements': ['text', 'tspan'],
            'group_elements': ['g', 'symbol', 'use'],
            'die_id_patterns': [r'die[_\-]?\d+', r'cell[_\-]?\d+', r'\d+'],
        }
    
    def parse_file(self, file_path: str, **kwargs) -> SchematicData:
        """
        Parse an SVG file and extract die boundary information.
        
        Args:
            file_path: Path to the SVG file
            **kwargs: Additional parsing options:
                - die_size_filter: (min_size, max_size) tuple
                - coordinate_scale: Scale factor for coordinates
                - viewport_size: Expected viewport dimensions
                - target_layer: Specific layer/group to process
        
        Returns:
            SchematicData object with parsed die boundaries
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"SVG file not found: {file_path}")
        
        logger.info(f"Parsing SVG file: {file_path}")
        
        try:
            # Parse XML structure
            tree = ET.parse(str(file_path))
            root = tree.getroot()
            
            # Extract metadata
            metadata = self._extract_metadata(file_path, root)
            
            # Extract die boundaries
            die_boundaries = self._extract_die_boundaries(root, **kwargs)
            
            # Validate and process boundaries
            die_boundaries = self._process_boundaries(die_boundaries, **kwargs)
            
            logger.info(f"Extracted {len(die_boundaries)} die boundaries from SVG")
            
            return SchematicData(
                id=str(uuid.uuid4()),
                filename=file_path.name,
                format_type=SchematicFormat.SVG,
                upload_date=datetime.utcnow(),
                die_boundaries=die_boundaries,
                coordinate_system=CoordinateSystem.CARTESIAN,
                wafer_size=self._estimate_wafer_size(die_boundaries),
                metadata=metadata
            )
            
        except Exception as e:
            logger.error(f"Error parsing SVG file {file_path}: {str(e)}")
            raise ValueError(f"Failed to parse SVG file: {str(e)}")
    
    def _extract_metadata(self, file_path: Path, root: ET.Element) -> SchematicMetadata:
        """Extract metadata from SVG file and root element."""
        file_stats = file_path.stat()
        
        # Extract SVG document information
        svg_info = {}
        try:
            # Get viewBox and dimensions
            viewbox = root.get('viewBox', '')
            width = root.get('width', '')
            height = root.get('height', '')
            
            # Extract title and description
            title_elem = root.find('.//svg:title', self.svg_ns)
            desc_elem = root.find('.//svg:desc', self.svg_ns)
            
            svg_info = {
                'viewBox': viewbox,
                'width': width,
                'height': height,
                'title': title_elem.text if title_elem is not None else None,
                'description': desc_elem.text if desc_elem is not None else None,
                'element_count': len(list(root.iter())),
                'namespaces': dict(root.attrib) if hasattr(root, 'attrib') else {}
            }
            
            # Count different element types
            element_counts = {}
            for elem in root.iter():
                tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
                element_counts[tag] = element_counts.get(tag, 0) + 1
            svg_info['element_counts'] = element_counts
            
        except Exception as e:
            logger.warning(f"Could not extract full SVG metadata: {e}")
        
        return SchematicMetadata(
            original_filename=file_path.name,
            file_size=file_stats.st_size,
            creation_date=datetime.fromtimestamp(file_stats.st_mtime),
            software_info="SVG (Scalable Vector Graphics)",
            units="SVG user units",
            scale_factor=1.0,
            layer_info=svg_info,
            custom_attributes={}
        )
    
    def _extract_die_boundaries(self, root: ET.Element, **kwargs) -> List[DieBoundary]:
        """Extract die boundaries from SVG elements."""
        die_boundaries = []
        coordinate_scale = kwargs.get('coordinate_scale', 1.0)
        target_layer = kwargs.get('target_layer')
        
        # Method 1: Extract from shape elements (rect, circle, etc.)
        boundaries_from_shapes = self._extract_from_shapes(root, coordinate_scale, target_layer)
        die_boundaries.extend(boundaries_from_shapes)
        
        # Method 2: Extract from text elements that might indicate die positions
        boundaries_from_text = self._extract_from_text(root, coordinate_scale, target_layer)
        die_boundaries.extend(boundaries_from_text)
        
        # Method 3: Extract from grouped elements and symbols
        boundaries_from_groups = self._extract_from_groups(root, coordinate_scale, target_layer)
        die_boundaries.extend(boundaries_from_groups)
        
        return die_boundaries
    
    def _extract_from_shapes(self, root: ET.Element, scale: float, target_layer: Optional[str]) -> List[DieBoundary]:
        """Extract die boundaries from shape elements."""
        boundaries = []
        die_counter = 0
        
        for shape_type in self.die_detection_config['target_shapes']:
            for elem in root.iter(f'{{{self.svg_ns["svg"]}}}{shape_type}'):
                # Filter by layer/group if specified
                if target_layer and not self._is_in_target_layer(elem, target_layer):
                    continue
                
                bbox = self._get_element_bounding_box(elem)
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
                    
                    # Extract element attributes
                    element_id = elem.get('id', f'{shape_type}_{die_counter}')
                    
                    boundary = DieBoundary(
                        die_id=element_id,
                        x_min=bbox[0][0] * scale,
                        y_min=bbox[0][1] * scale,
                        x_max=bbox[1][0] * scale,
                        y_max=bbox[1][1] * scale,
                        center_x=center_x,
                        center_y=center_y,
                        available=True,
                        metadata={
                            'element_type': shape_type,
                            'element_id': element_id,
                            'class': elem.get('class'),
                            'style': elem.get('style'),
                            'source': 'shape_detection'
                        }
                    )
                    boundaries.append(boundary)
        
        return boundaries
    
    def _extract_from_text(self, root: ET.Element, scale: float, target_layer: Optional[str]) -> List[DieBoundary]:
        """Extract die positions from text elements."""
        boundaries = []
        
        for text_type in self.die_detection_config['text_elements']:
            for elem in root.iter(f'{{{self.svg_ns["svg"]}}}{text_type}'):
                # Filter by layer/group if specified
                if target_layer and not self._is_in_target_layer(elem, target_layer):
                    continue
                
                try:
                    # Get text position
                    x = float(elem.get('x', 0))
                    y = float(elem.get('y', 0))
                    text_content = elem.text or ''
                    
                    # Check if text matches die ID patterns
                    is_die_id = any(re.search(pattern, text_content.lower()) 
                                   for pattern in self.die_detection_config['die_id_patterns'])
                    
                    if is_die_id or text_content.strip():
                        pos_x, pos_y = x * scale, y * scale
                        
                        # Estimate die size based on font size or use default
                        font_size = self._extract_font_size(elem)
                        estimated_size = max(font_size * 2, 10.0) * scale
                        half_size = estimated_size / 2
                        
                        boundary = DieBoundary(
                            die_id=text_content.strip() or f"text_die_{len(boundaries)+1}",
                            x_min=pos_x - half_size,
                            y_min=pos_y - half_size,
                            x_max=pos_x + half_size,
                            y_max=pos_y + half_size,
                            center_x=pos_x,
                            center_y=pos_y,
                            available=True,
                            metadata={
                                'source': 'text_detection',
                                'original_text': text_content,
                                'font_size': font_size,
                                'element_id': elem.get('id')
                            }
                        )
                        boundaries.append(boundary)
                        
                except (ValueError, TypeError) as e:
                    logger.warning(f"Error processing text element: {e}")
                    continue
        
        return boundaries
    
    def _extract_from_groups(self, root: ET.Element, scale: float, target_layer: Optional[str]) -> List[DieBoundary]:
        """Extract die boundaries from grouped elements and symbols."""
        boundaries = []
        die_counter = 0
        
        for group_type in self.die_detection_config['group_elements']:
            for elem in root.iter(f'{{{self.svg_ns["svg"]}}}{group_type}'):
                # Filter by layer/group if specified
                if target_layer and not self._is_in_target_layer(elem, target_layer):
                    continue
                
                # Calculate bounding box for the entire group
                bbox = self._get_group_bounding_box(elem)
                if bbox is None:
                    continue
                
                width = (bbox[1][0] - bbox[0][0]) * scale
                height = (bbox[1][1] - bbox[0][1]) * scale
                
                # Filter by size
                if (self.die_detection_config['min_die_size'] <= width <= self.die_detection_config['max_die_size'] and
                    self.die_detection_config['min_die_size'] <= height <= self.die_detection_config['max_die_size']):
                    
                    die_counter += 1
                    center_x = (bbox[0][0] + bbox[1][0]) / 2 * scale
                    center_y = (bbox[0][1] + bbox[1][1]) / 2 * scale
                    
                    element_id = elem.get('id', f'{group_type}_{die_counter}')
                    
                    boundary = DieBoundary(
                        die_id=element_id,
                        x_min=bbox[0][0] * scale,
                        y_min=bbox[0][1] * scale,
                        x_max=bbox[1][0] * scale,
                        y_max=bbox[1][1] * scale,
                        center_x=center_x,
                        center_y=center_y,
                        available=True,
                        metadata={
                            'element_type': group_type,
                            'element_id': element_id,
                            'class': elem.get('class'),
                            'source': 'group_detection',
                            'child_count': len(list(elem))
                        }
                    )
                    boundaries.append(boundary)
        
        return boundaries
    
    def _get_element_bounding_box(self, elem: ET.Element) -> Optional[Tuple[Tuple[float, float], Tuple[float, float]]]:
        """Get bounding box for an SVG element."""
        try:
            tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
            
            if tag == 'rect':
                x = float(elem.get('x', 0))
                y = float(elem.get('y', 0))
                width = float(elem.get('width', 0))
                height = float(elem.get('height', 0))
                return ((x, y), (x + width, y + height))
            
            elif tag == 'circle':
                cx = float(elem.get('cx', 0))
                cy = float(elem.get('cy', 0))
                r = float(elem.get('r', 0))
                return ((cx - r, cy - r), (cx + r, cy + r))
            
            elif tag == 'ellipse':
                cx = float(elem.get('cx', 0))
                cy = float(elem.get('cy', 0))
                rx = float(elem.get('rx', 0))
                ry = float(elem.get('ry', 0))
                return ((cx - rx, cy - ry), (cx + rx, cy + ry))
            
            elif tag == 'polygon' or tag == 'polyline':
                points_str = elem.get('points', '')
                points = self._parse_points(points_str)
                if points:
                    x_coords = [p[0] for p in points]
                    y_coords = [p[1] for p in points]
                    return ((min(x_coords), min(y_coords)), (max(x_coords), max(y_coords)))
            
            elif tag == 'path':
                # Simple path parsing - could be enhanced for complex paths
                d = elem.get('d', '')
                bbox = self._parse_path_bbox(d)
                return bbox
            
        except (ValueError, TypeError) as e:
            logger.warning(f"Error calculating bounding box for {tag}: {e}")
        
        return None
    
    def _get_group_bounding_box(self, group: ET.Element) -> Optional[Tuple[Tuple[float, float], Tuple[float, float]]]:
        """Calculate bounding box for a group of elements."""
        try:
            x_coords, y_coords = [], []
            
            # Apply group transformation if any
            transform = group.get('transform', '')
            
            for child in group:
                bbox = self._get_element_bounding_box(child)
                if bbox:
                    # Apply transformation if needed (simplified)
                    # TODO: Implement full SVG transformation parsing
                    x_coords.extend([bbox[0][0], bbox[1][0]])
                    y_coords.extend([bbox[0][1], bbox[1][1]])
            
            if x_coords and y_coords:
                return ((min(x_coords), min(y_coords)), (max(x_coords), max(y_coords)))
            
        except Exception as e:
            logger.warning(f"Error calculating group bounding box: {e}")
        
        return None
    
    def _parse_points(self, points_str: str) -> List[Tuple[float, float]]:
        """Parse SVG points attribute."""
        points = []
        try:
            # Handle different point formats
            coords = re.findall(r'[\d.-]+', points_str)
            for i in range(0, len(coords), 2):
                if i + 1 < len(coords):
                    points.append((float(coords[i]), float(coords[i + 1])))
        except (ValueError, IndexError):
            pass
        return points
    
    def _parse_path_bbox(self, path_d: str) -> Optional[Tuple[Tuple[float, float], Tuple[float, float]]]:
        """Parse SVG path to extract bounding box (simplified)."""
        try:
            # Extract coordinate numbers from path
            coords = re.findall(r'[\d.-]+', path_d)
            if len(coords) >= 4:
                x_coords = [float(coords[i]) for i in range(0, len(coords), 2)]
                y_coords = [float(coords[i]) for i in range(1, len(coords), 2)]
                return ((min(x_coords), min(y_coords)), (max(x_coords), max(y_coords)))
        except (ValueError, IndexError):
            pass
        return None
    
    def _extract_font_size(self, elem: ET.Element) -> float:
        """Extract font size from text element."""
        try:
            # Check font-size attribute
            font_size = elem.get('font-size')
            if font_size:
                return float(re.search(r'[\d.]+', font_size).group())
            
            # Check style attribute
            style = elem.get('style', '')
            font_size_match = re.search(r'font-size:\s*([\d.]+)', style)
            if font_size_match:
                return float(font_size_match.group(1))
            
        except (ValueError, AttributeError):
            pass
        
        return 12.0  # Default font size
    
    def _is_in_target_layer(self, elem: ET.Element, target_layer: str) -> bool:
        """Check if element is in the target layer/group."""
        # Check if element or any parent has the target layer in class or id
        current = elem
        while current is not None:
            element_class = current.get('class', '')
            element_id = current.get('id', '')
            
            if target_layer in element_class or target_layer in element_id:
                return True
            
            # Move to parent (simplified - would need proper parent tracking)
            current = None
        
        return True  # If no layer specified, include all
    
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
        merge_threshold = 1.0  # Threshold for SVG coordinates
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
        
        # Reassign die IDs for consistency (preserve meaningful IDs)
        counter = 1
        for boundary in unique_boundaries:
            if not any(pattern in boundary.die_id.lower() 
                      for pattern in ['die', 'cell', 'text']):
                boundary.die_id = f"die_{counter:03d}"
                counter += 1
        
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
        
        # Estimate wafer size based on layout diameter (assuming SVG units ~ mm)
        if layout_diameter < 100:
            return "100mm"
        elif layout_diameter < 150:
            return "150mm"
        elif layout_diameter < 200:
            return "200mm"
        elif layout_diameter < 300:
            return "300mm"
        else:
            return "300mm+"
    
    def get_supported_extensions(self) -> List[str]:
        """Return list of supported file extensions."""
        return ['.svg']
    
    def validate_file(self, file_path: str) -> bool:
        """Validate if file is a valid SVG file."""
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                return False
            
            # Check file extension
            if file_path.suffix.lower() not in self.get_supported_extensions():
                return False
            
            # Try to parse as XML
            tree = ET.parse(str(file_path))
            root = tree.getroot()
            
            # Check if it's an SVG file
            return 'svg' in root.tag.lower()
            
        except Exception:
            return False