"""
NeuroCode Modern Parser Implementation
=====================================

A modern Lark-based parser for NeuroCode that replaces regex pattern matching
with a proper AST-based approach.

This module provides:
- Lark grammar-based parsing
- Proper AST generation
- Syntax error handling
- Integration with existing NeuroCode ecosystem

Usage:
    from core.modern_parser import NeuroCodeModernParser

    parser = NeuroCodeModernParser()
    ast = parser.parse(neurocode_source)
    result = parser.execute(ast)
"""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

try:
    from lark import Lark, Token, Transformer, Tree
    from lark.exceptions import LarkError, LexError, ParseError

    LARK_AVAILABLE = True
except ImportError:
    LARK_AVAILABLE = False

    # Fallback types for when Lark is not available
    class Tree:
        pass

    class Token:
        pass

    class Transformer:
        pass


class ASTNodeType(Enum):
    """Enhanced AST node types for modern parser"""

    PROGRAM = "program"
    GOAL = "goal"
    IDENTITY = "identity"
    CONSCIOUSNESS = "consciousness"
    VOICE = "voice"
    MEMORY = "memory"
    AGENT = "agent"
    FUNCTION_DEF = "function_def"
    FUNCTION_CALL = "function_call"
    ASSIGNMENT = "assignment"
    CONDITIONAL = "conditional"
    LOOP = "loop"
    BLOCK = "block"
    EXPRESSION = "expression"
    LITERAL = "literal"
    IDENTIFIER = "identifier"
    COMMENT = "comment"
    INTENT_ACTION = "intent_action"
    WHEN_STATEMENT = "when_statement"


@dataclass
class ASTNode:
    """Modern AST node with enhanced metadata"""

    type: ASTNodeType
    value: Any = None
    children: Optional[List["ASTNode"]] = None
    metadata: Optional[Dict[str, Any]] = None
    source_location: Optional[Dict[str, int]] = None

    def __post_init__(self):
        if self.children is None:
            self.children = []
        if self.metadata is None:
            self.metadata = {}
        if self.source_location is None:
            self.source_location = {}


class NeuroCodeTransformer(Transformer):
    """Transforms Lark parse tree into NeuroCode AST"""

    def start(self, items):
        """Root program node"""
        return ASTNode(
            type=ASTNodeType.PROGRAM, children=items, metadata={"total_statements": len(items)}
        )

    def goal_statement(self, items):
        """Transform goal statement"""
        goal_value = items[0]
        modifiers = {}

        # Process any goal modifiers
        for item in items[1:]:
            if isinstance(item, dict):
                modifiers.update(item)

        return ASTNode(type=ASTNodeType.GOAL, value=goal_value, metadata=modifiers)

    def priority_clause(self, items):
        """Transform priority clause"""
        return {"priority": str(items[0])}

    def deadline_clause(self, items):
        """Transform deadline clause"""
        return {"deadline": str(items[0]).strip('"')}

    def condition_clause(self, items):
        """Transform condition clause"""
        return {"condition": items[0]}

    def identity_statement(self, items):
        """Transform identity statement"""
        properties = {}
        for prop in items:
            if isinstance(prop, dict):
                properties.update(prop)

        return ASTNode(
            type=ASTNodeType.IDENTITY,
            value=properties,
            metadata={"property_count": len(properties)},
        )

    def identity_property(self, items):
        """Transform identity property"""
        prop_name = str(items[0])
        prop_value = items[1]
        return {prop_name: prop_value}

    def memory_statement(self, items):
        """Transform memory operations"""
        memory_op = items[0]
        return ASTNode(
            type=ASTNodeType.MEMORY,
            value=memory_op,
            metadata={"operation": memory_op.get("action", "unknown")},
        )

    def memory_remember(self, items):
        """Transform remember operation"""
        content = str(items[0]).strip('"')
        modifiers = {}

        for item in items[1:]:
            if isinstance(item, dict):
                modifiers.update(item)

        return {"action": "remember", "content": content, **modifiers}

    def memory_recall(self, items):
        """Transform recall operation"""
        tag = str(items[0]).strip('"')
        modifiers = {}

        for item in items[1:]:
            if isinstance(item, dict):
                modifiers.update(item)

        return {"action": "recall", "tag": tag, **modifiers}

    def agent_statement(self, items):
        """Transform agent operations"""
        agent_op = items[0]
        return ASTNode(
            type=ASTNodeType.AGENT,
            value=agent_op,
            metadata={"operation": agent_op.get("action", "unknown")},
        )

    def agent_mode_set(self, items):
        """Transform agent mode setting"""
        mode = str(items[0]).strip('"')
        return {"action": "set_mode", "mode": mode}

    def agent_control(self, items):
        """Transform agent control commands"""
        action = str(items[0])
        return {"action": action}

    def agent_goal_management(self, items):
        """Transform agent goal management"""
        action = str(items[0])
        args = {}

        for item in items[1:]:
            if isinstance(item, dict):
                args.update(item)

        return {"action": action, **args}

    def function_definition(self, items):
        """Transform function definition"""
        func_name = str(items[0])
        params = items[1] if len(items) > 1 and isinstance(items[1], list) else []
        body = items[-1] if items else None

        return ASTNode(
            type=ASTNodeType.FUNCTION_DEF,
            value={"name": func_name, "parameters": params, "body": body},
            metadata={"param_count": len(params)},
        )

    def function_call(self, items):
        """Transform function call"""
        func_name = str(items[0])
        args = items[1] if len(items) > 1 and isinstance(items[1], list) else []

        return ASTNode(
            type=ASTNodeType.FUNCTION_CALL,
            value={"name": func_name, "arguments": args},
            metadata={"arg_count": len(args)},
        )

    def assignment(self, items):
        """Transform assignment"""
        var_name = str(items[0])
        var_value = items[1]

        return ASTNode(
            type=ASTNodeType.ASSIGNMENT, value={"variable": var_name, "value": var_value}
        )

    def intent_action(self, items):
        """Transform intent actions"""
        verb = str(items[0])
        target = items[1] if len(items) > 1 else None
        modifiers = {}

        for item in items[2:]:
            if isinstance(item, dict):
                modifiers.update(item)

        return ASTNode(
            type=ASTNodeType.INTENT_ACTION, value={"verb": verb, "target": target, **modifiers}
        )

    def when_statement(self, items):
        """Transform when statement"""
        condition = items[0]
        body = items[1] if len(items) > 1 else None

        return ASTNode(
            type=ASTNodeType.WHEN_STATEMENT, value={"condition": condition, "body": body}
        )

    def if_statement(self, items):
        """Transform if statement"""
        condition = items[0]
        if_body = items[1]
        else_body = items[2] if len(items) > 2 else None

        return ASTNode(
            type=ASTNodeType.CONDITIONAL,
            value={"condition": condition, "if_body": if_body, "else_body": else_body},
        )

    def block(self, items):
        """Transform code block"""
        return ASTNode(
            type=ASTNodeType.BLOCK, children=items, metadata={"statement_count": len(items)}
        )

    # Literal transformations
    def string_literal(self, items):
        return str(items[0]).strip("\"'")

    def number_literal(self, items):
        value = str(items[0])
        if "." in value:
            return float(value.rstrip("%"))
        return int(value.rstrip("%"))

    def boolean_literal(self, items):
        return str(items[0]) == "true"

    def list_literal(self, items):
        return list(items)

    def dict_literal(self, items):
        result = {}
        for i in range(0, len(items), 2):
            if i + 1 < len(items):
                key = items[i]
                value = items[i + 1]
                result[key] = value
        return result


class NeuroCodeModernParser:
    """Modern Lark-based parser for NeuroCode"""

    def __init__(self):
        """Initialize the modern parser"""
        self.grammar_file = Path(__file__).parent.parent / "docs" / "NEUROCODE_GRAMMAR.lark"
        self.parser = None
        self.transformer = NeuroCodeTransformer()

        if not LARK_AVAILABLE:
            raise ImportError(
                "Lark parser is required for modern parsing. Install with: pip install lark"
            )

        self._load_grammar()

    def _load_grammar(self):
        """Load the Lark grammar file"""
        try:
            if self.grammar_file.exists():
                with open(self.grammar_file, encoding="utf-8") as f:
                    grammar_content = f.read()
            else:
                # Fallback to embedded grammar
                grammar_content = self._get_embedded_grammar()

            self.parser = Lark(
                grammar_content, start="start", parser="lalr", transformer=self.transformer
            )

        except Exception as e:
            print(f"Warning: Could not load Lark grammar: {e}")
            print("Falling back to embedded grammar...")
            self.parser = Lark(
                self._get_embedded_grammar(),
                start="start",
                parser="lalr",
                transformer=self.transformer,
            )

    def _get_embedded_grammar(self) -> str:
        """Embedded minimal grammar for fallback"""
        return """
        start: statement_list
        
        statement_list: statement*
        
        statement: goal_statement
                 | assignment
                 | function_call
                 | intent_action
        
        goal_statement: "goal" ":" ESCAPED_STRING priority_clause?
        
        priority_clause: "priority" ":" priority_level
        priority_level: "critical" | "high" | "medium" | "low"
        
        assignment: IDENTIFIER "=" ESCAPED_STRING
        
        function_call: "run" IDENTIFIER "(" ")"
        
        intent_action: intent_verb intent_target?
        intent_verb: "think" | "analyze" | "optimize"
        intent_target: "about" ESCAPED_STRING
        
        %import common.ESCAPED_STRING
        %import common.CNAME -> IDENTIFIER
        %import common.WS
        %ignore WS
        """

    def parse(self, source_code: str) -> ASTNode:
        """Parse NeuroCode source into AST"""
        try:
            if not self.parser:
                raise RuntimeError("Parser not initialized")

            # Parse with Lark
            tree = self.parser.parse(source_code)

            # Transform to NeuroCode AST
            if isinstance(tree, ASTNode):
                return tree
            else:
                # Handle case where transformer wasn't applied
                return self.transformer.transform(tree)

        except (ParseError, LexError) as e:
            raise SyntaxError(f"NeuroCode syntax error: {e}")
        except Exception as e:
            raise RuntimeError(f"Parser error: {e}")

    def parse_file(self, file_path: Union[str, Path]) -> ASTNode:
        """Parse a NeuroCode file"""
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"NeuroCode file not found: {file_path}")

        with open(file_path, encoding="utf-8") as f:
            source_code = f.read()

        ast = self.parse(source_code)
        ast.metadata["source_file"] = str(file_path)

        return ast

    def validate_syntax(self, source_code: str) -> bool:
        """Validate NeuroCode syntax without execution"""
        try:
            self.parse(source_code)
            return True
        except (SyntaxError, RuntimeError):
            return False

    def get_syntax_errors(self, source_code: str) -> List[str]:
        """Get detailed syntax error information"""
        errors = []
        try:
            self.parse(source_code)
        except SyntaxError as e:
            errors.append(str(e))
        except RuntimeError as e:
            errors.append(str(e))

        return errors


def create_parser_migration_plan():
    """Create a plan for migrating from regex to modern parser"""
    return {
        "phase_1": {
            "description": "Install Lark dependency",
            "tasks": [
                "Add lark to requirements.txt",
                "Update setup.py dependencies",
                "Test Lark installation",
            ],
        },
        "phase_2": {
            "description": "Parallel parser implementation",
            "tasks": [
                "Implement NeuroCodeModernParser",
                "Create comprehensive test suite",
                "Add grammar validation tools",
            ],
        },
        "phase_3": {
            "description": "Integration and testing",
            "tasks": [
                "Add feature flag for parser selection",
                "Run regression tests with both parsers",
                "Performance comparison testing",
            ],
        },
        "phase_4": {
            "description": "Migration and cleanup",
            "tasks": [
                "Switch default to modern parser",
                "Deprecate regex parser",
                "Update documentation",
            ],
        },
    }


if __name__ == "__main__":
    # Example usage and testing
    if LARK_AVAILABLE:
        parser = NeuroCodeModernParser()

        test_code = """
        goal: "test the modern parser" priority: high
        
        identity {
            name: "TestBot"
            version: "1.0"
        }
        
        remember("parser test")
        think about "syntax trees"
        """

        try:
            ast = parser.parse(test_code)
            print("✅ Modern parser working correctly!")
            print(f"AST: {ast}")
        except Exception as e:
            print(f"❌ Parser error: {e}")
    else:
        print("❌ Lark not available. Install with: pip install lark")
        print("\nMigration plan:")
        plan = create_parser_migration_plan()
        for phase, details in plan.items():
            print(f"\n{phase.upper()}: {details['description']}")
            for task in details["tasks"]:
                print(f"  - {task}")
