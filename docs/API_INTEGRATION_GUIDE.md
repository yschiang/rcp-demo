# Backend API Integration Guide for Frontend Team

## 🚀 Backend Status: READY FOR INTEGRATION

**Server URL:** `http://localhost:8000`  
**Documentation:** `http://localhost:8000/docs` (Swagger UI)  
**Health Check:** `http://localhost:8000/health`

## 📋 Quick Start Checklist

- ✅ Backend server running on port 8000
- ✅ CORS configured for frontend ports (3000, 5173)
- ✅ All API endpoints functional and tested
- ✅ Progressive strategy creation workflow supported
- ✅ Error handling and validation implemented

## 🔧 API Endpoints Reference

### 1. Strategy Creation (Progressive Workflow)

**Create Draft Strategy**
```bash
POST /api/v1/strategies/
Content-Type: application/json

{
  "name": "My Test Strategy",
  "description": "Created from frontend wizard",
  "process_step": "litho",
  "tool_type": "ASML", 
  "strategy_type": "fixed_point",
  "author": "frontend_user"
}
```

**Response:**
```json
{
  "id": "c78e9fe4-1ca5-4404-8fbe-a9977722bd15",
  "name": "My Test Strategy",
  "description": "Created from frontend wizard",
  "strategy_type": "fixed_point",
  "process_step": "litho",
  "tool_type": "ASML",
  "version": "1.0.0",
  "author": "frontend_user",
  "created_at": "2025-07-13T16:37:54.338913",
  "modified_at": "2025-07-13T16:37:54.338917",
  "lifecycle_state": "draft",
  "rule_count": 0
}
```

### 2. Strategy Listing

**Get All Strategies**
```bash
GET /api/v1/strategies/
```

**Response:**
```json
[
  {
    "id": "c78e9fe4-1ca5-4404-8fbe-a9977722bd15",
    "name": "My Test Strategy",
    "description": "Created from frontend wizard",
    "strategy_type": "fixed_point",
    "process_step": "litho",
    "tool_type": "ASML",
    "version": "1.0.0",
    "author": "frontend_user",
    "created_at": "2025-07-13T16:37:54.338913",
    "modified_at": "2025-07-13T16:37:54.338917",
    "lifecycle_state": "draft",
    "rule_count": 0
  }
]
```

### 3. Strategy Details

**Get Single Strategy**
```bash
GET /api/v1/strategies/{strategy_id}
```

**Response:**
```json
{
  "id": "c78e9fe4-1ca5-4404-8fbe-a9977722bd15",
  "name": "My Test Strategy",
  "description": "Created from frontend wizard",
  "strategy_type": "fixed_point",
  "process_step": "litho",
  "tool_type": "ASML",
  "rules": [],
  "conditions": null,
  "transformations": null,
  "target_vendor": null,
  "vendor_specific_params": {},
  "version": "1.0.0",
  "author": "frontend_user",
  "created_at": "2025-07-13T16:37:54.338913",
  "modified_at": "2025-07-13T16:37:54.338917",
  "lifecycle_state": "draft",
  "schema_version": "1.0"
}
```

### 4. Add Rules to Strategy

**Update Strategy with Rules**
```bash
PUT /api/v1/strategies/{strategy_id}
Content-Type: application/json

{
  "rules": [
    {
      "rule_type": "fixed_point",
      "parameters": {
        "points": [[1, 1], [2, 2], [3, 3], [4, 4]]
      },
      "weight": 1.0,
      "enabled": true
    }
  ]
}
```

### 5. Strategy Simulation

**Simulate Strategy Execution**
```bash
POST /api/v1/strategies/{strategy_id}/simulate
Content-Type: application/json

{
  "strategy_id": "c78e9fe4-1ca5-4404-8fbe-a9977722bd15",
  "wafer_map_data": {
    "grid_size": 10
  },
  "process_parameters": {
    "wafer_size": "300mm",
    "product_type": "memory"
  },
  "tool_constraints": {
    "max_sites": 50
  }
}
```

**Response:**
```json
{
  "selected_points": [
    {"x": 1, "y": 1, "available": true},
    {"x": 2, "y": 2, "available": true},
    {"x": 3, "y": 3, "available": true},
    {"x": 4, "y": 4, "available": true}
  ],
  "coverage_stats": {
    "total_dies": 100,
    "available_dies": 100,
    "selected_count": 4,
    "coverage_percentage": 4.0,
    "distribution": {
      "x_range": {"min": 1, "max": 4},
      "y_range": {"min": 1, "max": 4},
      "center_of_mass": {"x": 2.5, "y": 2.5}
    }
  },
  "performance_metrics": {
    "estimated_execution_time_ms": 10,
    "memory_usage_estimate": "low",
    "complexity_score": 1
  },
  "warnings": []
}
```

## 🎯 Frontend Integration Strategy

### Step 1: Basic Connection
1. Update `src/frontend/src/services/api.ts` baseURL to `http://localhost:8000`
2. Test strategy creation from wizard form
3. Verify strategy appears in listing

### Step 2: Progressive Workflow
1. Create strategy without rules (draft)
2. Allow user to add rules through UI
3. Update strategy with rules via PUT endpoint
4. Enable simulation once rules are added

### Step 3: Visualization Integration
1. Call simulation endpoint when user previews
2. Parse `selected_points` for wafer map visualization
3. Display `coverage_stats` to user
4. Handle `warnings` and errors gracefully

## 🔍 Supported Rule Types

The backend supports these rule types in the plugin system:

- `fixed_point` - Select specific coordinates
- `center_edge` - Select center and edge points  
- `uniform_grid` - Uniform grid pattern
- `random_sampling` - Random point selection

## ⚠️ Error Handling

### Common Error Responses

**Validation Error:**
```json
{
  "detail": "Strategy validation failed: Strategy name is required"
}
```

**Not Found Error:**
```json
{
  "detail": "Strategy not found"
}
```

**Simulation Error:**
```json
{
  "selected_points": [],
  "coverage_stats": {},
  "performance_metrics": {},
  "warnings": ["Simulation failed: Strategy has no rules defined"]
}
```

## 🧪 Testing Examples

### Test Strategy Creation Flow
```javascript
// 1. Create strategy
const response = await fetch('http://localhost:8000/api/v1/strategies/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    name: "Test Strategy",
    description: "Frontend integration test",
    process_step: "litho",
    tool_type: "ASML",
    strategy_type: "fixed_point",
    author: "test_user"
  })
});
const strategy = await response.json();

// 2. Add rules
await fetch(`http://localhost:8000/api/v1/strategies/${strategy.id}`, {
  method: 'PUT',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    rules: [{
      rule_type: "fixed_point",
      parameters: { points: [[1,1], [2,2]] },
      weight: 1.0,
      enabled: true
    }]
  })
});

// 3. Simulate
const simResult = await fetch(`http://localhost:8000/api/v1/strategies/${strategy.id}/simulate`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    strategy_id: strategy.id,
    wafer_map_data: { grid_size: 5 },
    process_parameters: {},
    tool_constraints: {}
  })
});
const simulation = await simResult.json();
```

## 🚀 Next Steps for Frontend Team

1. **Update API Base URL** - Point to `http://localhost:8000`
2. **Test Basic Connection** - Verify health endpoint responds
3. **Connect Strategy Creation** - Wire wizard form to POST endpoint
4. **Implement Progressive Flow** - Create → Add Rules → Simulate
5. **Add Error Handling** - Handle validation and network errors
6. **Enhance UX** - Loading states, success messages, error notifications

## 📞 Backend Support

The backend is fully operational and ready for integration. If you encounter any issues:

1. Check server is running: `curl http://localhost:8000/health`
2. Verify CORS: Check browser console for CORS errors
3. Check request format: Use examples above as reference
4. Review error responses: Backend provides detailed error messages

Ready to support the frontend integration process! 🚀