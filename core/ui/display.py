"""
📺 Rich Display System
======================

Advanced display and rendering system for Neuroplex with support for
rich text, syntax highlighting, tables, and interactive elements.
"""

import re
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class DisplayType(Enum):
    """Types of display content"""

    PLAIN = "plain"
    MARKDOWN = "markdown"
    CODE = "code"
    TABLE = "table"
    LIST = "list"
    JSON = "json"
    ERROR = "error"
    SUCCESS = "success"
    WARNING = "warning"
    INFO = "info"


class CodeLanguage(Enum):
    """Supported programming languages for syntax highlighting"""

    NEUROCODE = "neurocode"
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    RUST = "rust"
    CPP = "cpp"
    C = "c"
    JAVA = "java"
    GO = "go"
    HTML = "html"
    CSS = "css"
    SQL = "sql"
    JSON = "json"
    YAML = "yaml"
    MARKDOWN = "markdown"
    BASH = "bash"
    POWERSHELL = "powershell"


@dataclass
class TextStyle:
    """Text styling configuration"""

    bold: bool = False
    italic: bool = False
    underline: bool = False
    strikethrough: bool = False
    color: Optional[str] = None
    background_color: Optional[str] = None
    font_size: Optional[str] = None


@dataclass
class DisplayElement:
    """Basic display element"""

    content: str
    display_type: DisplayType
    style: Optional[TextStyle] = None
    metadata: Optional[Dict[str, Any]] = None


class SyntaxHighlighter:
    """Syntax highlighting for code blocks"""

    def __init__(self):
        self.language_patterns = self._initialize_patterns()

    def _initialize_patterns(self) -> Dict[CodeLanguage, Dict[str, str]]:
        """Initialize syntax highlighting patterns"""
        return {
            CodeLanguage.aetherCODE: {
                "keywords": r"\b(think|remember|goal|agent|if|else|while|for|function|return|import|export)\b",
                "strings": r'(["\'])(?:(?=(\\?))\2.)*?\1',
                "comments": r"#.*$",
                "numbers": r"\b\d+\.?\d*\b",
                "operators": r"[+\-*/=<>!&|]",
                "memory_ops": r"\b(store|recall|forget|search)\b",
                "ai_ops": r"\b(ask|analyze|generate|predict)\b",
            },
            CodeLanguage.PYTHON: {
                "keywords": r"\b(def|class|if|else|elif|for|while|try|except|finally|import|from|return|yield|with|as|lambda|and|or|not|in|is|None|True|False)\b",
                "strings": r'(["\'])(?:(?=(\\?))\2.)*?\1',
                "comments": r"#.*$",
                "numbers": r"\b\d+\.?\d*\b",
                "operators": r"[+\-*/=<>!&|%]",
                "decorators": r"@\w+",
                "functions": r"\bdef\s+(\w+)",
                "classes": r"\bclass\s+(\w+)",
            },
            CodeLanguage.JAVASCRIPT: {
                "keywords": r"\b(function|const|let|var|if|else|for|while|try|catch|finally|return|class|extends|import|export|async|await|this|new|typeof|instanceof)\b",
                "strings": r'(["\'])(?:(?=(\\?))\2.)*?\1',
                "comments": r"//.*$|/\*[\s\S]*?\*/",
                "numbers": r"\b\d+\.?\d*\b",
                "operators": r"[+\-*/=<>!&|%]",
                "template_literals": r"`[^`]*`",
            },
        }

    def highlight(self, code: str, language: CodeLanguage) -> str:
        """Apply syntax highlighting to code"""
        if language not in self.language_patterns:
            return code

        patterns = self.language_patterns[language]
        highlighted_code = code

        # Apply patterns (simplified - in a real implementation you'd use a proper parser)
        for token_type, pattern in patterns.items():
            highlighted_code = re.sub(
                pattern,
                lambda m, tt=token_type: self._wrap_token(m.group(0), tt),
                highlighted_code,
                flags=re.MULTILINE,
            )

        return highlighted_code

    def _wrap_token(self, token: str, token_type: str) -> str:
        """Wrap token with styling markers"""
        # In a real implementation, this would apply actual colors/styles
        return f"<{token_type}>{token}</{token_type}>"


class TableRenderer:
    """Renders tables in various formats"""

    @staticmethod
    def render_table(
        headers: List[str], rows: List[List[str]], style: str = "grid"
    ) -> str:
        """Render a table with given headers and rows"""
        if not headers or not rows:
            return ""

        # Calculate column widths
        col_widths = [len(header) for header in headers]
        for row in rows:
            for i, cell in enumerate(row):
                if i < len(col_widths):
                    col_widths[i] = max(col_widths[i], len(str(cell)))

        if style == "grid":
            return TableRenderer._render_grid_table(headers, rows, col_widths)
        elif style == "simple":
            return TableRenderer._render_simple_table(headers, rows, col_widths)
        else:
            return TableRenderer._render_plain_table(headers, rows, col_widths)

    @staticmethod
    def _render_grid_table(
        headers: List[str], rows: List[List[str]], col_widths: List[int]
    ) -> str:
        """Render table with grid borders"""
        lines = []

        # Top border
        lines.append("┌" + "┬".join("─" * (w + 2) for w in col_widths) + "┐")

        # Headers
        header_line = "│"
        for i, header in enumerate(headers):
            header_line += f" {header:<{col_widths[i]}} │"
        lines.append(header_line)

        # Header separator
        lines.append("├" + "┼".join("─" * (w + 2) for w in col_widths) + "┤")

        # Data rows
        for row in rows:
            row_line = "│"
            for i, cell in enumerate(row):
                if i < len(col_widths):
                    row_line += f" {str(cell):<{col_widths[i]}} │"
            lines.append(row_line)

        # Bottom border
        lines.append("└" + "┴".join("─" * (w + 2) for w in col_widths) + "┘")

        return "\n".join(lines)

    @staticmethod
    def _render_simple_table(
        headers: List[str], rows: List[List[str]], col_widths: List[int]
    ) -> str:
        """Render simple table with minimal borders"""
        lines = []

        # Headers
        header_line = " ".join(
            f"{header:<{col_widths[i]}}" for i, header in enumerate(headers)
        )
        lines.append(header_line)

        # Header separator
        lines.append(" ".join("─" * w for w in col_widths))

        # Data rows
        for row in rows:
            row_line = " ".join(
                f"{str(cell):<{col_widths[i]}}"
                for i, cell in enumerate(row)
                if i < len(col_widths)
            )
            lines.append(row_line)

        return "\n".join(lines)

    @staticmethod
    def _render_plain_table(
        headers: List[str], rows: List[List[str]], col_widths: List[int]
    ) -> str:
        """Render plain table without borders"""
        lines = []

        # Headers
        header_line = " | ".join(
            f"{header:<{col_widths[i]}}" for i, header in enumerate(headers)
        )
        lines.append(header_line)

        # Data rows
        for row in rows:
            row_line = " | ".join(
                f"{str(cell):<{col_widths[i]}}"
                for i, cell in enumerate(row)
                if i < len(col_widths)
            )
            lines.append(row_line)

        return "\n".join(lines)


class MarkdownRenderer:
    """Renders markdown content"""

    def __init__(self):
        self.syntax_highlighter = SyntaxHighlighter()

    def render(self, markdown: str) -> str:
        """Render markdown to formatted text"""
        lines = markdown.split("\n")
        rendered_lines = []

        in_code_block = False
        code_language = None
        code_block = []

        for line in lines:
            # Handle code blocks
            if line.strip().startswith("```"):
                if in_code_block:
                    # End of code block
                    if code_language and code_block:
                        highlighted = self.syntax_highlighter.highlight(
                            "\n".join(code_block), code_language
                        )
                        rendered_lines.append(f"[CODE BLOCK: {code_language.value}]")
                        rendered_lines.append(highlighted)
                        rendered_lines.append("[/CODE BLOCK]")
                    else:
                        rendered_lines.extend(code_block)

                    in_code_block = False
                    code_language = None
                    code_block = []
                else:
                    # Start of code block
                    in_code_block = True
                    lang_name = line.strip()[3:].strip()
                    try:
                        code_language = CodeLanguage(lang_name.lower())
                    except ValueError:
                        code_language = None
                continue

            if in_code_block:
                code_block.append(line)
                continue

            # Handle other markdown elements
            rendered_line = self._render_line(line)
            rendered_lines.append(rendered_line)

        return "\n".join(rendered_lines)

    def _render_line(self, line: str) -> str:
        """Render a single markdown line"""
        # Headers
        if line.startswith("#"):
            level = len(line) - len(line.lstrip("#"))
            text = line.lstrip("# ").strip()
            return f"{'=' * level} {text} {'=' * level}"

        # Bold and italic
        line = re.sub(r"\*\*(.*?)\*\*", r"**\1**", line)  # Bold
        line = re.sub(r"\*(.*?)\*", r"*\1*", line)  # Italic

        # Inline code
        line = re.sub(r"`(.*?)`", r"[\1]", line)

        # Links
        line = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1 (\2)", line)

        # Lists
        if re.match(r"^\s*[-*+]\s", line):
            indent = len(line) - len(line.lstrip())
            content = re.sub(r"^\s*[-*+]\s", "", line)
            return f"{'  ' * (indent // 2)}• {content}"

        # Numbered lists
        if re.match(r"^\s*\d+\.\s", line):
            return line

        return line


class RichDisplay:
    """Main rich display system"""

    def __init__(self):
        self.syntax_highlighter = SyntaxHighlighter()
        self.table_renderer = TableRenderer()
        self.markdown_renderer = MarkdownRenderer()
        self.output_buffer: List[DisplayElement] = []
        self.max_buffer_size = 1000

    def clear(self):
        """Clear the display buffer"""
        self.output_buffer.clear()

    def add_element(self, element: DisplayElement):
        """Add an element to the display buffer"""
        self.output_buffer.append(element)

        # Maintain buffer size
        if len(self.output_buffer) > self.max_buffer_size:
            self.output_buffer.pop(0)

    def print_text(self, text: str, style: Optional[TextStyle] = None):
        """Print plain text"""
        element = DisplayElement(
            content=text, display_type=DisplayType.PLAIN, style=style
        )
        self.add_element(element)

    def print_markdown(self, markdown: str):
        """Print markdown content"""
        rendered = self.markdown_renderer.render(markdown)
        element = DisplayElement(content=rendered, display_type=DisplayType.MARKDOWN)
        self.add_element(element)

    def print_code(self, code: str, language: CodeLanguage = CodeLanguage.aetherCODE):
        """Print code with syntax highlighting"""
        highlighted = self.syntax_highlighter.highlight(code, language)
        element = DisplayElement(
            content=highlighted,
            display_type=DisplayType.CODE,
            metadata={"language": language.value},
        )
        self.add_element(element)

    def print_table(
        self, headers: List[str], rows: List[List[str]], style: str = "grid"
    ):
        """Print a table"""
        table_content = self.table_renderer.render_table(headers, rows, style)
        element = DisplayElement(
            content=table_content,
            display_type=DisplayType.TABLE,
            metadata={"style": style, "headers": headers, "rows": rows},
        )
        self.add_element(element)

    def print_list(self, items: List[str], ordered: bool = False):
        """Print a list"""
        if ordered:
            content = "\n".join(f"{i + 1}. {item}" for i, item in enumerate(items))
        else:
            content = "\n".join(f"• {item}" for item in items)

        element = DisplayElement(
            content=content,
            display_type=DisplayType.LIST,
            metadata={"ordered": ordered, "items": items},
        )
        self.add_element(element)

    def print_json(self, data: Any, indent: int = 2):
        """Print JSON data"""
        import json

        try:
            content = json.dumps(data, indent=indent, ensure_ascii=False)
            element = DisplayElement(content=content, display_type=DisplayType.JSON)
            self.add_element(element)
        except Exception as e:
            self.print_error(f"Failed to format JSON: {e}")

    def print_success(self, message: str, details: Optional[str] = None):
        """Print success message"""
        content = f"✅ {message}"
        if details:
            content += f"\n   {details}"

        element = DisplayElement(
            content=content,
            display_type=DisplayType.SUCCESS,
            style=TextStyle(color="green", bold=True),
        )
        self.add_element(element)

    def print_error(self, message: str, details: Optional[str] = None):
        """Print error message"""
        content = f"❌ {message}"
        if details:
            content += f"\n   {details}"

        element = DisplayElement(
            content=content,
            display_type=DisplayType.ERROR,
            style=TextStyle(color="red", bold=True),
        )
        self.add_element(element)

    def print_warning(self, message: str, details: Optional[str] = None):
        """Print warning message"""
        content = f"⚠️  {message}"
        if details:
            content += f"\n   {details}"

        element = DisplayElement(
            content=content,
            display_type=DisplayType.WARNING,
            style=TextStyle(color="yellow", bold=True),
        )
        self.add_element(element)

    def print_info(self, message: str, details: Optional[str] = None):
        """Print info message"""
        content = f"ℹ️  {message}"
        if details:
            content += f"\n   {details}"

        element = DisplayElement(
            content=content,
            display_type=DisplayType.INFO,
            style=TextStyle(color="blue", bold=True),
        )
        self.add_element(element)

    def print_separator(self, char: str = "─", width: int = 60):
        """Print a separator line"""
        content = char * width
        element = DisplayElement(
            content=content,
            display_type=DisplayType.PLAIN,
            style=TextStyle(color="gray"),
        )
        self.add_element(element)

    def print_timestamp(self, timestamp: Optional[datetime] = None):
        """Print timestamp"""
        if timestamp is None:
            timestamp = datetime.now()

        content = f"[{timestamp.strftime('%Y-%m-%d %H:%M:%S')}]"
        element = DisplayElement(
            content=content,
            display_type=DisplayType.PLAIN,
            style=TextStyle(color="gray", italic=True),
        )
        self.add_element(element)

    def get_buffer_content(self) -> List[DisplayElement]:
        """Get current buffer content"""
        return self.output_buffer.copy()

    def export_buffer(self, format_type: str = "text") -> str:
        """Export buffer content in specified format"""
        if format_type == "text":
            return "\n".join(element.content for element in self.output_buffer)
        elif format_type == "html":
            # Would implement HTML export
            pass
        elif format_type == "json":
            import json

            return json.dumps(
                [
                    {
                        "content": element.content,
                        "type": element.display_type.value,
                        "style": element.style.__dict__ if element.style else None,
                        "metadata": element.metadata,
                    }
                    for element in self.output_buffer
                ],
                indent=2,
            )

        return ""
