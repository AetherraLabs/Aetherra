"""
Code Generator Tool for Lyrixa
==============================

Converts natural language descriptions to .aether code.
"""

from typing import Optional

from ..models.model_router import router


class CodeGenerator:
    """Generates .aether code from natural language descriptions"""

    def __init__(self, model_router=None):
        self.router = model_router or router
        self.language = "aether"

    def generate_function(
        self, description: str, function_name: Optional[str] = None
    ) -> str:
        """Generate an .aether function from description"""

        system_prompt = f"""You are an expert {self.language} programmer.
        Generate clean, well-documented {self.language} code based on the description.

        {self.language} syntax guidelines:
        - Use natural language for complex operations
        - Functions are defined with 'function name(params)'
        - Variables can be declared naturally
        - Use '->' for assignments from AI calls
        - Include helpful comments
        """

        if function_name:
            prompt = f"Create a function named '{function_name}' that {description}"
        else:
            prompt = f"Create a function that {description}"

        return self.router.generate_response(
            prompt=prompt,
            system_prompt=system_prompt,
            model=self.router.route_by_task("code_generation"),
        )

    def generate_plugin(
        self, description: str, plugin_name: Optional[str] = None
    ) -> str:
        """Generate a complete .aether plugin from description"""

        system_prompt = f"""You are an expert {self.language} plugin developer.
        Generate a complete plugin with proper structure and exports.

        Plugin structure:
        - Include function definitions
        - Add proper exports at the end
        - Include metadata comments
        - Follow plugin best practices
        """

        name = plugin_name or "generated_plugin"
        prompt = f"Create a {self.language} plugin named '{name}' that {description}"

        return self.router.generate_response(
            prompt=prompt,
            system_prompt=system_prompt,
            model=self.router.route_by_task("code_generation"),
        )

    def generate_script(self, description: str, includes_ai: bool = True) -> str:
        """Generate a complete .aether script"""

        ai_context = ""
        if includes_ai:
            ai_context = """
        - Use ask_ai() for intelligent operations
        - Include proper context building
        - Handle AI responses appropriately
        """

        system_prompt = f"""Generate a complete {self.language} script.

        Script guidelines:
        - Include proper variable declarations
        - Add error handling where appropriate
        - Use clear, descriptive names
        - Include helpful comments{ai_context}
        """

        prompt = f"Create a {self.language} script that {description}"

        return self.router.generate_response(
            prompt=prompt,
            system_prompt=system_prompt,
            model=self.router.route_by_task("code_generation"),
        )

    def improve_code(self, existing_code: str, improvement_request: str) -> str:
        """Improve existing .aether code based on request"""

        system_prompt = f"""You are a {self.language} code improvement expert.
        Analyze the existing code and apply the requested improvements.
        Maintain the original functionality while enhancing the code.
        """

        prompt = f"""Improve this {self.language} code:

{existing_code}

Improvement request: {improvement_request}

Provide the improved code:"""

        return self.router.generate_response(
            prompt=prompt,
            system_prompt=system_prompt,
            model=self.router.route_by_task("code_generation"),
        )

    def explain_code(self, code: str) -> str:
        """Explain what .aether code does"""

        system_prompt = f"""You are a {self.language} code analysis expert.
        Explain what the given code does in clear, simple terms.
        Break down complex operations and highlight key features.
        """

        prompt = f"""Explain this {self.language} code:

{code}

Provide a clear explanation:"""

        return self.router.generate_response(
            prompt=prompt,
            system_prompt=system_prompt,
            model=self.router.route_by_task("analysis"),
        )


# Default instance
code_generator = CodeGenerator()
