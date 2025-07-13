"""
Local Model Integration for Lyrixa
==================================

Support for Ollama, LM Studio, and other local LLM deployments.
"""

from typing import Dict, Optional

try:
    import requests

    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


class LocalModel:
    """Local LLM integration via API endpoints"""

    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama2"):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.max_tokens = 2048
        self.temperature = 0.7

    def generate_response(
        self,
        prompt: str,
        context: Optional[Dict] = None,
        system_prompt: Optional[str] = None,
    ) -> str:
        """Generate response using local model"""

        if not REQUESTS_AVAILABLE:
            return "Error: requests library not available. Please install with: pip install requests"

        # Build full prompt with context
        full_prompt = ""

        if system_prompt:
            full_prompt += f"System: {system_prompt}\n\n"

        if context:
            memory_summary = str(context.get("memory", ""))
            if memory_summary:
                full_prompt += f"Context: {memory_summary}\n\n"

        full_prompt += f"User: {prompt}\nAssistant: "

        try:
            # Try Ollama API format first
            response = self._call_ollama_api(full_prompt)
            if response:
                return response

            # Fallback to generic completion API
            return self._call_generic_api(full_prompt)

        except Exception as e:
            return f"Error generating response from local model: {str(e)}"

    def _call_ollama_api(self, prompt: str) -> Optional[str]:
        """Call Ollama API endpoint"""
        if not REQUESTS_AVAILABLE:
            return None

        try:
            response = requests.post(  # type: ignore
                f"{self.base_url}/api/generate",
                json={"model": self.model, "prompt": prompt, "stream": False},
                timeout=30,
            )

            if response.status_code == 200:
                return response.json().get("response", "")

        except Exception:
            pass

        return None

    def _call_generic_api(self, prompt: str) -> str:
        """Fallback to generic completion API"""
        if not REQUESTS_AVAILABLE:
            return "Error: requests library not available"

        try:
            response = requests.post(  # type: ignore
                f"{self.base_url}/v1/completions",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "max_tokens": self.max_tokens,
                    "temperature": self.temperature,
                },
                headers={"Content-Type": "application/json"},
                timeout=30,
            )

            if response.status_code == 200:
                result = response.json()
                return result.get("choices", [{}])[0].get("text", "").strip()

        except Exception as e:
            return f"API call failed: {str(e)}"

        return "No response from local model"

    def is_available(self) -> bool:
        """Check if local model is available"""
        if not REQUESTS_AVAILABLE:
            return False

        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)  # type: ignore
            return response.status_code == 200
        except Exception:
            return False


# Common local model configurations
OLLAMA_DEFAULT = LocalModel("http://localhost:11434", "llama2")
LM_STUDIO = LocalModel("http://localhost:1234", "local-model")
OOBABOOGA = LocalModel("http://localhost:5000", "text-generation")
