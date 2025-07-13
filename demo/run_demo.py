#!/usr/bin/env python3
"""
Automated Demo Script for Wafer Sampling Strategy System
Phase 2 Demo: Complete workflow automation with validation
"""

import requests
import json
import time
import sys
from pathlib import Path
import argparse
from typing import Dict, Any, Optional

class DemoRunner:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.demo_data = {}
        self.verbose = False
        
    def log(self, message: str, level: str = "INFO"):
        """Log message with timestamp."""
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def check_health(self) -> bool:
        """Check if the API is healthy."""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                self.log("✅ Backend API is healthy")
                return True
            else:
                self.log(f"❌ Backend health check failed: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            self.log(f"❌ Cannot connect to backend: {e}")
            return False
            
    def upload_schematic(self, file_path: str, created_by: str = "demo_user") -> Optional[str]:
        """Upload a schematic file and return the ID."""
        file_path = Path(file_path)
        if not file_path.exists():
            self.log(f"❌ File not found: {file_path}")
            return None
            
        try:
            with open(file_path, 'rb') as f:
                files = {'file': (file_path.name, f, 'application/octet-stream')}
                data = {'created_by': created_by}
                
                self.log(f"📤 Uploading {file_path.name}...")
                response = self.session.post(
                    f"{self.base_url}/api/v1/schematics/upload?created_by={created_by}",
                    files=files,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    schematic_id = result.get('id')
                    die_count = result.get('die_count', 'unknown')
                    self.log(f"✅ Uploaded {file_path.name} - ID: {schematic_id}, Dies: {die_count}")
                    return schematic_id
                else:
                    self.log(f"❌ Upload failed: {response.status_code} - {response.text}")
                    return None
                    
        except requests.exceptions.RequestException as e:
            self.log(f"❌ Upload error: {e}")
            return None
            
    def create_strategy(self, name: str, schematic_id: Optional[str] = None) -> Optional[str]:
        """Create a strategy and return the ID."""
        strategy_data = {
            "name": name,
            "description": f"Demo strategy created by automation - {time.strftime('%Y-%m-%d %H:%M')}",
            "process_step": "Lithography",
            "tool_type": "ASML_PAS5500",
            "strategy_type": "custom",
            "author": "demo_automation"
        }
        
        try:
            self.log(f"🏗️ Creating strategy: {name}")
            response = self.session.post(
                f"{self.base_url}/api/v1/strategies/",
                json=strategy_data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                strategy_id = result.get('id')
                self.log(f"✅ Created strategy - ID: {strategy_id}")
                return strategy_id
            else:
                self.log(f"❌ Strategy creation failed: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            self.log(f"❌ Strategy creation error: {e}")
            return None
            
    def update_strategy_rules(self, strategy_id: str) -> bool:
        """Add rules to a strategy."""
        rules_data = {
            "rules": [
                {
                    "rule_type": "fixed_point",
                    "parameters": {"points": [[0,0], [1,1], [2,2]]},
                    "weight": 0.4,
                    "enabled": True
                },
                {
                    "rule_type": "center_edge",
                    "parameters": {"edge_margin": 5},
                    "weight": 0.3,
                    "enabled": True
                },
                {
                    "rule_type": "uniform_grid",
                    "parameters": {"grid_spacing": 10, "offset_x": 2, "offset_y": 2},
                    "weight": 0.3,
                    "enabled": True
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
                "flip_x": False,
                "flip_y": False
            }
        }
        
        try:
            self.log(f"⚙️ Adding rules to strategy {strategy_id}")
            response = self.session.put(
                f"{self.base_url}/api/v1/strategies/{strategy_id}",
                json=rules_data,
                timeout=10
            )
            
            if response.status_code == 200:
                self.log("✅ Strategy rules updated successfully")
                return True
            else:
                self.log(f"❌ Rule update failed: {response.status_code} - {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.log(f"❌ Rule update error: {e}")
            return False
            
    def validate_strategy(self, schematic_id: str, strategy_id: str) -> Dict[str, Any]:
        """Validate strategy against schematic."""
        validation_data = {
            "strategy_id": strategy_id,
            "validation_mode": "strict"
        }
        
        try:
            self.log(f"🔍 Validating strategy {strategy_id} against schematic {schematic_id}")
            response = self.session.post(
                f"{self.base_url}/api/v1/schematics/{schematic_id}/validate",
                json=validation_data,
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                status = result.get('validation_status', 'unknown')
                score = result.get('alignment_score', 0)
                coverage = result.get('coverage_analysis', {}).get('coverage_percentage', 0)
                
                self.log(f"✅ Validation complete - Status: {status}, Score: {score:.2f}, Coverage: {coverage}%")
                return result
            else:
                self.log(f"❌ Validation failed: {response.status_code} - {response.text}")
                return {}
                
        except requests.exceptions.RequestException as e:
            self.log(f"❌ Validation error: {e}")
            return {}
            
    def simulate_strategy(self, strategy_id: str) -> Dict[str, Any]:
        """Run strategy simulation."""
        simulation_data = {
            "wafer_map_data": {
                "dies": [
                    {"x": x, "y": y, "available": True}
                    for x in range(3) for y in range(3)
                ]
            },
            "process_parameters": {"temperature": 25, "pressure": 1013},
            "tool_constraints": {"max_sites": 50, "min_spacing": 2}
        }
        
        try:
            self.log(f"🎯 Running simulation for strategy {strategy_id}")
            response = self.session.post(
                f"{self.base_url}/api/v1/strategies/{strategy_id}/simulate",
                json=simulation_data,
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                selected_count = len(result.get('selected_points', []))
                coverage_stats = result.get('coverage_stats', {})
                total_dies = coverage_stats.get('total_dies', 0)
                coverage_pct = coverage_stats.get('coverage_percentage', 0)
                
                self.log(f"✅ Simulation complete - Selected: {selected_count}, Coverage: {coverage_pct}%")
                return result
            else:
                self.log(f"❌ Simulation failed: {response.status_code} - {response.text}")
                return {}
                
        except requests.exceptions.RequestException as e:
            self.log(f"❌ Simulation error: {e}")
            return {}
            
    def export_schematic(self, schematic_id: str, format_type: str = "svg") -> bool:
        """Export schematic in specified format."""
        try:
            self.log(f"📥 Exporting schematic {schematic_id} as {format_type.upper()}")
            response = self.session.get(
                f"{self.base_url}/api/v1/schematics/{schematic_id}/export/{format_type}",
                timeout=10
            )
            
            if response.status_code == 200:
                content_length = len(response.content)
                self.log(f"✅ Export successful - {content_length} bytes received")
                return True
            else:
                self.log(f"❌ Export failed: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.log(f"❌ Export error: {e}")
            return False
            
    def run_complete_demo(self) -> Dict[str, Any]:
        """Run the complete Phase 2 demo workflow."""
        self.log("🚀 Starting Phase 2 Demo - Complete Workflow")
        demo_results = {
            "start_time": time.time(),
            "steps_completed": [],
            "errors": [],
            "data": {}
        }
        
        # Step 1: Health Check
        if not self.check_health():
            demo_results["errors"].append("Health check failed")
            return demo_results
        demo_results["steps_completed"].append("health_check")
        
        # Step 2: Upload Schematics
        demo_dir = Path(__file__).parent
        simple_svg = demo_dir / "schematics" / "simple_wafer_layout.svg"
        complex_svg = demo_dir / "schematics" / "complex_wafer_layout.svg"
        dxf_file = demo_dir / "schematics" / "processor_die.dxf"
        
        schematic_ids = {}
        
        if simple_svg.exists():
            schematic_id = self.upload_schematic(simple_svg)
            if schematic_id:
                schematic_ids["simple"] = schematic_id
                demo_results["data"]["simple_schematic_id"] = schematic_id
        
        if complex_svg.exists():
            schematic_id = self.upload_schematic(complex_svg)
            if schematic_id:
                schematic_ids["complex"] = schematic_id
                demo_results["data"]["complex_schematic_id"] = schematic_id
                
        if dxf_file.exists():
            schematic_id = self.upload_schematic(dxf_file)
            if schematic_id:
                schematic_ids["dxf"] = schematic_id
                demo_results["data"]["dxf_schematic_id"] = schematic_id
        
        if not schematic_ids:
            demo_results["errors"].append("No schematics uploaded successfully")
            return demo_results
        demo_results["steps_completed"].append("schematic_upload")
        
        # Step 3: Create Strategy
        primary_schematic_id = list(schematic_ids.values())[0]
        strategy_id = self.create_strategy("Demo Strategy - Automated")
        if not strategy_id:
            demo_results["errors"].append("Strategy creation failed")
            return demo_results
        demo_results["data"]["strategy_id"] = strategy_id
        demo_results["steps_completed"].append("strategy_creation")
        
        # Step 4: Update Strategy Rules
        if not self.update_strategy_rules(strategy_id):
            demo_results["errors"].append("Strategy rule update failed")
            return demo_results
        demo_results["steps_completed"].append("strategy_rules")
        
        # Step 5: Validate Strategy
        validation_result = self.validate_strategy(primary_schematic_id, strategy_id)
        if validation_result:
            demo_results["data"]["validation"] = validation_result
            demo_results["steps_completed"].append("validation")
        
        # Step 6: Run Simulation
        simulation_result = self.simulate_strategy(strategy_id)
        if simulation_result:
            demo_results["data"]["simulation"] = simulation_result
            demo_results["steps_completed"].append("simulation")
        
        # Step 7: Export Results
        export_success = self.export_schematic(primary_schematic_id, "svg")
        if export_success:
            demo_results["steps_completed"].append("export")
        
        # Calculate completion
        demo_results["end_time"] = time.time()
        demo_results["duration"] = demo_results["end_time"] - demo_results["start_time"]
        demo_results["success_rate"] = len(demo_results["steps_completed"]) / 7 * 100
        
        # Final summary
        self.log(f"🎉 Demo completed in {demo_results['duration']:.1f} seconds")
        self.log(f"📊 Success rate: {demo_results['success_rate']:.1f}% ({len(demo_results['steps_completed'])}/7 steps)")
        
        if demo_results["errors"]:
            self.log(f"⚠️ Errors encountered: {len(demo_results['errors'])}")
            for error in demo_results["errors"]:
                self.log(f"   - {error}")
        
        return demo_results
        
    def print_summary(self, results: Dict[str, Any]):
        """Print a detailed summary of the demo results."""
        print("\n" + "="*60)
        print("PHASE 2 DEMO SUMMARY")
        print("="*60)
        
        print(f"Duration: {results.get('duration', 0):.1f} seconds")
        print(f"Success Rate: {results.get('success_rate', 0):.1f}%")
        print(f"Steps Completed: {len(results.get('steps_completed', []))}/7")
        
        print("\nCompleted Steps:")
        for step in results.get('steps_completed', []):
            print(f"  ✅ {step.replace('_', ' ').title()}")
        
        if results.get('errors'):
            print("\nErrors:")
            for error in results['errors']:
                print(f"  ❌ {error}")
        
        data = results.get('data', {})
        if data:
            print("\nGenerated Data:")
            for key, value in data.items():
                if isinstance(value, dict):
                    print(f"  📊 {key}: {len(value)} items")
                else:
                    print(f"  🆔 {key}: {value}")
        
        print("\n" + "="*60)
        
        # Success criteria
        success_rate = results.get('success_rate', 0)
        if success_rate >= 85:
            print("🎉 DEMO SUCCESS: Ready for Phase 2 deployment!")
        elif success_rate >= 70:
            print("⚠️ DEMO PARTIAL: Minor issues detected")
        else:
            print("❌ DEMO ISSUES: Significant problems need resolution")
        
        print("="*60)

def main():
    parser = argparse.ArgumentParser(description="Run Phase 2 Demo for Wafer Sampling Strategy System")
    parser.add_argument("--base-url", default="http://localhost:8000", 
                       help="Base URL for the API (default: http://localhost:8000)")
    parser.add_argument("--verbose", action="store_true", 
                       help="Enable verbose logging")
    
    args = parser.parse_args()
    
    demo = DemoRunner(base_url=args.base_url)
    demo.verbose = args.verbose
    
    try:
        results = demo.run_complete_demo()
        demo.print_summary(results)
        
        # Exit with appropriate code
        success_rate = results.get('success_rate', 0)
        sys.exit(0 if success_rate >= 85 else 1)
        
    except KeyboardInterrupt:
        print("\n⚠️ Demo interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()