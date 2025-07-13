# Wafer Sampling Strategy System - API Reference

## Overview

This document provides comprehensive API documentation for the Wafer Sampling Strategy System backend. The system provides REST APIs for strategy management, schematic file processing, and validation workflows.

**Base URL**: `http://localhost:8000`  
**API Version**: `v1`  
**Content Type**: `application/json` (unless specified otherwise)

---

## Table of Contents

1. [Authentication & Health](#authentication--health)
2. [Strategy Management APIs](#strategy-management-apis)
3. [Schematic Management APIs](#schematic-management-apis)
4. [Error Handling](#error-handling)
5. [Data Models](#data-models)

---

## Authentication & Health

### Health Check
```http
GET /health
```
**Description**: Check system health and status.

**Response**:
```json
{
  "status": "healthy",
  "environment": "development",
  "version": "1.0.0",
  "timestamp": 1672531200.0
}
```

---

## Strategy Management APIs

### 1. Create Strategy
```http
POST /api/v1/strategies
```
**Description**: Create a new sampling strategy.

**Request Body**:
```json
{
  "name": "Center Edge Strategy",
  "description": "Center and edge sampling for critical layers",
  "strategy_type": "center_edge",
  "process_step": "lithography",
  "tool_type": "ASML_scanner",
  "rules": [
    {
      "rule_type": "center_edge",
      "parameters": {
        "center_count": 5,
        "edge_count": 12,
        "edge_margin": 2.0
      },
      "weight": 1.0,
      "enabled": true
    }
  ],
  "conditions": {
    "wafer_size": ["200mm", "300mm"],
    "product_types": ["logic", "memory"],
    "process_layers": ["poly", "metal1"]
  },
  "transformations": {
    "rotation_angle": 0.0,
    "coordinate_offset": {"x": 0.0, "y": 0.0},
    "scaling_factor": 1.0
  },
  "target_vendor": "ASML",
  "author": "engineer@company.com"
}
```

**Response** `201 Created`:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Center Edge Strategy",
  "status": "created",
  "version": "1.0.0",
  "created_at": "2024-01-01T10:00:00Z"
}
```

### 2. List Strategies
```http
GET /api/v1/strategies
```
**Query Parameters**:
- `author` (optional): Filter by author
- `strategy_type` (optional): Filter by strategy type
- `process_step` (optional): Filter by process step
- `lifecycle_state` (optional): Filter by lifecycle state
- `limit` (optional): Maximum results (default: 100)

**Response** `200 OK`:
```json
{
  "strategies": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "Center Edge Strategy",
      "strategy_type": "center_edge",
      "process_step": "lithography",
      "tool_type": "ASML_scanner",
      "author": "engineer@company.com",
      "version": "1.0.0",
      "lifecycle_state": "draft",
      "created_at": "2024-01-01T10:00:00Z",
      "modified_at": "2024-01-01T10:00:00Z"
    }
  ],
  "total_count": 1
}
```

### 3. Get Strategy Details
```http
GET /api/v1/strategies/{strategy_id}
```
**Path Parameters**:
- `strategy_id`: Strategy UUID

**Response** `200 OK`:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Center Edge Strategy",
  "description": "Center and edge sampling for critical layers",
  "strategy_type": "center_edge",
  "process_step": "lithography",
  "tool_type": "ASML_scanner",
  "rules": [...],
  "conditions": {...},
  "transformations": {...},
  "target_vendor": "ASML",
  "vendor_specific_params": {},
  "version": "1.0.0",
  "author": "engineer@company.com",
  "created_at": "2024-01-01T10:00:00Z",
  "modified_at": "2024-01-01T10:00:00Z",
  "lifecycle_state": "draft",
  "schema_version": "1.0"
}
```

### 4. Update Strategy
```http
PUT /api/v1/strategies/{strategy_id}
```
**Request Body**: Same as create strategy

**Response** `200 OK`:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "updated",
  "version": "1.0.1",
  "modified_at": "2024-01-01T11:00:00Z"
}
```

### 5. Update Strategy Rules
```http
PUT /api/v1/strategies/{strategy_id}/rules
```
**Request Body**:
```json
{
  "rules": [
    {
      "rule_type": "fixed_point",
      "parameters": {
        "points": [[10, 10], [50, 50], [90, 90]]
      },
      "weight": 1.0,
      "enabled": true
    }
  ]
}
```

### 6. Simulate Strategy
```http
POST /api/v1/strategies/{strategy_id}/simulate
```
**Request Body**:
```json
{
  "wafer_map": {
    "dies": [
      {"x": 10, "y": 10, "available": true},
      {"x": 20, "y": 20, "available": true}
    ]
  },
  "process_parameters": {
    "wafer_size": "300mm",
    "product_type": "logic"
  }
}
```

**Response** `200 OK`:
```json
{
  "simulation_id": "sim-123",
  "selected_dies": [
    {"x": 10, "y": 10, "available": true},
    {"x": 50, "y": 50, "available": true}
  ],
  "statistics": {
    "total_dies": 100,
    "available_dies": 95,
    "selected_count": 25,
    "coverage_percentage": 26.32,
    "distribution": {
      "x_range": {"min": 5, "max": 95},
      "y_range": {"min": 5, "max": 95},
      "center_of_mass": {"x": 50.2, "y": 49.8}
    }
  }
}
```

### 7. Delete Strategy
```http
DELETE /api/v1/strategies/{strategy_id}
```
**Response** `204 No Content`

---

## Schematic Management APIs

### 1. Upload Schematic File
```http
POST /api/v1/schematics/upload
```
**Content Type**: `multipart/form-data`

**Form Parameters**:
- `file`: Schematic file (GDSII/DXF/SVG, max 100MB)
- `created_by`: User email/ID
- `coordinate_scale` (optional): Scale factor (default: 1.0)
- `die_size_filter_min` (optional): Minimum die size
- `die_size_filter_max` (optional): Maximum die size
- `target_cell` (optional): Specific cell to parse (GDSII only)
- `target_layer` (optional): Specific layer to process

**Response** `200 OK`:
```json
{
  "id": "schem-550e8400-e29b-41d4-a716-446655440000",
  "filename": "wafer_layout.gds",
  "format_type": "gdsii",
  "upload_date": "2024-01-01T10:00:00Z",
  "die_count": 284,
  "available_die_count": 276,
  "coordinate_system": "gdsii_units",
  "wafer_size": "300mm",
  "statistics": {
    "die_count": 284,
    "available_die_count": 276,
    "layout_bounds": {
      "x_min": -150000,
      "y_min": -150000,
      "x_max": 150000,
      "y_max": 150000
    },
    "layout_size": {
      "width": 300000,
      "height": 300000
    },
    "coordinate_system": "gdsii_units",
    "format_type": "gdsii",
    "wafer_size": "300mm"
  },
  "metadata": {
    "original_filename": "wafer_layout.gds",
    "file_size": 2048576,
    "software_info": "GDSII Stream Format",
    "units": "1e-6 user units, 1e-9 database units",
    "scale_factor": 1e-6
  }
}
```

### 2. List Schematics
```http
GET /api/v1/schematics/
```
**Query Parameters**:
- `created_by` (optional): Filter by creator
- `format_type` (optional): Filter by format (gdsii, dxf, svg)
- `limit` (optional): Maximum results (default: 100)

**Response** `200 OK`:
```json
{
  "schematics": [
    {
      "id": "schem-550e8400-e29b-41d4-a716-446655440000",
      "filename": "wafer_layout.gds",
      "format_type": "gdsii",
      "upload_date": "2024-01-01T10:00:00Z",
      "die_count": 284,
      "available_die_count": 276,
      "wafer_size": "300mm",
      "created_by": "engineer@company.com"
    }
  ],
  "total_count": 1
}
```

### 3. Get Schematic Details
```http
GET /api/v1/schematics/{schematic_id}
```
**Response**: Same as upload response format

### 4. Get Die Boundaries
```http
GET /api/v1/schematics/{schematic_id}/die-boundaries
```
**Query Parameters**:
- `limit` (optional): Limit number of boundaries returned

**Response** `200 OK`:
```json
{
  "schematic_id": "schem-550e8400-e29b-41d4-a716-446655440000",
  "total_die_count": 284,
  "returned_count": 284,
  "die_boundaries": [
    {
      "die_id": "die_001",
      "x_min": -12500.0,
      "y_min": -12500.0,
      "x_max": 12500.0,
      "y_max": 12500.0,
      "center_x": 0.0,
      "center_y": 0.0,
      "width": 25000.0,
      "height": 25000.0,
      "area": 625000000.0,
      "available": true,
      "metadata": {
        "layer": 0,
        "datatype": 0,
        "source": "shape_detection"
      }
    }
  ]
}
```

### 5. Validate Strategy Against Schematic
```http
POST /api/v1/schematics/{schematic_id}/validate
```
**Request Body**:
```json
{
  "strategy_id": "550e8400-e29b-41d4-a716-446655440000",
  "validated_by": "engineer@company.com"
}
```

**Response** `200 OK`:
```json
{
  "validation_id": "val-123-456-789",
  "schematic_id": "schem-550e8400-e29b-41d4-a716-446655440000",
  "strategy_id": "550e8400-e29b-41d4-a716-446655440000",
  "validation_status": "warning",
  "alignment_score": 0.85,
  "coverage_percentage": 92.5,
  "total_points": 25,
  "valid_points": 23,
  "error_count": 0,
  "warning_count": 2,
  "recommendations": [
    "Consider adjusting edge margin to improve alignment",
    "Review strategy rules for optimal die coverage"
  ],
  "validation_date": "2024-01-01T10:30:00Z"
}
```

### 6. Get Validation Results
```http
GET /api/v1/schematics/validations/{validation_id}
```
**Response** `200 OK`:
```json
{
  "validation_id": "val-123-456-789",
  "schematic_id": "schem-550e8400-e29b-41d4-a716-446655440000",
  "strategy_id": "550e8400-e29b-41d4-a716-446655440000",
  "validation_date": "2024-01-01T10:30:00Z",
  "validation_status": "warning",
  "alignment_score": 0.85,
  "coverage_percentage": 92.5,
  "total_strategy_points": 25,
  "valid_strategy_points": 23,
  "conflicts": [
    {
      "conflict_type": "out_of_bounds",
      "strategy_point": [150000, 150000],
      "description": "Strategy point (150000, 150000) is outside all die boundaries",
      "severity": "warning",
      "recommendation": "Adjust strategy rules to stay within die boundaries",
      "affected_die_id": null
    }
  ],
  "warnings": [
    {
      "warning_type": "low_coverage",
      "description": "Strategy coverage is only 92.5%",
      "affected_area": null,
      "recommendation": "Consider adjusting strategy rules to improve coverage"
    }
  ],
  "recommendations": [
    "Consider adjusting edge margin to improve alignment",
    "Review strategy rules for optimal die coverage"
  ]
}
```

### 7. Export Schematic
```http
GET /api/v1/schematics/{schematic_id}/export/{format_type}
```
**Path Parameters**:
- `format_type`: Export format (svg, dxf)

**Response**: Binary file download with appropriate content type
- SVG: `image/svg+xml`
- DXF: `application/dxf`

### 8. List Validation Results
```http
GET /api/v1/schematics/{schematic_id}/validations
```
**Query Parameters**:
- `limit` (optional): Maximum results (default: 50)

**Response** `200 OK`:
```json
{
  "schematic_id": "schem-550e8400-e29b-41d4-a716-446655440000",
  "total_validations": 3,
  "validations": [
    {
      "validation_id": "val-123-456-789",
      "schematic_id": "schem-550e8400-e29b-41d4-a716-446655440000",
      "strategy_id": "550e8400-e29b-41d4-a716-446655440000",
      "validation_date": "2024-01-01T10:30:00Z",
      "validation_status": "warning",
      "alignment_score": 0.85,
      "coverage_percentage": 92.5,
      "total_points": 25,
      "valid_points": 23,
      "validated_by": "engineer@company.com"
    }
  ]
}
```

### 9. Get Supported Formats
```http
GET /api/v1/schematics/formats/supported
```
**Response** `200 OK`:
```json
{
  "supported_formats": [
    {
      "format": "gdsii",
      "description": "GDSII Stream Format for IC layouts",
      "extensions": [".gds", ".gdsii"],
      "features": ["die_boundaries", "text_labels", "cell_references"],
      "parser_status": "available"
    },
    {
      "format": "dxf",
      "description": "AutoCAD Drawing Exchange Format",
      "extensions": [".dxf"],
      "features": ["geometric_entities", "text_elements", "block_inserts"],
      "parser_status": "available"
    },
    {
      "format": "svg",
      "description": "Scalable Vector Graphics",
      "extensions": [".svg"],
      "features": ["shape_elements", "text_labels", "grouped_elements"],
      "parser_status": "available"
    }
  ],
  "upload_limits": {
    "max_file_size": "100MB",
    "supported_coordinate_systems": ["cartesian", "gdsii_units", "cad_units"],
    "die_detection_methods": ["shape_analysis", "text_parsing", "reference_extraction"]
  }
}
```

### 10. Delete Schematic
```http
DELETE /api/v1/schematics/{schematic_id}
```
**Response** `200 OK`:
```json
{
  "message": "Schematic schem-550e8400-e29b-41d4-a716-446655440000 deleted successfully"
}
```

---

## Error Handling

All endpoints use standardized error responses:

### Error Response Format
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": {
      "field": "name",
      "issue": "Field is required"
    }
  }
}
```

### HTTP Status Codes
- `200`: Success
- `201`: Created
- `204`: No Content
- `400`: Bad Request (validation errors)
- `404`: Not Found
- `413`: Payload Too Large (file size exceeded)
- `422`: Unprocessable Entity (business logic errors)
- `500`: Internal Server Error

### Common Error Types
- `VALIDATION_ERROR`: Request validation failed
- `NOT_FOUND`: Resource not found
- `BUSINESS_LOGIC_ERROR`: Business rule violation
- `FILE_UPLOAD_ERROR`: File upload or processing failed
- `PARSER_ERROR`: Schematic parsing failed

---

## Data Models

### Strategy Types
- `center_edge`: Center and edge sampling
- `uniform_grid`: Uniform grid sampling  
- `random_sampling`: Random statistical sampling
- `fixed_point`: Fixed coordinate sampling
- `hotspot_priority`: Hotspot-based sampling

### Rule Types
- `fixed_point`: Specific coordinate points
- `center_edge`: Center and edge patterns
- `uniform_grid`: Grid-based sampling
- `random_sampling`: Statistical sampling

### Coordinate Systems
- `cartesian`: Standard X/Y coordinates
- `polar`: Polar coordinates
- `gdsii_units`: GDSII database units
- `cad_units`: CAD drawing units
- `normalized`: Normalized 0-1 coordinates

### Validation Status
- `pass`: Validation successful
- `warning`: Warnings present but acceptable
- `fail`: Critical errors found
- `not_validated`: Not yet validated

### Lifecycle States
- `draft`: Under development
- `review`: Under review
- `approved`: Approved for use
- `active`: Currently deployed
- `deprecated`: No longer recommended

---

## Rate Limits

- **File Upload**: 10 uploads per minute per user
- **API Requests**: 1000 requests per minute per user
- **Simulation**: 50 simulations per minute per user

---

## Examples

### Complete Workflow Example

1. **Upload Schematic**:
```bash
curl -X POST "http://localhost:8000/api/v1/schematics/upload" \
  -F "file=@wafer_layout.gds" \
  -F "created_by=engineer@company.com" \
  -F "coordinate_scale=1e-6"
```

2. **Create Strategy**:
```bash
curl -X POST "http://localhost:8000/api/v1/strategies" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Strategy",
    "strategy_type": "center_edge",
    "process_step": "lithography",
    "tool_type": "ASML_scanner",
    "rules": [...]
  }'
```

3. **Validate Strategy**:
```bash
curl -X POST "http://localhost:8000/api/v1/schematics/{schematic_id}/validate" \
  -H "Content-Type: application/json" \
  -d '{
    "strategy_id": "{strategy_id}",
    "validated_by": "engineer@company.com"
  }'
```

4. **Export Results**:
```bash
curl -X GET "http://localhost:8000/api/v1/schematics/{schematic_id}/export/svg" \
  -o "exported_layout.svg"
```

---

## Support

For API support and documentation updates:
- **Repository**: [rcp-demo](https://github.com/yschiang/rcp-demo)
- **API Documentation**: Auto-generated Swagger docs available at `/docs` when running in development mode
- **Health Check**: `/health` endpoint for system status

**Last Updated**: 2024-07-13  
**API Version**: 1.0.0