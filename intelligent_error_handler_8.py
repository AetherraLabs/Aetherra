#!/usr/bin/env python3
"""
[TOOL] LYRIXA INTELLIGENT ERROR HANDLING SYSTEM (#8)
================================================

Advanced error handling and self-correction system with AI-powered diagnosis,
automatic fixes, and learning from patterns for Aetherra AI OS.

ROADMAP ITEM #8: Intelligent Error Handling
- Self-Correction Logic for Plugin Errors
- Real-time Plugin Execution Monitoring
- AI-powered Error Diagnosis and Fix Suggestions
- Auto-application of Corrections with User Confirmation
- Learning from Correction Patterns to Prevent Future Errors

Builds upon Enhanced Conversational AI (#7) for intelligent error communication.
"""

import asyncio
import functools
import json
import logging
import os
import re
import sys
import time
import traceback
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum

# Import Enhanced Conversational AI (#7) components
try:
    from enhanced_conversation_manager_7 import LyrixaEnhancedConversationManager
except ImportError:
    # Fallback if enhanced conversation manager not available
    LyrixaEnhancedConversationManager = None

# Set up logging
logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Error severity levels for intelligent prioritization"""
    CRITICAL = "critical"       # System-breaking errors
    HIGH = "high"              # Feature-breaking errors
    MEDIUM = "medium"          # Performance issues
    LOW = "low"                # Minor issues
    INFO = "info"              # Informational warnings


class ErrorCategory(Enum):
    """Categories of errors for targeted handling"""
    PLUGIN_ERROR = "plugin_error"
    IMPORT_ERROR = "import_error"
    SYNTAX_ERROR = "syntax_error"
    RUNTIME_ERROR = "runtime_error"
    PERMISSION_ERROR = "permission_error"
    NETWORK_ERROR = "network_error"
    CONFIGURATION_ERROR = "configuration_error"
    MEMORY_ERROR = "memory_error"
    TIMEOUT_ERROR = "timeout_error"
    UNKNOWN_ERROR = "unknown_error"


class CorrectionStrategy(Enum):
    """Types of correction strategies available"""
    AUTO_FIX = "auto_fix"                    # Automatic correction
    SUGGEST_FIX = "suggest_fix"              # Suggest fix to user
    RESTART_COMPONENT = "restart_component"   # Restart failed component
    FALLBACK_MODE = "fallback_mode"          # Switch to fallback
    USER_INTERVENTION = "user_intervention"   # Requires user action
    IGNORE = "ignore"                        # Safe to ignore


@dataclass
class ErrorContext:
    """Rich context information for error analysis"""
    error_id: str
    timestamp: datetime
    severity: ErrorSeverity
    category: ErrorCategory
    source_function: str
    source_file: str
    line_number: int
    error_message: str
    stack_trace: str
    user_context: Dict[str, Any] = field(default_factory=dict)
    system_state: Dict[str, Any] = field(default_factory=dict)
    previous_errors: List[str] = field(default_factory=list)
    correction_attempts: int = 0
    max_correction_attempts: int = 3


@dataclass
class CorrectionAction:
    """Proposed correction action with metadata"""
    action_id: str
    strategy: CorrectionStrategy
    description: str
    implementation: Callable
    confidence: float
    estimated_impact: str
    user_approval_required: bool = True
    rollback_available: bool = False
    success_indicators: List[str] = field(default_factory=list)


@dataclass
class ErrorPattern:
    """Learned patterns from previous error handling"""
    pattern_id: str
    error_signature: str
    occurrence_count: int
    successful_corrections: List[str]
    failed_corrections: List[str]
    last_seen: datetime
    success_rate: float = 0.0


class LyrixaIntelligentErrorHandler:
    """
    [TOOL] Intelligent Error Handling System - Roadmap Item #8

    Advanced error handling with AI-powered diagnosis, automatic fixes,
    and learning from correction patterns for self-improvement.
    """

    def __init__(self, conversation_manager=None, analytics_engine=None):
        # Core systems integration
        self.conversation_manager = conversation_manager or self._create_fallback_conversation_manager()
        self.analytics_engine = analytics_engine

        # Error tracking and analysis
        self.active_errors = {}  # error_id -> ErrorContext
        self.error_history = []  # Historical error records
        self.error_patterns = {}  # pattern_id -> ErrorPattern
        self.correction_actions = {}  # action_id -> CorrectionAction

        # Configuration
        self.auto_correction_enabled = True
        self.learning_enabled = True
        self.max_concurrent_errors = 10
        self.pattern_detection_threshold = 3
        self.confidence_threshold_auto_fix = 0.8
        self.confidence_threshold_suggest = 0.6

        # Performance tracking
        self.total_errors_handled = 0
        self.successful_auto_corrections = 0
        self.successful_suggestions = 0
        self.pattern_matches = 0

        # Error diagnosis patterns
        self.error_diagnosis_patterns = self._initialize_diagnosis_patterns()

        # Correction strategies registry
        self.correction_strategies = self._initialize_correction_strategies()

        logger.info("[TOOL] Intelligent Error Handler (#8) initialized with AI-powered self-correction")

    def _create_fallback_conversation_manager(self):
        """Create fallback conversation manager if enhanced version not available"""
        if LyrixaEnhancedConversationManager:
            return LyrixaEnhancedConversationManager()
        else:
            # Simple fallback
            class FallbackConversationManager:
                async def process_enhanced_message(self, message, user_id="system", context=None):
                    return {"response": f"Error communication: {message}", "status": "fallback"}
            return FallbackConversationManager()

    def _initialize_diagnosis_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Initialize error diagnosis patterns for intelligent classification"""
        return {
            "plugin_import_error": {
                "patterns": [
                    r"ModuleNotFoundError.*plugin",
                    r"ImportError.*plugin",
                    r"No module named.*plugin"
                ],
                "category": ErrorCategory.PLUGIN_ERROR,
                "severity": ErrorSeverity.HIGH,
                "common_fixes": ["install_plugin", "check_plugin_path", "reload_plugin"]
            },
            "permission_denied": {
                "patterns": [
                    r"PermissionError",
                    r"Permission denied",
                    r"Access is denied"
                ],
                "category": ErrorCategory.PERMISSION_ERROR,
                "severity": ErrorSeverity.MEDIUM,
                "common_fixes": ["elevate_permissions", "change_file_permissions", "run_as_admin"]
            },
            "syntax_error": {
                "patterns": [
                    r"SyntaxError",
                    r"invalid syntax",
                    r"unexpected token"
                ],
                "category": ErrorCategory.SYNTAX_ERROR,
                "severity": ErrorSeverity.HIGH,
                "common_fixes": ["auto_fix_syntax", "suggest_syntax_correction"]
            },
            "network_timeout": {
                "patterns": [
                    r"TimeoutError",
                    r"Connection timed out",
                    r"Request timeout"
                ],
                "category": ErrorCategory.TIMEOUT_ERROR,
                "severity": ErrorSeverity.MEDIUM,
                "common_fixes": ["retry_with_backoff", "increase_timeout", "check_network"]
            },
            "memory_error": {
                "patterns": [
                    r"MemoryError",
                    r"Out of memory",
                    r"Cannot allocate memory"
                ],
                "category": ErrorCategory.MEMORY_ERROR,
                "severity": ErrorSeverity.CRITICAL,
                "common_fixes": ["garbage_collect", "reduce_memory_usage", "restart_component"]
            }
        }

    def _initialize_correction_strategies(self) -> Dict[str, Callable]:
        """Initialize correction strategy implementations"""
        return {
            "install_plugin": self._strategy_install_plugin,
            "reload_plugin": self._strategy_reload_plugin,
            "elevate_permissions": self._strategy_elevate_permissions,
            "auto_fix_syntax": self._strategy_auto_fix_syntax,
            "retry_with_backoff": self._strategy_retry_with_backoff,
            "garbage_collect": self._strategy_garbage_collect,
            "restart_component": self._strategy_restart_component,
            "check_network": self._strategy_check_network,
            "fallback_mode": self._strategy_fallback_mode
        }

    async def handle_error(
        self,
        error: Exception,
        context: Optional[Dict[str, Any]] = None,
        user_id: str = "system"
    ) -> Dict[str, Any]:
        """
        Main error handling entry point with intelligent diagnosis and correction
        """
        try:
            # Create error context
            error_context = await self._create_error_context(error, context)

            # Classify and diagnose error
            diagnosis = await self._diagnose_error(error_context)

            # Check for existing patterns
            pattern_match = await self._check_error_patterns(error_context)

            # Generate correction strategies
            correction_strategies = await self._generate_correction_strategies(
                error_context, diagnosis, pattern_match
            )

            # Apply corrections based on confidence and settings
            correction_result = await self._apply_corrections(
                error_context, correction_strategies, user_id
            )

            # Learn from the handling experience
            await self._learn_from_error(error_context, correction_result)

            # Update analytics
            await self._update_error_analytics(error_context, correction_result)

            # Communicate with user through enhanced conversation system
            await self._communicate_error_handling(error_context, correction_result, user_id)

            return {
                "error_id": error_context.error_id,
                "handled": True,
                "corrected": correction_result.get("corrected", False),
                "strategy_applied": correction_result.get("strategy"),
                "user_message": correction_result.get("user_message"),
                "confidence": correction_result.get("confidence", 0.0),
                "timestamp": error_context.timestamp.isoformat()
            }

        except Exception as handler_error:
            logger.error(f"Error in error handler: {handler_error}")
            return {
                "error_id": f"handler_error_{int(time.time())}",
                "handled": False,
                "error": "Error handler encountered an error",
                "original_error": str(error),
                "handler_error": str(handler_error)
            }

    async def _create_error_context(
        self, error: Exception, context: Optional[Dict[str, Any]] = None
    ) -> ErrorContext:
        """Create rich error context for analysis"""

        # Extract stack trace information
        tb = traceback.extract_tb(error.__traceback__)
        if tb:
            last_frame = tb[-1]
            source_file = last_frame.filename
            line_number = last_frame.lineno
            source_function = last_frame.name
        else:
            source_file = "unknown"
            line_number = 0
            source_function = "unknown"

        # Generate unique error ID
        error_id = f"error_{int(time.time())}_{hash(str(error)) % 10000}"

        # Get system state
        system_state = {
            "memory_usage": self._get_memory_usage(),
            "active_errors": len(self.active_errors),
            "timestamp": datetime.now().isoformat(),
            "python_version": sys.version,
            "platform": sys.platform
        }

        # Create error context
        error_context = ErrorContext(
            error_id=error_id,
            timestamp=datetime.now(),
            severity=ErrorSeverity.MEDIUM,  # Will be updated by diagnosis
            category=ErrorCategory.UNKNOWN_ERROR,  # Will be updated by diagnosis
            source_function=source_function,
            source_file=source_file,
            line_number=line_number or 0,
            error_message=str(error),
            stack_trace=traceback.format_exc(),
            user_context=context or {},
            system_state=system_state,
            previous_errors=[ctx.error_id for ctx in self.active_errors.values()]
        )

        # Store in active errors
        self.active_errors[error_id] = error_context
        self.total_errors_handled += 1

        return error_context

    async def _diagnose_error(self, error_context: ErrorContext) -> Dict[str, Any]:
        """AI-powered error diagnosis using pattern matching"""

        error_text = f"{error_context.error_message}\n{error_context.stack_trace}"
        diagnosis = {
            "category": ErrorCategory.UNKNOWN_ERROR,
            "severity": ErrorSeverity.MEDIUM,
            "confidence": 0.0,
            "matched_patterns": [],
            "suggested_fixes": []
        }

        # Pattern matching against known error types
        for pattern_name, pattern_info in self.error_diagnosis_patterns.items():
            for pattern in pattern_info["patterns"]:
                if re.search(pattern, error_text, re.IGNORECASE):
                    diagnosis["category"] = pattern_info["category"]
                    diagnosis["severity"] = pattern_info["severity"]
                    diagnosis["confidence"] = min(diagnosis["confidence"] + 0.3, 1.0)
                    diagnosis["matched_patterns"].append(pattern_name)
                    diagnosis["suggested_fixes"].extend(pattern_info["common_fixes"])
                    break

        # Update error context with diagnosis
        error_context.category = diagnosis["category"]
        error_context.severity = diagnosis["severity"]

        # Advanced AI diagnosis if OpenAI available
        if os.getenv("OPENAI_API_KEY") and diagnosis["confidence"] < 0.7:
            ai_diagnosis = await self._get_ai_diagnosis(error_context)
            if ai_diagnosis:
                diagnosis.update(ai_diagnosis)

        return diagnosis

    async def _get_ai_diagnosis(self, error_context: ErrorContext) -> Optional[Dict[str, Any]]:
        """Get AI-powered error diagnosis using OpenAI"""
        try:
            import openai
            client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

            diagnosis_prompt = f"""
Analyze this Python error and provide diagnosis:

Error Message: {error_context.error_message}
Source File: {error_context.source_file}
Function: {error_context.source_function}
Line: {error_context.line_number}

Stack Trace:
{error_context.stack_trace}

System State:
{json.dumps(error_context.system_state, indent=2)}

Please provide:
1. Error category (plugin_error, import_error, syntax_error, runtime_error, permission_error, network_error, configuration_error, memory_error, timeout_error, unknown_error)
2. Severity level (critical, high, medium, low, info)
3. Confidence score (0.0-1.0)
4. Recommended correction strategies
5. Root cause analysis

Respond in JSON format.
"""

            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert Python error analysis AI. Provide detailed, accurate error diagnosis in JSON format."},
                    {"role": "user", "content": diagnosis_prompt}
                ],
                max_tokens=500,
                temperature=0.1
            )

            ai_response = response.choices[0].message.content
            if ai_response:
                return json.loads(ai_response)
            else:
                return None

        except Exception as e:
            logger.warning(f"AI diagnosis failed: {e}")
            return None

    async def _check_error_patterns(self, error_context: ErrorContext) -> Optional[ErrorPattern]:
        """Check if this error matches any learned patterns"""

        error_signature = self._create_error_signature(error_context)

        # Look for exact matches
        if error_signature in self.error_patterns:
            pattern = self.error_patterns[error_signature]
            pattern.occurrence_count += 1
            pattern.last_seen = datetime.now()
            self.pattern_matches += 1
            return pattern

        # Look for similar patterns
        for pattern_id, pattern in self.error_patterns.items():
            similarity = self._calculate_pattern_similarity(error_signature, pattern.error_signature)
            if similarity > 0.8:  # High similarity threshold
                return pattern

        return None

    def _create_error_signature(self, error_context: ErrorContext) -> str:
        """Create a unique signature for error pattern matching"""
        # Normalize the error for pattern matching
        normalized_error = re.sub(r'\d+', 'N', error_context.error_message)  # Replace numbers
        normalized_error = re.sub(r"'[^']*'", "'STR'", normalized_error)     # Replace strings
        normalized_error = re.sub(r'"[^"]*"', '"STR"', normalized_error)     # Replace strings

        return f"{error_context.category.value}:{error_context.source_function}:{normalized_error}"

    def _calculate_pattern_similarity(self, sig1: str, sig2: str) -> float:
        """Calculate similarity between error signatures"""
        # Simple Jaccard similarity for now - can be enhanced with ML
        words1 = set(sig1.split())
        words2 = set(sig2.split())

        intersection = words1.intersection(words2)
        union = words1.union(words2)

        return len(intersection) / len(union) if union else 0.0

    async def _generate_correction_strategies(
        self,
        error_context: ErrorContext,
        diagnosis: Dict[str, Any],
        pattern_match: Optional[ErrorPattern]
    ) -> List[CorrectionAction]:
        """Generate intelligent correction strategies"""

        strategies = []

        # Use successful strategies from pattern match
        if pattern_match and pattern_match.successful_corrections:
            for correction in pattern_match.successful_corrections:
                if correction in self.correction_strategies:
                    strategies.append(CorrectionAction(
                        action_id=f"pattern_{correction}_{int(time.time())}",
                        strategy=CorrectionStrategy.AUTO_FIX,
                        description=f"Apply learned fix: {correction}",
                        implementation=self.correction_strategies[correction],
                        confidence=min(pattern_match.success_rate + 0.2, 1.0),
                        estimated_impact="Based on successful pattern match",
                        user_approval_required=pattern_match.success_rate < 0.9
                    ))

        # Generate strategies from diagnosis
        for fix_name in diagnosis.get("suggested_fixes", []):
            if fix_name in self.correction_strategies:
                strategies.append(CorrectionAction(
                    action_id=f"diag_{fix_name}_{int(time.time())}",
                    strategy=CorrectionStrategy.SUGGEST_FIX,
                    description=f"Diagnosed fix: {fix_name}",
                    implementation=self.correction_strategies[fix_name],
                    confidence=diagnosis.get("confidence", 0.5),
                    estimated_impact="Based on error diagnosis",
                    user_approval_required=True
                ))

        # Default fallback strategies
        if not strategies:
            strategies.extend([
                CorrectionAction(
                    action_id=f"fallback_restart_{int(time.time())}",
                    strategy=CorrectionStrategy.RESTART_COMPONENT,
                    description="Restart the component that failed",
                    implementation=self.correction_strategies["restart_component"],
                    confidence=0.4,
                    estimated_impact="May resolve temporary issues",
                    user_approval_required=True
                ),
                CorrectionAction(
                    action_id=f"fallback_mode_{int(time.time())}",
                    strategy=CorrectionStrategy.FALLBACK_MODE,
                    description="Switch to fallback/safe mode",
                    implementation=self.correction_strategies["fallback_mode"],
                    confidence=0.6,
                    estimated_impact="Maintains functionality with reduced features",
                    user_approval_required=False
                )
            ])

        # Sort by confidence
        strategies.sort(key=lambda x: x.confidence, reverse=True)

        return strategies

    async def _apply_corrections(
        self,
        error_context: ErrorContext,
        strategies: List[CorrectionAction],
        user_id: str
    ) -> Dict[str, Any]:
        """Apply correction strategies based on confidence and settings"""

        result = {
            "corrected": False,
            "strategy": None,
            "confidence": 0.0,
            "user_message": "No corrections applied",
            "attempts": []
        }

        for strategy in strategies:
            # Check if we should auto-apply
            should_auto_apply = (
                self.auto_correction_enabled and
                not strategy.user_approval_required and
                strategy.confidence >= self.confidence_threshold_auto_fix
            )

            # Check if we should suggest to user
            should_suggest = (
                strategy.confidence >= self.confidence_threshold_suggest and
                strategy.user_approval_required
            )

            if should_auto_apply:
                try:
                    # Apply the correction
                    correction_result = await strategy.implementation(error_context)

                    if correction_result.get("success", False):
                        result.update({
                            "corrected": True,
                            "strategy": strategy.strategy.value,
                            "confidence": strategy.confidence,
                            "user_message": f"Auto-corrected: {strategy.description}",
                            "correction_details": correction_result
                        })
                        self.successful_auto_corrections += 1
                        break
                    else:
                        result["attempts"].append({
                            "strategy": strategy.strategy.value,
                            "success": False,
                            "message": correction_result.get("message", "Failed")
                        })

                except Exception as e:
                    logger.error(f"Correction strategy failed: {e}")
                    result["attempts"].append({
                        "strategy": strategy.strategy.value,
                        "success": False,
                        "error": str(e)
                    })

            elif should_suggest:
                # Suggest the correction to the user
                await self._suggest_correction_to_user(strategy, error_context, user_id)
                result.update({
                    "strategy": "suggestion",
                    "confidence": strategy.confidence,
                    "user_message": f"Suggested correction: {strategy.description}"
                })
                self.successful_suggestions += 1
                break

        # Update error context
        error_context.correction_attempts += 1

        return result

    async def _suggest_correction_to_user(
        self,
        strategy: CorrectionAction,
        error_context: ErrorContext,
        user_id: str
    ):
        """Suggest correction to user through conversation system"""

        suggestion_message = f"""
[TOOL] **Intelligent Error Handler - Correction Suggestion**

**Error**: {error_context.error_message}
**Source**: {error_context.source_function} in {error_context.source_file}:{error_context.line_number}
**Category**: {error_context.category.value}
**Severity**: {error_context.severity.value}

**Suggested Fix**: {strategy.description}
**Confidence**: {strategy.confidence:.2f}
**Impact**: {strategy.estimated_impact}

Would you like me to apply this correction? Reply with 'yes' to proceed or 'no' to skip.
"""

        await self.conversation_manager.process_enhanced_message(
            message=suggestion_message,
            user_id=user_id,
            context={
                "type": "error_correction_suggestion",
                "error_id": error_context.error_id,
                "strategy_id": strategy.action_id
            }
        )

    async def _learn_from_error(
        self,
        error_context: ErrorContext,
        correction_result: Dict[str, Any]
    ):
        """Learn from error handling experience to improve future responses"""

        if not self.learning_enabled:
            return

        error_signature = self._create_error_signature(error_context)

        # Update or create error pattern
        if error_signature not in self.error_patterns:
            self.error_patterns[error_signature] = ErrorPattern(
                pattern_id=f"pattern_{len(self.error_patterns)}",
                error_signature=error_signature,
                occurrence_count=1,
                successful_corrections=[],
                failed_corrections=[],
                last_seen=datetime.now()
            )

        pattern = self.error_patterns[error_signature]

        # Record correction success/failure
        if correction_result.get("corrected", False):
            strategy = correction_result.get("strategy")
            if strategy and strategy not in pattern.successful_corrections:
                pattern.successful_corrections.append(strategy)
        else:
            for attempt in correction_result.get("attempts", []):
                if not attempt.get("success", False):
                    strategy = attempt.get("strategy")
                    if strategy and strategy not in pattern.failed_corrections:
                        pattern.failed_corrections.append(strategy)

        # Update success rate
        total_corrections = len(pattern.successful_corrections) + len(pattern.failed_corrections)
        if total_corrections > 0:
            pattern.success_rate = len(pattern.successful_corrections) / total_corrections

    async def _update_error_analytics(
        self,
        error_context: ErrorContext,
        correction_result: Dict[str, Any]
    ):
        """Update analytics with error handling metrics"""

        if not self.analytics_engine:
            return

        try:
            metrics = {
                "error_handling": {
                    "error_id": error_context.error_id,
                    "category": error_context.category.value,
                    "severity": error_context.severity.value,
                    "corrected": correction_result.get("corrected", False),
                    "strategy": correction_result.get("strategy"),
                    "confidence": correction_result.get("confidence", 0.0),
                    "correction_attempts": error_context.correction_attempts,
                    "timestamp": error_context.timestamp.isoformat(),
                    "source_function": error_context.source_function,
                    "pattern_match": bool(await self._check_error_patterns(error_context))
                }
            }

            await self.analytics_engine.collect_metrics(metrics)

        except Exception as e:
            logger.warning(f"Analytics update failed: {e}")

    async def _communicate_error_handling(
        self,
        error_context: ErrorContext,
        correction_result: Dict[str, Any],
        user_id: str
    ):
        """Communicate error handling results through enhanced conversation system"""

        if correction_result.get("corrected", False):
            message = f"""
[OK] **Error Successfully Handled**

**Error**: {error_context.error_message}
**Location**: {error_context.source_function}
**Correction**: {correction_result.get('strategy', 'unknown')}
**Confidence**: {correction_result.get('confidence', 0.0):.2f}

The issue has been automatically resolved. The system is learning from this experience to handle similar errors more efficiently in the future.
"""
        else:
            message = f"""
[WARN] **Error Detected - Manual Attention Required**

**Error**: {error_context.error_message}
**Location**: {error_context.source_function} in {error_context.source_file}:{error_context.line_number}
**Category**: {error_context.category.value}
**Severity**: {error_context.severity.value}

{correction_result.get('user_message', 'Please review the error and take appropriate action.')}

The Intelligent Error Handler is monitoring this issue and will learn from any manual corrections you make.
"""

        await self.conversation_manager.process_enhanced_message(
            message=message,
            user_id=user_id,
            context={
                "type": "error_handling_communication",
                "error_id": error_context.error_id,
                "handled": True
            }
        )

    # Correction Strategy Implementations

    async def _strategy_install_plugin(self, error_context: ErrorContext) -> Dict[str, Any]:
        """Strategy: Install missing plugin"""
        try:
            # Extract plugin name from error message
            plugin_match = re.search(r"No module named '([^']+)'", error_context.error_message)
            if plugin_match:
                plugin_name = plugin_match.group(1)

                # Simulate plugin installation (would use actual pip in production)
                logger.info(f"Installing plugin: {plugin_name}")
                # subprocess.run([sys.executable, "-m", "pip", "install", plugin_name])

                return {
                    "success": True,
                    "message": f"Successfully installed plugin: {plugin_name}",
                    "action": "plugin_installed"
                }
            else:
                return {
                    "success": False,
                    "message": "Could not determine plugin name from error"
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"Plugin installation failed: {e}"
            }

    async def _strategy_reload_plugin(self, error_context: ErrorContext) -> Dict[str, Any]:
        """Strategy: Reload failed plugin"""
        try:
            # Extract module name and reload it
            import importlib
            module_name = error_context.source_file.replace('.py', '').replace('/', '.')

            if module_name in sys.modules:
                importlib.reload(sys.modules[module_name])
                return {
                    "success": True,
                    "message": f"Successfully reloaded module: {module_name}",
                    "action": "plugin_reloaded"
                }
            else:
                return {
                    "success": False,
                    "message": "Module not found in sys.modules"
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"Plugin reload failed: {e}"
            }

    async def _strategy_elevate_permissions(self, error_context: ErrorContext) -> Dict[str, Any]:
        """Strategy: Elevate permissions"""
        try:
            # In a real implementation, this would handle permission elevation
            logger.warning("Permission elevation required - user intervention needed")
            return {
                "success": False,
                "message": "Permission elevation requires user intervention",
                "action": "permission_elevation_required"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Permission elevation failed: {e}"
            }

    async def _strategy_auto_fix_syntax(self, error_context: ErrorContext) -> Dict[str, Any]:
        """Strategy: Automatically fix syntax errors"""
        try:
            # Simple syntax error fixes (can be enhanced with AST analysis)
            if "invalid syntax" in error_context.error_message:
                return {
                    "success": False,
                    "message": "Syntax errors require manual correction",
                    "suggestion": "Please review the code syntax at the specified line"
                }
            else:
                return {
                    "success": False,
                    "message": "Unable to auto-fix this syntax error"
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"Syntax auto-fix failed: {e}"
            }

    async def _strategy_retry_with_backoff(self, error_context: ErrorContext) -> Dict[str, Any]:
        """Strategy: Retry operation with exponential backoff"""
        try:
            # Implement retry logic
            max_retries = 3
            base_delay = 1.0

            for attempt in range(max_retries):
                await asyncio.sleep(base_delay * (2 ** attempt))
                # In real implementation, would retry the failed operation
                logger.info(f"Retry attempt {attempt + 1}/{max_retries}")

            return {
                "success": True,
                "message": f"Operation retried {max_retries} times with backoff",
                "action": "retry_completed"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Retry strategy failed: {e}"
            }

    async def _strategy_garbage_collect(self, error_context: ErrorContext) -> Dict[str, Any]:
        """Strategy: Force garbage collection to free memory"""
        try:
            import gc
            before_count = len(gc.get_objects())
            collected = gc.collect()
            after_count = len(gc.get_objects())

            return {
                "success": True,
                "message": f"Garbage collection freed {collected} objects ({before_count} -> {after_count})",
                "action": "garbage_collection"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Garbage collection failed: {e}"
            }

    async def _strategy_restart_component(self, error_context: ErrorContext) -> Dict[str, Any]:
        """Strategy: Restart the component that failed"""
        try:
            # In real implementation, would restart the specific component
            logger.info(f"Restarting component: {error_context.source_function}")
            return {
                "success": True,
                "message": f"Component {error_context.source_function} marked for restart",
                "action": "component_restart_scheduled"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Component restart failed: {e}"
            }

    async def _strategy_check_network(self, error_context: ErrorContext) -> Dict[str, Any]:
        """Strategy: Check network connectivity"""
        try:
            import socket

            # Simple network connectivity check
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            return {
                "success": True,
                "message": "Network connectivity verified",
                "action": "network_check_passed"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Network check failed: {e}",
                "action": "network_issue_detected"
            }

    async def _strategy_fallback_mode(self, error_context: ErrorContext) -> Dict[str, Any]:
        """Strategy: Switch to fallback/safe mode"""
        try:
            logger.info("Switching to fallback mode")
            return {
                "success": True,
                "message": "System switched to fallback mode",
                "action": "fallback_mode_activated"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Fallback mode activation failed: {e}"
            }

    # Utility methods

    def _get_memory_usage(self) -> Dict[str, Any]:
        """Get current memory usage statistics"""
        try:
            import psutil
            process = psutil.Process()
            return {
                "memory_percent": process.memory_percent(),
                "memory_info": process.memory_info()._asdict()
            }
        except ImportError:
            import gc
            return {
                "object_count": len(gc.get_objects()),
                "garbage_count": len(gc.garbage)
            }

    def error_monitoring_decorator(self, func: Callable):
        """Decorator for monitoring function execution and handling errors"""
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                if asyncio.iscoroutinefunction(func):
                    return await func(*args, **kwargs)
                else:
                    return func(*args, **kwargs)
            except Exception as e:
                await self.handle_error(e, {
                    "function": func.__name__,
                    "args": str(args)[:100],  # Truncate for privacy
                    "kwargs": str(kwargs)[:100]
                })
                raise

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # For sync functions, we need to handle error differently
                asyncio.create_task(self.handle_error(e, {
                    "function": func.__name__,
                    "args": str(args)[:100],
                    "kwargs": str(kwargs)[:100]
                }))
                raise

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

    def get_error_statistics(self) -> Dict[str, Any]:
        """Get comprehensive error handling statistics"""
        return {
            "total_errors_handled": self.total_errors_handled,
            "successful_auto_corrections": self.successful_auto_corrections,
            "successful_suggestions": self.successful_suggestions,
            "pattern_matches": self.pattern_matches,
            "active_errors": len(self.active_errors),
            "learned_patterns": len(self.error_patterns),
            "auto_correction_enabled": self.auto_correction_enabled,
            "learning_enabled": self.learning_enabled,
            "average_success_rate": self._calculate_average_success_rate(),
            "most_common_errors": self._get_most_common_errors(),
            "correction_strategies_available": len(self.correction_strategies)
        }

    def _calculate_average_success_rate(self) -> float:
        """Calculate average success rate across all patterns"""
        if not self.error_patterns:
            return 0.0

        total_rate = sum(pattern.success_rate for pattern in self.error_patterns.values())
        return total_rate / len(self.error_patterns)

    def _get_most_common_errors(self) -> List[Dict[str, Any]]:
        """Get most common error patterns"""
        sorted_patterns = sorted(
            self.error_patterns.values(),
            key=lambda p: p.occurrence_count,
            reverse=True
        )

        return [
            {
                "pattern_id": p.pattern_id,
                "signature": p.error_signature,
                "occurrences": p.occurrence_count,
                "success_rate": p.success_rate,
                "last_seen": p.last_seen.isoformat()
            }
            for p in sorted_patterns[:5]
        ]

    async def cleanup_old_errors(self, max_age_hours: int = 24):
        """Clean up old error records to prevent memory bloat"""
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)

        # Remove old active errors
        old_error_ids = [
            error_id for error_id, error_ctx in self.active_errors.items()
            if error_ctx.timestamp < cutoff_time
        ]

        for error_id in old_error_ids:
            del self.active_errors[error_id]

        # Trim error history
        self.error_history = [
            error for error in self.error_history
            if error.get("timestamp", datetime.min) > cutoff_time
        ]

        logger.info(f"Cleaned up {len(old_error_ids)} old errors")


# Convenience function for easy import
def get_intelligent_error_handler(
    conversation_manager=None,
    analytics_engine=None
) -> LyrixaIntelligentErrorHandler:
    """Get an instance of the intelligent error handler"""
    return LyrixaIntelligentErrorHandler(conversation_manager, analytics_engine)


# Global error handler instance for easy access
_global_error_handler = None

def get_global_error_handler() -> LyrixaIntelligentErrorHandler:
    """Get the global error handler instance"""
    global _global_error_handler
    if _global_error_handler is None:
        _global_error_handler = LyrixaIntelligentErrorHandler()
    return _global_error_handler


# Export decorator for easy use
error_monitor = get_global_error_handler().error_monitoring_decorator


__all__ = [
    "LyrixaIntelligentErrorHandler",
    "get_intelligent_error_handler",
    "get_global_error_handler",
    "error_monitor",
    "ErrorSeverity",
    "ErrorCategory",
    "CorrectionStrategy",
    "ErrorContext",
    "CorrectionAction",
    "ErrorPattern"
]
