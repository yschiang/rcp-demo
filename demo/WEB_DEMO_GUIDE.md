# 🌐 Web Demo Guide: Wafer Sampling Strategy System

> **Interactive web interface demonstration - Much more impressive than API calls!**

---

## 🚀 Quick Setup

### Start Both Services
```bash
# Terminal 1: Backend
cd src/backend
python -m uvicorn app.main:app --reload --port 8000

# Terminal 2: Frontend  
cd src/frontend
npm run dev
```

### Access Points
- **Frontend UI**: http://localhost:5173/
- **Backend API**: http://localhost:8000/
- **API Docs**: http://localhost:8000/docs

---

## 🎯 Web Demo Flow (20 minutes)

### **Pre-Demo Setup** (2 minutes)
1. Open browser to `http://localhost:5173/`
2. Verify both services are running
3. Have demo files ready in `demo/schematics/`

---

## Phase 1: Strategy List & Navigation (3 minutes)

### 1.1 Landing Page
- **URL**: `http://localhost:5173/`
- **Action**: Navigate to strategies page
- **Demo Point**: "Clean, professional interface designed for fab engineers"

### 1.2 Strategy List View
- **Page**: Strategy List (`/strategies`)
- **Features to Show**:
  - List of existing strategies
  - Filter by process step, tool type
  - Search functionality
  - Create new strategy button

**Talking Point**: *"Engineers can see all strategies at a glance, filter by their specific tools and processes"*

---

## Phase 2: Strategy Builder Wizard (10 minutes)

### 2.1 Start New Strategy
- **Action**: Click "Create New Strategy"
- **URL**: `/strategy-builder`
- **Demo Point**: "6-step wizard guides users through the complete process"

### 2.2 Step 1: Basic Information
**What to Show**:
- Strategy name: "Demo Strategy - Live"
- Description: "Demonstration of Phase 2 web interface"
- Process step: "Lithography" 
- Tool type: "ASML_PAS5500"
- Author: "Demo Engineer"

**Demo Points**:
- Dropdown menus for standard values
- Form validation in real-time
- Professional tool type selection

### 2.3 Step 2: Schematic Upload
**What to Demo**:
- Drag & drop interface for file upload
- Upload `demo/schematics/simple_wafer_layout.svg`
- Show upload progress
- Display parsing results

**Expected Results**:
- File upload progress bar
- "✅ Uploaded successfully: 18 dies detected"
- Preview of schematic if available

**Talking Points**:
- *"Drag and drop - just like any modern file interface"*
- *"Real-time parsing with immediate feedback"*
- *"Supports all industry formats: GDSII, DXF, SVG"*

### 2.4 Step 3: Rules Configuration
**What to Show**:
- Visual rule builder interface
- Add multiple rules:
  1. **Fixed Points**: Points [0,0], [1,1], [2,2] - Weight 40%
  2. **Center Edge**: Margin 5mm - Weight 30%  
  3. **Uniform Grid**: Spacing 10mm - Weight 30%

**Demo Features**:
- Rule type dropdown selection
- Parameter input fields
- Weight sliders that sum to 100%
- Real-time validation

**Talking Points**:
- *"Visual rule builder - no coding required"*
- *"Weights automatically balanced"*
- *"Complex strategies made simple"*

### 2.5 Step 4: Conditions
**Configuration to Demo**:
- Wafer size: 300mm
- Product type: Memory
- Process layer: Metal1
- Temperature range: 22-28°C
- Defect density threshold: 0.05

**Demo Point**: *"Process constraints ensure strategies work in real fab conditions"*

### 2.6 Step 5: Transformations
**Show Options**:
- Rotation: 90 degrees
- Scale: 1.0x
- Offset: (0,0)
- Flip options

**Demo Point**: *"Handle coordinate system differences between tools automatically"*

### 2.7 Step 6: Preview & Validation
**This is the WOW moment!**

**What Should Display**:
- Interactive wafer map visualization
- Schematic overlay (purple dashed lines)
- Strategy points (blue dots)
- Coverage statistics
- Real-time validation results

**Expected Visualization**:
```
┌─────────────────────────────────┐
│     Wafer Map Visualization     │
│                                 │
│  ┌─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─┐   │
│  ┆ ● ● ●   ● ● ●   ● ● ● ┆   │
│  ┆                       ┆   │ 
│  ┆ ● ● ●   ● ● ●   ● ● ● ┆   │
│  ┆                       ┆   │
│  ┆ ● ● ●   ● ● ●   ● ● ● ┆   │
│  └─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─┘   │
│                                 │
│ Stats: 12/18 dies (67% coverage)│
│ Validation Score: 0.94          │
└─────────────────────────────────┘
```

**Key Features to Highlight**:
- Interactive zoom/pan
- Hover for die details
- Real-time coverage calculation
- Validation score display
- Strategy point attribution

**Talking Points**:
- *"See exactly what your strategy does before deployment"*
- *"Interactive visualization with zoom and pan"*
- *"Real-time validation prevents fab errors"*
- *"94% alignment score - exceeds 80% requirement"*

---

## Phase 3: Advanced Features (5 minutes)

### 3.1 Strategy Simulation
**If Available in UI**:
- Run simulation button
- Progress indicator
- Results display with metrics

### 3.2 Export Options
**Demo Export Features**:
- Download button for tool-specific formats
- ASML JSON export
- KLA XML export
- Format selection dropdown

**Demo Point**: *"Direct export to your fab tools - no manual translation"*

### 3.3 Strategy Management
**Show Strategy Lifecycle**:
- Save as draft
- Submit for review
- Approval workflow
- Version tracking

---

## 🎭 Web Demo Script & Talking Points

### **Opening Hook** (1 minute)
*"Instead of showing you command lines and JSON files, let me show you the actual interface your engineers will use daily. This is designed by engineers, for engineers."*

### **Navigation Demo** (2 minutes)
*"Clean, intuitive interface. Engineers can find existing strategies instantly or create new ones without IT support."*

### **Upload Demo** (3 minutes)
*"Drag and drop - just like any modern application. Upload any format, get instant feedback. Watch this - 18 dies detected automatically from our SVG file."*

### **Strategy Builder Demo** (8 minutes)
*"Now the magic happens. Visual rule builder - no programming required. Watch as we build a complex 3-rule strategy..."*

**Key Moments**:
- Adding rules: *"Point and click rule configuration"*
- Weight balancing: *"Automatic weight validation"*  
- Conditions: *"Real fab constraints built in"*
- Preview: *"And here's the WOW moment - see exactly what you get"*

### **Visualization Demo** (4 minutes)
*"This isn't just a pretty picture - this is your actual sampling pattern. Each blue dot is where the tool will measure. Purple dashed line shows your schematic overlay. 67% coverage with 0.94 validation score."*

### **Value Proposition** (2 minutes)
*"What you just saw would normally take 4 hours of manual work, phone calls to IT, and multiple revision cycles. We just did it in 10 minutes with zero errors."*

---

## 🚨 Web Demo Troubleshooting

### Frontend Won't Load
```bash
# Check if frontend is running
curl http://localhost:5173

# Restart if needed
cd src/frontend
npm run dev
```

### Upload Failures in UI
- Check browser console for errors
- Verify backend is running on port 8000
- Check file size (< 100MB limit)

### Visualization Not Showing
- Check browser console for JavaScript errors
- Verify schematic uploaded successfully
- Check that strategy has rules configured

### API Connection Issues
- Verify CORS settings in backend
- Check browser network tab for failed requests
- Ensure API endpoints are accessible

---

## 🎯 Web Demo Success Criteria

### Visual Impact
- ✅ Clean, professional interface loads quickly
- ✅ File upload works smoothly with progress
- ✅ Wafer map visualization renders correctly
- ✅ All animations and transitions work
- ✅ No browser console errors

### Functional Demonstration
- ✅ Complete workflow in < 15 minutes
- ✅ File upload with die detection
- ✅ Multi-rule strategy configuration
- ✅ Real-time validation with score > 0.8
- ✅ Interactive wafer map with coverage stats
- ✅ Export functionality accessible

### Business Impact
- ✅ Self-service capability clearly demonstrated
- ✅ Error prevention through validation
- ✅ Professional tool integration shown
- ✅ Time savings visually obvious
- ✅ No technical expertise required

---

## 📊 Web Demo Advantages vs API Demo

| Aspect | API Demo | Web Demo | Winner |
|--------|----------|----------|---------|
| **Visual Impact** | Low | High | 🌐 Web |
| **Stakeholder Appeal** | Technical only | Business + Technical | 🌐 Web |
| **User Experience** | Command line | Point & click | 🌐 Web |
| **Error Handling** | JSON responses | Visual feedback | 🌐 Web |
| **Validation Display** | Text scores | Interactive visualization | 🌐 Web |
| **Learning Curve** | High | None | 🌐 Web |
| **Demo Reliability** | Script dependent | UI robust | 🌐 Web |
| **Wow Factor** | Low | High | 🌐 Web |

---

## 🎉 Web Demo Closing

### Summary Points
*"What you've seen is a production-ready system that transforms wafer sampling from a 4-hour technical task to a 15-minute self-service process. Your engineers get a tool designed for their workflow, and your IT team gets reliable, validated deployments."*

### Next Steps
1. **Pilot Program**: Start with 5 engineers next week
2. **Training**: 2-hour session covers everything shown
3. **Integration**: Connect to your existing fab tools  
4. **Rollout**: Full deployment within 30 days

### Call to Action
*"The interface you just saw is ready for production. We can begin pilot deployment immediately and start seeing benefits from day one."*

---

**🌐 The web interface is your best demo tool - visual, intuitive, and impressive!**

*This creates an engaging, professional demonstration that showcases both technical capabilities and business value through an interface stakeholders can immediately understand and appreciate.*