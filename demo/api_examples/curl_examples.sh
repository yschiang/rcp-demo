#!/bin/bash

# Wafer Sampling Strategy System - API Demo Examples
# Phase 2 Demo: Complete workflow demonstration

BASE_URL="http://localhost:8000"

echo "=== Wafer Sampling Strategy System API Demo ==="
echo "Base URL: $BASE_URL"
echo ""

# ========================================
# HEALTH CHECKS
# ========================================

echo "1. Health Check"
echo "curl $BASE_URL/health"
curl -s "$BASE_URL/health" | jq '.'
echo ""

echo "2. Strategy API Health"
echo "curl $BASE_URL/api/v1/strategies/health"
curl -s "$BASE_URL/api/v1/strategies/health" | jq '.'
echo ""

# ========================================
# SCHEMATIC OPERATIONS
# ========================================

echo "=== SCHEMATIC UPLOAD DEMO ==="

echo "3. Upload SVG Schematic"
echo "curl -X POST '$BASE_URL/api/v1/schematics/upload?created_by=demo_user' \\"
echo "  -F 'file=@demo/schematics/simple_wafer_layout.svg'"

# Create a variable to store the schematic ID for later use
SVG_SCHEMATIC_ID=$(curl -s -X POST "$BASE_URL/api/v1/schematics/upload?created_by=demo_user" \
  -F "file=@demo/schematics/simple_wafer_layout.svg" | jq -r '.id // "demo_svg_123"')

echo "Schematic ID: $SVG_SCHEMATIC_ID"
echo ""

echo "4. Upload Complex SVG Schematic"
echo "curl -X POST '$BASE_URL/api/v1/schematics/upload?created_by=demo_user' \\"
echo "  -F 'file=@demo/schematics/complex_wafer_layout.svg' \\"
echo "  -F 'coordinate_scale=1.0'"

COMPLEX_SCHEMATIC_ID=$(curl -s -X POST "$BASE_URL/api/v1/schematics/upload?created_by=demo_user" \
  -F "file=@demo/schematics/complex_wafer_layout.svg" \
  -F "coordinate_scale=1.0" | jq -r '.id // "demo_complex_123"')

echo "Complex Schematic ID: $COMPLEX_SCHEMATIC_ID"
echo ""

echo "5. Upload DXF Schematic"
echo "curl -X POST '$BASE_URL/api/v1/schematics/upload?created_by=demo_user' \\"
echo "  -F 'file=@demo/schematics/processor_die.dxf' \\"
echo "  -F 'target_layer=DIE_BOUNDARY'"

DXF_SCHEMATIC_ID=$(curl -s -X POST "$BASE_URL/api/v1/schematics/upload?created_by=demo_user" \
  -F "file=@demo/schematics/processor_die.dxf" \
  -F "target_layer=DIE_BOUNDARY" | jq -r '.id // "demo_dxf_123"')

echo "DXF Schematic ID: $DXF_SCHEMATIC_ID"
echo ""

echo "6. List All Schematics"
echo "curl '$BASE_URL/api/v1/schematics/'"
curl -s "$BASE_URL/api/v1/schematics/" | jq '.'
echo ""

echo "7. Get Schematic Details"
echo "curl '$BASE_URL/api/v1/schematics/$SVG_SCHEMATIC_ID'"
curl -s "$BASE_URL/api/v1/schematics/$SVG_SCHEMATIC_ID" | jq '.'
echo ""

echo "8. Get Die Boundaries"
echo "curl '$BASE_URL/api/v1/schematics/$SVG_SCHEMATIC_ID/die-boundaries'"
curl -s "$BASE_URL/api/v1/schematics/$SVG_SCHEMATIC_ID/die-boundaries" | jq '.'
echo ""

# ========================================
# STRATEGY OPERATIONS
# ========================================

echo "=== STRATEGY CREATION DEMO ==="

echo "9. Create Basic Strategy"
echo "curl -X POST '$BASE_URL/api/v1/strategies/' \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{"
echo "    \"name\": \"Demo Strategy - SVG\","
echo "    \"description\": \"Demo strategy using uploaded SVG schematic\","
echo "    \"process_step\": \"Lithography\","
echo "    \"tool_type\": \"ASML_PAS5500\","
echo "    \"strategy_type\": \"custom\","
echo "    \"author\": \"demo_user\""
echo "  }'"

STRATEGY_ID=$(curl -s -X POST "$BASE_URL/api/v1/strategies/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Demo Strategy - SVG",
    "description": "Demo strategy using uploaded SVG schematic",
    "process_step": "Lithography",
    "tool_type": "ASML_PAS5500",
    "strategy_type": "custom",
    "author": "demo_user"
  }' | jq -r '.id // "demo_strategy_123"')

echo "Strategy ID: $STRATEGY_ID"
echo ""

echo "10. Update Strategy with Rules"
echo "curl -X PUT '$BASE_URL/api/v1/strategies/$STRATEGY_ID' \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{"
echo "    \"rules\": ["
echo "      {"
echo "        \"rule_type\": \"fixed_point\","
echo "        \"parameters\": {\"points\": [[0,0], [1,1], [2,2]]},"
echo "        \"weight\": 0.4,"
echo "        \"enabled\": true"
echo "      },"
echo "      {"
echo "        \"rule_type\": \"center_edge\","
echo "        \"parameters\": {\"edge_margin\": 5},"
echo "        \"weight\": 0.3,"
echo "        \"enabled\": true"
echo "      },"
echo "      {"
echo "        \"rule_type\": \"uniform_grid\","
echo "        \"parameters\": {\"grid_spacing\": 10, \"offset_x\": 2, \"offset_y\": 2},"
echo "        \"weight\": 0.3,"
echo "        \"enabled\": true"
echo "      }"
echo "    ],"
echo "    \"conditions\": {"
echo "      \"wafer_size\": \"300mm\","
echo "      \"product_type\": \"Memory\","
echo "      \"process_layer\": \"Metal1\","
echo "      \"defect_density_threshold\": 0.05"
echo "    },"
echo "    \"transformations\": {"
echo "      \"rotation_angle\": 90,"
echo "      \"scale_factor\": 1.0,"
echo "      \"offset_x\": 0,"
echo "      \"offset_y\": 0,"
echo "      \"flip_x\": false,"
echo "      \"flip_y\": false"
echo "    }"
echo "  }'"

curl -s -X PUT "$BASE_URL/api/v1/strategies/$STRATEGY_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "rules": [
      {
        "rule_type": "fixed_point",
        "parameters": {"points": [[0,0], [1,1], [2,2]]},
        "weight": 0.4,
        "enabled": true
      },
      {
        "rule_type": "center_edge",
        "parameters": {"edge_margin": 5},
        "weight": 0.3,
        "enabled": true
      },
      {
        "rule_type": "uniform_grid",
        "parameters": {"grid_spacing": 10, "offset_x": 2, "offset_y": 2},
        "weight": 0.3,
        "enabled": true
      }
    ],
    "conditions": {
      "wafer_size": "300mm",
      "product_type": "Memory",
      "process_layer": "Metal1",
      "defect_density_threshold": 0.05
    },
    "transformations": {
      "rotation_angle": 90,
      "scale_factor": 1.0,
      "offset_x": 0,
      "offset_y": 0,
      "flip_x": false,
      "flip_y": false
    }
  }' | jq '.'
echo ""

echo "11. List All Strategies"
echo "curl '$BASE_URL/api/v1/strategies/'"
curl -s "$BASE_URL/api/v1/strategies/" | jq '.'
echo ""

echo "12. Get Strategy Details"
echo "curl '$BASE_URL/api/v1/strategies/$STRATEGY_ID'"
curl -s "$BASE_URL/api/v1/strategies/$STRATEGY_ID" | jq '.'
echo ""

# ========================================
# VALIDATION & SIMULATION
# ========================================

echo "=== VALIDATION & SIMULATION DEMO ==="

echo "13. Validate Strategy Against Schematic"
echo "curl -X POST '$BASE_URL/api/v1/schematics/$SVG_SCHEMATIC_ID/validate' \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{"
echo "    \"strategy_id\": \"$STRATEGY_ID\","
echo "    \"validation_mode\": \"strict\""
echo "  }'"

curl -s -X POST "$BASE_URL/api/v1/schematics/$SVG_SCHEMATIC_ID/validate" \
  -H "Content-Type: application/json" \
  -d '{
    "strategy_id": "'$STRATEGY_ID'",
    "validation_mode": "strict"
  }' | jq '.'
echo ""

echo "14. Run Strategy Simulation"
echo "curl -X POST '$BASE_URL/api/v1/strategies/$STRATEGY_ID/simulate' \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{"
echo "    \"wafer_map_data\": {"
echo "      \"dies\": ["
echo "        {\"x\": 0, \"y\": 0, \"available\": true},"
echo "        {\"x\": 1, \"y\": 0, \"available\": true},"
echo "        {\"x\": 2, \"y\": 0, \"available\": true},"
echo "        {\"x\": 0, \"y\": 1, \"available\": true},"
echo "        {\"x\": 1, \"y\": 1, \"available\": true},"
echo "        {\"x\": 2, \"y\": 1, \"available\": true},"
echo "        {\"x\": 0, \"y\": 2, \"available\": true},"
echo "        {\"x\": 1, \"y\": 2, \"available\": true},"
echo "        {\"x\": 2, \"y\": 2, \"available\": true}"
echo "      ]"
echo "    },"
echo "    \"process_parameters\": {\"temperature\": 25, \"pressure\": 1013},"
echo "    \"tool_constraints\": {\"max_sites\": 50, \"min_spacing\": 2}"
echo "  }'"

curl -s -X POST "$BASE_URL/api/v1/strategies/$STRATEGY_ID/simulate" \
  -H "Content-Type: application/json" \
  -d '{
    "wafer_map_data": {
      "dies": [
        {"x": 0, "y": 0, "available": true},
        {"x": 1, "y": 0, "available": true},
        {"x": 2, "y": 0, "available": true},
        {"x": 0, "y": 1, "available": true},
        {"x": 1, "y": 1, "available": true},
        {"x": 2, "y": 1, "available": true},
        {"x": 0, "y": 2, "available": true},
        {"x": 1, "y": 2, "available": true},
        {"x": 2, "y": 2, "available": true}
      ]
    },
    "process_parameters": {"temperature": 25, "pressure": 1013},
    "tool_constraints": {"max_sites": 50, "min_spacing": 2}
  }' | jq '.'
echo ""

# ========================================
# EXPORT OPERATIONS
# ========================================

echo "=== EXPORT DEMO ==="

echo "15. Export Schematic as SVG"
echo "curl '$BASE_URL/api/v1/schematics/$SVG_SCHEMATIC_ID/export/svg'"
curl -s "$BASE_URL/api/v1/schematics/$SVG_SCHEMATIC_ID/export/svg"
echo ""

echo "16. Export Schematic as DXF"
echo "curl '$BASE_URL/api/v1/schematics/$SVG_SCHEMATIC_ID/export/dxf'"
curl -s "$BASE_URL/api/v1/schematics/$SVG_SCHEMATIC_ID/export/dxf"
echo ""

# ========================================
# LIFECYCLE MANAGEMENT
# ========================================

echo "=== LIFECYCLE MANAGEMENT DEMO ==="

echo "17. Promote Strategy (Draft → Review)"
echo "curl -X POST '$BASE_URL/api/v1/strategies/$STRATEGY_ID/promote' \\"
echo "  -F 'user=review_engineer'"

curl -s -X POST "$BASE_URL/api/v1/strategies/$STRATEGY_ID/promote" \
  -F "user=review_engineer" | jq '.'
echo ""

echo "18. Clone Strategy"
echo "curl -X POST '$BASE_URL/api/v1/strategies/$STRATEGY_ID/clone' \\"
echo "  -F 'new_name=Demo Strategy - Cloned' \\"
echo "  -F 'author=demo_user'"

CLONED_STRATEGY_ID=$(curl -s -X POST "$BASE_URL/api/v1/strategies/$STRATEGY_ID/clone" \
  -F "new_name=Demo Strategy - Cloned" \
  -F "author=demo_user" | jq -r '.id // "demo_cloned_123"')

echo "Cloned Strategy ID: $CLONED_STRATEGY_ID"
echo ""

echo "19. Get Strategy Versions"
echo "curl '$BASE_URL/api/v1/strategies/$STRATEGY_ID/versions'"
curl -s "$BASE_URL/api/v1/strategies/$STRATEGY_ID/versions" | jq '.'
echo ""

# ========================================
# ADVANCED FEATURES
# ========================================

echo "=== ADVANCED FEATURES DEMO ==="

echo "20. Get Available Rule Types"
echo "curl '$BASE_URL/api/v1/strategies/rule-types'"
curl -s "$BASE_URL/api/v1/strategies/rule-types" | jq '.'
echo ""

echo "21. Get Available Vendors"
echo "curl '$BASE_URL/api/v1/strategies/vendors'"
curl -s "$BASE_URL/api/v1/strategies/vendors" | jq '.'
echo ""

echo "22. Filter Strategies by Process Step"
echo "curl '$BASE_URL/api/v1/strategies/?process_step=Lithography'"
curl -s "$BASE_URL/api/v1/strategies/?process_step=Lithography" | jq '.'
echo ""

echo "23. Filter Strategies by Tool Type"
echo "curl '$BASE_URL/api/v1/strategies/?tool_type=ASML_PAS5500'"
curl -s "$BASE_URL/api/v1/strategies/?tool_type=ASML_PAS5500" | jq '.'
echo ""

echo "24. Filter Strategies by Lifecycle State"
echo "curl '$BASE_URL/api/v1/strategies/?lifecycle_state=review'"
curl -s "$BASE_URL/api/v1/strategies/?lifecycle_state=review" | jq '.'
echo ""

# ========================================
# CLEANUP (Optional)
# ========================================

echo "=== CLEANUP (Uncomment to run) ==="

echo "# Delete Strategy"
echo "# curl -X DELETE '$BASE_URL/api/v1/strategies/$STRATEGY_ID'"

echo "# Delete Cloned Strategy"
echo "# curl -X DELETE '$BASE_URL/api/v1/strategies/$CLONED_STRATEGY_ID'"

echo "# Delete Schematic"
echo "# curl -X DELETE '$BASE_URL/api/v1/schematics/$SVG_SCHEMATIC_ID'"

echo ""
echo "=== Demo Complete ==="
echo "Summary:"
echo "- Uploaded 3 schematic files (SVG simple, SVG complex, DXF)"
echo "- Created and configured a multi-rule strategy"
echo "- Validated strategy against schematic layout"
echo "- Ran simulation with coverage analysis"
echo "- Exported results in multiple formats"
echo "- Demonstrated lifecycle management"
echo "- Showed advanced filtering and cloning features"
echo ""
echo "All APIs ready for Phase 2 demo deployment!"