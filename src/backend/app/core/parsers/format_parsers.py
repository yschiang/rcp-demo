"""
Standard Schematic and Data Format Parsers
Supports industry-standard formats for wafer maps and sampling strategies.
"""
from typing import Dict, List, Any, Optional, Union
from abc import ABC, abstractmethod
import csv
import io
import json
import os
import yaml
import xml.etree.ElementTree as ET
from dataclasses import dataclass
import logging

from ..strategy.definition import StrategyDefinition, RuleConfig, ConditionalLogic, TransformationConfig
from ..models.die import Die
from ..models.wafer_map import WaferMap

logger = logging.getLogger(__name__)


@dataclass
class ParseResult:
    """Result of parsing operation."""
    success: bool
    data: Optional[Union[StrategyDefinition, WaferMap]] = None
    errors: List[str] = None
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []


class FormatParser(ABC):
    """Base class for format parsers."""
    
    @property
    @abstractmethod
    def supported_extensions(self) -> List[str]:
        """Return list of supported file extensions."""
        pass
    
    @property
    @abstractmethod
    def format_name(self) -> str:
        """Return human-readable format name."""
        pass
    
    @abstractmethod
    def parse_strategy(self, content: str, filename: str = "") -> ParseResult:
        """Parse strategy from content."""
        pass
    
    @abstractmethod
    def parse_wafer_map(self, content: str, filename: str = "") -> ParseResult:
        """Parse wafer map from content."""
        pass


class YAMLParser(FormatParser):
    """YAML format parser for strategies."""
    
    @property
    def supported_extensions(self) -> List[str]:
        return [".yaml", ".yml"]
    
    @property
    def format_name(self) -> str:
        return "YAML Strategy Format"
    
    def parse_strategy(self, content: str, filename: str = "") -> ParseResult:
        """Parse YAML strategy content."""
        try:
            data = yaml.safe_load(content)
            
            # Validate required fields
            errors = []
            if not data.get("name", "").strip():
                errors.append("Strategy name is required")
            if not data.get("rules"):
                errors.append("At least one rule is required")
            if errors:
                return ParseResult(success=False, errors=errors)
            
            # Convert to StrategyDefinition
            strategy = StrategyDefinition(
                name=data.get("name", ""),
                description=data.get("description", ""),
                process_step=data.get("process_step", ""),
                tool_type=data.get("tool_type", ""),
                rules=[
                    RuleConfig(
                        rule_type=rule.get("type", ""),
                        parameters=rule.get("parameters", {}),
                        weight=rule.get("weight", 1.0),
                        enabled=rule.get("enabled", True)
                    )
                    for rule in data.get("rules", [])
                ],
                target_vendor=data.get("tool_model")  # Legacy support
            )
            
            return ParseResult(success=True, data=strategy)
            
        except Exception as e:
            return ParseResult(success=False, errors=[f"YAML parsing error: {str(e)}"])
    
    def parse_wafer_map(self, content: str, filename: str = "") -> ParseResult:
        """Parse YAML wafer map content."""
        try:
            data = yaml.safe_load(content)
            
            dies = []
            if "dies" in data:
                for die_data in data["dies"]:
                    dies.append(Die(
                        x=die_data["x"],
                        y=die_data["y"],
                        available=die_data.get("available", True)
                    ))
            
            wafer_map = WaferMap(dies)
            return ParseResult(success=True, data=wafer_map)
            
        except Exception as e:
            return ParseResult(success=False, errors=[f"YAML wafer map parsing error: {str(e)}"])


class JSONParser(FormatParser):
    """JSON format parser."""
    
    @property
    def supported_extensions(self) -> List[str]:
        return [".json"]
    
    @property
    def format_name(self) -> str:
        return "JSON Strategy/WaferMap Format"
    
    def parse_strategy(self, content: str, filename: str = "") -> ParseResult:
        """Parse JSON strategy content."""
        try:
            data = json.loads(content)
            
            # Handle different JSON schema variations
            if "strategy" in data:
                data = data["strategy"]
            
            strategy = StrategyDefinition(
                name=data.get("name", ""),
                description=data.get("description", ""),
                process_step=data.get("process_step", ""),
                tool_type=data.get("tool_type", ""),
                rules=[
                    RuleConfig(
                        rule_type=rule.get("rule_type", rule.get("type", "")),
                        parameters=rule.get("parameters", {}),
                        weight=rule.get("weight", 1.0),
                        enabled=rule.get("enabled", True)
                    )
                    for rule in data.get("rules", [])
                ]
            )
            
            return ParseResult(success=True, data=strategy)
            
        except Exception as e:
            return ParseResult(success=False, errors=[f"JSON parsing error: {str(e)}"])
    
    def parse_wafer_map(self, content: str, filename: str = "") -> ParseResult:
        """Parse JSON wafer map content."""
        try:
            data = json.loads(content)
            
            dies = []
            if "wafer_map" in data:
                data = data["wafer_map"]
            
            if "dies" in data:
                for die_data in data["dies"]:
                    dies.append(Die(
                        x=die_data["x"],
                        y=die_data["y"],
                        available=die_data.get("available", True)
                    ))
            
            wafer_map = WaferMap(dies)
            return ParseResult(success=True, data=wafer_map)
            
        except Exception as e:
            return ParseResult(success=False, errors=[f"JSON wafer map parsing error: {str(e)}"])


class SEMIStandardParser(FormatParser):
    """SEMI standard format parser for semiconductor data."""
    
    @property
    def supported_extensions(self) -> List[str]:
        return [".stdf", ".semi"]
    
    @property
    def format_name(self) -> str:
        return "SEMI Standard Format"
    
    def parse_strategy(self, content: str, filename: str = "") -> ParseResult:
        """Parse SEMI format strategy (typically not used for strategies)."""
        return ParseResult(success=False, errors=["SEMI format not supported for strategies"])
    
    def parse_wafer_map(self, content: str, filename: str = "") -> ParseResult:
        """Parse SEMI format wafer map."""
        # Placeholder for SEMI format parsing
        # This would require specialized SEMI format libraries
        return ParseResult(
            success=False, 
            errors=["SEMI format parsing not yet implemented"],
            warnings=["Consider using JSON or YAML format for wafer maps"]
        )


class CSVParser(FormatParser):
    """CSV format parser for tabular data."""
    
    @property
    def supported_extensions(self) -> List[str]:
        return [".csv"]
    
    @property
    def format_name(self) -> str:
        return "CSV Tabular Format"
    
    def parse_strategy(self, content: str, filename: str = "") -> ParseResult:
        """Parse CSV strategy content."""
        try:
            reader = csv.DictReader(io.StringIO(content))
            
            # Use streaming approach for large files
            try:
                strategy_row = next(reader)
            except StopIteration:
                return ParseResult(success=False, errors=["Empty CSV file"])
            
            # Expect CSV format with strategy metadata and rules
            # First row should contain strategy info
            
            rules = []
            # Process first row if it has rule data
            if strategy_row.get("rule_type"):
                rules.append(RuleConfig(
                    rule_type=strategy_row["rule_type"],
                    parameters={
                        k: v for k, v in strategy_row.items() 
                        if k not in ["name", "description", "process_step", "tool_type", "rule_type"]
                    },
                    weight=float(strategy_row.get("weight", 1.0)),
                    enabled=strategy_row.get("enabled", "true").lower() == "true"
                ))
            
            # Process remaining rows
            for row in reader:
                if row.get("rule_type"):
                    rules.append(RuleConfig(
                        rule_type=row["rule_type"],
                        parameters={
                            k: v for k, v in row.items() 
                            if k not in ["name", "description", "process_step", "tool_type", "rule_type"]
                        },
                        weight=float(row.get("weight", 1.0)),
                        enabled=row.get("enabled", "true").lower() == "true"
                    ))
            
            strategy = StrategyDefinition(
                name=strategy_row.get("name", ""),
                description=strategy_row.get("description", ""),
                process_step=strategy_row.get("process_step", ""),
                tool_type=strategy_row.get("tool_type", ""),
                rules=rules
            )
            
            return ParseResult(success=True, data=strategy)
            
        except Exception as e:
            return ParseResult(success=False, errors=[f"CSV parsing error: {str(e)}"])
    
    def parse_wafer_map(self, content: str, filename: str = "") -> ParseResult:
        """Parse CSV wafer map content."""
        try:
            reader = csv.DictReader(io.StringIO(content))
            dies = []
            
            for row_num, row in enumerate(reader, start=2):  # Start at 2 since header is row 1
                try:
                    dies.append(Die(
                        x=int(row["x"]),
                        y=int(row["y"]),
                        available=row.get("available", "true").lower() == "true"
                    ))
                except (ValueError, KeyError) as e:
                    return ParseResult(success=False, errors=[f"Invalid die data in row {row_num}: {e}"])
            
            wafer_map = WaferMap(dies)
            return ParseResult(success=True, data=wafer_map)
            
        except Exception as e:
            return ParseResult(success=False, errors=[f"CSV wafer map parsing error: {str(e)}"])


class KLASPECParser(FormatParser):
    """KLA-specific SPEC format parser."""
    
    @property
    def supported_extensions(self) -> List[str]:
        return [".spec", ".kla"]
    
    @property
    def format_name(self) -> str:
        return "KLA SPEC Format"
    
    def parse_strategy(self, content: str, filename: str = "") -> ParseResult:
        """Parse KLA SPEC format."""
        try:
            # Parse KLA-specific XML format
            try:
                root = ET.fromstring(content)
            except ET.ParseError as e:
                return ParseResult(success=False, errors=[f"Invalid XML format: {e}"])
            
            strategy_name = root.get("name", filename)
            
            rules = []
            for site in root.findall(".//Site"):
                x = int(site.find("X_Position").text)
                y = int(site.find("Y_Position").text)
                enabled = site.find("Enabled").text.lower() == "true"
                
                # Convert to FixedPoint rule
                if not rules or rules[0].rule_type != "fixed_point":
                    rules.append(RuleConfig(
                        rule_type="fixed_point",
                        parameters={"points": []},
                        weight=1.0,
                        enabled=True
                    ))
                
                if enabled:
                    rules[0].parameters["points"].append([x, y])
            
            strategy = StrategyDefinition(
                name=strategy_name,
                description=f"Imported from KLA SPEC: {filename}",
                process_step="Unknown",
                tool_type="KLA",
                rules=rules,
                target_vendor="KLA"
            )
            
            return ParseResult(success=True, data=strategy)
            
        except Exception as e:
            return ParseResult(success=False, errors=[f"KLA SPEC parsing error: {str(e)}"])
    
    def parse_wafer_map(self, content: str, filename: str = "") -> ParseResult:
        """KLA SPEC typically contains strategy, not wafer map."""
        return ParseResult(success=False, errors=["KLA SPEC format contains strategy, not wafer map"])


class FormatRegistry:
    """Registry for format parsers."""
    
    def __init__(self):
        self.parsers: Dict[str, FormatParser] = {}
        self._register_default_parsers()
    
    def _register_default_parsers(self):
        """Register default format parsers."""
        parsers = [
            YAMLParser(),
            JSONParser(),
            CSVParser(),
            KLASPECParser(),
            SEMIStandardParser()
        ]
        
        for parser in parsers:
            for ext in parser.supported_extensions:
                self.parsers[ext.lower()] = parser
    
    def register_parser(self, parser: FormatParser):
        """Register a custom format parser."""
        for ext in parser.supported_extensions:
            self.parsers[ext.lower()] = parser
            logger.info(f"Registered parser for {ext}: {parser.format_name}")
    
    def get_parser(self, filename: str) -> Optional[FormatParser]:
        """Get parser for file extension."""
        _, ext = os.path.splitext(filename.lower())
        return self.parsers.get(ext)
    
    def parse_strategy(self, content: str, filename: str) -> ParseResult:
        """Parse strategy from content based on filename extension."""
        parser = self.get_parser(filename)
        if not parser:
            return ParseResult(
                success=False, 
                errors=[f"Unsupported file format: {filename}"]
            )
        
        return parser.parse_strategy(content, filename)
    
    def parse_wafer_map(self, content: str, filename: str) -> ParseResult:
        """Parse wafer map from content based on filename extension."""
        parser = self.get_parser(filename)
        if not parser:
            return ParseResult(
                success=False, 
                errors=[f"Unsupported file format: {filename}"]
            )
        
        return parser.parse_wafer_map(content, filename)
    
    def get_supported_formats(self) -> Dict[str, str]:
        """Get mapping of extensions to format names."""
        return {
            ext: parser.format_name 
            for ext, parser in self.parsers.items()
        }


# Global format registry
format_registry = FormatRegistry()