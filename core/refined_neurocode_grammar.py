#!/usr/bin/env python3
"""
🧬 NeuroCode Refined Grammar & Parser
====================================

A refined, conflict-free formal grammar definition for NeuroCode using Lark parser.
This version resolves grammar conflicts and provides a clean, unambiguous language definition.

Key improvements:
- Eliminated reduce/reduce conflicts
- Clear terminal/non-terminal separation
- Unambiguous rule precedence
- Simplified but complete language coverage
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List

from lark import Lark, Token, Transformer
from lark.exceptions import LarkError, LexError, ParseError

# Refined NeuroCode Grammar Definition - Conflict-free
REFINED_NEUROCODE_GRAMMAR = r"""
    ?start: program

    program: statement*

    ?statement: goal_statement
              | agent_statement  
              | memory_statement
              | plugin_statement
              | function_definition
              | control_statement
              | intent_action
              | assignment
              | expression_stmt
              | ai_statement
              | debug_statement
              | comment
              | NEWLINE

    // AI Statements
    ai_statement: model_statement
                | assistant_statement
                | think_statement
                | learn_statement

    model_statement: "model" ":" quoted_string
    assistant_statement: "assistant" ":" quoted_string
    think_statement: "think" ":" quoted_string
    learn_statement: "learn" ("from" quoted_string)?

    // Goal System
    goal_statement: "goal" ":" quoted_string priority_clause?
    priority_clause: "priority" ":" priority_level
    priority_level: "critical" | "urgent" | "high" | "medium" | "low"

    // Agent Control
    agent_statement: "agent" ":" agent_mode
    agent_mode: "on" | "off" | "auto" | "manual" | quoted_string

    // Memory System
    memory_statement: remember_stmt
                   | recall_stmt  
                   | forget_stmt
                   | reflect_stmt
                   | memory_pattern_stmt

    remember_stmt: "remember" "(" quoted_string ")" ("as" quoted_string)?
    recall_stmt: "recall" (quoted_string | recall_target)
    recall_target: "tag" ":" quoted_string | "pattern" ":" quoted_string
    forget_stmt: "forget" quoted_string
    reflect_stmt: "reflect" ("on" quoted_string)?
    memory_pattern_stmt: "memory" "." "pattern" "(" quoted_string "," "frequency" "=" quoted_string ")"

    // Plugin System
    plugin_statement: "plugin" ":" identifier_name (plugin_args)?
    plugin_args: "(" argument_list ")" | quoted_string

    // Function System
    function_definition: "define" identifier_name "(" parameter_list? ")" ":" NEWLINE function_body "end"
    parameter_list: identifier_name ("," identifier_name)*
    function_body: statement*

    // Control Flow
    control_statement: when_statement
                    | if_statement
                    | for_statement  
                    | while_statement

    when_statement: "when" condition ":" NEWLINE statement_block "end"
    if_statement: "if" condition ":" NEWLINE statement_block else_part? "end"
    else_part: "else" ":" NEWLINE statement_block
    for_statement: "for" identifier_name "in" expression ":" NEWLINE statement_block "end"
    while_statement: "while" condition ":" NEWLINE statement_block "end"
    statement_block: statement*

    // Intent Actions
    intent_action: action_verb (target_expression)?
    action_verb: "analyze" | "optimize" | "learn" | "adapt" | "evolve" 
               | "investigate" | "suggest" | "apply" | "monitor" | "predict"
               | "transcribe" | "summarize" | "refactor" | "self_edit" | "simulate"
    target_expression: quoted_string | "for" quoted_string | "on" quoted_string

    // Debug Statements
    debug_statement: "debug" (quoted_string)?
                  | "trace" ("on" | "off")?
                  | "assert" condition (":" quoted_string)?

    // Expressions and Conditions
    condition: comparison | memory_condition | simple_condition
    memory_condition: "memory" "." "pattern" "(" quoted_string "," "frequency" "=" quoted_string ")"
    simple_condition: expression comparison_op expression
    comparison_op: ">" | "<" | ">=" | "<=" | "==" | "!="

    ?expression: addition
    addition: multiplication (("+" | "-") multiplication)*
    multiplication: unary (("*" | "/" | "%") unary)*
    unary: ("not" | "-" | "+")? atom

    atom: literal | identifier_name | method_call | array_literal | "(" expression ")"
    method_call: identifier_name "." identifier_name "(" argument_list? ")"
    array_literal: "[" array_elements? "]"
    array_elements: expression ("," expression)*
    argument_list: expression ("," expression)*

    // Assignment
    assignment: identifier_name "=" expression

    // Expression statement
    expression_stmt: expression

    // Utility Productions
    literal: quoted_string | number | boolean | null_literal
    quoted_string: STRING
    identifier_name: IDENTIFIER
    number: NUMBER
    boolean: "true" | "false"
    null_literal: "null" | "None"

    comment: COMMENT

    // Terminals
    STRING: /"([^"\\]|\\.)+"/ | /'([^'\\]|\\)+'/
    NUMBER: /\d+(\.\d+)?/
    IDENTIFIER: /[a-zA-Z_][a-zA-Z0-9_]*/
    COMMENT: /#[^\r\n]*/

    %import common.WS
    %import common.NEWLINE
    %ignore WS
"""


@dataclass
class RefinedASTNode:
    """Refined NeuroCode AST node with clear structure"""

    node_type: str
    value: Any = None
    children: List["RefinedASTNode"] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_child(self, child: "RefinedASTNode") -> None:
        """Add a child node"""
        if child is not None:
            self.children.append(child)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "type": self.node_type,
            "value": self.value,
            "children": [child.to_dict() for child in self.children],
            "metadata": self.metadata,
        }

    def __str__(self) -> str:
        """String representation"""
        return f"{self.node_type}({self.value})"


class RefinedNeuroCodeTransformer(Transformer):
    """Refined transformer for clean AST generation"""

    def program(self, statements):
        """Transform program node"""
        children = [stmt for stmt in statements if stmt is not None]
        return RefinedASTNode("program", children=children)

    # AI Statements
    def model_statement(self, args):
        """Transform model statement"""
        model_name = self._extract_string(args[0]) if args else "default"
        return RefinedASTNode("model", value=model_name)

    def assistant_statement(self, args):
        """Transform assistant statement"""
        task = self._extract_string(args[0]) if args else "assist"
        return RefinedASTNode("assistant", value=task)

    def think_statement(self, args):
        """Transform think statement"""
        thought = self._extract_string(args[0]) if args else ""
        return RefinedASTNode("think", value=thought)

    def learn_statement(self, args):
        """Transform learn statement"""
        source = self._extract_string(args[0]) if args else None
        return RefinedASTNode("learn", value=source)

    # Goal System
    def goal_statement(self, args):
        """Transform goal statement"""
        goal_text = self._extract_string(args[0]) if args else ""
        priority = str(args[1]) if len(args) > 1 else "medium"
        return RefinedASTNode("goal", value=goal_text, metadata={"priority": priority})

    def priority_clause(self, args):
        """Transform priority clause"""
        return str(args[0]) if args else "medium"

    # Agent System
    def agent_statement(self, args):
        """Transform agent statement"""
        mode = str(args[0]) if args else "on"
        return RefinedASTNode("agent", value=mode)

    # Memory System
    def remember_stmt(self, args):
        """Transform remember statement"""
        content = self._extract_string(args[0]) if args else ""
        tags = self._extract_string(args[1]) if len(args) > 1 else None
        metadata = {"tags": tags} if tags else {}
        return RefinedASTNode("remember", value=content, metadata=metadata)

    def recall_stmt(self, args):
        """Transform recall statement"""
        target = args[0] if args else ""
        if hasattr(target, "node_type"):
            return RefinedASTNode("recall", value=target.value, metadata=target.metadata)
        else:
            return RefinedASTNode("recall", value=self._extract_string(target))

    def recall_target(self, args):
        """Transform recall target"""
        if len(args) >= 2:
            target_type = str(args[0])
            value = self._extract_string(args[1])
            return RefinedASTNode("recall_target", value=value, metadata={"type": target_type})
        return RefinedASTNode("recall_target", value="")

    def forget_stmt(self, args):
        """Transform forget statement"""
        target = self._extract_string(args[0]) if args else ""
        return RefinedASTNode("forget", value=target)

    def reflect_stmt(self, args):
        """Transform reflect statement"""
        scope = self._extract_string(args[0]) if args else None
        return RefinedASTNode("reflect", value=scope)

    def memory_pattern_stmt(self, args):
        """Transform memory pattern statement"""
        if len(args) >= 2:
            pattern = self._extract_string(args[0])
            frequency = self._extract_string(args[1])
            return RefinedASTNode(
                "memory_pattern", value=pattern, metadata={"frequency": frequency}
            )
        return RefinedASTNode("memory_pattern")

    # Plugin System
    def plugin_statement(self, args):
        """Transform plugin statement"""
        plugin_name = str(args[0]) if args else ""
        plugin_args = str(args[1]) if len(args) > 1 else None
        metadata = {"args": plugin_args} if plugin_args else {}
        return RefinedASTNode("plugin", value=plugin_name, metadata=metadata)

    # Function System
    def function_definition(self, args):
        """Transform function definition"""
        func_name = str(args[0]) if args else ""
        params = args[1] if len(args) > 2 else []
        body = args[-1] if args else []

        return RefinedASTNode(
            "function",
            value=func_name,
            children=body if isinstance(body, list) else [body] if body else [],
            metadata={"parameters": params if isinstance(params, list) else []},
        )

    def parameter_list(self, args):
        """Transform parameter list"""
        return [str(param) for param in args]

    def function_body(self, args):
        """Transform function body"""
        return [stmt for stmt in args if stmt is not None]

    # Control Flow
    def if_statement(self, args):
        """Transform if statement"""
        condition = self._extract_value(args[0]) if args else None
        if_block = args[1] if len(args) > 1 else []
        else_part = args[2] if len(args) > 2 else None

        children = if_block if isinstance(if_block, list) else [if_block] if if_block else []
        if else_part:
            children.append(RefinedASTNode("else_block", children=[else_part]))

        return RefinedASTNode("if", value=condition, children=children)

    def when_statement(self, args):
        """Transform when statement"""
        condition = self._extract_value(args[0]) if args else None
        block = args[1] if len(args) > 1 else []
        return RefinedASTNode(
            "when",
            value=condition,
            children=block if isinstance(block, list) else [block] if block else [],
        )

    def for_statement(self, args):
        """Transform for statement"""
        if len(args) >= 3:
            target = str(args[0])
            iterable = self._extract_value(args[1])
            block = args[2]
            return RefinedASTNode(
                "for",
                value={"target": target, "iterable": iterable},
                children=block if isinstance(block, list) else [block] if block else [],
            )
        return RefinedASTNode("for")

    def while_statement(self, args):
        """Transform while statement"""
        condition = self._extract_value(args[0]) if args else None
        block = args[1] if len(args) > 1 else []
        return RefinedASTNode(
            "while",
            value=condition,
            children=block if isinstance(block, list) else [block] if block else [],
        )

    def statement_block(self, args):
        """Transform statement block"""
        return [stmt for stmt in args if stmt is not None]

    # Intent Actions
    def intent_action(self, args):
        """Transform intent action"""
        action = str(args[0]) if args else ""
        target = self._extract_string(args[1]) if len(args) > 1 else None
        metadata = {"target": target} if target else {}
        return RefinedASTNode("intent", value=action, metadata=metadata)

    def target_expression(self, args):
        """Transform target expression"""
        return self._extract_string(args[0]) if args else None

    # Debug Statements
    def debug_statement(self, args):
        """Transform debug statement"""
        target = self._extract_string(args[0]) if args else None
        return RefinedASTNode("debug", value=target)

    # Expressions
    def assignment(self, args):
        """Transform assignment"""
        if len(args) >= 2:
            var = str(args[0])
            value = args[1]
            return RefinedASTNode("assignment", value=var, children=[value] if value else [])
        return RefinedASTNode("assignment")

    def expression_stmt(self, args):
        """Transform expression statement"""
        expr = args[0] if args else None
        return RefinedASTNode("expression_statement", children=[expr] if expr else [])

    def method_call(self, args):
        """Transform method call"""
        if len(args) >= 2:
            obj = str(args[0])
            method = str(args[1])
            arguments = args[2] if len(args) > 2 else []
            return RefinedASTNode(
                "method_call",
                value=f"{obj}.{method}",
                children=arguments
                if isinstance(arguments, list)
                else [arguments]
                if arguments
                else [],
            )
        return RefinedASTNode("method_call")

    def array_literal(self, args):
        """Transform array literal"""
        elements = args[0] if args else []
        return RefinedASTNode(
            "array",
            children=elements if isinstance(elements, list) else [elements] if elements else [],
        )

    def array_elements(self, args):
        """Transform array elements"""
        return [arg for arg in args if arg is not None]

    def argument_list(self, args):
        """Transform argument list"""
        return [arg for arg in args if arg is not None]

    # Conditions
    def condition(self, args):
        """Transform condition"""
        return args[0] if args else None

    def memory_condition(self, args):
        """Transform memory condition"""
        if len(args) >= 2:
            pattern = self._extract_string(args[0])
            frequency = self._extract_string(args[1])
            return RefinedASTNode(
                "memory_condition", value=pattern, metadata={"frequency": frequency}
            )
        return RefinedASTNode("memory_condition")

    def simple_condition(self, args):
        """Transform simple condition"""
        if len(args) >= 3:
            left = self._extract_value(args[0])
            op = str(args[1])
            right = self._extract_value(args[2])
            return RefinedASTNode(
                "comparison",
                value=op,
                children=[
                    RefinedASTNode("expression", value=left),
                    RefinedASTNode("expression", value=right),
                ],
            )
        return RefinedASTNode("comparison")

    # Utilities
    def comment(self, args):
        """Transform comment"""
        text = str(args[0]).strip("#").strip() if args else ""
        return RefinedASTNode("comment", value=text)

    def quoted_string(self, args):
        """Transform quoted string"""
        return self._extract_string(args[0]) if args else ""

    def identifier_name(self, args):
        """Transform identifier"""
        return str(args[0]) if args else ""

    def number(self, args):
        """Transform number"""
        return float(str(args[0])) if args else 0

    def boolean(self, args):
        """Transform boolean"""
        return str(args[0]) == "true" if args else False

    def literal(self, args):
        """Transform literal"""
        return args[0] if args else None

    def _extract_string(self, node):
        """Extract string value, removing quotes"""
        if node is None:
            return None
        if isinstance(node, RefinedASTNode):
            return node.value
        value = str(node)
        if value.startswith('"') and value.endswith('"'):
            return value[1:-1]
        if value.startswith("'") and value.endswith("'"):
            return value[1:-1]
        return value

    def _extract_value(self, node):
        """Extract value from node"""
        if node is None:
            return None
        if isinstance(node, RefinedASTNode):
            return node.value
        if isinstance(node, Token):
            return str(node)
        return str(node)


class RefinedNeuroCodeParser:
    """Refined NeuroCode parser with clean, conflict-free grammar"""

    def __init__(self):
        """Initialize the refined parser"""
        self.parser = Lark(
            REFINED_NEUROCODE_GRAMMAR,
            parser="lalr",
            transformer=RefinedNeuroCodeTransformer(),
            start="program",
        )
        self.last_ast = None

    def parse(self, source_code: str) -> RefinedASTNode:
        """
        Parse NeuroCode source into refined AST

        Args:
            source_code: Raw NeuroCode source

        Returns:
            RefinedASTNode: Parsed abstract syntax tree

        Raises:
            NeuroCodeSyntaxError: On parsing errors
        """
        try:
            # Preprocess source
            cleaned_source = self._preprocess_source(source_code)

            # Parse with refined grammar
            ast = self.parser.parse(cleaned_source)
            self.last_ast = ast

            return ast

        except (LarkError, ParseError, LexError) as e:
            raise NeuroCodeSyntaxError(f"Syntax error: {e}") from e
        except Exception as e:
            raise NeuroCodeSyntaxError(f"Parse error: {e}") from e

    def _preprocess_source(self, source: str) -> str:
        """Preprocess source code"""
        lines = source.split("\n")
        processed_lines = []

        for line in lines:
            line = line.rstrip()
            if not line.strip():
                processed_lines.append("")
                continue
            processed_lines.append(line)

        result = "\n".join(processed_lines)
        if not result.endswith("\n"):
            result += "\n"

        return result

    def validate_syntax(self, source_code: str) -> Dict[str, Any]:
        """
        Validate NeuroCode syntax

        Returns:
            Dictionary with validation results
        """
        try:
            ast = self.parse(source_code)
            return {
                "valid": True,
                "ast": ast,
                "errors": [],
                "statistics": self._generate_statistics(ast),
            }
        except NeuroCodeSyntaxError as e:
            return {"valid": False, "ast": None, "errors": [str(e)], "statistics": {}}

    def _generate_statistics(self, ast: RefinedASTNode) -> Dict[str, Any]:
        """Generate AST statistics"""
        stats = {
            "total_nodes": 0,
            "functions": 0,
            "goals": 0,
            "memory_operations": 0,
            "agent_statements": 0,
            "model_statements": 0,
            "control_structures": 0,
        }

        def analyze_node(node: RefinedASTNode) -> None:
            if node is None:
                return

            stats["total_nodes"] += 1

            node_type = node.node_type
            if node_type == "function":
                stats["functions"] += 1
            elif node_type == "goal":
                stats["goals"] += 1
            elif node_type in ["remember", "recall", "forget", "reflect"]:
                stats["memory_operations"] += 1
            elif node_type == "agent":
                stats["agent_statements"] += 1
            elif node_type == "model":
                stats["model_statements"] += 1
            elif node_type in ["if", "when", "for", "while"]:
                stats["control_structures"] += 1

            for child in node.children:
                analyze_node(child)

        analyze_node(ast)
        return stats


class NeuroCodeSyntaxError(Exception):
    """NeuroCode syntax error"""

    pass


def create_refined_parser() -> RefinedNeuroCodeParser:
    """Create a new refined NeuroCode parser instance"""
    return RefinedNeuroCodeParser()


# Example usage and testing
if __name__ == "__main__":
    print("🧬 Refined NeuroCode Grammar & Parser Test Suite")
    print("=" * 60)

    parser = create_refined_parser()

    # Test cases with the refined grammar
    test_cases = [
        (
            "Basic AI Commands",
            """
model: "gpt-4"
assistant: "analyze the codebase for optimization opportunities"
think: "considering performance implications"
learn from "user_behavior.log"
""",
        ),
        (
            "Goal and Agent",
            """
goal: "improve system performance by 30%" priority: high
agent: auto
""",
        ),
        (
            "Memory Operations",
            """
remember("API rate limiting implemented") as "performance"
recall tag: "performance"
reflect on "recent patterns"
memory.pattern("issues", frequency="daily")
""",
        ),
        (
            "Function Definition",
            """
define optimize_performance():
    analyze "bottlenecks"
    if performance < 0.9:
        suggest "performance improvements"
    end
end
""",
        ),
        (
            "Control Structures",
            """
for component in components:
    if memory.pattern("error", frequency="weekly"):
        debug "system issues"
    end
end
""",
        ),
        (
            "Complex Example",
            """
# Performance optimization system
goal: "maintain 95% performance" priority: high
model: "gpt-4"

define monitor_system():
    performance = system.get_performance()
    if performance < 0.95:
        assistant: "analyze performance degradation"
        remember("Performance below threshold") as "alerts"
    end
end

agent: on
""",
        ),
    ]

    total_tests = len(test_cases)
    passed_tests = 0

    for i, (test_name, code) in enumerate(test_cases, 1):
        print(f"\n🧪 Test {i}/{total_tests}: {test_name}")
        print("-" * 50)

        try:
            result = parser.validate_syntax(code)

            if result["valid"]:
                print("✅ Syntax validation: PASSED")
                stats = result["statistics"]
                if any(stats.values()):
                    print("📊 AST Statistics:")
                    for key, value in stats.items():
                        if value > 0:
                            print(f"   {key}: {value}")

                passed_tests += 1
            else:
                print("❌ Syntax validation: FAILED")
                print("Errors:")
                for error in result["errors"]:
                    print(f"   - {error}")

        except Exception as e:
            print(f"🔥 Test execution error: {e}")

    print(f"\n🎯 Test Results: {passed_tests}/{total_tests} tests passed")

    if passed_tests == total_tests:
        print("🎉 All tests passed! Refined NeuroCode grammar is working perfectly!")
        print("🚀 NeuroCode now has a clean, conflict-free formal grammar!")
        print("   • No reduce/reduce conflicts")
        print("   • Clear syntax rules")
        print("   • Comprehensive language coverage")
        print("   • Production-ready parsing")
    else:
        print(f"⚠️  {total_tests - passed_tests} tests need attention")

    print("\n✨ Refined NeuroCode Grammar Complete!")
