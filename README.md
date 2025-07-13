# Wafer Sampling Strategy System

A comprehensive system for creating, simulating, validating, and deploying wafer sampling strategies for semiconductor manufacturing tools.

## 🏗️ Architecture Overview

This system implements a layered, plugin-based architecture designed for scalability and extensibility:

### Backend Architecture (Python/FastAPI)
- **Strategy Definition Layer**: User-created templates (serializable, versionable)
- **Compilation Layer**: Converts definitions into validated, executable forms
- **Execution Layer**: Runtime context with wafer/tool/process state
- **Plugin Framework**: Extensible rules, vendors, and transformations
- **Repository Layer**: Strategy persistence, versioning, and lifecycle management

### Frontend Architecture (React/TypeScript)
- **Strategy Builder**: Multi-step wizard for strategy creation
- **Wafer Map Visualization**: Interactive SVG-based wafer representation
- **State Management**: Zustand stores with separation of concerns
- **Component Library**: Reusable UI components with consistent design

## 📋 Requirements Implementation

### Functional Requirements Status
- ✅ **FR1.3**: YAML Import for strategy definition
- ⚠️ **FR1.1**: System UI (guided wizard implemented, needs integration)
- ❌ **FR1.2**: Excel Import capability
- ⚠️ **FR2**: Simulation framework (backend ready, needs UI integration)
- ❌ **FR3**: Strategy deployment and version control
- ❌ **FR4**: Process-specific strategy configuration
- ✅ **FR5**: Vendor-specific data mapping (ASML/KLA implemented)

### Non-Functional Requirements
- ✅ **NFR1**: Self-Service UI (strategy wizard implemented)
- ✅ **NFR2**: No-Code Usage (plugin-based rule system)
- ⚠️ **NFR3**: Visualization (wafer map component ready)
- ❌ **NFR4**: Access Control (framework ready, needs implementation)
- ✅ **NFR5**: Extensibility (comprehensive plugin system)

## 🚀 Quick Start

### Backend Setup

1. **Install Dependencies**
```bash
cd src/backend
pip install -r requirements.txt
```

2. **Configuration**
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Run Development Server**
```bash
python -m app.main
# or
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

1. **Install Dependencies**
```bash
cd src/frontend
npm install
```

2. **Run Development Server**
```bash
npm run dev
```

The application will be available at:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## 🔧 Development

### Backend Development

**Core Components:**
- `app/core/strategy/` - Strategy definition, compilation, and repository
- `app/core/plugins/` - Plugin framework and built-in plugins
- `app/api/` - REST API endpoints
- `app/services/` - Business logic layer

**Adding New Rule Types:**
```python
from app.core.plugins.registry import register_plugin
from app.core.plugins.rules import RulePlugin

@register_plugin("rule", "my_custom_rule")
class MyCustomRulePlugin(RulePlugin):
    # Implementation
```

**Configuration:**
All configuration is environment-based using Pydantic settings. See `app/config.py`.

### Frontend Development

**Key Components:**
- `src/components/StrategyBuilder/` - Multi-step strategy creation wizard
- `src/components/WaferMap/` - Interactive wafer visualization
- `src/stores/` - Zustand state management
- `src/services/` - API client and utilities

**State Management:**
The application uses Zustand for state management with domain-specific stores.

## 🧪 Testing

### Backend Tests
```bash
cd src/backend
pytest
```

### Frontend Tests
```bash
cd src/frontend
npm test
```

## 📊 Plugin System

The system features a comprehensive plugin architecture:

### Rule Plugins
- **FixedPointRule**: Select specific coordinates
- **CenterEdgeRule**: Center and edge sampling
- **UniformGridRule**: Regular grid patterns
- **RandomSamplingRule**: Statistical sampling

### Vendor Plugins
- **ASMLMapping**: ASML lithography tools (JSON output)
- **KLAMapping**: KLA inspection tools (XML output)

### Adding Custom Plugins
1. Inherit from appropriate base class (`RulePlugin`, `VendorMapping`)
2. Use `@register_plugin` decorator
3. Implement required methods
4. Plugin auto-discovery handles registration

## 🔄 Workflow

The complete system workflow follows the specification:

1. **Strategy Creation**
   - UI guided form OR YAML/Excel import
   - Multi-step validation and preview

2. **Compilation**
   - Convert definition to executable form
   - Dependency resolution and validation

3. **Simulation**
   - Execute against test wafer maps
   - Coverage analysis and visualization

4. **Deployment**
   - Version control and lifecycle management
   - Vendor-specific format generation
   - Tool control system integration

## 📁 Project Structure

```
src/
├── backend/
│   ├── app/
│   │   ├── core/
│   │   │   ├── strategy/          # Strategy management
│   │   │   ├── plugins/           # Plugin framework
│   │   │   ├── models/            # Data models
│   │   │   └── vendor/            # Vendor integrations
│   │   ├── api/                   # REST API
│   │   ├── services/              # Business logic
│   │   ├── config.py              # Configuration
│   │   └── main.py                # FastAPI app
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── components/            # React components
    │   ├── stores/                # State management
    │   ├── services/              # API clients
    │   ├── types/                 # TypeScript types
    │   └── pages/                 # Route components
    └── package.json
```

## 🛣️ Roadmap

See [TODO.md](TODO.md) for the complete 20-week implementation roadmap covering:
- Phase 1: Core Infrastructure (Weeks 1-3)
- Phase 2: Self-Service UI (Weeks 4-7)
- Phase 3: Production Deployment (Weeks 8-11)
- Phase 4: Advanced Features (Weeks 12-16)
- Phase 5: Enterprise Integration (Weeks 17-20)

## 📖 Documentation

- **Architecture**: See `docs/1_oo.mermaid` for class diagrams
- **User Flow**: See `docs/0_flowchart.mermaid` for system workflow
- **Development Guide**: This README and inline code documentation
- **API Documentation**: Available at `/docs` when running the backend

## 🤝 Contributing

1. Follow the existing architectural patterns
2. Maintain separation of concerns between layers
3. Add tests for new functionality
4. Update documentation for architectural changes
5. Use the plugin system for extensibility

## 🔐 Security

- Environment-based configuration management
- Role-based access control framework (ready for implementation)
- Input validation and sanitization
- Secure API design with proper error handling

## 📄 License

[Add your license information here]