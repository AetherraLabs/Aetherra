#!/usr/bin/env python3
"""
🌐➡️⚡ NATURAL LANGUAGE TO AETHER GENERATOR
===========================================

Advanced system for converting plain English descriptions into executable .aether workflows.
Features intent analysis, parameter auto-filling, and workflow optimization.
"""

import json
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from .memory import LyrixaMemorySystem


@dataclass
class IntentAnalysis:
    """Analysis of natural language intent"""
    primary_intent: str
    secondary_intents: List[str]
    entities: Dict[str, Any]
    parameters: Dict[str, Any]
    data_flow: List[str]
    complexity: float  # 0.0 to 1.0
    confidence: float  # 0.0 to 1.0


@dataclass
class AetherTemplate:
    """Template for generating .aether workflows"""
    name: str
    description: str
    pattern: str
    required_entities: List[str]
    optional_entities: List[str]
    default_parameters: Dict[str, Any]
    complexity_level: float


@dataclass
class ParameterSuggestion:
    """Suggested parameter values with confidence"""
    parameter: str
    value: Any
    confidence: float
    source: str  # 'memory', 'context', 'default', 'inferred'
    explanation: str


class NaturalLanguageAetherGenerator:
    """
    🌐➡️⚡ Natural Language to Aether Generator

    Converts plain English descriptions into executable .aether workflows using:
    - Advanced intent analysis
    - Template-based generation
    - Memory-driven parameter suggestion
    - Workflow optimization
    """

    def __init__(self, memory_system: Optional[LyrixaMemorySystem] = None):
        self.memory_system = memory_system
        self.templates = self._initialize_templates()
        self.entity_extractors = self._initialize_entity_extractors()
        self.parameter_suggesters = self._initialize_parameter_suggesters()
        self.workflow_optimizer = WorkflowOptimizer()

        print("🌐➡️⚡ Natural Language to Aether Generator initialized")

    def _initialize_templates(self) -> Dict[str, AetherTemplate]:
        """Initialize .aether workflow templates"""
        return {
            "data_processing": AetherTemplate(
                name="Data Processing Pipeline",
                description="Process and transform data through multiple stages",
                pattern="""# {workflow_name}
node input_{input_type} input
  source: "{input_source}"
  format: "{input_format}"

node processor transform
  operation: "{operation}"
  parameters: {processing_params}

node validator validator
  schema: "{validation_schema}"
  strict: {strict_validation}

node output_{output_type} output
  destination: "{output_destination}"
  format: "{output_format}"

input_{input_type} -> processor
processor -> validator
validator -> output_{output_type}""",
                required_entities=["input_source", "operation"],
                optional_entities=["output_destination", "validation_schema"],
                default_parameters={
                    "input_format": "json",
                    "output_format": "json",
                    "strict_validation": True
                },
                complexity_level=0.6
            ),

            "api_integration": AetherTemplate(
                name="API Integration Workflow",
                description="Interact with external APIs and process responses",
                pattern="""# {workflow_name}
node api_request api_call
  url: "{api_url}"
  method: "{http_method}"
  headers: {api_headers}
  payload: {request_payload}

node response_handler transform
  operation: "json_parse"
  extract_fields: {extract_fields}
  error_handling: "{error_strategy}"

node data_processor transform
  operation: "{data_operation}"
  filters: {data_filters}

node result_store output
  destination: "{output_location}"
  format: "{result_format}"

api_request -> response_handler
response_handler -> data_processor
data_processor -> result_store""",
                required_entities=["api_url", "http_method"],
                optional_entities=["api_headers", "request_payload", "output_location"],
                default_parameters={
                    "http_method": "GET",
                    "error_strategy": "log_and_continue",
                    "result_format": "json"
                },
                complexity_level=0.7
            ),

            "machine_learning": AetherTemplate(
                name="Machine Learning Pipeline",
                description="Train, validate, and deploy ML models",
                pattern="""# {workflow_name}
node data_loader input
  source: "{training_data}"
  preprocessing: {preprocessing_steps}

node feature_engineer transform
  operations: {feature_operations}
  target_column: "{target_variable}"

node model_trainer model
  algorithm: "{ml_algorithm}"
  hyperparameters: {model_params}
  validation_split: {validation_ratio}

node model_evaluator analyzer
  metrics: {evaluation_metrics}
  threshold: {performance_threshold}

node model_deployer output
  deployment_target: "{deployment_location}"
  model_format: "{model_export_format}"

data_loader -> feature_engineer
feature_engineer -> model_trainer
model_trainer -> model_evaluator
model_evaluator -> model_deployer""",
                required_entities=["training_data", "ml_algorithm", "target_variable"],
                optional_entities=["deployment_location", "evaluation_metrics"],
                default_parameters={
                    "validation_ratio": 0.2,
                    "performance_threshold": 0.8,
                    "model_export_format": "pickle"
                },
                complexity_level=0.9
            ),

            "data_analysis": AetherTemplate(
                name="Data Analysis Workflow",
                description="Analyze and visualize data with statistical insights",
                pattern="""# {workflow_name}
node data_input input
  source: "{data_source}"
  format: "{data_format}"
  columns: {column_selection}

node statistics_analyzer analyzer
  analysis_type: "{analysis_type}"
  statistical_tests: {statistical_methods}
  confidence_level: {confidence_interval}

node visualizer generator
  chart_types: {visualization_types}
  output_format: "{chart_format}"
  style_theme: "{visual_theme}"

node insights_extractor analyzer
  pattern_detection: {pattern_methods}
  anomaly_detection: {anomaly_settings}

node report_generator output
  report_format: "{report_type}"
  destination: "{report_location}"
  include_raw_data: {include_data}

data_input -> statistics_analyzer
data_input -> visualizer
statistics_analyzer -> insights_extractor
visualizer -> report_generator
insights_extractor -> report_generator""",
                required_entities=["data_source", "analysis_type"],
                optional_entities=["visualization_types", "report_location"],
                default_parameters={
                    "data_format": "csv",
                    "confidence_interval": 0.95,
                    "chart_format": "png",
                    "report_type": "html"
                },
                complexity_level=0.5
            ),

            "file_operations": AetherTemplate(
                name="File Operations Workflow",
                description="Batch file processing and organization",
                pattern="""# {workflow_name}
node file_scanner input
  source_directory: "{source_path}"
  file_patterns: {file_filters}
  recursive: {scan_recursive}

node file_processor transform
  operations: {file_operations}
  batch_size: {processing_batch}
  parallel_processing: {enable_parallel}

node file_validator validator
  validation_rules: {validation_criteria}
  error_handling: "{error_action}"

node file_organizer output
  destination_directory: "{target_path}"
  organization_strategy: "{organization_method}"
  preserve_structure: {keep_structure}

file_scanner -> file_processor
file_processor -> file_validator
file_validator -> file_organizer""",
                required_entities=["source_path", "file_operations"],
                optional_entities=["target_path", "file_filters"],
                default_parameters={
                    "scan_recursive": True,
                    "processing_batch": 10,
                    "enable_parallel": True,
                    "error_action": "skip"
                },
                complexity_level=0.4
            )
        }

    def _initialize_entity_extractors(self) -> Dict[str, callable]:
        """Initialize entity extraction functions"""
        return {
            "file_paths": self._extract_file_paths,
            "urls": self._extract_urls,
            "operations": self._extract_operations,
            "data_types": self._extract_data_types,
            "algorithms": self._extract_algorithms,
            "parameters": self._extract_parameters,
            "formats": self._extract_formats
        }

    def _initialize_parameter_suggesters(self) -> Dict[str, callable]:
        """Initialize parameter suggestion functions"""
        return {
            "input_source": self._suggest_input_source,
            "output_destination": self._suggest_output_destination,
            "operation": self._suggest_operation,
            "format": self._suggest_format,
            "api_url": self._suggest_api_url,
            "algorithm": self._suggest_algorithm
        }

    async def generate_aether_from_natural_language(
        self,
        description: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Main method: Convert natural language description to .aether workflow

        Args:
            description: Plain English description of desired workflow
            context: Optional context from previous interactions

        Returns:
            Complete generation result with code, suggestions, and metadata
        """
        try:
            print(f"🌐 Analyzing natural language: {description[:50]}...")

            # Step 1: Analyze intent and extract entities
            intent_analysis = await self._analyze_intent(description, context)

            # Step 2: Select appropriate template
            template = self._select_template(intent_analysis)

            # Step 3: Auto-fill parameters using memory and context
            parameters = await self._auto_fill_parameters(intent_analysis, template, context)

            # Step 4: Generate .aether code
            aether_code = self._generate_code_from_template(template, parameters)

            # Step 5: Optimize workflow
            optimized_code = await self.workflow_optimizer.optimize(aether_code, intent_analysis)

            # Step 6: Generate improvement suggestions
            suggestions = await self._generate_suggestions(intent_analysis, parameters, template)

            # Step 7: Create metadata
            metadata = self._create_generation_metadata(
                description, intent_analysis, template, parameters
            )

            result = {
                "aether_code": optimized_code,
                "intent_analysis": intent_analysis.__dict__,
                "template_used": template.name,
                "parameters": parameters,
                "suggestions": suggestions,
                "metadata": metadata,
                "confidence": intent_analysis.confidence,
                "complexity": intent_analysis.complexity
            }

            print(f"✅ Generated .aether workflow with {intent_analysis.confidence:.2f} confidence")
            return result

        except Exception as e:
            print(f"[ERROR] Error generating .aether from natural language: {e}")
            return {
                "error": str(e),
                "aether_code": "# Error: Could not generate workflow",
                "confidence": 0.0,
                "suggestions": ["Try rephrasing your request", "Provide more specific details"]
            }

    async def _analyze_intent(self, description: str, context: Optional[Dict[str, Any]]) -> IntentAnalysis:
        """Analyze natural language intent and extract key entities"""
        description_lower = description.lower()

        # Extract primary intent
        primary_intent = self._classify_primary_intent(description_lower)

        # Extract secondary intents
        secondary_intents = self._extract_secondary_intents(description_lower)

        # Extract entities
        entities = {}
        for extractor_name, extractor_func in self.entity_extractors.items():
            entities[extractor_name] = extractor_func(description)

        # Extract parameters
        parameters = self._extract_parameters(description)

        # Analyze data flow
        data_flow = self._analyze_data_flow(description)

        # Calculate complexity and confidence
        complexity = self._calculate_complexity(description, entities, data_flow)
        confidence = self._calculate_confidence(description, entities, parameters)

        return IntentAnalysis(
            primary_intent=primary_intent,
            secondary_intents=secondary_intents,
            entities=entities,
            parameters=parameters,
            data_flow=data_flow,
            complexity=complexity,
            confidence=confidence
        )

    def _classify_primary_intent(self, description: str) -> str:
        """Classify the primary intent from description"""
        intent_patterns = {
            "data_processing": ["process", "transform", "clean", "filter", "convert"],
            "api_integration": ["api", "request", "fetch", "call", "endpoint"],
            "machine_learning": ["train", "model", "predict", "classify", "ml", "ai"],
            "data_analysis": ["analyze", "statistics", "visualize", "explore", "insights"],
            "file_operations": ["file", "directory", "folder", "organize", "batch"]
        }

        for intent, keywords in intent_patterns.items():
            if any(keyword in description for keyword in keywords):
                return intent

        return "data_processing"  # Default intent

    def _extract_secondary_intents(self, description: str) -> List[str]:
        """Extract secondary intents that might apply"""
        secondary = []

        if any(word in description for word in ["save", "store", "output"]):
            secondary.append("data_storage")
        if any(word in description for word in ["validate", "check", "verify"]):
            secondary.append("validation")
        if any(word in description for word in ["optimize", "improve", "enhance"]):
            secondary.append("optimization")
        if any(word in description for word in ["schedule", "automate", "batch"]):
            secondary.append("automation")

        return secondary

    def _extract_file_paths(self, text: str) -> List[str]:
        """Extract file paths from text"""
        # Pattern for file paths
        path_pattern = r'["\']([^"\']*\.[a-zA-Z0-9]{2,4})["\']|([/\\][\w\s/\\.-]*\.[a-zA-Z0-9]{2,4})'
        matches = re.findall(path_pattern, text)
        return [match[0] or match[1] for match in matches if match[0] or match[1]]

    def _extract_urls(self, text: str) -> List[str]:
        """Extract URLs from text"""
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        return re.findall(url_pattern, text)

    def _extract_operations(self, text: str) -> List[str]:
        """Extract operation keywords"""
        operations = {
            "clean", "filter", "transform", "convert", "normalize", "aggregate",
            "sort", "group", "join", "merge", "split", "parse", "validate"
        }
        found_ops = []
        for op in operations:
            if op in text.lower():
                found_ops.append(op)
        return found_ops

    def _extract_data_types(self, text: str) -> List[str]:
        """Extract data type mentions"""
        data_types = {
            "json", "csv", "xml", "yaml", "parquet", "excel", "txt", "pdf",
            "image", "video", "audio", "binary"
        }
        found_types = []
        for dtype in data_types:
            if dtype in text.lower():
                found_types.append(dtype)
        return found_types

    def _extract_algorithms(self, text: str) -> List[str]:
        """Extract algorithm mentions"""
        algorithms = {
            "linear regression", "random forest", "neural network", "svm", "kmeans",
            "decision tree", "gradient boosting", "naive bayes", "clustering"
        }
        found_algos = []
        for algo in algorithms:
            if algo in text.lower():
                found_algos.append(algo)
        return found_algos

    def _extract_parameters(self, text: str) -> Dict[str, Any]:
        """Extract parameter values from text"""
        parameters = {}

        # Extract numbers
        number_pattern = r'(\d+(?:\.\d+)?)'
        numbers = re.findall(number_pattern, text)
        if numbers:
            parameters["numeric_values"] = [float(n) for n in numbers]

        # Extract quoted strings
        string_pattern = r'["\']([^"\']+)["\']'
        strings = re.findall(string_pattern, text)
        if strings:
            parameters["string_values"] = strings

        return parameters

    def _extract_formats(self, text: str) -> List[str]:
        """Extract format specifications"""
        formats = {
            "json", "csv", "xml", "yaml", "html", "pdf", "png", "jpg", "svg"
        }
        found_formats = []
        for fmt in formats:
            if fmt in text.lower():
                found_formats.append(fmt)
        return found_formats

    def _analyze_data_flow(self, description: str) -> List[str]:
        """Analyze implied data flow in description"""
        flow_keywords = {
            "input": ["from", "load", "read", "input", "source"],
            "process": ["process", "transform", "analyze", "convert"],
            "output": ["to", "save", "write", "output", "store", "export"]
        }

        flow = []
        for stage, keywords in flow_keywords.items():
            if any(keyword in description.lower() for keyword in keywords):
                flow.append(stage)

        return flow if flow else ["input", "process", "output"]

    def _calculate_complexity(self, description: str, entities: Dict, data_flow: List[str]) -> float:
        """Calculate workflow complexity (0.0 to 1.0)"""
        complexity = 0.3  # Base complexity

        # Add complexity for multiple data sources
        if len(entities.get("file_paths", [])) > 1:
            complexity += 0.1

        # Add complexity for API integrations
        if entities.get("urls", []):
            complexity += 0.2

        # Add complexity for ML algorithms
        if entities.get("algorithms", []):
            complexity += 0.3

        # Add complexity for multiple operations
        if len(entities.get("operations", [])) > 2:
            complexity += 0.2

        return min(complexity, 1.0)

    def _calculate_confidence(self, description: str, entities: Dict, parameters: Dict) -> float:
        """Calculate generation confidence (0.0 to 1.0)"""
        confidence = 0.5  # Base confidence

        # Increase confidence for specific entities
        if entities.get("file_paths"):
            confidence += 0.1
        if entities.get("operations"):
            confidence += 0.1
        if entities.get("data_types"):
            confidence += 0.1
        if parameters.get("numeric_values"):
            confidence += 0.1

        # Increase confidence for clear intent words
        intent_words = ["process", "analyze", "transform", "generate", "create"]
        if any(word in description.lower() for word in intent_words):
            confidence += 0.2

        return min(confidence, 1.0)

    def _select_template(self, intent_analysis: IntentAnalysis) -> AetherTemplate:
        """Select the most appropriate template based on intent analysis"""
        return self.templates.get(intent_analysis.primary_intent, self.templates["data_processing"])

    async def _auto_fill_parameters(
        self,
        intent_analysis: IntentAnalysis,
        template: AetherTemplate,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Auto-fill template parameters using memory, context, and inference"""
        parameters = template.default_parameters.copy()

        # Fill from extracted entities
        entities = intent_analysis.entities

        if entities.get("file_paths"):
            parameters["input_source"] = entities["file_paths"][0]
            if len(entities["file_paths"]) > 1:
                parameters["output_destination"] = entities["file_paths"][1]

        if entities.get("urls"):
            parameters["api_url"] = entities["urls"][0]

        if entities.get("operations"):
            parameters["operation"] = entities["operations"][0]

        if entities.get("data_types"):
            parameters["input_format"] = entities["data_types"][0]
            parameters["output_format"] = entities["data_types"][0]

        if entities.get("algorithms"):
            parameters["ml_algorithm"] = entities["algorithms"][0]

        # Use memory system to suggest parameters
        if self.memory_system:
            memory_suggestions = await self._get_memory_suggestions(intent_analysis)
            parameters.update(memory_suggestions)

        # Use context for parameters
        if context:
            context_params = self._extract_context_parameters(context)
            parameters.update(context_params)

        # Generate workflow name
        parameters["workflow_name"] = self._generate_workflow_name(intent_analysis)

        return parameters

    async def _get_memory_suggestions(self, intent_analysis: IntentAnalysis) -> Dict[str, Any]:
        """Get parameter suggestions from memory system"""
        suggestions = {}

        try:
            # Check if memory system is available
            if not self.memory_system:
                return suggestions

            # Search for similar workflows in memory using recall_memories
            search_query = f"{intent_analysis.primary_intent} workflow parameters"
            memories = await self.memory_system.recall_memories(search_query, limit=3)

            # Extract common parameters from past workflows
            for memory in memories:
                # Handle both dict and object types for memory content
                content = None
                if hasattr(memory, 'content'):
                    content = memory.content
                elif isinstance(memory, dict):
                    content = memory.get('content', {})

                if content and isinstance(content, dict):
                    # Look for parameters in the content
                    if 'parameters' in content:
                        for key, value in content['parameters'].items():
                            if key not in suggestions:
                                suggestions[key] = value

                    # Also check for direct parameter values
                    param_keys = ['input_source', 'output_destination', 'api_url', 'format', 'operation']
                    for key in param_keys:
                        if key in content and key not in suggestions:
                            suggestions[key] = content[key]

        except Exception as e:
            print(f"[WARN] Error getting memory suggestions: {e}")

        return suggestions

    def _extract_context_parameters(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract parameters from context"""
        context_params = {}

        if "workspace_path" in context:
            context_params["default_input_path"] = context["workspace_path"]
            context_params["default_output_path"] = context["workspace_path"]

        if "user_preferences" in context:
            prefs = context["user_preferences"]
            if "default_format" in prefs:
                context_params["preferred_format"] = prefs["default_format"]

        return context_params

    def _generate_workflow_name(self, intent_analysis: IntentAnalysis) -> str:
        """Generate a descriptive workflow name"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        intent = intent_analysis.primary_intent.replace("_", " ").title()
        return f"{intent} Workflow {timestamp}"

    def _generate_code_from_template(self, template: AetherTemplate, parameters: Dict[str, Any]) -> str:
        """Generate .aether code by filling template with parameters"""
        try:
            # Create a copy of parameters to avoid modifying the original
            working_params = parameters.copy()

            # Ensure ALL template placeholders have values
            template_placeholders = self._extract_template_placeholders(template.pattern)

            for placeholder in template_placeholders:
                if placeholder not in working_params:
                    working_params[placeholder] = self._get_default_parameter_value(placeholder)

            # Convert complex parameters to JSON strings
            formatted_params = {}
            for key, value in working_params.items():
                if isinstance(value, (dict, list)):
                    formatted_params[key] = json.dumps(value)
                elif isinstance(value, bool):
                    formatted_params[key] = str(value).lower()
                elif value is None:
                    formatted_params[key] = f"<{key}>"
                else:
                    formatted_params[key] = str(value)

            # Fill template
            aether_code = template.pattern.format(**formatted_params)
            return aether_code

        except KeyError as e:
            print(f"[WARN] Missing parameter for template: {e}")
            # Create comprehensive fallback parameters
            fallback_params = self._create_comprehensive_fallback_params(template)
            fallback_params.update(parameters)

            try:
                # Convert fallback params to strings
                formatted_fallback = {}
                for key, value in fallback_params.items():
                    if isinstance(value, (dict, list)):
                        formatted_fallback[key] = json.dumps(value)
                    elif isinstance(value, bool):
                        formatted_fallback[key] = str(value).lower()
                    else:
                        formatted_fallback[key] = str(value)

                return template.pattern.format(**formatted_fallback)
            except KeyError as e2:
                print(f"[WARN] Still missing parameter after fallback: {e2}")
                return self._create_error_workflow(str(e2), template.name)
        except Exception as e:
            print(f"[ERROR] Unexpected error in template generation: {e}")
            return self._create_error_workflow(str(e), template.name)

    def _extract_template_placeholders(self, template_pattern: str) -> List[str]:
        """Extract all placeholders from template pattern"""
        placeholder_pattern = r'\{([^}]+)\}'
        return re.findall(placeholder_pattern, template_pattern)

    def _create_comprehensive_fallback_params(self, template: AetherTemplate) -> Dict[str, Any]:
        """Create comprehensive fallback parameters for templates"""
        fallback_params = {}

        # Add all required entities with placeholders
        for required_param in template.required_entities:
            fallback_params[required_param] = f"<{required_param}>"

        # Add all optional entities with defaults
        for optional_param in template.optional_entities:
            fallback_params[optional_param] = self._get_default_parameter_value(optional_param)

        # Add comprehensive common parameters
        common_defaults = {
            # Workflow naming
            "workflow_name": "Generated Workflow",
            "input_type": "data",
            "output_type": "result",

            # File and data parameters
            "input_source": "data/input.json",
            "input_format": "json",
            "output_destination": "output/results.json",
            "output_format": "json",
            "data_format": "json",
            "data_source": "data/input.csv",

            # API parameters
            "api_url": "https://api.example.com/v1/data",
            "api_headers": "{}",
            "request_payload": "{}",
            "extract_fields": '["data"]',
            "error_strategy": "log_and_continue",
            "http_method": "GET",
            "data_operation": "process",
            "data_filters": "{}",
            "output_location": "output/results.json",
            "result_format": "json",

            # Processing parameters
            "operation": "transform",
            "processing_params": "{}",
            "validation_schema": "schema.json",
            "strict_validation": "true",

            # ML parameters
            "training_data": "data/training.csv",
            "preprocessing_steps": '["normalize", "clean"]',
            "feature_operations": '["encode_categorical", "scale_numerical"]',
            "target_variable": "target",
            "ml_algorithm": "random_forest",
            "model_params": "{}",
            "validation_ratio": "0.2",
            "evaluation_metrics": '["accuracy", "precision", "recall"]',
            "performance_threshold": "0.8",
            "deployment_location": "production",
            "model_export_format": "pickle",

            # Analysis parameters
            "analysis_type": "descriptive",
            "statistical_methods": '["mean", "std", "correlation"]',
            "confidence_interval": "0.95",
            "visualization_types": '["bar", "line", "scatter"]',
            "chart_format": "png",
            "visual_theme": "default",
            "pattern_methods": '["trend_analysis"]',
            "anomaly_settings": "{}",
            "report_type": "html",
            "report_location": "reports/",
            "include_data": "false",
            "column_selection": '["all"]',

            # File operations parameters
            "source_path": "input/",
            "file_filters": '["*"]',
            "scan_recursive": "true",
            "file_operations": '["process"]',
            "processing_batch": "10",
            "enable_parallel": "true",
            "validation_criteria": '["file_size", "format"]',
            "error_action": "skip",
            "target_path": "output/",
            "organization_method": "by_type",
            "keep_structure": "true"
        }

        fallback_params.update(common_defaults)
        return fallback_params

    def _create_error_workflow(self, error_message: str, template_name: str) -> str:
        """Create a basic error workflow when template generation fails"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return f"""# Error Workflow - {template_name}
# Generated: {timestamp}
# Error: {error_message}

node error_input input
  source: "Please specify input source"
  format: "json"

node error_processor transform
  operation: "Please specify operation"
  error: "{error_message}"

node error_output output
  destination: "output/error_log.json"
  format: "json"

error_input -> error_processor
error_processor -> error_output

# Please review and update the parameters above
# Missing parameter: {error_message}"""

    async def _generate_suggestions(
        self,
        intent_analysis: IntentAnalysis,
        parameters: Dict[str, Any],
        template: AetherTemplate
    ) -> List[Dict[str, Any]]:
        """Generate improvement and optimization suggestions"""
        suggestions = []

        # Suggest missing required parameters
        for required_param in template.required_entities:
            if required_param not in parameters or str(parameters[required_param]).startswith("<"):
                suggestions.append({
                    "type": "missing_parameter",
                    "message": f"Consider specifying {required_param}",
                    "priority": "high",
                    "parameter": required_param
                })

        # Suggest optimizations based on complexity
        if intent_analysis.complexity > 0.7:
            suggestions.append({
                "type": "optimization",
                "message": "Consider breaking this into smaller workflows for better maintainability",
                "priority": "medium"
            })

        # Suggest validation nodes
        if "validator" not in str(parameters):
            suggestions.append({
                "type": "enhancement",
                "message": "Consider adding validation steps for data quality",
                "priority": "low"
            })

        # Suggest error handling
        suggestions.append({
            "type": "robustness",
            "message": "Add error handling and retry mechanisms",
            "priority": "medium"
        })

        return suggestions

    def _create_generation_metadata(
        self,
        description: str,
        intent_analysis: IntentAnalysis,
        template: AetherTemplate,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create metadata about the generation process"""
        return {
            "generated_at": datetime.now().isoformat(),
            "original_description": description,
            "template_used": template.name,
            "intent_confidence": intent_analysis.confidence,
            "complexity_score": intent_analysis.complexity,
            "entities_extracted": len([v for v in intent_analysis.entities.values() if v]),
            "parameters_filled": len(parameters),
            "required_parameters": len(template.required_entities),
            "generation_method": "template_based_with_memory_enhancement"
        }

    # Parameter suggestion methods for specific types
    async def _suggest_input_source(self, context: Dict[str, Any]) -> ParameterSuggestion:
        """Suggest input source based on context and memory"""
        # Implementation would check recent file usage, workspace files, etc.
        return ParameterSuggestion(
            parameter="input_source",
            value="data/input.json",
            confidence=0.6,
            source="default",
            explanation="Common input file pattern"
        )

    async def _suggest_output_destination(self, context: Dict[str, Any]) -> ParameterSuggestion:
        """Suggest output destination"""
        return ParameterSuggestion(
            parameter="output_destination",
            value="output/results.json",
            confidence=0.6,
            source="default",
            explanation="Standard output location"
        )

    async def _suggest_operation(self, context: Dict[str, Any]) -> ParameterSuggestion:
        """Suggest operation type"""
        return ParameterSuggestion(
            parameter="operation",
            value="transform",
            confidence=0.7,
            source="default",
            explanation="Most common operation type"
        )

    async def _suggest_format(self, context: Dict[str, Any]) -> ParameterSuggestion:
        """Suggest data format"""
        return ParameterSuggestion(
            parameter="format",
            value="json",
            confidence=0.8,
            source="default",
            explanation="Standard data interchange format"
        )

    async def _suggest_api_url(self, context: Dict[str, Any]) -> ParameterSuggestion:
        """Suggest API URL from memory"""
        # Would check memory for previously used APIs
        return ParameterSuggestion(
            parameter="api_url",
            value="https://api.example.com/v1/data",
            confidence=0.3,
            source="placeholder",
            explanation="Example API endpoint - replace with actual URL"
        )

    async def _suggest_algorithm(self, context: Dict[str, Any]) -> ParameterSuggestion:
        """Suggest ML algorithm"""
        return ParameterSuggestion(
            parameter="algorithm",
            value="random_forest",
            confidence=0.7,
            source="default",
            explanation="Robust general-purpose algorithm"
        )

    def _get_default_parameter_value(self, parameter_name: str) -> str:
        """Get default value for a parameter"""
        defaults = {
            # File and data parameters
            "input_source": "data/input.json",
            "output_destination": "output/results.json",
            "data_source": "data/input.csv",
            "input_format": "json",
            "output_format": "json",
            "data_format": "csv",

            # Validation and schema
            "validation_schema": "schema.json",
            "strict_validation": "true",

            # API parameters
            "api_url": "https://api.example.com/v1/data",
            "api_headers": "{}",
            "request_payload": "{}",
            "http_method": "GET",
            "extract_fields": '["data"]',
            "error_strategy": "log_and_continue",
            "data_operation": "process",
            "data_filters": "{}",
            "output_location": "output/results.json",
            "result_format": "json",

            # Processing parameters
            "operation": "transform",
            "processing_params": "{}",

            # ML parameters
            "training_data": "data/training.csv",
            "ml_algorithm": "random_forest",
            "target_variable": "target",
            "deployment_location": "production",
            "evaluation_metrics": '["accuracy", "precision", "recall"]',
            "model_params": "{}",
            "validation_ratio": "0.2",
            "performance_threshold": "0.8",
            "model_export_format": "pickle",
            "preprocessing_steps": '["normalize", "clean"]',
            "feature_operations": '["encode_categorical"]',

            # Analysis parameters
            "analysis_type": "descriptive",
            "visualization_types": '["bar", "line", "scatter"]',
            "report_location": "reports/",
            "statistical_methods": '["mean", "std"]',
            "confidence_interval": "0.95",
            "chart_format": "png",
            "visual_theme": "default",
            "pattern_methods": '["trend_analysis"]',
            "anomaly_settings": "{}",
            "report_type": "html",
            "include_data": "false",
            "column_selection": '["all"]',

            # File operations parameters
            "source_path": "input/",
            "target_path": "output/",
            "file_filters": '["*"]',
            "scan_recursive": "true",
            "file_operations": '["process"]',
            "processing_batch": "10",
            "enable_parallel": "true",
            "validation_criteria": '["file_size"]',
            "error_action": "skip",
            "organization_method": "by_type",
            "keep_structure": "true",

            # Workflow parameters
            "workflow_name": "Generated Workflow",
            "input_type": "data",
            "output_type": "result"
        }
        return defaults.get(parameter_name, f"<{parameter_name}>")

class WorkflowOptimizer:
    """Optimizes generated .aether workflows for performance and maintainability"""

    def __init__(self):
        self.optimization_rules = self._initialize_optimization_rules()

    def _initialize_optimization_rules(self) -> List[Dict[str, Any]]:
        """Initialize workflow optimization rules"""
        return [
            {
                "name": "parallel_processing",
                "condition": lambda code: "transform" in code and "input" in code,
                "optimization": self._add_parallel_processing,
                "description": "Add parallel processing for independent transforms"
            },
            {
                "name": "error_handling",
                "condition": lambda code: "api_call" in code,
                "optimization": self._add_error_handling,
                "description": "Add error handling for API calls"
            },
            {
                "name": "caching",
                "condition": lambda code: "expensive_operation" in code.lower(),
                "optimization": self._add_caching,
                "description": "Add caching for expensive operations"
            }
        ]

    async def optimize(self, aether_code: str, intent_analysis: IntentAnalysis) -> str:
        """Apply optimization rules to .aether code"""
        optimized_code = aether_code

        for rule in self.optimization_rules:
            if rule["condition"](optimized_code):
                try:
                    optimized_code = rule["optimization"](optimized_code)
                    print(f"✅ Applied optimization: {rule['name']}")
                except Exception as e:
                    print(f"[WARN] Failed to apply {rule['name']}: {e}")

        return optimized_code

    def _add_parallel_processing(self, code: str) -> str:
        """Add parallel processing annotations"""
        return code.replace("node processor transform",
                          "node processor transform\n  parallel: true\n  max_workers: 4")

    def _add_error_handling(self, code: str) -> str:
        """Add error handling to API calls"""
        return code.replace("node api_request api_call",
                          "node api_request api_call\n  retry_attempts: 3\n  timeout: 30")

    def _add_caching(self, code: str) -> str:
        """Add caching for expensive operations"""
        return code.replace("node processor transform",
                          "node processor transform\n  cache_enabled: true\n  cache_ttl: 3600")
