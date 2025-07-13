"""
Schematic file parsers for various formats.

This package provides parsers for:
- GDSII: IC layout format for die boundary extraction
- DXF: CAD drawing format for coordinate extraction
- SVG: Web-friendly schematic format
"""

from .gdsii_parser import GDSIIParser
from .dxf_parser import DXFParser
from .svg_parser import SVGParser

__all__ = ['GDSIIParser', 'DXFParser', 'SVGParser']