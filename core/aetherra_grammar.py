#!/usr/bin/env python3
"""
🧬 NeuroCode Formal Grammar & Parser
==================================

A complete formal grammar definition for NeuroCode using Lark parser.
This transforms NeuroCode from a framework into a true programming language
with proper syntax, grammar rules, and AST generation.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List

from lark import Lark, Transformer
from lark.exceptions import LarkError

# NeuroCode Formal Grammar Definition - Corrected Structure
NEUROCODE_GRAMMAR = r"""
    ?start: program

    program: statement*

    ?statement: goal_statement
              | agent_statement
              | memory_statement
              | plugin_statement
              | function_definition
              | when_statement
              | if_statement
              | for_statement
              | while_statement
              | intent_action
              | assignment
              | expression_statement
              | model_statement
              | assistant_statement
              | comment
              | NEWLINE

    // Goal declarations
    goal_statement: "goal" ":" value priority_clause?
    priority_clause: "priority" ":" ("critical" | "high" | "medium" | "low")

    // Agent activation and tasks
    agent_statement: "agent" ":" ("on" | "off" | value)

    // LLM Model configuration
    model_statement: "model" ":" model_name model_config?
    model_name: STRING | IDENTIFIER
    model_config: "(" model_param ("," model_param)* ")"
    model_param: IDENTIFIER "=" value

    // AI Assistant tasks
    assistant_statement: "assistant" ":" assistant_task
    assistant_task: value

    // Memory operations
    memory_statement: remember_stmt
                   | recall_stmt
                   | forget_stmt
                   | memory_pattern_stmt

    remember_stmt: "remember" "(" value ")" "as" STRING
    recall_stmt: "recall" value ("with" STRING)?
    forget_stmt: "forget" value
    memory_pattern_stmt: "memory" "." "pattern" "(" value "," "frequency" "=" STRING ")"

    // Plugin integration
    plugin_statement: "plugin" ":" IDENTIFIER NEWLINE plugin_body "end"
    plugin_body: statement*

    // Function definitions
    function_definition: "define" IDENTIFIER "(" parameter_list? ")" ":" NEWLINE function_body "end"
    parameter_list: IDENTIFIER ("," IDENTIFIER)*
    function_body: statement*

    // Control flow
    when_statement: "when" condition ":" NEWLINE statement_block "end"
    if_statement: "if" condition ":" NEWLINE statement_block else_clause? "end"
    else_clause: "else" ":" NEWLINE statement_block
    for_statement: "for" for_target "in" value ":" NEWLINE statement_block "end"
    while_statement: "while" condition ":" NEWLINE statement_block "end"

    for_target: ("each")? IDENTIFIER
    statement_block: statement*

    // Intent-driven actions
    intent_action: action_verb (intent_modifier value)?
    action_verb: "analyze" | "optimize" | "learn" | "adapt" | "evolve" | "investigate"
               | "suggest" | "apply" | "monitor" | "predict" | "transcribe" | "summarize"
               | "refactor" | "self_edit" | "simulate"

    intent_modifier: "for" | "from" | "to" | "with" | "based_on"

    // Conditions
    condition: comparison | memory_condition | pattern_condition | value
    memory_condition: "memory" "." "pattern" "(" value "," "frequency" "=" STRING ")"
    pattern_condition: "contains" "(" value ")"
    comparison: value comparison_op value
    comparison_op: ">" | "<" | ">=" | "<=" | "==" | "!="

    // Values and expressions
    ?value: STRING | NUMBER | BOOLEAN | IDENTIFIER | method_call | arithmetic_expr | array_expr

    array_expr: "[" array_elements? "]"
    array_elements: value ("," value)*

    method_call: IDENTIFIER "." IDENTIFIER "(" argument_list? ")"
    argument_list: value ("," value)*
    arithmetic_expr: value ("+" | "-" | "*" | "/") value

    // Assignment
    assignment: IDENTIFIER "=" value

    // Expression statement
    expression_statement: value

    // Comments
    comment: COMMENT

    // Terminals
    STRING: /"[^"]*"/ | /'[^']*'/
    NUMBER: /\d+(\.\d+)?(%)?/
    BOOLEAN: "true" | "false"
    IDENTIFIER: /[a-zA-Z_][a-zA-Z0-9_]*/
    COMMENT: /#[^\r\n]*/

    %import common.WS
    %import common.NEWLINE
    %ignore WS
"""


@dataclass
class NeuroCodeAST:
    """NeuroCode Abstract Syntax Tree node"""

    type: str
    value: Any = None
    children: List["NeuroCodeAST"] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class NeuroCodeTransformer(Transformer):
    """Transforms parse tree into NeuroCode AST"""

    def program(self, statements):
        return NeuroCodeAST(
            type="program", children=[s for s in statements if s is not None]
        )

    # Goal statements
    def goal_statement(self, args):
        if not args:
            return NeuroCodeAST(type="goal", value="")
        value = self._extract_value(args[0])
        node = NeuroCodeAST(type="goal", value=value)
        if len(args) > 1:  # Has priority clause
            node.metadata["priority"] = str(args[1])
        return node

    def priority_clause(self, args):
        return str(args[0]) if args else "medium"

    # Agent statements
    def agent_statement(self, args):
        if not args:
            return NeuroCodeAST(type="agent", value="on")
        return NeuroCodeAST(type="agent", value=self._extract_value(args[0]))

    # LLM Model statements
    def model_statement(self, args):
        if not args:
            return NeuroCodeAST(type="model", value="gpt-3.5-turbo")

        model_name = self._extract_value(args[0])
        node = NeuroCodeAST(type="model", value=model_name)

        # Add configuration parameters if provided
        if len(args) > 1:
            config = args[1] if isinstance(args[1], dict) else {}
            node.metadata = {"config": config}

        return node

    def model_config(self, args):
        """Parse model configuration parameters"""
        config = {}
        for param in args:
            if hasattr(param, "children") and len(param.children) >= 2:
                key = str(param.children[0])
                value = self._extract_value(param.children[1])
                config[key] = value
        return config

    def model_param(self, args):
        """Parse individual model parameter"""
        if len(args) >= 2:
            return NeuroCodeAST(type="model_param", children=[args[0], args[1]])
        return NeuroCodeAST(type="model_param", value="")

    # AI Assistant statements
    def assistant_statement(self, args):
        if not args:
            return NeuroCodeAST(type="assistant", value="Help me with NeuroCode")

        task = self._extract_value(args[0])
        return NeuroCodeAST(type="assistant", value=task)

    def assistant_task(self, args):
        """Parse assistant task specification"""
        if not args:
            return "Help me with NeuroCode"
        return self._extract_value(args[0])

    # Memory operations
    def remember_stmt(self, args):
        if len(args) < 2:
            return NeuroCodeAST(type="remember", value="", metadata={"tag": ""})
        return NeuroCodeAST(
            type="remember",
            value=self._extract_value(args[0]),
            metadata={"tag": self._extract_value(args[1])},
        )

    def recall_stmt(self, args):
        node = NeuroCodeAST(type="recall", value=self._extract_value(args[0]))
        if len(args) > 1:
            node.metadata["with"] = self._extract_value(args[1])
        return node

    def forget_stmt(self, args):
        return NeuroCodeAST(type="forget", value=self._extract_value(args[0]))

    def memory_pattern_stmt(self, args):
        return NeuroCodeAST(
            type="memory_pattern",
            value=self._extract_value(args[0]),
            metadata={"frequency": self._extract_value(args[1])},
        )

    # Plugin statements
    def plugin_statement(self, args):
        plugin_name = str(args[0])
        plugin_body = args[1] if len(args) > 1 else []
        return NeuroCodeAST(
            type="plugin",
            value=plugin_name,
            children=plugin_body if isinstance(plugin_body, list) else [plugin_body],
        )

    def plugin_body(self, statements):
        return [s for s in statements if s is not None]

    # Function definitions
    def function_definition(self, args):
        func_name = str(args[0])
        params = args[1] if len(args) > 2 else []
        body = args[-1]
        return NeuroCodeAST(
            type="function",
            value=func_name,
            children=body if isinstance(body, list) else [body],
            metadata={"parameters": params},
        )

    def parameter_list(self, params):
        return [str(p) for p in params]

    def function_body(self, statements):
        return [s for s in statements if s is not None]

    # Control flow
    def when_statement(self, args):
        condition = self._extract_value(args[0])
        block = args[1]
        return NeuroCodeAST(
            type="when",
            value=condition,
            children=block if isinstance(block, list) else [block],
        )

    def if_statement(self, args):
        condition = self._extract_value(args[0])
        if_block = args[1]
        else_block = args[2] if len(args) > 2 else None

        children = if_block if isinstance(if_block, list) else [if_block]
        if else_block:
            children.append(
                NeuroCodeAST(
                    type="else_block",
                    children=else_block
                    if isinstance(else_block, list)
                    else [else_block],
                )
            )

        return NeuroCodeAST(type="if", value=condition, children=children)

    def else_clause(self, args):
        return args[0]

    def for_statement(self, args):
        target = str(args[0])
        iterable = self._extract_value(args[1])
        block = args[2]
        return NeuroCodeAST(
            type="for",
            value={"target": target, "iterable": iterable},
            children=block if isinstance(block, list) else [block],
        )

    def for_target(self, args):
        if len(args) == 1:
            return str(args[0])
        else:
            return f"each {args[1]}"

    def while_statement(self, args):
        condition = self._extract_value(args[0])
        block = args[1]
        return NeuroCodeAST(
            type="while",
            value=condition,
            children=block if isinstance(block, list) else [block],
        )

    def statement_block(self, statements):
        return [s for s in statements if s is not None]

    # Intent actions
    def intent_action(self, args):
        action = str(args[0])
        if len(args) > 1:
            modifier = str(args[1]) if args[1] else None
            target = self._extract_value(args[2]) if len(args) > 2 else None
            return NeuroCodeAST(
                type="intent",
                value=action,
                metadata={"modifier": modifier, "target": target},
            )
        return NeuroCodeAST(type="intent", value=action)

    def action_verb(self, args):
        return str(args[0])

    def intent_modifier(self, args):
        return str(args[0])

    # Conditions and comparisons
    def condition(self, args):
        return self._extract_value(args[0])

    def comparison(self, args):
        left = self._extract_value(args[0])
        op = str(args[1])
        right = self._extract_value(args[2])
        return NeuroCodeAST(
            type="comparison",
            value=op,
            children=[
                NeuroCodeAST(type="expression", value=left),
                NeuroCodeAST(type="expression", value=right),
            ],
        )

    def comparison_op(self, args):
        return str(args[0])

    def memory_condition(self, args):
        return NeuroCodeAST(
            type="memory_condition",
            value=self._extract_value(args[0]),
            metadata={"frequency": self._extract_value(args[1])},
        )

    def pattern_condition(self, args):
        return NeuroCodeAST(
            type="pattern_condition", value=self._extract_value(args[0])
        )

    # Method calls and expressions
    def method_call(self, args):
        obj = str(args[0])
        method = str(args[1])
        arguments = args[2] if len(args) > 2 else []
        return NeuroCodeAST(
            type="method_call",
            value=f"{obj}.{method}",
            children=arguments
            if isinstance(arguments, list)
            else [arguments]
            if arguments
            else [],
        )

    def argument_list(self, args):
        return [self._create_ast_from_value(arg) for arg in args]

    def arithmetic_expr(self, args):
        left = self._extract_value(args[0])
        op = str(args[1])
        right = self._extract_value(args[2])
        return NeuroCodeAST(
            type="arithmetic",
            value=op,
            children=[
                NeuroCodeAST(type="expression", value=left),
                NeuroCodeAST(type="expression", value=right),
            ],
        )

    def array_expr(self, args):
        elements = args[0] if args else []
        return NeuroCodeAST(
            type="array",
            children=elements
            if isinstance(elements, list)
            else [elements]
            if elements
            else [],
        )

    def array_elements(self, args):
        return [self._create_ast_from_value(arg) for arg in args]

    # Assignment
    def assignment(self, args):
        var = str(args[0])
        value = self._extract_value(args[1])
        return NeuroCodeAST(
            type="assignment", value=var, children=[self._create_ast_from_value(value)]
        )

    def expression_statement(self, args):
        return NeuroCodeAST(
            type="expression_statement", value=self._extract_value(args[0])
        )

    def comment(self, args):
        return NeuroCodeAST(type="comment", value=str(args[0]).strip("#").strip())

    # Helper methods
    def _extract_value(self, node):
        """Extract value from AST node or token"""
        if isinstance(node, NeuroCodeAST):
            return node.value
        # Remove quotes from strings
        node_str = str(node)
        if node_str.startswith('"') and node_str.endswith('"'):
            return node_str[1:-1]
        if node_str.startswith("'") and node_str.endswith("'"):
            return node_str[1:-1]
        return node_str

    def _create_ast_from_value(self, value):
        """Create AST node from a value"""
        if isinstance(value, NeuroCodeAST):
            return value
        return NeuroCodeAST(type="value", value=self._extract_value(value))


class AetherraParser:
    """Formal NeuroCode parser using Lark grammar"""

    def __init__(self):
        self.parser = Lark(
            NEUROCODE_GRAMMAR,
            parser="lalr",
            transformer=NeuroCodeTransformer(),
            start="program",
        )
        self.last_ast = None

    def parse(self, source_code: str) -> NeuroCodeAST:
        """
        Parse NeuroCode source into AST

        Args:
            source_code: Raw NeuroCode source

        Returns:
            NeuroCodeAST: Parsed abstract syntax tree

        Raises:
            NeuroCodeSyntaxError: On parsing errors
        """
        try:
            # Clean source code
            cleaned_source = self._preprocess_source(source_code)

            # Parse with Lark - transformer automatically converts to NeuroCodeAST
            ast = self.parser.parse(cleaned_source)
            self.last_ast = ast

            # Ensure we have a NeuroCodeAST
            if not isinstance(ast, NeuroCodeAST):
                raise NeuroCodeSyntaxError("Parser did not return NeuroCodeAST")

            return ast

        except LarkError as e:
            raise NeuroCodeSyntaxError(f"Syntax error: {e}") from e
        except Exception as e:
            raise NeuroCodeSyntaxError(f"Parse error: {e}") from e

    def _preprocess_source(self, source: str) -> str:
        """Clean and preprocess source code"""
        lines = source.split("\n")
        processed_lines = []

        for line in lines:
            # Strip leading/trailing whitespace
            line = line.strip()

            # Skip empty lines but preserve them for structure
            if not line:
                processed_lines.append("")
                continue

            # Ensure proper newlines for statements
            if not line.endswith("\n"):
                line += "\n"

            processed_lines.append(line)

        return "\n".join(processed_lines)

    def validate_syntax(self, source_code: str) -> Dict[str, Any]:
        """
        Validate NeuroCode syntax and return detailed results

        Returns:
            Dictionary with validation results
        """
        try:
            ast = self.parse(source_code)
            return {"valid": True, "ast": ast, "errors": [], "warnings": []}
        except NeuroCodeSyntaxError as e:
            return {"valid": False, "ast": None, "errors": [str(e)], "warnings": []}

    def get_ast_info(self) -> Dict[str, Any]:
        """Get information about the last parsed AST"""
        if not self.last_ast or not isinstance(self.last_ast, NeuroCodeAST):
            return {"ast": None, "stats": {}}

        stats = self._analyze_ast(self.last_ast)
        return {"ast": self.last_ast, "stats": stats}

    def _analyze_ast(self, ast: NeuroCodeAST) -> Dict[str, int]:
        """Analyze AST and return statistics"""
        stats = {
            "total_nodes": 0,
            "functions": 0,
            "goals": 0,
            "memory_operations": 0,
            "agent_statements": 0,
            "plugin_calls": 0,
        }

        def count_nodes(node):
            stats["total_nodes"] += 1

            if node.type == "function":
                stats["functions"] += 1
            elif node.type == "goal":
                stats["goals"] += 1
            elif node.type in ["remember", "recall", "forget", "reflect"]:
                stats["memory_operations"] += 1
            elif node.type == "agent":
                stats["agent_statements"] += 1
            elif node.type == "plugin":
                stats["plugin_calls"] += 1

            for child in node.children:
                count_nodes(child)

        count_nodes(ast)
        return stats


class NeuroCodeSyntaxError(Exception):
    """NeuroCode-specific syntax error"""

    pass


# Factory function for easy access
def create_neurocode_parser() -> AetherraParser:
    """Create a new NeuroCode parser instance"""
    return AetherraParser()


# Example usage and testing
if __name__ == "__main__":
    # Test the parser with comprehensive NeuroCode examples
    parser = create_neurocode_parser()

    # Test 1: Basic constructs
    basic_code = '''goal: "improve system performance"
agent: on
remember("API optimization completed") as "performance"
x = "test"'''

    # Test 2: Array syntax
    array_code = '''my_list = ["cpu", "memory", "disk"]
optimize for "performance"'''

    # Test 3: Comments and priorities
    priority_code = """# This is a comment
goal: "improve database speed" priority: high
agent: off"""

    test_cases = [
        ("Basic Constructs", basic_code),
        ("Array Syntax", array_code),
        ("Comments and Priorities", priority_code),
    ]

    for test_name, code in test_cases:
        print(f"\n🧬 Testing {test_name}:")
        print("=" * 50)
        try:
            result = parser.validate_syntax(code)
            if result["valid"]:
                print("✅ NeuroCode syntax is valid!")
                stats = parser.get_ast_info()["stats"]
                print(f"📊 AST Stats: {stats}")

                # Print AST structure for first test
                if test_name == "Basic Constructs":
                    ast = result["ast"]
                    print(
                        f"🌳 AST Structure: {ast.type} with {len(ast.children)} children"
                    )
                    for i, child in enumerate(
                        ast.children[:3]
                    ):  # Show first 3 children
                        print(f"   Child {i + 1}: {child.type} = {child.value}")
            else:
                print("❌ Syntax errors found:")
                for error in result["errors"]:
                    print(f"   {error}")
        except Exception as e:
            print(f"🔥 Parser error: {e}")

    print("\n🎉 NeuroCode is now a syntax-native programming language!")
    print("🚀 Ready for .aether file execution and full language implementation!")
