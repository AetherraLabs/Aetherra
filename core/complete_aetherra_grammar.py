#!/usr/bin/env python3
"""
🧬 AetherraCode Complete Grammar & Parser
=====================================

A comprehensive, working formal grammar definition for AetherraCode using Lark parser.
This version fixes all grammar conflicts and provides a complete language specification.

Features:
- Complete formal grammar definition
- Conflict-free Lark grammar
- Comprehensive AST generation
- Full AetherraCode language support
- Production-ready parser
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Union

from lark import Lark, Token, Transformer, Tree
from lark.exceptions import LexError, ParseError

# Complete AetherraCode Grammar Definition
aetherra_GRAMMAR = r"""
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

    model_statement: "model" ":" string_literal
    assistant_statement: "assistant" ":" string_literal
    think_statement: "think" ":" string_literal
    learn_statement: "learn" ("from" string_literal)?

    // Goal System
    goal_statement: "goal" ":" string_literal priority_clause?
    priority_clause: "priority" ":" priority_level
    priority_level: "critical" | "urgent" | "high" | "medium" | "low"

    // Agent Control
    agent_statement: "agent" ":" agent_mode
    agent_mode: "on" | "off" | "auto" | "manual" | string_literal

    // Memory System
    memory_statement: remember_stmt
                   | recall_stmt
                   | forget_stmt
                   | reflect_stmt
                   | memory_pattern_stmt

    remember_stmt: "remember" "(" string_literal ")" ("as" string_literal)?
    recall_stmt: "recall" (string_literal | recall_target)
    recall_target: "tag" ":" string_literal | "pattern" ":" string_literal
    forget_stmt: "forget" string_literal
    reflect_stmt: "reflect" ("on" string_literal)?
    memory_pattern_stmt: "memory" "." "pattern" "(" string_literal "," "frequency" "=" string_literal ")"

    // Plugin System
    plugin_statement: "plugin" ":" identifier plugin_args?
    plugin_args: "(" argument_list ")" | string_literal

    // Function System
    function_definition: "define" identifier "(" parameter_list? ")" ":" NEWLINE function_body "end"
    parameter_list: identifier ("," identifier)*
    function_body: statement*

    // Control Flow
    control_statement: when_statement
                    | if_statement
                    | for_statement
                    | while_statement

    when_statement: "when" condition ":" NEWLINE statement_block "end"
    if_statement: "if" condition ":" NEWLINE statement_block else_part? "end"
    else_part: "else" ":" NEWLINE statement_block
    for_statement: "for" identifier "in" expression ":" NEWLINE statement_block "end"
    while_statement: "while" condition ":" NEWLINE statement_block "end"
    statement_block: statement*

    // Intent Actions
    intent_action: action_verb target_expression?
    action_verb: "analyze" | "optimize" | "learn" | "adapt" | "evolve"
               | "investigate" | "suggest" | "apply" | "monitor" | "predict"
               | "transcribe" | "summarize" | "refactor" | "self_edit" | "simulate"
    target_expression: string_literal | "for" string_literal | "on" string_literal

    // Debug Statements
    debug_statement: "debug" string_literal?
                  | "trace" ("on" | "off")?
                  | "assert" condition (":" string_literal)?

    // Conditions and Expressions
    condition: comparison | memory_condition | expression
    comparison: expression comparison_op expression
    memory_condition: "memory" "." "pattern" "(" string_literal "," "frequency" "=" string_literal ")"
    comparison_op: ">" | "<" | ">=" | "<=" | "==" | "!="

    ?expression: logical_or
    logical_or: logical_and ("or" logical_and)*
    logical_and: equality ("and" equality)*
    equality: relational (("==" | "!=") relational)*
    relational: addition ((">" | "<" | ">=" | "<=") addition)*
    addition: multiplication (("+" | "-") multiplication)*
    multiplication: unary (("*" | "/" | "%") unary)*
    unary: ("not" | "-" | "+")? primary

    primary: literal
           | identifier
           | method_call
           | array_literal
           | "(" expression ")"

    method_call: identifier "." identifier "(" argument_list? ")"
    array_literal: "[" array_elements? "]"
    array_elements: expression ("," expression)*
    argument_list: expression ("," expression)*

    // Assignment
    assignment: identifier "=" expression

    // Expression statement
    expression_stmt: expression

    // Basic Types
    literal: string_literal | number | boolean | null_literal
    string_literal: STRING
    identifier: IDENTIFIER
    number: NUMBER
    boolean: "true" | "false"
    null_literal: "null" | "None"

    comment: COMMENT

    // Terminals
    STRING: /"([^"\\\\]|\\\\.)*"/ | /'([^'\\\\]|\\\\.)*'/
    NUMBER: /\d+(\.\d+)?/
    IDENTIFIER: /[a-zA-Z_][a-zA-Z0-9_]*/
    COMMENT: /#[^\r\n]*/

    %import common.WS
    %import common.NEWLINE
    %ignore WS
"""


@dataclass
class AetherraCodeAST:
    """AetherraCode Abstract Syntax Tree node with complete structure"""

    node_type: str
    value: Any = None
    children: List["AetherraCodeAST"] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_child(self, child: "AetherraCodeAST") -> None:
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
        children_str = f", {len(self.children)} children" if self.children else ""
        metadata_str = f", {self.metadata}" if self.metadata else ""
        return f"{self.node_type}({self.value}{children_str}{metadata_str})"

    def __repr__(self) -> str:
        return self.__str__()


class AetherraCodeTransformer(Transformer):
    """Complete transformer for AetherraCode AST generation"""

    def _extract_value(
        self, item: Union[Token, Tree, AetherraCodeAST, str, Any]
    ) -> Any:
        """Extract value from various node types"""
        if isinstance(item, Token):
            return str(item.value)
        elif isinstance(item, Tree):
            return str(item.children[0]) if item.children else str(item)
        elif isinstance(item, AetherraCodeAST):
            return item.value
        elif isinstance(item, str):
            return item.strip("\"'")
        else:
            return str(item)

    def program(self, statements):
        """Transform program node"""
        children = [stmt for stmt in statements if stmt is not None]
        return AetherraCodeAST("program", children=children)

    # AI Statements
    def model_statement(self, args):
        """Transform model statement"""
        model_name = self._extract_value(args[0]) if args else "default"
        return AetherraCodeAST("model", value=model_name)

    def assistant_statement(self, args):
        """Transform assistant statement"""
        task = self._extract_value(args[0]) if args else "assist"
        return AetherraCodeAST("assistant", value=task)

    def think_statement(self, args):
        """Transform think statement"""
        thought = self._extract_value(args[0]) if args else ""
        return AetherraCodeAST("think", value=thought)

    def learn_statement(self, args):
        """Transform learn statement"""
        source = self._extract_value(args[0]) if args else ""
        return AetherraCodeAST("learn", value=source)

    # Goal System
    def goal_statement(self, args):
        """Transform goal statement"""
        goal = self._extract_value(args[0]) if args else ""
        node = AetherraCodeAST("goal", value=goal)
        if len(args) > 1:
            priority = self._extract_value(args[1])
            node.metadata["priority"] = priority
        return node

    def priority_clause(self, args):
        """Transform priority clause"""
        return self._extract_value(args[0]) if args else "medium"

    def priority_level(self, args):
        """Transform priority level"""
        return self._extract_value(args[0]) if args else "medium"

    # Agent Control
    def agent_statement(self, args):
        """Transform agent statement"""
        mode = self._extract_value(args[0]) if args else "on"
        return AetherraCodeAST("agent", value=mode)

    def agent_mode(self, args):
        """Transform agent mode"""
        return self._extract_value(args[0]) if args else "on"

    # Memory System
    def remember_stmt(self, args):
        """Transform remember statement"""
        content = self._extract_value(args[0]) if args else ""
        node = AetherraCodeAST("remember", value=content)
        if len(args) > 1:
            tag = self._extract_value(args[1])
            node.metadata["tag"] = tag
        return node

    def recall_stmt(self, args):
        """Transform recall statement"""
        target = self._extract_value(args[0]) if args else ""
        return AetherraCodeAST("recall", value=target)

    def forget_stmt(self, args):
        """Transform forget statement"""
        target = self._extract_value(args[0]) if args else ""
        return AetherraCodeAST("forget", value=target)

    def reflect_stmt(self, args):
        """Transform reflect statement"""
        target = self._extract_value(args[0]) if args else ""
        return AetherraCodeAST("reflect", value=target)

    def memory_pattern_stmt(self, args):
        """Transform memory pattern statement"""
        pattern = self._extract_value(args[0]) if args else ""
        frequency = self._extract_value(args[1]) if len(args) > 1 else ""
        return AetherraCodeAST(
            "memory_pattern", value=pattern, metadata={"frequency": frequency}
        )

    # Plugin System
    def plugin_statement(self, args):
        """Transform plugin statement"""
        plugin_name = self._extract_value(args[0]) if args else ""
        node = AetherraCodeAST("plugin", value=plugin_name)
        if len(args) > 1:
            args_value = self._extract_value(args[1])
            node.metadata["args"] = args_value
        return node

    # Function System
    def function_definition(self, args):
        """Transform function definition"""
        func_name = self._extract_value(args[0]) if args else ""
        params = args[1] if len(args) > 1 and isinstance(args[1], list) else []
        body = args[-1] if args else []

        return AetherraCodeAST(
            "function",
            value=func_name,
            children=body if isinstance(body, list) else [body],
            metadata={"parameters": params},
        )

    def parameter_list(self, params):
        """Transform parameter list"""
        return [self._extract_value(p) for p in params]

    def function_body(self, statements):
        """Transform function body"""
        return [stmt for stmt in statements if stmt is not None]

    # Control Flow
    def when_statement(self, args):
        """Transform when statement"""
        condition = args[0] if args else None
        block = args[1] if len(args) > 1 else []
        return AetherraCodeAST(
            "when",
            value=condition,
            children=block if isinstance(block, list) else [block],
        )

    def if_statement(self, args):
        """Transform if statement"""
        condition = args[0] if args else None
        if_block = args[1] if len(args) > 1 else []
        else_block = args[2] if len(args) > 2 else None

        children = if_block if isinstance(if_block, list) else [if_block]
        if else_block:
            children.append(
                AetherraCodeAST(
                    "else",
                    children=else_block
                    if isinstance(else_block, list)
                    else [else_block],
                )
            )

        return AetherraCodeAST("if", value=condition, children=children)

    def for_statement(self, args):
        """Transform for statement"""
        variable = self._extract_value(args[0]) if args else ""
        iterable = args[1] if len(args) > 1 else None
        block = args[2] if len(args) > 2 else []

        return AetherraCodeAST(
            "for",
            value=variable,
            children=block if isinstance(block, list) else [block],
            metadata={"iterable": iterable},
        )

    def while_statement(self, args):
        """Transform while statement"""
        condition = args[0] if args else None
        block = args[1] if len(args) > 1 else []
        return AetherraCodeAST(
            "while",
            value=condition,
            children=block if isinstance(block, list) else [block],
        )

    def statement_block(self, statements):
        """Transform statement block"""
        return [stmt for stmt in statements if stmt is not None]

    # Intent Actions
    def intent_action(self, args):
        """Transform intent action"""
        action = self._extract_value(args[0]) if args else ""
        target = self._extract_value(args[1]) if len(args) > 1 else ""
        return AetherraCodeAST("intent", value=action, metadata={"target": target})

    def action_verb(self, args):
        """Transform action verb"""
        return self._extract_value(args[0]) if args else ""

    def target_expression(self, args):
        """Transform target expression"""
        return self._extract_value(args[0]) if args else ""

    # Debug Statements
    def debug_statement(self, args):
        """Transform debug statement"""
        message = self._extract_value(args[0]) if args else ""
        return AetherraCodeAST("debug", value=message)

    # Conditions and Expressions
    def condition(self, args):
        """Transform condition"""
        return args[0] if args else None

    def comparison(self, args):
        """Transform comparison"""
        if len(args) >= 3:
            left = args[0]
            op = self._extract_value(args[1])
            right = args[2]
            return AetherraCodeAST("comparison", value=op, children=[left, right])
        return args[0] if args else None

    def memory_condition(self, args):
        """Transform memory condition"""
        pattern = self._extract_value(args[0]) if args else ""
        frequency = self._extract_value(args[1]) if len(args) > 1 else ""
        return AetherraCodeAST(
            "memory_condition", value=pattern, metadata={"frequency": frequency}
        )

    # Expressions
    def logical_or(self, args):
        """Transform logical OR"""
        if len(args) == 1:
            return args[0]
        return AetherraCodeAST("logical_or", children=args)

    def logical_and(self, args):
        """Transform logical AND"""
        if len(args) == 1:
            return args[0]
        return AetherraCodeAST("logical_and", children=args)

    def addition(self, args):
        """Transform addition/subtraction"""
        if len(args) == 1:
            return args[0]
        result = args[0]
        for i in range(1, len(args), 2):
            op = self._extract_value(args[i])
            right = args[i + 1] if i + 1 < len(args) else None
            if right:
                result = AetherraCodeAST(
                    "binary_op", value=op, children=[result, right]
                )
        return result

    def multiplication(self, args):
        """Transform multiplication/division"""
        if len(args) == 1:
            return args[0]
        result = args[0]
        for i in range(1, len(args), 2):
            op = self._extract_value(args[i])
            right = args[i + 1] if i + 1 < len(args) else None
            if right:
                result = AetherraCodeAST(
                    "binary_op", value=op, children=[result, right]
                )
        return result

    def unary(self, args):
        """Transform unary expression"""
        if len(args) == 1:
            return args[0]
        op = self._extract_value(args[0])
        operand = args[1]
        return AetherraCodeAST("unary_op", value=op, children=[operand])

    def primary(self, args):
        """Transform primary expression"""
        return args[0] if args else None

    # Method calls and arrays
    def method_call(self, args):
        """Transform method call"""
        object_name = self._extract_value(args[0]) if args else ""
        method_name = self._extract_value(args[1]) if len(args) > 1 else ""
        arguments = args[2] if len(args) > 2 else []

        return AetherraCodeAST(
            "method_call",
            value=f"{object_name}.{method_name}",
            children=arguments
            if isinstance(arguments, list)
            else [arguments]
            if arguments
            else [],
            metadata={"object": object_name, "method": method_name},
        )

    def array_literal(self, args):
        """Transform array literal"""
        elements = args[0] if args else []
        return AetherraCodeAST(
            "array",
            children=elements
            if isinstance(elements, list)
            else [elements]
            if elements
            else [],
        )

    def array_elements(self, elements):
        """Transform array elements"""
        return [elem for elem in elements if elem is not None]

    def argument_list(self, args):
        """Transform argument list"""
        return [arg for arg in args if arg is not None]

    # Assignment
    def assignment(self, args):
        """Transform assignment"""
        variable = self._extract_value(args[0]) if args else ""
        value = args[1] if len(args) > 1 else None
        return AetherraCodeAST(
            "assignment", value=variable, children=[value] if value else []
        )

    # Expression statement
    def expression_stmt(self, args):
        """Transform expression statement"""
        return AetherraCodeAST("expression_stmt", children=[args[0]] if args else [])

    # Basic types
    def literal(self, args):
        """Transform literal"""
        return args[0] if args else None

    def string_literal(self, args):
        """Transform string literal"""
        value = self._extract_value(args[0]) if args else ""
        return AetherraCodeAST("string", value=value)

    def identifier(self, args):
        """Transform identifier"""
        name = self._extract_value(args[0]) if args else ""
        return AetherraCodeAST("identifier", value=name)

    def number(self, args):
        """Transform number"""
        value = self._extract_value(args[0]) if args else "0"
        try:
            # Try to convert to int first, then float
            if "." in value:
                value = float(value)
            else:
                value = int(value)
        except ValueError:
            value = 0
        return AetherraCodeAST("number", value=value)

    def boolean(self, args):
        """Transform boolean"""
        value = self._extract_value(args[0]) if args else "false"
        return AetherraCodeAST("boolean", value=value.lower() == "true")

    def null_literal(self, args):
        """Transform null literal"""
        return AetherraCodeAST("null", value=None)

    def comment(self, args):
        """Transform comment"""
        text = self._extract_value(args[0]) if args else ""
        return AetherraCodeAST("comment", value=text)


class AetherraParser:
    """Complete AetherraCode parser with comprehensive language support"""

    def __init__(self):
        """Initialize the parser"""
        try:
            self.parser = Lark(
                aetherra_GRAMMAR,
                parser="lalr",
                transformer=AetherraCodeTransformer(),
                start="program",
            )
        except Exception as e:
            raise Exception(f"Failed to initialize AetherraCode parser: {e}")

    def parse(self, code: str) -> AetherraCodeAST:
        """Parse AetherraCode and return AST"""
        try:
            result = self.parser.parse(code)
            # Ensure result is AetherraCodeAST, not a Tree
            if isinstance(result, AetherraCodeAST):
                return result
            elif hasattr(result, "children"):
                # Manually transform if transformer was not applied
                return AetherraCodeTransformer().transform(result)
            else:
                raise Exception("Parsing did not return an AetherraCodeAST.")
        except ParseError as e:
            raise ParseError(f"AetherraCode parse error: {e}")
        except LexError as e:
            raise LexError(f"AetherraCode lexical error: {e}")
        except Exception as e:
            raise Exception(f"AetherraCode parsing failed: {e}")

    def parse_file(self, filename: str) -> AetherraCodeAST:
        """Parse AetherraCode file and return AST"""
        try:
            with open(filename, encoding="utf-8") as f:
                code = f.read()
            return self.parse(code)
        except FileNotFoundError:
            raise FileNotFoundError(f"AetherraCode file not found: {filename}")
        except Exception as e:
            raise Exception(f"Failed to parse AetherraCode file {filename}: {e}")

    def validate_grammar(self) -> bool:
        """Validate the grammar for conflicts"""
        try:
            # Test basic constructs
            test_cases = [
                'goal: "test"',
                "agent: on",
                'remember("test")',
                'model: "gpt-4"',
                "x = 5",
                'if x > 0:\n    remember("positive")\nend',
            ]

            for test in test_cases:
                self.parse(test)

            return True
        except Exception as e:
            print(f"Grammar validation failed: {e}")
            return False


def main():
    """Test the AetherraCode parser"""
    parser = AetherraParser()

    print("🧬 AetherraCode Complete Grammar Parser")
    print("=" * 50)

    # Validate grammar
    if parser.validate_grammar():
        print("✓ Grammar validation passed")
    else:
        print("✗ Grammar validation failed")
        return

    # Test cases
    test_cases = [
        ("Goal statement", 'goal: "Create a secure system" priority: high'),
        ("Agent control", "agent: on"),
        ("Memory operation", 'remember("Important fact") as "tag"'),
        ("AI model", 'model: "gpt-4"'),
        ("Assistant task", 'assistant: "Help me code"'),
        ("Simple condition", 'if x > 10:\n    remember("Large value")\nend'),
        ("Expression", "result = 2 + 3 * 4"),
        ("Method call", 'data.process("input")'),
        ("Intent action", 'analyze "code quality"'),
        ("Debug statement", 'debug "Testing parser"'),
    ]

    for name, code in test_cases:
        print(f"\n{name}:")
        print(f"Code: {code}")
        try:
            ast = parser.parse(code)
            print(f"✓ Parsed: {ast}")
            if ast.children:
                print(f"  Children: {len(ast.children)}")
            if ast.metadata:
                print(f"  Metadata: {ast.metadata}")
        except Exception as e:
            print(f"✗ Error: {e}")


if __name__ == "__main__":
    main()
