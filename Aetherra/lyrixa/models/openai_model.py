"""
OpenAI Model Integration for Lyrixa
===================================

GPT-4 and ChatGPT model integration with intelligent routing and context management.
"""

from typing import Dict, List, Optional

import openai


class OpenAIModel:
    """OpenAI GPT model integration"""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4"):
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model
        self.max_tokens = 4096
        self.temperature = 0.7

    def generate_response(
        self,
        prompt: str,
        context: Optional[Dict] = None,
        system_prompt: Optional[str] = None,
    ) -> str:
        """Generate response using OpenAI model"""

        messages = []

        # Add system prompt if provided
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        # Add context from memory if available
        if context:
            memory_summary = str(context.get("memory", ""))
            if memory_summary:
                messages.append(
                    {"role": "system", "content": f"Relevant context: {memory_summary}"}
                )

        # Add user prompt
        messages.append({"role": "user", "content": prompt})

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
            )

            return response.choices[0].message.content or "No response generated"

        except Exception as e:
            return f"Error generating response: {str(e)}"

    def generate_code(self, description: str, language: str = "aether") -> str:
        """Generate code from natural language description"""

        system_prompt = f"""You are an expert {language} programmer.
        Generate clean, efficient code based on the user's description.
        Follow best practices and include helpful comments."""

        prompt = f"Generate {language} code for: {description}"

        return self.generate_response(prompt, system_prompt=system_prompt)

    def analyze_memory(self, memories: List[Dict]) -> Dict:
        """Analyze and summarize memory patterns"""

        system_prompt = """You are a memory analysis expert.
        Analyze the provided memories and extract patterns, insights, and suggestions."""

        memory_summary = "\n".join([f"- {mem.get('content', '')}" for mem in memories])
        prompt = f"Analyze these memories and provide insights:\n{memory_summary}"

        response = self.generate_response(prompt, system_prompt=system_prompt)

        return {
            "analysis": response,
            "memory_count": len(memories),
            "patterns_detected": True if "pattern" in response.lower() else False,
        }


# Default instance
default_openai_model = OpenAIModel()
