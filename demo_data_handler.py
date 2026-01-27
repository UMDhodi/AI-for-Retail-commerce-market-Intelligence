"""
Demo Data Handler for BharatSignal
Manages sample data and demo scenarios for demonstration purposes
"""

import json
import os
from typing import List, Dict, Any, Optional, Tuple
from models import SalesRecord, LocalContext
from csv_processor import parse_csv_from_file

class DemoDataHandler:
    """Handles demo data scenarios and sample CSV files"""
    
    def __init__(self, sample_data_dir: str = "sample_data"):
        self.sample_data_dir = sample_data_dir
        self.scenarios_file = os.path.join(sample_data_dir, "demo_scenarios.json")
        self._scenarios = None
    
    def load_scenarios(self) -> Dict[str, Any]:
        """Load demo scenarios from JSON file"""
        if self._scenarios is None:
            try:
                with open(self.scenarios_file, 'r', encoding='utf-8') as f:
                    self._scenarios = json.load(f)
            except FileNotFoundError:
                # Fallback scenarios if file doesn't exist
                self._scenarios = self._get_fallback_scenarios()
            except json.JSONDecodeError:
                self._scenarios = self._get_fallback_scenarios()
        
        return self._scenarios
    
    def _get_fallback_scenarios(self) -> Dict[str, Any]:
        """Fallback scenarios if JSON file is not available"""
        return {
            "scenarios": [
                {
                    "name": "Basic Demo",
                    "csv_file": "kirana_sales_sample.csv",
                    "context": "This is a basic demo with sample kirana shop data. Diwali festival is coming next week."
                }
            ]
        }
    
    def get_available_scenarios(self) -> List[Dict[str, str]]:
        """Get list of available demo scenarios"""
        scenarios = self.load_scenarios()
        return [
            {
                "name": scenario["name"],
                "description": scenario.get("description", f"Demo scenario: {scenario['name']}")
            }
            for scenario in scenarios["scenarios"]
        ]
    
    def get_scenario_by_name(self, scenario_name: str) -> Optional[Dict[str, Any]]:
        """Get a specific scenario by name"""
        scenarios = self.load_scenarios()
        for scenario in scenarios["scenarios"]:
            if scenario["name"] == scenario_name:
                return scenario
        return None
    
    def load_demo_data(self, scenario_name: str) -> Tuple[List[SalesRecord], LocalContext, bool]:
        """
        Load demo data for a specific scenario
        Returns: (sales_records, context, success)
        """
        scenario = self.get_scenario_by_name(scenario_name)
        if not scenario:
            return [], LocalContext(""), False
        
        # Load CSV data
        csv_file_path = os.path.join(self.sample_data_dir, scenario["csv_file"])
        try:
            with open(csv_file_path, 'r', encoding='utf-8') as f:
                csv_result = parse_csv_from_file(f)
                
            if not csv_result.success:
                return [], LocalContext(""), False
            
            sales_records = csv_result.valid_records
            
        except FileNotFoundError:
            return [], LocalContext(""), False
        except Exception:
            return [], LocalContext(""), False
        
        # Create context
        context = LocalContext(scenario["context"])
        
        return sales_records, context, True
    
    def get_default_scenario(self) -> str:
        """Get the name of the default demo scenario"""
        scenarios = self.load_scenarios()
        if scenarios["scenarios"]:
            return scenarios["scenarios"][0]["name"]
        return "Basic Demo"
    
    def is_demo_mode_available(self) -> bool:
        """Check if demo mode is available (has scenarios and data files)"""
        try:
            scenarios = self.load_scenarios()
            return len(scenarios["scenarios"]) > 0
        except Exception:
            return False

# Global demo handler instance
demo_handler = DemoDataHandler()

def get_demo_handler() -> DemoDataHandler:
    """Get the global demo handler instance"""
    return demo_handler