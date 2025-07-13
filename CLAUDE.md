# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **By Tool Type Sampling Strategy System** that enables Metrology Engineers to create, simulate, validate, and deploy wafer sampling strategies based on Tool Type and Process. The system supports diverse sampling needs across tools and vendors with process-specific strategies and tool-vendor-specific data handling.

### Key Objectives
- Self-service strategy creation via UI, Excel import, or YAML configuration
- Generic strategy schema that maps to vendor-specific formats
- Process-specific strategy configuration (strategies vary per process step)
- Simulation and validation with WaferMap preview
- Version control and deployment management

## User Workflow

The system supports three input paths that converge into a unified backend processing flow:

1. **YAML/Excel Input Path**: Metrology Engineer prepares strategy in structured format
2. **UI Guided Form Path**: Interactive web-based strategy creation with validation
3. **Backend Processing**: All inputs convert to Generic Strategy Object → Tool Model Mapping → Vendor Format Conversion → Tool Control System deployment

**Complete Flow** (from `docs/0_flowchart.mermaid`):
```
User Input → Generic Strategy Object → Tool Model Lookup → Vendor Format → Tool-Specific File → Tool Control System
```

## Architecture

### Backend (Python)
- **Core Models** (`src/backend/app/core/models/`):
  - `Die`: Represents individual die coordinates (x, y) with availability status
  - `WaferMap`: Container for dies with `get_available_dies()` filtering capabilities
  - `Rule` (Abstract): Base class for sampling rules with `apply(WaferMap) -> List[Die]` method
    - `FixedPointRule`: Selects dies at specific coordinates (implemented)
    - `CenterEdgeRule`: Planned rule type for center-edge sampling patterns
  - `GenericStrategy`: Combines multiple rules and optional vendor mapping transformations
  - `VendorMapping` (Abstract): Base class for vendor-specific coordinate transformations
    - `ASMLMapping`: ASML tool format converter (planned)
    - `KLAMapping`: KLA tool format converter (planned)

- **Parser** (`src/backend/app/core/parser/`):
  - `StrategyParser`: Parses YAML configurations into `GenericStrategy` objects
  - Plugin registry system (`plugin_registry: Dict[String, VendorMapping]`) for vendor mappings

### Frontend (React/TypeScript)
- **Components** (`src/frontend/src/components/`):
  - `StrategyForm`: File upload interface for YAML strategy configurations
- **Pages** (`src/frontend/src/pages/`):
  - `StrategyBuilder`: Main strategy configuration interface

### Strategy Input Formats
The system must support multiple input methods that all convert to a unified **Generic Strategy Object**:

1. **System UI**: Interactive web-based form with validation and preview
2. **Excel Import**: Tabular format for rule-based strategies and bulk setup
3. **YAML Import**: Structured configuration for advanced users

Current YAML structure:
```yaml
name: strategy_name
tool_model: VENDOR_NAME  # Maps to vendor-specific format
rules:
  - type: FixedPoint
    points: [[x1, y1], [x2, y2], ...]
```

**Required Strategy Components** (per spec):
- Tool Type and Process Step
- Strategy Type (center-edge, hotspot-priority, uniform grid, etc.)
- Conditional Logic (wafer size, product, process layer)
- Transformations (rotation angle, flips, coordinate offsets)

## Documentation

- **System Flowchart**: `docs/0_flowchart.mermaid` - User workflow from strategy creation to tool deployment
- **Class Diagram**: `docs/1_oo.mermaid` - Object-oriented architecture and relationships

## Development Commands

### Python Backend
- **Run tests**: `python -m pytest src/backend/tests/ -v`
- **Test single file**: `python -m pytest src/backend/tests/test_strategy.py -v`

### Demo/Examples
- Sample strategy configuration: `demo/sample_strategy.yaml`
- Dummy wafer generator: `demo/dummy_wafer.py`

## Key Design Patterns

1. **Strategy Pattern**: Rules are pluggable via the `Rule` abstract base class
2. **Plugin Registry**: Vendor mappings are registered in `StrategyParser.plugin_registry`
3. **Separation of Concerns**: Strategy parsing, rule application, and coordinate transformation are separate responsibilities

## Requirements Implementation Status

### Implementation Status: Current vs Planned Architecture

**Implemented Components:**
- ✅ `Die`, `WaferMap`, `Rule` (abstract), `FixedPointRule` - basic data models
- ✅ `GenericStrategy` - strategy execution framework
- ✅ `StrategyParser` - YAML parsing with plugin registry structure
- ✅ Basic React frontend with file upload (`StrategyForm`, `StrategyBuilder`)

**Planned Components (from Class Diagram):**
- ❌ `CenterEdgeRule` - center-edge sampling patterns
- ❌ `VendorMapping` (abstract), `ASMLMapping`, `KLAMapping` - vendor transformations
- ❌ Additional rule types for hotspot-priority, uniform grid strategies

**Functional Requirements Status:**
- ✅ **FR1.3**: YAML Import for strategy definition
- ⚠️ **FR1.1**: System UI (basic upload exists, needs guided form from flowchart)
- ❌ **FR1.2**: Excel Import capability
- ❌ **FR2**: Simulation and validation with WaferMap preview
- ❌ **FR3**: Strategy deployment and version control
- ❌ **FR4**: Process-specific strategy configuration
- ⚠️ **FR5**: Vendor mapping framework exists but implementations missing

**Architecture Gaps for Full Specification:**
- No process step tracking in strategy model
- Missing conditional logic support (wafer size, product, process layer)
- No transformation capabilities (rotation, flips, coordinate offsets)
- No simulation/visualization capabilities
- No version control or deployment system
- No access control framework