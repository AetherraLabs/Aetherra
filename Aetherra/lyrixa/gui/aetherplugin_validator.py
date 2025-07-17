# aetherplugin_validator.py
# 🔍 Inline .aetherplugin Validator
# "Add inline .aetherplugin validator (to check metadata, inputs/outputs)"

import json
import re
import ast
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime


@dataclass
class ValidationResult:
    """Result of .aetherplugin validation"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    info: List[str]
    metadata: Dict[str, Any]
    score: float  # 0.0 to 1.0


@dataclass
class PluginMetadata:
    """Structured plugin metadata"""
    name: str
    version: str
    description: str
    author: str
    license: str

    # Functional metadata
    inputs: List[Dict[str, Any]]
    outputs: List[Dict[str, Any]]
    capabilities: List[str]
    permissions: List[str]

    # Technical metadata
    dependencies: List[str]
    min_aetherra_version: str
    platform: List[str]

    # Optional metadata
    documentation_url: Optional[str] = None
    repository_url: Optional[str] = None
    homepage_url: Optional[str] = None
    tags: Optional[List[str]] = None
    icon: Optional[str] = None


class AetherPluginValidator:
    """Comprehensive validator for .aetherplugin files"""

    def __init__(self):
        self.schema = self._load_plugin_schema()
        self.validation_rules = self._load_validation_rules()

    def _load_plugin_schema(self) -> Dict[str, Any]:
        """Load the JSON schema for .aetherplugin files"""
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "metadata": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "pattern": "^[a-zA-Z0-9_-]+$"},
                        "version": {"type": "string", "pattern": "^\\d+\\.\\d+\\.\\d+$"},
                        "description": {"type": "string", "minLength": 10, "maxLength": 500},
                        "author": {"type": "string", "minLength": 1},
                        "license": {"type": "string", "enum": ["MIT", "Apache-2.0", "GPL-3.0", "BSD-3-Clause", "ISC"]},
                        "min_aetherra_version": {"type": "string", "pattern": "^\\d+\\.\\d+\\.\\d+$"},
                        "platform": {"type": "array", "items": {"type": "string", "enum": ["windows", "linux", "macos", "all"]}},
                        "documentation_url": {"type": "string", "format": "uri"},
                        "repository_url": {"type": "string", "format": "uri"},
                        "homepage_url": {"type": "string", "format": "uri"},
                        "tags": {"type": "array", "items": {"type": "string"}},
                        "icon": {"type": "string"}
                    },
                    "required": ["name", "version", "description", "author", "license", "min_aetherra_version"]
                },
                "inputs": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "type": {"type": "string", "enum": ["string", "number", "boolean", "object", "array"]},
                            "description": {"type": "string"},
                            "required": {"type": "boolean"},
                            "default": {},
                            "validation": {"type": "object"}
                        },
                        "required": ["name", "type", "description"]
                    }
                },
                "outputs": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "type": {"type": "string", "enum": ["string", "number", "boolean", "object", "array"]},
                            "description": {"type": "string"}
                        },
                        "required": ["name", "type", "description"]
                    }
                },
                "capabilities": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": [
                            "memory_read", "memory_write", "file_read", "file_write",
                            "network_access", "system_commands", "database_access",
                            "ai_inference", "plugin_interaction", "ui_modification",
                            "background_processing", "scheduled_tasks"
                        ]
                    }
                },
                "permissions": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "dependencies": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "configuration": {
                    "type": "object",
                    "properties": {
                        "timeout": {"type": "number", "minimum": 0},
                        "retries": {"type": "number", "minimum": 0},
                        "cache_enabled": {"type": "boolean"},
                        "logging_level": {"type": "string", "enum": ["debug", "info", "warning", "error"]},
                        "custom": {"type": "object"}
                    }
                },
                "tests": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "input": {},
                            "expected_output": {},
                            "description": {"type": "string"}
                        },
                        "required": ["name", "input", "expected_output"]
                    }
                }
            },
            "required": ["metadata", "inputs", "outputs", "capabilities"]
        }

    def _load_validation_rules(self) -> Dict[str, Any]:
        """Load additional validation rules"""
        return {
            "name_patterns": {
                "reserved_names": ["aetherra", "lyrixa", "system", "core", "admin"],
                "valid_pattern": r"^[a-zA-Z][a-zA-Z0-9_-]*$",
                "max_length": 50
            },
            "security_rules": {
                "dangerous_capabilities": [
                    "system_commands", "file_write", "network_access"
                ],
                "capability_combinations": {
                    "file_write,network_access": "High risk: Can exfiltrate data"
                }
            },
            "performance_rules": {
                "max_inputs": 20,
                "max_outputs": 10,
                "max_dependencies": 15
            }
        }

    def validate_plugin_content(self, content: str) -> ValidationResult:
        """Validate .aetherplugin content"""
        errors = []
        warnings = []
        info = []
        metadata = {}

        # Parse JSON
        try:
            plugin_data = json.loads(content)
        except json.JSONDecodeError as e:
            return ValidationResult(
                is_valid=False,
                errors=[f"Invalid JSON: {e.msg} at line {e.lineno}"],
                warnings=[],
                info=[],
                metadata={},
                score=0.0
            )

        # Schema validation (manual implementation)
        try:
            schema_errors = self._validate_schema(plugin_data)
            errors.extend(schema_errors)
        except Exception as e:
            errors.append(f"Schema validation error: {str(e)}")

        # Extract metadata
        metadata = plugin_data.get("metadata", {})

        # Custom validation rules
        errors.extend(self._validate_metadata(metadata))
        warnings.extend(self._validate_security(plugin_data))
        warnings.extend(self._validate_performance(plugin_data))
        info.extend(self._validate_best_practices(plugin_data))

        # Calculate score
        score = self._calculate_plugin_score(plugin_data, errors, warnings)

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            info=info,
            metadata=metadata,
            score=score
        )

    def _validate_schema(self, plugin_data: Dict[str, Any]) -> List[str]:
        """Manual schema validation"""
        errors = []

        # Check required top-level fields
        required_fields = ["metadata", "inputs", "outputs", "capabilities"]
        for field in required_fields:
            if field not in plugin_data:
                errors.append(f"Missing required field: {field}")

        # Validate metadata structure
        if "metadata" in plugin_data:
            metadata = plugin_data["metadata"]
            if not isinstance(metadata, dict):
                errors.append("metadata must be an object")
            else:
                required_meta_fields = ["name", "version", "description", "author", "license", "min_aetherra_version"]
                for field in required_meta_fields:
                    if field not in metadata:
                        errors.append(f"Missing required metadata field: {field}")

        # Validate inputs structure
        if "inputs" in plugin_data:
            inputs = plugin_data["inputs"]
            if not isinstance(inputs, list):
                errors.append("inputs must be an array")
            else:
                for i, inp in enumerate(inputs):
                    if not isinstance(inp, dict):
                        errors.append(f"inputs[{i}] must be an object")
                    else:
                        required_inp_fields = ["name", "type", "description"]
                        for field in required_inp_fields:
                            if field not in inp:
                                errors.append(f"Missing required input field: inputs[{i}].{field}")

        # Validate outputs structure
        if "outputs" in plugin_data:
            outputs = plugin_data["outputs"]
            if not isinstance(outputs, list):
                errors.append("outputs must be an array")
            else:
                for i, out in enumerate(outputs):
                    if not isinstance(out, dict):
                        errors.append(f"outputs[{i}] must be an object")
                    else:
                        required_out_fields = ["name", "type", "description"]
                        for field in required_out_fields:
                            if field not in out:
                                errors.append(f"Missing required output field: outputs[{i}].{field}")

        # Validate capabilities structure
        if "capabilities" in plugin_data:
            capabilities = plugin_data["capabilities"]
            if not isinstance(capabilities, list):
                errors.append("capabilities must be an array")
            else:
                valid_capabilities = [
                    "memory_read", "memory_write", "file_read", "file_write",
                    "network_access", "system_commands", "database_access",
                    "ai_inference", "plugin_interaction", "ui_modification",
                    "background_processing", "scheduled_tasks"
                ]
                for cap in capabilities:
                    if cap not in valid_capabilities:
                        errors.append(f"Invalid capability: {cap}")

        return errors

    def _validate_metadata(self, metadata: Dict[str, Any]) -> List[str]:
        """Validate metadata fields"""
        errors = []
        rules = self.validation_rules["name_patterns"]

        # Name validation
        name = metadata.get("name", "")
        if not name:
            errors.append("Plugin name is required")
        elif name.lower() in rules["reserved_names"]:
            errors.append(f"Plugin name '{name}' is reserved")
        elif not re.match(rules["valid_pattern"], name):
            errors.append(f"Invalid plugin name format: {name}")
        elif len(name) > rules["max_length"]:
            errors.append(f"Plugin name too long (max {rules['max_length']} chars)")

        # Version validation
        version = metadata.get("version", "")
        if not version:
            errors.append("Plugin version is required")
        elif not re.match(r"^\d+\.\d+\.\d+$", version):
            errors.append(f"Invalid version format: {version} (use semver: x.y.z)")

        # Description validation
        description = metadata.get("description", "")
        if not description:
            errors.append("Plugin description is required")
        elif len(description) < 10:
            errors.append("Description too short (minimum 10 characters)")
        elif len(description) > 500:
            errors.append("Description too long (maximum 500 characters)")

        return errors

    def _validate_security(self, plugin_data: Dict[str, Any]) -> List[str]:
        """Validate security aspects"""
        warnings = []
        security_rules = self.validation_rules["security_rules"]

        capabilities = plugin_data.get("capabilities", [])

        # Check for dangerous capabilities
        dangerous_caps = [cap for cap in capabilities if cap in security_rules["dangerous_capabilities"]]
        if dangerous_caps:
            warnings.append(f"Plugin requests dangerous capabilities: {', '.join(dangerous_caps)}")

        # Check for risky capability combinations
        cap_set = set(capabilities)
        for combo, warning in security_rules["capability_combinations"].items():
            combo_caps = set(combo.split(","))
            if combo_caps.issubset(cap_set):
                warnings.append(f"Risky capability combination: {warning}")

        # Check permissions
        permissions = plugin_data.get("permissions", [])
        if "admin" in permissions:
            warnings.append("Plugin requests admin permissions - high security risk")

        return warnings

    def _validate_performance(self, plugin_data: Dict[str, Any]) -> List[str]:
        """Validate performance aspects"""
        warnings = []
        perf_rules = self.validation_rules["performance_rules"]

        # Check input count
        inputs = plugin_data.get("inputs", [])
        if len(inputs) > perf_rules["max_inputs"]:
            warnings.append(f"Too many inputs ({len(inputs)}) - may impact performance")

        # Check output count
        outputs = plugin_data.get("outputs", [])
        if len(outputs) > perf_rules["max_outputs"]:
            warnings.append(f"Too many outputs ({len(outputs)}) - may impact performance")

        # Check dependencies
        dependencies = plugin_data.get("dependencies", [])
        if len(dependencies) > perf_rules["max_dependencies"]:
            warnings.append(f"Too many dependencies ({len(dependencies)}) - may slow loading")

        return warnings

    def _validate_best_practices(self, plugin_data: Dict[str, Any]) -> List[str]:
        """Validate best practices"""
        info = []

        metadata = plugin_data.get("metadata", {})

        # Check for documentation
        if not metadata.get("documentation_url"):
            info.append("Consider adding documentation_url for better usability")

        # Check for repository
        if not metadata.get("repository_url"):
            info.append("Consider adding repository_url for transparency")

        # Check for tags
        if not metadata.get("tags"):
            info.append("Consider adding tags for better discoverability")

        # Check for tests
        tests = plugin_data.get("tests", [])
        if not tests:
            info.append("Consider adding test cases for better reliability")

        # Check for configuration
        config = plugin_data.get("configuration", {})
        if not config:
            info.append("Consider adding configuration options for flexibility")

        return info

    def _calculate_plugin_score(self, plugin_data: Dict[str, Any], errors: List[str], warnings: List[str]) -> float:
        """Calculate overall plugin quality score"""
        score = 1.0

        # Deduct for errors
        score -= len(errors) * 0.2

        # Deduct for warnings
        score -= len(warnings) * 0.1

        # Bonus for best practices
        metadata = plugin_data.get("metadata", {})
        if metadata.get("documentation_url"):
            score += 0.05
        if metadata.get("repository_url"):
            score += 0.05
        if metadata.get("tags"):
            score += 0.05

        # Bonus for tests
        if plugin_data.get("tests"):
            score += 0.1

        # Bonus for configuration
        if plugin_data.get("configuration"):
            score += 0.05

        return max(0.0, min(1.0, score))

    def validate_io_compatibility(self, inputs: List[Dict[str, Any]], outputs: List[Dict[str, Any]]) -> List[str]:
        """Validate input/output compatibility"""
        warnings = []

        # Check for input/output type mismatches
        input_types = {inp["name"]: inp["type"] for inp in inputs}
        output_types = {out["name"]: out["type"] for out in outputs}

        # Check for passthrough parameters
        for inp_name, inp_type in input_types.items():
            if inp_name in output_types:
                if inp_type != output_types[inp_name]:
                    warnings.append(f"Type mismatch for passthrough parameter '{inp_name}': {inp_type} -> {output_types[inp_name]}")

        # Check for required inputs without defaults
        required_inputs = [inp for inp in inputs if inp.get("required", False)]
        inputs_without_defaults = [inp for inp in required_inputs if "default" not in inp]

        if inputs_without_defaults:
            names = [inp["name"] for inp in inputs_without_defaults]
            warnings.append(f"Required inputs without defaults: {', '.join(names)}")

        return warnings

    def suggest_improvements(self, plugin_data: Dict[str, Any]) -> List[str]:
        """Suggest improvements for the plugin"""
        suggestions = []

        metadata = plugin_data.get("metadata", {})

        # Metadata improvements
        if len(metadata.get("description", "")) < 50:
            suggestions.append("📝 Expand the description to better explain the plugin's purpose")

        if not metadata.get("tags"):
            suggestions.append("🏷️ Add tags to improve discoverability")

        # Input/output improvements
        inputs = plugin_data.get("inputs", [])
        outputs = plugin_data.get("outputs", [])

        if not inputs:
            suggestions.append("📥 Consider adding input parameters for flexibility")

        if not outputs:
            suggestions.append("📤 Define output format for better integration")

        # Validation improvements
        inputs_with_validation = [inp for inp in inputs if inp.get("validation")]
        if len(inputs_with_validation) < len(inputs):
            suggestions.append("✅ Add validation rules for input parameters")

        # Testing improvements
        if not plugin_data.get("tests"):
            suggestions.append("🧪 Add test cases to ensure reliability")

        # Security improvements
        capabilities = plugin_data.get("capabilities", [])
        if "network_access" in capabilities:
            suggestions.append("🔒 Consider adding timeout and retry configuration for network operations")

        return suggestions

    def generate_template(self, plugin_name: str) -> str:
        """Generate a template .aetherplugin file"""
        template = {
            "metadata": {
                "name": plugin_name,
                "version": "1.0.0",
                "description": f"A powerful {plugin_name} plugin for Aetherra",
                "author": "Your Name",
                "license": "MIT",
                "min_aetherra_version": "1.0.0",
                "platform": ["all"],
                "documentation_url": f"https://docs.example.com/{plugin_name}",
                "repository_url": f"https://github.com/example/{plugin_name}",
                "tags": ["utility", "productivity"]
            },
            "inputs": [
                {
                    "name": "input_text",
                    "type": "string",
                    "description": "Text input for processing",
                    "required": True,
                    "validation": {
                        "minLength": 1,
                        "maxLength": 1000
                    }
                }
            ],
            "outputs": [
                {
                    "name": "result",
                    "type": "string",
                    "description": "Processed result"
                },
                {
                    "name": "success",
                    "type": "boolean",
                    "description": "Operation success status"
                }
            ],
            "capabilities": [
                "memory_read",
                "ai_inference"
            ],
            "permissions": [],
            "dependencies": [],
            "configuration": {
                "timeout": 30,
                "retries": 3,
                "cache_enabled": True,
                "logging_level": "info"
            },
            "tests": [
                {
                    "name": "basic_functionality",
                    "input": {"input_text": "Hello, world!"},
                    "expected_output": {"result": "Processed: Hello, world!", "success": True},
                    "description": "Test basic plugin functionality"
                }
            ]
        }

        return json.dumps(template, indent=2)

    def lint_plugin_file(self, file_path: str) -> ValidationResult:
        """Lint a .aetherplugin file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            result = self.validate_plugin_content(content)

            # Add file-specific validation
            if not file_path.endswith('.aetherplugin'):
                result.warnings.append("File should have .aetherplugin extension")

            return result

        except FileNotFoundError:
            return ValidationResult(
                is_valid=False,
                errors=[f"File not found: {file_path}"],
                warnings=[],
                info=[],
                metadata={},
                score=0.0
            )
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                errors=[f"Error reading file: {str(e)}"],
                warnings=[],
                info=[],
                metadata={},
                score=0.0
            )


# Interactive validator for real-time editing
class InlineValidator:
    """Real-time validator for editing .aetherplugin files"""

    def __init__(self):
        self.validator = AetherPluginValidator()
        self.last_validation = None
        self.validation_cache = {}

    def validate_real_time(self, content: str, cursor_position: int = 0) -> Dict[str, Any]:
        """Validate content in real-time during editing"""
        # Cache validation results to avoid repeated computation
        content_hash = hash(content)
        if content_hash in self.validation_cache:
            return self.validation_cache[content_hash]

        result = self.validator.validate_plugin_content(content)

        # Add cursor-specific information
        cursor_info = self._get_cursor_context(content, cursor_position)

        validation_result = {
            "is_valid": result.is_valid,
            "errors": result.errors,
            "warnings": result.warnings,
            "info": result.info,
            "score": result.score,
            "cursor_context": cursor_info,
            "suggestions": self.validator.suggest_improvements(json.loads(content) if content.strip() else {}),
            "validation_time": datetime.now().isoformat()
        }

        # Cache result
        self.validation_cache[content_hash] = validation_result

        # Limit cache size
        if len(self.validation_cache) > 50:
            # Remove oldest entries
            old_keys = list(self.validation_cache.keys())[:-25]
            for key in old_keys:
                del self.validation_cache[key]

        return validation_result

    def _get_cursor_context(self, content: str, cursor_position: int) -> Dict[str, Any]:
        """Get context information for cursor position"""
        if not content or cursor_position >= len(content):
            return {"section": "unknown", "suggestions": []}

        lines = content[:cursor_position].split('\n')
        current_line = lines[-1] if lines else ""
        line_number = len(lines)

        # Determine context
        context = {"section": "unknown", "line": line_number, "suggestions": []}

        # Check if we're in metadata section
        if '"metadata"' in content[:cursor_position]:
            context["section"] = "metadata"
            context["suggestions"] = [
                "Add name, version, description, author, license",
                "Consider adding documentation_url and repository_url"
            ]

        # Check if we're in inputs section
        elif '"inputs"' in content[:cursor_position]:
            context["section"] = "inputs"
            context["suggestions"] = [
                "Define input parameters with name, type, description",
                "Add validation rules for input parameters",
                "Mark required inputs"
            ]

        # Check if we're in outputs section
        elif '"outputs"' in content[:cursor_position]:
            context["section"] = "outputs"
            context["suggestions"] = [
                "Define output format with name, type, description",
                "Consider success/error status outputs"
            ]

        return context

    def get_completion_suggestions(self, content: str, cursor_position: int) -> List[str]:
        """Get auto-completion suggestions for cursor position"""
        cursor_context = self._get_cursor_context(content, cursor_position)

        suggestions = []

        if cursor_context["section"] == "metadata":
            suggestions.extend([
                '"name": "plugin_name"',
                '"version": "1.0.0"',
                '"description": "Plugin description"',
                '"author": "Your Name"',
                '"license": "MIT"',
                '"min_aetherra_version": "1.0.0"',
                '"platform": ["all"]',
                '"tags": ["utility"]'
            ])

        elif cursor_context["section"] == "inputs":
            suggestions.extend([
                '{"name": "input_name", "type": "string", "description": "Input description", "required": true}',
                '{"name": "options", "type": "object", "description": "Configuration options", "required": false}',
                '{"name": "data", "type": "array", "description": "Input data", "required": true}'
            ])

        elif cursor_context["section"] == "outputs":
            suggestions.extend([
                '{"name": "result", "type": "string", "description": "Operation result"}',
                '{"name": "success", "type": "boolean", "description": "Success status"}',
                '{"name": "error", "type": "string", "description": "Error message if failed"}'
            ])

        return suggestions


# Example usage
if __name__ == "__main__":
    # Create validator
    validator = AetherPluginValidator()

    # Test with sample plugin
    sample_plugin = {
        "metadata": {
            "name": "weather_helper",
            "version": "1.0.0",
            "description": "A comprehensive weather information plugin",
            "author": "Weather Team",
            "license": "MIT",
            "min_aetherra_version": "1.0.0",
            "platform": ["all"],
            "tags": ["weather", "utility"]
        },
        "inputs": [
            {
                "name": "location",
                "type": "string",
                "description": "Location for weather query",
                "required": True,
                "validation": {"minLength": 2, "maxLength": 100}
            }
        ],
        "outputs": [
            {
                "name": "weather_data",
                "type": "object",
                "description": "Weather information"
            },
            {
                "name": "success",
                "type": "boolean",
                "description": "Operation success"
            }
        ],
        "capabilities": ["network_access", "ai_inference"],
        "permissions": [],
        "dependencies": []
    }

    # Validate
    result = validator.validate_plugin_content(json.dumps(sample_plugin, indent=2))

    print(f"🔍 Validation Result:")
    print(f"  Valid: {result.is_valid}")
    print(f"  Score: {result.score:.2f}")
    print(f"  Errors: {len(result.errors)}")
    print(f"  Warnings: {len(result.warnings)}")

    for error in result.errors:
        print(f"  ❌ {error}")

    for warning in result.warnings:
        print(f"  ⚠️ {warning}")

    for info in result.info:
        print(f"  ℹ️ {info}")

    # Generate template
    template = validator.generate_template("my_plugin")
    print(f"\n📄 Generated Template:")
    print(template[:200] + "..." if len(template) > 200 else template)
