#!/usr/bin/env python3
"""
Enhanced Aetherra Language Integration
=====================================

Integration module that connects the enhanced .aether language features
to the main Aetherra system, providing backward compatibility while
adding the new control structures and language features.
"""

import sys
from pathlib import Path
from typing import Any, Dict

# Add the Aetherra core to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from .aetherra_grammar import AetherraParser
    from .aetherra_interpreter import AetherraInterpreter
    from .interpreter.enhanced_interpreter import AetherraEnhancedInterpreter
except ImportError:
    from aetherra_grammar import AetherraParser
    from aetherra_interpreter import AetherraInterpreter
    from interpreter.enhanced_interpreter import AetherraEnhancedInterpreter


class EnhancedAetherraLanguage:
    """
    Enhanced Aetherra Language System

    Provides a unified interface for parsing and executing .aether scripts
    with both legacy and enhanced language features.
    """

    def __init__(self):
        self.parser = AetherraParser()
        self.base_interpreter = None
        self.enhanced_interpreter = None

        # Try to initialize interpreters
        try:
            # Initialize base interpreter if available
            self.base_interpreter = AetherraInterpreter()
        except Exception as e:
            print(f"Warning: Could not initialize base interpreter: {e}")

        # Initialize enhanced interpreter
        self.enhanced_interpreter = AetherraEnhancedInterpreter(self.base_interpreter)

    def parse(self, source_code: str):
        """Parse .aether source code into AST"""
        try:
            return self.parser.parse(source_code)
        except Exception as e:
            print(f"Parse error: {e}")
            return None

    def execute(self, source_code: str, context: Dict[str, Any] | None = None) -> Any:
        """Parse and execute .aether source code"""
        ast = self.parse(source_code)
        if ast is None:
            return None

        return self.execute_ast(ast, context)

    def execute_ast(self, ast, context: Dict[str, Any] | None = None) -> Any:
        """Execute an .aether AST"""
        try:
            if self.enhanced_interpreter:
                return self.enhanced_interpreter.execute(ast, context)
            else:
                print("No interpreter available")
                return None
        except Exception as e:
            print(f"Execution error: {e}")
            return None

    def validate_syntax(self, source_code: str) -> Dict[str, Any]:
        """Validate .aether syntax"""
        return self.parser.validate_syntax(source_code)

    def get_language_info(self) -> Dict[str, Any]:
        """Get information about the enhanced language features"""
        return {
            "version": "2.0",
            "features": {
                "enhanced_control_flow": {
                    "if_else": "Conditional execution with {} syntax",
                    "loops": "for/while loops with break/continue support",
                    "error_handling": "try/catch exception handling",
                    "pattern_matching": "match/switch statements",
                    "timing": "wait/delay timing control",
                },
                "functions": {
                    "return_values": "Functions can return values",
                    "parameters": "Function parameter support",
                },
                "modules": {
                    "import": "import 'path' as alias syntax",
                    "use": "use module syntax",
                },
            },
            "syntax_changes": {
                "block_delimiters": "Changed from : ... end to { ... }",
                "function_definition": "fn name() { ... } instead of define name(): ... end",
            },
        }


def create_enhanced_language() -> EnhancedAetherraLanguage:
    """Factory function to create enhanced language instance"""
    return EnhancedAetherraLanguage()


def test_enhanced_features():
    """Test function for the enhanced language features"""
    print("🧪 Testing Enhanced Aetherra Language Features")

    lang = create_enhanced_language()

    # Test 1: Basic if/else
    test_code_1 = """
    if true {
        log "If statement works!"
    } else {
        log "This shouldn't execute"
    }
    """

    print("\n📋 Test 1: if/else statement")
    result = lang.execute(test_code_1)
    print(f"Result: {result}")

    # Test 2: For loop
    test_code_2 = """
    for i in [1, 2, 3] {
        log f"Loop iteration: {i}"
    }
    """

    print("\n📋 Test 2: for loop")
    result = lang.execute(test_code_2)
    print(f"Result: {result}")

    # Test 3: Function with return value
    test_code_3 = """
    fn add(a, b) {
        return a + b
    }

    let result = add(5, 3)
    log f"Addition result: {result}"
    """

    print("\n📋 Test 3: function return")
    result = lang.execute(test_code_3)
    print(f"Result: {result}")

    # Test 4: Wait statement
    test_code_4 = """
    log "Starting wait..."
    wait 1s
    log "Wait completed!"
    """

    print("\n📋 Test 4: wait statement")
    result = lang.execute(test_code_4)
    print(f"Result: {result}")

    # Test 5: Match statement
    test_code_5 = """
    let status = "pending"

    match status {
        case "pending": {
            log "Status is pending"
        }
        case "completed": {
            log "Status is completed"
        }
        default: {
            log "Unknown status"
        }
    }
    """

    print("\n📋 Test 5: match statement")
    result = lang.execute(test_code_5)
    print(f"Result: {result}")

    print("\n✅ Enhanced language feature tests completed!")


if __name__ == "__main__":
    test_enhanced_features()
