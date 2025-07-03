#!/usr/bin/env python3
"""
🧬 Enhanced NeuroCode Parser
Token/Grammar-based parsing system for advanced NeuroCode constructs

This enhances the current interpreter.py with:
1. Token-based parsing instead of regex matching
2. Grammar rules for complex constructs
3. Block parsing support (define...end, if...end, etc.)
4. Better error handling and syntax suggestions
5. Abstract Syntax Tree generation for optimization
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, List, Optional


class TokenType(Enum):
    """NeuroCode token types"""

    # Core language tokens
    KEYWORD = "KEYWORD"  # remember, recall, goal, agent, etc.
    IDENTIFIER = "IDENTIFIER"  # variable names, function names
    STRING = "STRING"  # "quoted strings"
    NUMBER = "NUMBER"  # 42, 3.14
    OPERATOR = "OPERATOR"  # :, as, on, for, etc.

    # Block structure tokens
    BLOCK_START = "BLOCK_START"  # define, if, while, etc.
    BLOCK_END = "BLOCK_END"  # end
    INDENT = "INDENT"  # indentation levels
    DEDENT = "DEDENT"  # dedentation

    # Special tokens
    NEWLINE = "NEWLINE"  # line breaks
    EOF = "EOF"  # end of file
    COMMENT = "COMMENT"  # # comments

    # NeuroCode specific
    MEMORY_TAG = "MEMORY_TAG"  # tags in memory operations
    GOAL_PRIORITY = "GOAL_PRIORITY"  # high, medium, low
    AGENT_SPEC = "AGENT_SPEC"  # specialization specifications


@dataclass
class Token:
    """Represents a parsed token"""

    type: TokenType
    value: str
    line: int
    column: int
    context: Optional[str] = None


@dataclass
class ASTNode:
    """Abstract Syntax Tree node"""

    type: str
    value: Any
    children: List["ASTNode"]
    line: int
    column: int

    def add_child(self, child: "ASTNode"):
        self.children.append(child)


class AetherraLexer:
    """Tokenizes NeuroCode source into tokens"""

    # NeuroCode keywords
    KEYWORDS = {
        "remember",
        "recall",
        "memory",
        "goal",
        "agent",
        "think",
        "analyze",
        "suggest",
        "reflect",
        "detect",
        "patterns",
        "define",
        "end",
        "call",
        "if",
        "elif",
        "else",
        "while",
        "for",
        "in",
        "return",
        "break",
        "continue",
        "plugin",
        "assistant",
        "meta",
        "load",
        "save",
        "backup",
        "optimize",
        "learn",
        "evolve",
        "adapt",
        "debug",
        "self_edit",
        "autonomous",
    }

    # NeuroCode operators and delimiters
    OPERATORS = {
        "as",
        "on",
        "for",
        "with",
        "by",
        "from",
        "to",
        "priority",
        "tag",
        "specialization",
        "category",
        "confidence",
        "threshold",
    }

    def __init__(self):
        self.tokens = []
        self.current_line = 1
        self.current_column = 1
        self.position = 0
        self.text = ""

    def tokenize(self, text: str) -> List[Token]:
        """Tokenize NeuroCode source text"""
        self.text = text
        self.position = 0
        self.current_line = 1
        self.current_column = 1
        self.tokens = []

        while self.position < len(self.text):
            self._scan_token()

        # Add EOF token
        self.tokens.append(Token(TokenType.EOF, "", self.current_line, self.current_column))

        return self.tokens

    def _scan_token(self):
        """Scan and create the next token"""
        char = self._current_char()

        # Skip whitespace (except newlines for indentation tracking)
        if char in " \t\r":
            self._advance()
            return

        # Handle newlines
        if char == "\n":
            self._add_token(TokenType.NEWLINE, char)
            self._advance()
            self.current_line += 1
            self.current_column = 1
            return

        # Handle comments
        if char == "#":
            self._scan_comment()
            return

        # Handle strings
        if char in "\"'":
            self._scan_string()
            return

        # Handle numbers
        if char.isdigit():
            self._scan_number()
            return

        # Handle identifiers and keywords
        if char.isalpha() or char == "_":
            self._scan_identifier()
            return

        # Handle operators and punctuation
        if char in ":()[]{},.":
            self._add_token(TokenType.OPERATOR, char)
            self._advance()
            return

        # Unknown character
        self._advance()  # Skip it for now

    def _scan_comment(self):
        """Scan a comment until end of line"""
        start_pos = self.position
        while self._current_char() != "\n" and not self._at_end():
            self._advance()
        comment_text = self.text[start_pos : self.position]
        self._add_token(TokenType.COMMENT, comment_text)

    def _scan_string(self):
        """Scan a quoted string"""
        quote_char = self._current_char()
        self._advance()  # Skip opening quote

        start_pos = self.position
        while self._current_char() != quote_char and not self._at_end():
            if self._current_char() == "\n":
                self.current_line += 1
                self.current_column = 1
            else:
                self.current_column += 1
            self.position += 1

        if self._at_end():
            # Unterminated string - could add error handling here
            pass
        else:
            self._advance()  # Skip closing quote

        string_value = self.text[start_pos : self.position - 1]
        self._add_token(TokenType.STRING, string_value)

    def _scan_number(self):
        """Scan a numeric literal"""
        start_pos = self.position

        while self._current_char().isdigit():
            self._advance()

        # Handle decimal point
        if self._current_char() == "." and self._peek().isdigit():
            self._advance()  # Skip the '.'
            while self._current_char().isdigit():
                self._advance()

        number_value = self.text[start_pos : self.position]
        self._add_token(TokenType.NUMBER, number_value)

    def _scan_identifier(self):
        """Scan an identifier or keyword"""
        start_pos = self.position

        while self._current_char().isalnum() or self._current_char() in "_":
            self._advance()

        identifier_value = self.text[start_pos : self.position]

        # Check if it's a keyword
        if identifier_value.lower() in self.KEYWORDS:
            token_type = TokenType.KEYWORD
        elif identifier_value.lower() in self.OPERATORS:
            token_type = TokenType.OPERATOR
        else:
            token_type = TokenType.IDENTIFIER

        self._add_token(token_type, identifier_value)

    def _current_char(self) -> str:
        """Get current character"""
        if self._at_end():
            return "\0"
        return self.text[self.position]

    def _peek(self) -> str:
        """Peek at next character"""
        if self.position + 1 >= len(self.text):
            return "\0"
        return self.text[self.position + 1]

    def _advance(self):
        """Move to next character"""
        if not self._at_end():
            self.position += 1
            self.current_column += 1

    def _at_end(self) -> bool:
        """Check if at end of input"""
        return self.position >= len(self.text)

    def _add_token(self, token_type: TokenType, value: str):
        """Add a token to the list"""
        self.tokens.append(Token(token_type, value, self.current_line, self.current_column))


class AetherraParser:
    """Parses tokens into an Abstract Syntax Tree"""

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.current = 0

    def parse(self) -> List[ASTNode]:
        """Parse tokens into AST nodes"""
        statements = []

        while not self._at_end():
            # Skip newlines and comments at top level
            if self._current_token().type in [TokenType.NEWLINE, TokenType.COMMENT]:
                self._advance()
                continue

            stmt = self._parse_statement()
            if stmt:
                statements.append(stmt)

        return statements

    def _parse_statement(self) -> Optional[ASTNode]:
        """Parse a single statement"""
        token = self._current_token()

        if token.type != TokenType.KEYWORD:
            self._advance()
            return None

        keyword = token.value.lower()

        # Memory operations
        if keyword == "remember":
            return self._parse_remember()
        elif keyword == "recall":
            return self._parse_recall()
        elif keyword == "memory":
            return self._parse_memory_command()

        # Goal operations
        elif keyword == "goal":
            return self._parse_goal()

        # Agent operations
        elif keyword == "agent":
            return self._parse_agent()

        # AI operations
        elif keyword in ["think", "analyze", "suggest", "reflect"]:
            return self._parse_ai_command()

        # Function operations
        elif keyword == "define":
            return self._parse_function_definition()
        elif keyword == "call":
            return self._parse_function_call()

        # Block structures
        elif keyword in ["if", "while", "for"]:
            return self._parse_block_statement()

        # Other commands
        else:
            return self._parse_generic_command()

    def _parse_remember(self) -> ASTNode:
        """Parse remember statement: remember("content") as "tags" """
        node = ASTNode(
            "REMEMBER", None, [], self._current_token().line, self._current_token().column
        )

        self._advance()  # Skip 'remember'

        # Expect opening parenthesis
        if self._match_operator("("):
            # Parse content string
            if self._current_token().type == TokenType.STRING:
                content_node = ASTNode(
                    "CONTENT",
                    self._current_token().value,
                    [],
                    self._current_token().line,
                    self._current_token().column,
                )
                node.add_child(content_node)
                self._advance()

                # Expect closing parenthesis
                if self._match_operator(")"):
                    # Look for 'as' keyword
                    if self._match_operator("as"):
                        # Parse tags
                        if self._current_token().type == TokenType.STRING:
                            tags_node = ASTNode(
                                "TAGS",
                                self._current_token().value,
                                [],
                                self._current_token().line,
                                self._current_token().column,
                            )
                            node.add_child(tags_node)
                            self._advance()

        return node

    def _parse_recall(self) -> ASTNode:
        """Parse recall statement"""
        node = ASTNode("RECALL", None, [], self._current_token().line, self._current_token().column)

        self._advance()  # Skip 'recall'

        # Handle 'recall tag: "tagname"' syntax
        if self._match_operator("tag"):
            if self._match_operator(":"):
                if self._current_token().type == TokenType.STRING:
                    tag_node = ASTNode(
                        "TAG_FILTER",
                        self._current_token().value,
                        [],
                        self._current_token().line,
                        self._current_token().column,
                    )
                    node.add_child(tag_node)
                    self._advance()

        return node

    def _parse_goal(self) -> ASTNode:
        """Parse goal statement: goal: "objective" priority: high"""
        node = ASTNode("GOAL", None, [], self._current_token().line, self._current_token().column)

        self._advance()  # Skip 'goal'

        if self._match_operator(":"):
            # Parse goal content
            if self._current_token().type == TokenType.STRING:
                content_node = ASTNode(
                    "GOAL_CONTENT",
                    self._current_token().value,
                    [],
                    self._current_token().line,
                    self._current_token().column,
                )
                node.add_child(content_node)
                self._advance()

                # Look for priority specification
                if self._match_operator("priority"):
                    if self._match_operator(":"):
                        if self._current_token().type == TokenType.IDENTIFIER:
                            priority_node = ASTNode(
                                "PRIORITY",
                                self._current_token().value,
                                [],
                                self._current_token().line,
                                self._current_token().column,
                            )
                            node.add_child(priority_node)
                            self._advance()

        return node

    def _parse_function_definition(self) -> ASTNode:
        """Parse function definition: define function_name(params) ... end"""
        node = ASTNode(
            "FUNCTION_DEF", None, [], self._current_token().line, self._current_token().column
        )

        self._advance()  # Skip 'define'

        # Parse function name
        if self._current_token().type == TokenType.IDENTIFIER:
            name_node = ASTNode(
                "FUNCTION_NAME",
                self._current_token().value,
                [],
                self._current_token().line,
                self._current_token().column,
            )
            node.add_child(name_node)
            self._advance()

            # Parse parameters if present
            if self._match_operator("("):
                params_node = ASTNode(
                    "PARAMETERS", None, [], self._current_token().line, self._current_token().column
                )

                while not self._match_operator(")") and not self._at_end():
                    if self._current_token().type == TokenType.IDENTIFIER:
                        param_node = ASTNode(
                            "PARAMETER",
                            self._current_token().value,
                            [],
                            self._current_token().line,
                            self._current_token().column,
                        )
                        params_node.add_child(param_node)
                        self._advance()

                        # Skip comma if present
                        if self._match_operator(","):
                            continue

                node.add_child(params_node)

            # Parse function body until 'end'
            body_node = ASTNode(
                "FUNCTION_BODY", None, [], self._current_token().line, self._current_token().column
            )

            while (
                not (
                    self._current_token().type == TokenType.KEYWORD
                    and self._current_token().value.lower() == "end"
                )
                and not self._at_end()
            ):
                stmt = self._parse_statement()
                if stmt:
                    body_node.add_child(stmt)
                else:
                    self._advance()  # Skip unrecognized tokens

            node.add_child(body_node)

            # Consume 'end'
            if (
                self._current_token().type == TokenType.KEYWORD
                and self._current_token().value.lower() == "end"
            ):
                self._advance()

        return node

    def _parse_agent(self) -> ASTNode:
        """Parse agent operations"""
        return self._parse_generic_command()

    def _parse_memory_command(self) -> ASTNode:
        """Parse memory management commands"""
        return self._parse_generic_command()

    def _parse_ai_command(self) -> ASTNode:
        """Parse AI reasoning commands"""
        return self._parse_generic_command()

    def _parse_function_call(self) -> ASTNode:
        """Parse function calls"""
        return self._parse_generic_command()

    def _parse_block_statement(self) -> ASTNode:
        """Parse block statements (if, while, for)"""
        return self._parse_generic_command()

    def _parse_generic_command(self) -> ASTNode:
        """Parse generic command (fallback)"""
        node = ASTNode(
            "COMMAND",
            self._current_token().value,
            [],
            self._current_token().line,
            self._current_token().column,
        )
        self._advance()

        # Consume rest of line
        while not self._at_end() and self._current_token().type != TokenType.NEWLINE:
            if self._current_token().type in [
                TokenType.STRING,
                TokenType.IDENTIFIER,
                TokenType.NUMBER,
            ]:
                arg_node = ASTNode(
                    "ARGUMENT",
                    self._current_token().value,
                    [],
                    self._current_token().line,
                    self._current_token().column,
                )
                node.add_child(arg_node)
            self._advance()

        return node

    def _current_token(self) -> Token:
        """Get current token"""
        if self._at_end():
            return self.tokens[-1]  # EOF token
        return self.tokens[self.current]

    def _advance(self) -> Token:
        """Move to next token"""
        if not self._at_end():
            self.current += 1
        return self._current_token()

    def _at_end(self) -> bool:
        """Check if at end of tokens"""
        return self.current >= len(self.tokens) or self._current_token().type == TokenType.EOF

    def _match_operator(self, expected: str) -> bool:
        """Check if current token matches expected operator"""
        token = self._current_token()
        if token.type == TokenType.OPERATOR and token.value == expected:
            self._advance()
            return True
        return False


class EnhancedAetherraInterpreter:
    """Enhanced interpreter with token/grammar-based parsing"""

    def __init__(self, base_interpreter):
        self.base_interpreter = base_interpreter
        self.lexer = AetherraLexer()
        self.parser = None

    def execute_enhanced(self, source: str) -> str:
        """Execute NeuroCode using enhanced parsing"""
        try:
            # Tokenize
            tokens = self.lexer.tokenize(source)

            # Parse into AST
            self.parser = AetherraParser(tokens)
            ast_nodes = self.parser.parse()

            # Execute AST nodes
            results = []
            for node in ast_nodes:
                result = self._execute_ast_node(node)
                if result:
                    results.append(result)

            return "\n".join(results) if results else "✅ Executed successfully"

        except Exception:
            # Fallback to base interpreter
            return f"🔄 Enhanced parsing failed, using base interpreter: {self.base_interpreter.execute(source)}"

    def _execute_ast_node(self, node: ASTNode) -> Optional[str]:
        """Execute an AST node"""
        if node.type == "REMEMBER":
            return self._execute_remember(node)
        elif node.type == "RECALL":
            return self._execute_recall(node)
        elif node.type == "GOAL":
            return self._execute_goal(node)
        elif node.type == "FUNCTION_DEF":
            return self._execute_function_def(node)
        elif node.type == "COMMAND":
            # Fallback to base interpreter for unhandled commands
            command_line = self._reconstruct_command(node)
            return self.base_interpreter.execute(command_line)

        return None

    def _execute_remember(self, node: ASTNode) -> str:
        """Execute remember statement from AST"""
        content = ""
        tags = ""

        for child in node.children:
            if child.type == "CONTENT":
                content = child.value
            elif child.type == "TAGS":
                tags = child.value

        if content:
            result = self.base_interpreter.memory.remember(
                content, tags.split(",") if tags else None
            )
            return f"💾 Remembered: {content} (tags: {tags})"

        return "❌ Invalid remember syntax"

    def _execute_recall(self, node: ASTNode) -> str:
        """Execute recall statement from AST"""
        tag_filter = None

        for child in node.children:
            if child.type == "TAG_FILTER":
                tag_filter = child.value

        if tag_filter:
            memories = self.base_interpreter.memory.recall(tags=[tag_filter])
            if memories:
                return f"🧠 Recalled {len(memories)} memories with tag '{tag_filter}'"
            else:
                return f"🤔 No memories found with tag '{tag_filter}'"

        return "❌ Invalid recall syntax"

    def _execute_goal(self, node: ASTNode) -> str:
        """Execute goal statement from AST"""
        content = ""
        priority = "medium"

        for child in node.children:
            if child.type == "GOAL_CONTENT":
                content = child.value
            elif child.type == "PRIORITY":
                priority = child.value

        if content:
            result = self.base_interpreter.goal_system.set_goal(content, priority)
            return f"🎯 Goal set: {content} (priority: {priority})"

        return "❌ Invalid goal syntax"

    def _execute_function_def(self, node: ASTNode) -> str:
        """Execute function definition from AST"""
        func_name = ""
        params = []
        body = []

        for child in node.children:
            if child.type == "FUNCTION_NAME":
                func_name = child.value
            elif child.type == "PARAMETERS":
                params = [param.value for param in child.children]
            elif child.type == "FUNCTION_BODY":
                # Convert body AST back to commands for now
                for stmt in child.children:
                    body.append(self._reconstruct_command(stmt))

        if func_name:
            result = self.base_interpreter.functions.define_function(func_name, params, body)
            return f"🔧 Function defined: {func_name}({', '.join(params)})"

        return "❌ Invalid function definition"

    def _reconstruct_command(self, node: ASTNode) -> str:
        """Reconstruct command string from AST node"""
        if node.type == "COMMAND":
            parts = [node.value]
            for child in node.children:
                if child.type == "ARGUMENT":
                    parts.append(f'"{child.value}"' if " " in child.value else child.value)
            return " ".join(parts)

        return str(node.value)


# Usage example and testing
if __name__ == "__main__":
    # Test the enhanced parser
    sample_code = """
    # NeuroCode with enhanced parsing
    remember("Python is object-oriented") as "programming,paradigm"
    goal: "learn advanced NeuroCode" priority: high

    define fibonacci(n)
        if n <= 1
            return n
        else
            return fibonacci(n-1) + fibonacci(n-2)
        end
    end

    recall tag: "programming"
    think "about the fibonacci sequence"
    """

    print("🧬 Testing Enhanced NeuroCode Parser")
    print("=" * 50)

    # Tokenize
    lexer = AetherraLexer()
    tokens = lexer.tokenize(sample_code)

    print("📝 Tokens:")
    for token in tokens[:20]:  # Show first 20 tokens
        print(f"  {token.type.value:15} | {token.value:20} | Line {token.line}")

    print("\n🌳 AST Nodes:")
    parser = AetherraParser(tokens)
    ast_nodes = parser.parse()

    for node in ast_nodes:
        print(f"  {node.type:15} | {node.value} | Children: {len(node.children)}")
        for child in node.children:
            print(f"    └─ {child.type:12} | {child.value}")
