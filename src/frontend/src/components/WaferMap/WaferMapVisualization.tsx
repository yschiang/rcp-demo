/**
 * Interactive wafer map visualization component.
 */
import React, { useRef, useEffect, useState, useCallback } from 'react';
import { useStrategyStore } from '../../stores/strategyStore';
import { Die, WaferMap } from '../../types/strategy';
import { SchematicPreview } from '../SchematicUpload/FilePreview';

interface WaferMapVisualizationProps {
  waferMap: WaferMap;
  selectedPoints?: Array<{x: number, y: number, available: boolean}>;
  onDieClick?: (die: Die) => void;
  onDieHover?: (die: Die | null) => void;
  className?: string;
  interactive?: boolean;
  showTooltip?: boolean;
  schematic?: SchematicPreview;
  showSchematicOverlay?: boolean;
}

export default function WaferMapVisualization({
  waferMap,
  selectedPoints = [],
  onDieClick,
  onDieHover,
  className = '',
  interactive = true,
  showTooltip = true,
  schematic,
  showSchematicOverlay = true
}: WaferMapVisualizationProps) {
  const svgRef = useRef<SVGSVGElement>(null);
  const [hoveredDie, setHoveredDie] = useState<Die | null>(null);
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  
  const {
    waferMapState,
    setWaferMapZoom,
    setWaferMapPan,
    selectDies,
    toggleWaferMapOption
  } = useStrategyStore();

  // Calculate wafer bounds and layout
  const waferBounds = React.useMemo(() => {
    if (!waferMap.dies.length) return { minX: 0, maxX: 0, minY: 0, maxY: 0, width: 0, height: 0 };
    
    const xCoords = waferMap.dies.map(die => die.x);
    const yCoords = waferMap.dies.map(die => die.y);
    
    const minX = Math.min(...xCoords);
    const maxX = Math.max(...xCoords);
    const minY = Math.min(...yCoords);
    const maxY = Math.max(...yCoords);
    
    return {
      minX, maxX, minY, maxY,
      width: maxX - minX + 1,
      height: maxY - minY + 1
    };
  }, [waferMap.dies]);

  // SVG dimensions and scaling
  const SVG_SIZE = 500;
  const MARGIN = 40;
  const scale = (SVG_SIZE - 2 * MARGIN) / Math.max(waferBounds.width, waferBounds.height);
  const dieSize = Math.max(2, Math.min(scale * 0.8, 20));

  // Convert die coordinates to SVG coordinates
  const dieToSVG = useCallback((die: Die) => {
    const x = MARGIN + (die.x - waferBounds.minX) * scale + scale / 2;
    const y = MARGIN + (waferBounds.maxY - die.y) * scale + scale / 2; // Flip Y axis
    return { x, y };
  }, [waferBounds, scale]);

  // Check if die is selected
  const isDieSelected = useCallback((die: Die) => {
    return selectedPoints.some(point => point.x === die.x && point.y === die.y);
  }, [selectedPoints]);

  // Handle die interactions
  const handleDieClick = (die: Die, event: React.MouseEvent) => {
    event.stopPropagation();
    if (interactive && onDieClick) {
      onDieClick(die);
    }
  };

  const handleDieMouseEnter = (die: Die, event: React.MouseEvent) => {
    if (showTooltip) {
      setHoveredDie(die);
      setMousePosition({ x: event.clientX, y: event.clientY });
    }
    if (onDieHover) {
      onDieHover(die);
    }
  };

  const handleDieMouseLeave = () => {
    setHoveredDie(null);
    if (onDieHover) {
      onDieHover(null);
    }
  };

  const handleMouseMove = (event: React.MouseEvent) => {
    if (hoveredDie) {
      setMousePosition({ x: event.clientX, y: event.clientY });
    }
  };

  // Handle zoom and pan
  const handleWheel = (event: React.WheelEvent) => {
    if (interactive) {
      event.preventDefault();
      const delta = event.deltaY > 0 ? 0.9 : 1.1;
      const newZoom = Math.max(0.1, Math.min(5, waferMapState.zoom * delta));
      setWaferMapZoom(newZoom);
    }
  };

  const renderGrid = () => {
    if (!waferMapState.show_grid) return null;

    const lines = [];
    
    // Vertical lines
    for (let x = waferBounds.minX; x <= waferBounds.maxX + 1; x++) {
      const svgX = MARGIN + (x - waferBounds.minX) * scale;
      lines.push(
        <line
          key={`v${x}`}
          x1={svgX}
          y1={MARGIN}
          x2={svgX}
          y2={MARGIN + waferBounds.height * scale}
          stroke="#e5e7eb"
          strokeWidth="0.5"
        />
      );
    }
    
    // Horizontal lines
    for (let y = waferBounds.minY; y <= waferBounds.maxY + 1; y++) {
      const svgY = MARGIN + (waferBounds.maxY - y + 1) * scale;
      lines.push(
        <line
          key={`h${y}`}
          x1={MARGIN}
          y1={svgY}
          x2={MARGIN + waferBounds.width * scale}
          y2={svgY}
          stroke="#e5e7eb"
          strokeWidth="0.5"
        />
      );
    }
    
    return <g className="grid">{lines}</g>;
  };

  const renderCoordinateLabels = () => {
    if (!waferMapState.show_coordinates) return null;

    const labels = [];
    const labelInterval = Math.max(1, Math.floor(waferBounds.width / 10));
    
    // X-axis labels
    for (let x = waferBounds.minX; x <= waferBounds.maxX; x += labelInterval) {
      const svgX = MARGIN + (x - waferBounds.minX) * scale + scale / 2;
      labels.push(
        <text
          key={`x${x}`}
          x={svgX}
          y={MARGIN - 10}
          textAnchor="middle"
          className="fill-gray-500 text-xs"
        >
          {x}
        </text>
      );
    }
    
    // Y-axis labels
    for (let y = waferBounds.minY; y <= waferBounds.maxY; y += labelInterval) {
      const svgY = MARGIN + (waferBounds.maxY - y) * scale + scale / 2;
      labels.push(
        <text
          key={`y${y}`}
          x={MARGIN - 10}
          y={svgY + 4}
          textAnchor="middle"
          className="fill-gray-500 text-xs"
        >
          {y}
        </text>
      );
    }
    
    return <g className="coordinates">{labels}</g>;
  };

  const renderDies = () => {
    return waferMap.dies.map((die, index) => {
      const { x, y } = dieToSVG(die);
      const isSelected = isDieSelected(die);
      const isHovered = hoveredDie === die;
      
      let fillColor = die.available ? '#f3f4f6' : '#fca5a5'; // Gray or red for unavailable
      let strokeColor = '#d1d5db';
      
      if (isSelected) {
        fillColor = '#3b82f6'; // Blue for selected
        strokeColor = '#1d4ed8';
      } else if (isHovered) {
        fillColor = '#e5e7eb'; // Light gray for hover
        strokeColor = '#6b7280';
      }
      
      return (
        <rect
          key={`${die.x}-${die.y}`}
          x={x - dieSize / 2}
          y={y - dieSize / 2}
          width={dieSize}
          height={dieSize}
          fill={fillColor}
          stroke={strokeColor}
          strokeWidth={isSelected ? 2 : 1}
          className={interactive ? 'cursor-pointer' : ''}
          onClick={(e) => handleDieClick(die, e)}
          onMouseEnter={(e) => handleDieMouseEnter(die, e)}
          onMouseLeave={handleDieMouseLeave}
        />
      );
    });
  };

  const renderSchematicOverlay = () => {
    if (!schematic || !showSchematicOverlay) return null;

    // Convert schematic layout bounds to SVG coordinates
    const schematicBounds = schematic.layoutBounds;
    
    // Calculate scale factor to fit schematic within wafer bounds
    // Convert micrometers to die coordinates (approximation)
    const micrometersPerDie = 10000; // Typical 10mm die size
    const schematicWidthInDies = schematicBounds.width / micrometersPerDie;
    const schematicHeightInDies = schematicBounds.height / micrometersPerDie;
    
    // Center the schematic on the wafer
    const centerX = (waferBounds.minX + waferBounds.maxX) / 2;
    const centerY = (waferBounds.minY + waferBounds.maxY) / 2;
    
    const schematicLeft = centerX - schematicWidthInDies / 2;
    const schematicRight = centerX + schematicWidthInDies / 2;
    const schematicTop = centerY + schematicHeightInDies / 2;
    const schematicBottom = centerY - schematicHeightInDies / 2;
    
    // Convert to SVG coordinates
    const svgLeft = MARGIN + (schematicLeft - waferBounds.minX) * scale;
    const svgRight = MARGIN + (schematicRight - waferBounds.minX) * scale;
    const svgTop = MARGIN + (waferBounds.maxY - schematicTop) * scale;
    const svgBottom = MARGIN + (waferBounds.maxY - schematicBottom) * scale;
    
    return (
      <g className="schematic-overlay" opacity="0.6">
        {/* Schematic boundary rectangle */}
        <rect
          x={svgLeft}
          y={svgTop}
          width={svgRight - svgLeft}
          height={svgBottom - svgTop}
          fill="none"
          stroke="#7c3aed"
          strokeWidth="2"
          strokeDasharray="8,4"
        />
        
        {/* Schematic info label */}
        <rect
          x={svgLeft}
          y={svgTop - 20}
          width={Math.max(100, (svgRight - svgLeft) / 2)}
          height="18"
          fill="#7c3aed"
          fillOpacity="0.9"
          rx="3"
        />
        <text
          x={svgLeft + 5}
          y={svgTop - 6}
          className="fill-white text-xs font-medium"
        >
          {schematic.filename}
        </text>
        
        {/* Die boundary indicators (mock grid) */}
        {renderSchematicDieGrid(svgLeft, svgTop, svgRight, svgBottom)}
      </g>
    );
  };

  const renderSchematicDieGrid = (left: number, top: number, right: number, bottom: number) => {
    if (!schematic) return null;
    
    const gridElements = [];
    const gridSpacing = Math.max(5, Math.min(20, (right - left) / 20)); // Adaptive grid spacing
    
    // Vertical grid lines
    for (let x = left; x <= right; x += gridSpacing) {
      gridElements.push(
        <line
          key={`schematic-v-${x}`}
          x1={x}
          y1={top}
          x2={x}
          y2={bottom}
          stroke="#a855f7"
          strokeWidth="0.5"
          opacity="0.4"
        />
      );
    }
    
    // Horizontal grid lines
    for (let y = top; y <= bottom; y += gridSpacing) {
      gridElements.push(
        <line
          key={`schematic-h-${y}`}
          x1={left}
          y1={y}
          x2={right}
          y2={y}
          stroke="#a855f7"
          strokeWidth="0.5"
          opacity="0.4"
        />
      );
    }
    
    return gridElements;
  };

  return (
    <div className={`relative ${className}`}>
      {/* Controls */}
      <div className="absolute top-4 right-4 z-10 bg-white rounded-lg shadow-lg p-3 space-y-2">
        <div className="flex items-center gap-2">
          <input
            type="checkbox"
            id="show-grid"
            checked={waferMapState.show_grid}
            onChange={() => toggleWaferMapOption('show_grid')}
            className="rounded"
          />
          <label htmlFor="show-grid" className="text-sm text-gray-700">Grid</label>
        </div>
        <div className="flex items-center gap-2">
          <input
            type="checkbox"
            id="show-coordinates"
            checked={waferMapState.show_coordinates}
            onChange={() => toggleWaferMapOption('show_coordinates')}
            className="rounded"
          />
          <label htmlFor="show-coordinates" className="text-sm text-gray-700">Coordinates</label>
        </div>
        {schematic && (
          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="show-schematic"
              checked={showSchematicOverlay}
              onChange={() => {}} // TODO: Add state management for schematic overlay
              className="rounded"
            />
            <label htmlFor="show-schematic" className="text-sm text-gray-700">Schematic</label>
          </div>
        )}
        <div className="text-xs text-gray-500 pt-2 border-t">
          Zoom: {Math.round(waferMapState.zoom * 100)}%
        </div>
        {schematic && (
          <div className="text-xs text-gray-500">
            Dies: {schematic.dieCount.toLocaleString()}
          </div>
        )}
      </div>

      {/* SVG Wafer Map */}
      <svg
        ref={svgRef}
        width={SVG_SIZE}
        height={SVG_SIZE}
        className="border border-gray-300 rounded-lg bg-white"
        onWheel={handleWheel}
        onMouseMove={handleMouseMove}
        style={{
          transform: `scale(${waferMapState.zoom}) translate(${waferMapState.pan.x}px, ${waferMapState.pan.y}px)`,
          transformOrigin: 'center'
        }}
      >
        {renderGrid()}
        {renderCoordinateLabels()}
        {renderDies()}
        {renderSchematicOverlay()}
        
        {/* Wafer outline */}
        <circle
          cx={SVG_SIZE / 2}
          cy={SVG_SIZE / 2}
          r={(SVG_SIZE - 2 * MARGIN) / 2}
          fill="none"
          stroke="#374151"
          strokeWidth="2"
          strokeDasharray="5,5"
          opacity="0.5"
        />
      </svg>

      {/* Tooltip */}
      {hoveredDie && showTooltip && (
        <div
          className="fixed z-50 bg-gray-900 text-white text-xs rounded px-2 py-1 pointer-events-none"
          style={{
            left: mousePosition.x + 10,
            top: mousePosition.y - 30
          }}
        >
          <div>Die ({hoveredDie.x}, {hoveredDie.y})</div>
          <div>Status: {hoveredDie.available ? 'Available' : 'Unavailable'}</div>
          {isDieSelected(hoveredDie) && <div>Selected</div>}
        </div>
      )}

      {/* Legend */}
      <div className="mt-4 flex items-center gap-6 text-sm flex-wrap">
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-gray-100 border border-gray-300 rounded"></div>
          <span>Available</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-red-200 border border-red-300 rounded"></div>
          <span>Unavailable</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-blue-500 border border-blue-600 rounded"></div>
          <span>Selected</span>
        </div>
        {schematic && showSchematicOverlay && (
          <div className="flex items-center gap-2">
            <div className="w-4 h-1 bg-purple-600 rounded" style={{ borderStyle: 'dashed' }}></div>
            <span>Schematic Boundary</span>
          </div>
        )}
      </div>

      {/* Statistics */}
      <div className={`mt-4 grid gap-4 text-sm ${schematic ? 'grid-cols-4' : 'grid-cols-3'}`}>
        <div className="text-center">
          <div className="font-semibold">{waferMap.dies.length}</div>
          <div className="text-gray-500">Total Dies</div>
        </div>
        <div className="text-center">
          <div className="font-semibold">{waferMap.dies.filter(d => d.available).length}</div>
          <div className="text-gray-500">Available</div>
        </div>
        <div className="text-center">
          <div className="font-semibold">{selectedPoints.length}</div>
          <div className="text-gray-500">Selected</div>
        </div>
        {schematic && (
          <div className="text-center">
            <div className="font-semibold">{schematic.dieCount.toLocaleString()}</div>
            <div className="text-gray-500">Schematic Dies</div>
          </div>
        )}
      </div>
    </div>
  );
}