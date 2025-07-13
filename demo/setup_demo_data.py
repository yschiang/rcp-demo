#!/usr/bin/env python3
"""
Setup Demo Data for Wafer Sampling Strategy System
Pre-populates the system with sample data for demonstration purposes
"""

import requests
import json
import time
from pathlib import Path
import yaml

class DemoDataSetup:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        
    def log(self, message: str):
        """Log message with timestamp."""
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")
        
    def check_connection(self) -> bool:
        """Check if we can connect to the API."""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
            
    def create_sample_strategies(self):
        """Create a variety of sample strategies for demo."""
        strategies = [
            {
                "name": "Memory Chip - Basic Sampling",
                "description": "Standard sampling pattern for memory chip production",
                "process_step": "Lithography",
                "tool_type": "ASML_PAS5500",
                "strategy_type": "uniform_grid",
                "author": "Memory Team",
                "rules": [
                    {
                        "rule_type": "uniform_grid",
                        "parameters": {"grid_spacing": 20, "offset_x": 5, "offset_y": 5},
                        "weight": 0.7,
                        "enabled": True
                    },
                    {
                        "rule_type": "center_edge",
                        "parameters": {"edge_margin": 10},
                        "weight": 0.3,
                        "enabled": True
                    }
                ],
                "conditions": {
                    "wafer_size": "300mm",
                    "product_type": "Memory",
                    "process_layer": "Poly",
                    "defect_density_threshold": 0.02
                }
            },
            {
                "name": "Processor Die - Advanced Pattern",
                "description": "Optimized sampling for high-performance processor dies",
                "process_step": "Etch",
                "tool_type": "KLA_2132",
                "strategy_type": "hotspot_priority",
                "author": "Logic Team",
                "rules": [
                    {
                        "rule_type": "hotspot_priority",
                        "parameters": {"hotspot_threshold": 0.8, "priority_zones": ["center"]},
                        "weight": 0.5,
                        "enabled": True
                    },
                    {
                        "rule_type": "fixed_point",
                        "parameters": {"points": [[0,0], [10,10], [-10,-10], [10,-10], [-10,10]]},
                        "weight": 0.3,
                        "enabled": True
                    },
                    {
                        "rule_type": "uniform_grid",
                        "parameters": {"grid_spacing": 15, "offset_x": 2, "offset_y": 2},
                        "weight": 0.2,
                        "enabled": True
                    }
                ],
                "conditions": {
                    "wafer_size": "300mm",
                    "product_type": "Logic",
                    "process_layer": "Metal3",
                    "defect_density_threshold": 0.05
                },
                "transformations": {
                    "rotation_angle": 45,
                    "scale_factor": 1.1,
                    "offset_x": 0,
                    "offset_y": 0,
                    "flip_x": False,
                    "flip_y": True
                }
            },
            {
                "name": "Mixed Signal - Adaptive Sampling",
                "description": "Adaptive sampling strategy for mixed-signal devices",
                "process_step": "CMP",
                "tool_type": "Applied_Materials_Reflexion",
                "strategy_type": "adaptive",
                "author": "Mixed Signal Team",
                "rules": [
                    {
                        "rule_type": "adaptive",
                        "parameters": {"base_density": 0.1, "hotspot_multiplier": 3.0},
                        "weight": 0.6,
                        "enabled": True
                    },
                    {
                        "rule_type": "center_edge",
                        "parameters": {"edge_margin": 8, "center_density": 2.0},
                        "weight": 0.4,
                        "enabled": True
                    }
                ],
                "conditions": {
                    "wafer_size": "200mm",
                    "product_type": "Mixed_Signal",
                    "process_layer": "Metal1",
                    "defect_density_threshold": 0.03
                }
            }
        ]
        
        created_strategies = []
        for strategy_data in strategies:
            try:
                # Create basic strategy first
                basic_data = {
                    "name": strategy_data["name"],
                    "description": strategy_data["description"],
                    "process_step": strategy_data["process_step"],
                    "tool_type": strategy_data["tool_type"],
                    "strategy_type": strategy_data["strategy_type"],
                    "author": strategy_data["author"]
                }
                
                self.log(f"Creating strategy: {strategy_data['name']}")
                response = self.session.post(
                    f"{self.base_url}/api/v1/strategies/",
                    json=basic_data,
                    timeout=10
                )
                
                if response.status_code == 200:
                    strategy = response.json()
                    strategy_id = strategy.get('id')
                    
                    # Update with rules and conditions
                    update_data = {}
                    if "rules" in strategy_data:
                        update_data["rules"] = strategy_data["rules"]
                    if "conditions" in strategy_data:
                        update_data["conditions"] = strategy_data["conditions"]
                    if "transformations" in strategy_data:
                        update_data["transformations"] = strategy_data["transformations"]
                    
                    if update_data:
                        update_response = self.session.put(
                            f"{self.base_url}/api/v1/strategies/{strategy_id}",
                            json=update_data,
                            timeout=10
                        )
                        
                        if update_response.status_code == 200:
                            self.log(f"✅ Strategy created and updated: {strategy_id}")
                            created_strategies.append(strategy_id)
                        else:
                            self.log(f"⚠️ Strategy created but update failed: {strategy_id}")
                            created_strategies.append(strategy_id)
                    else:
                        self.log(f"✅ Basic strategy created: {strategy_id}")
                        created_strategies.append(strategy_id)
                        
                else:
                    self.log(f"❌ Failed to create strategy: {strategy_data['name']}")
                    
            except Exception as e:
                self.log(f"❌ Error creating strategy {strategy_data['name']}: {e}")
                
        return created_strategies
        
    def upload_demo_schematics(self):
        """Upload all demo schematic files."""
        demo_dir = Path(__file__).parent
        schematic_files = [
            demo_dir / "schematics" / "simple_wafer_layout.svg",
            demo_dir / "schematics" / "complex_wafer_layout.svg", 
            demo_dir / "schematics" / "processor_die.dxf"
        ]
        
        uploaded_schematics = []
        for file_path in schematic_files:
            if file_path.exists():
                try:
                    with open(file_path, 'rb') as f:
                        files = {'file': (file_path.name, f, 'application/octet-stream')}
                        data = {'created_by': 'demo_setup'}
                        
                        self.log(f"Uploading schematic: {file_path.name}")
                        response = self.session.post(
                            f"{self.base_url}/api/v1/schematics/upload?created_by=demo_setup",
                            files=files,
                            timeout=30
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            schematic_id = result.get('id')
                            die_count = result.get('die_count', 'unknown')
                            self.log(f"✅ Uploaded {file_path.name}: {schematic_id} ({die_count} dies)")
                            uploaded_schematics.append(schematic_id)
                        else:
                            self.log(f"❌ Failed to upload {file_path.name}")
                            
                except Exception as e:
                    self.log(f"❌ Error uploading {file_path.name}: {e}")
            else:
                self.log(f"⚠️ Schematic file not found: {file_path}")
                
        return uploaded_schematics
        
    def create_demo_validations(self, strategy_ids, schematic_ids):
        """Create sample validation results."""
        if not strategy_ids or not schematic_ids:
            self.log("⚠️ No strategies or schematics available for validation")
            return
            
        # Validate first strategy against first schematic
        strategy_id = strategy_ids[0]
        schematic_id = schematic_ids[0]
        
        try:
            validation_data = {
                "strategy_id": strategy_id,
                "validation_mode": "strict"
            }
            
            self.log(f"Creating validation: strategy {strategy_id} vs schematic {schematic_id}")
            response = self.session.post(
                f"{self.base_url}/api/v1/schematics/{schematic_id}/validate",
                json=validation_data,
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                score = result.get('alignment_score', 0)
                self.log(f"✅ Validation created with score: {score:.2f}")
            else:
                self.log(f"❌ Validation failed: {response.status_code}")
                
        except Exception as e:
            self.log(f"❌ Error creating validation: {e}")
            
    def create_test_data_summary(self):
        """Create a summary of all test data for demo reference."""
        summary = {
            "demo_setup_completed": time.strftime("%Y-%m-%d %H:%M:%S"),
            "api_endpoints": {
                "health": f"{self.base_url}/health",
                "strategies": f"{self.base_url}/api/v1/strategies/",
                "schematics": f"{self.base_url}/api/v1/schematics/",
                "docs": f"{self.base_url}/docs"
            },
            "sample_data": {
                "strategies_created": 3,
                "schematics_uploaded": "3 (SVG simple, SVG complex, DXF)",
                "formats_supported": ["GDSII", "DXF", "SVG"],
                "demo_workflow": [
                    "Upload schematic file",
                    "Create strategy with rules",
                    "Validate strategy against schematic",
                    "Run simulation",
                    "Export results"
                ]
            },
            "demo_files": {
                "simple_svg": "9 dies in 3x3 grid",
                "complex_svg": "49 dies in 7x7 grid with edge dies",
                "dxf_cad": "4 dies in 2x2 CAD format",
                "advanced_yaml": "Complex multi-rule strategy template"
            }
        }
        
        summary_file = Path(__file__).parent / "demo_data_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        self.log(f"📋 Demo summary written to: {summary_file}")
        
    def run_setup(self):
        """Run the complete demo data setup."""
        self.log("🚀 Starting demo data setup...")
        
        # Check connection
        if not self.check_connection():
            self.log("❌ Cannot connect to API. Make sure the backend is running.")
            return False
            
        self.log("✅ Connected to API successfully")
        
        # Upload schematics first
        schematic_ids = self.upload_demo_schematics()
        self.log(f"📤 Uploaded {len(schematic_ids)} schematic files")
        
        # Create sample strategies
        strategy_ids = self.create_sample_strategies()
        self.log(f"🏗️ Created {len(strategy_ids)} sample strategies")
        
        # Create validations
        self.create_demo_validations(strategy_ids, schematic_ids)
        
        # Create summary
        self.create_test_data_summary()
        
        self.log("🎉 Demo data setup completed successfully!")
        self.log(f"📊 Summary: {len(strategy_ids)} strategies, {len(schematic_ids)} schematics")
        self.log(f"🌐 Access API docs at: {self.base_url}/docs")
        
        return True

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Setup demo data for Phase 2 demonstration")
    parser.add_argument("--base-url", default="http://localhost:8000",
                       help="Base URL for the API")
    
    args = parser.parse_args()
    
    setup = DemoDataSetup(base_url=args.base_url)
    
    try:
        success = setup.run_setup()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️ Setup interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        exit(1)

if __name__ == "__main__":
    main()