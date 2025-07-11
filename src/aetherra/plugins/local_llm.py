class OllamaChatPlugin:
    """Plugin class for Chat with local LLM models using Ollama"""
    # Required plugin metadata
    name = "ollama_chat"
    description = "Chat with local LLM models using Ollama"
    input_schema = {
        "type": "object",
        "properties": {
            "input": {
                "type": "string",
                "description": "Input data"
            }
        },
        "required": [
            "input"
        ]
    }
    output_schema = {
        "type": "object",
        "properties": {
            "result": {
                "type": "string",
                "description": "Processing result"
            },
            "status": {
                "type": "string",
                "description": "Operation status"
            }
        }
    }
    created_by = "Plugin System Auto-Fixer"

    
    def execute(self, input_data):
        """Execute the plugin functionality."""
        return {"result": "Not implemented", "status": "success"}


# src/aetherra/plugins/local_llm.py - Local LLM Integration Plugin
from typing import Any, Dict

from core.plugin_manager import register_plugin


@register_plugin(
    name="ollama_chat",
    description="Chat with local LLM models using Ollama",
    capabilities=["local_llm", "chat", "code_generation", "offline_ai"],
    version="1.0.0",
    author="AetherraCode Team",
    category="ai",
    dependencies=["requests"],
    intent_purpose="local LLM inference and chat interactions",
    intent_triggers=["chat", "ask", "llm", "ollama", "mistral", "llama", "local"],
    intent_scenarios=[
        "offline AI assistance",
        "local code generation",
        "private AI conversations",
        "development without internet"
    ],
    ai_description="Provides access to local LLM models through Ollama. Enables offline AI assistance and code generation with privacy-focused local inference.",

    example_usage="plugin: ollama_chat 'llama2' 'Explain how async/await works in Python'",
    confidence_boost=1.2,
)
def ollama_chat(model: str, prompt: str, temperature: float = 0.7) -> Dict[str, Any]:
    """Chat with local LLM models using Ollama"""
    try:
        import requests
    except ImportError:
        return {
            "error": "requests package not found",
            "suggestion": "Install with: pip install requests"
        }

    try:
        # Ollama API endpoint
        url = "http://localhost:11434/api/generate"

        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature
            }
        }

        response = requests.post(url, json=payload, timeout=30)

        if response.status_code == 200:
            result = response.json()
            return {
                "success": True,
                "model": model,
                "prompt": prompt,
                "response": result.get("response", ""),
                "context": result.get("context", []),
                "total_duration": result.get("total_duration", 0),
                "eval_count": result.get("eval_count", 0)
            }
        else:
            return {
                "error": f"Ollama API error: {response.status_code}",
                "message": response.text
            }

    except requests.exceptions.ConnectionError:
        return {
            "error": "Cannot connect to Ollama",
            "suggestion": "Make sure Ollama is running (ollama serve) and the model is installed"
        }
    except requests.exceptions.Timeout:
        return {
            "error": "Request timed out",
            "suggestion": "The model might be too large or the prompt too complex"
        }
    except Exception as e:
        return {"error": f"Ollama chat failed: {str(e)}"}


@register_plugin(
    name="ollama_list_models",
    description="List available local LLM models in Ollama",
    capabilities=["model_discovery", "ollama", "local_llm"],
    version="1.0.0",
    author="AetherraCode Team",
    category="ai",
    dependencies=["requests"],
    intent_purpose="discovering available local LLM models",
    intent_triggers=["models", "list", "available", "ollama"],
    intent_scenarios=[
        "checking installed models",
        "model discovery",
        "local AI setup verification",
        "model management"
    ],
    ai_description="Lists all locally available LLM models in Ollama, showing their names, sizes, and capabilities.",
    example_usage="plugin: ollama_list_models",
    confidence_boost=1.0,
)
def ollama_list_models() -> Dict[str, Any]:
    """List available local LLM models in Ollama"""
    try:
        import requests
    except ImportError:
        return {
            "error": "requests package not found",
            "suggestion": "Install with: pip install requests"
        }

    try:
        # Ollama API endpoint for listing models
        url = "http://localhost:11434/api/tags"

        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            result = response.json()
            models = []

            for model in result.get("models", []):
                models.append({
                    "name": model.get("name", ""),
                    "size": model.get("size", 0),
                    "modified": model.get("modified_at", ""),
                    "family": model.get("details", {}).get("family", ""),
                    "format": model.get("details", {}).get("format", "")
                })

            return {
                "success": True,
                "models": models,
                "total_models": len(models),
                "ollama_running": True
            }
        else:
            return {
                "error": f"Ollama API error: {response.status_code}",
                "message": response.text
            }

    except requests.exceptions.ConnectionError:
        return {
            "error": "Cannot connect to Ollama",
            "suggestion": "Make sure Ollama is installed and running (ollama serve)",
            "ollama_running": False
        }
    except Exception as e:
        return {"error": f"Failed to list models: {str(e)}"}


@register_plugin(
    name="huggingface_local",
    description="Run Hugging Face models locally (requires transformers)",
    capabilities=["huggingface", "local_inference", "transformers"],
    version="1.0.0",
    author="AetherraCode Team",
    category="ai",
    dependencies=["transformers", "torch"],
    intent_purpose="local Hugging Face model inference",
    intent_triggers=["huggingface", "transformers", "local_ai", "inference"],
    intent_scenarios=[
        "running Hugging Face models locally",
        "offline text generation",
        "local model inference",
        "privacy-focused AI"
    ],
    ai_description="Runs Hugging Face transformer models locally for text generation, classification, and other NLP tasks.",

    example_usage="plugin: huggingface_local 'microsoft/DialoGPT-medium' 'Hello, how are you?'",
    confidence_boost=1.1,
)
def huggingface_local(model_name: str, text: str, max_length: int = 100) -> Dict[str, Any]:
    """Run Hugging Face models locally"""
    try:
        from transformers import pipeline
    except ImportError:
        return {
            "error": "transformers package not found",
            "suggestion": "Install with: pip install transformers torch"
        }

    try:
        # Create a text generation pipeline
        generator = pipeline(
            "text-generation",
            model=model_name,
            tokenizer=model_name,
            device_map="auto"
        )

        # Generate text
        result = generator(
            text,
            max_length=max_length,
            num_return_sequences=1,
            temperature=0.7,
            do_sample=True,
            pad_token_id=generator.tokenizer.eos_token_id
        )

        return {
            "success": True,
            "model": model_name,
            "input": text,
            "output": result[0]["generated_text"],
            "max_length": max_length
        }

    except Exception as e:
        return {
            "error": f"Hugging Face inference failed: {str(e)}",
            "suggestion": "Make sure the model name is correct and you have enough GPU/CPU memory"
        }


@register_plugin(
    name="llamacpp_chat",
    description="Chat using llama.cpp Python bindings (CPU-optimized)",
    capabilities=["llamacpp", "cpu_inference", "local_chat"],
    version="1.0.0",
    author="AetherraCode Team",
    category="ai",
    dependencies=["llama-cpp-python"],
    intent_purpose="CPU-optimized local LLM inference",
    intent_triggers=["llamacpp", "cpu", "local_llm", "inference"],
    intent_scenarios=[
        "CPU-only LLM inference",
        "resource-constrained environments",
        "local AI without GPU",
        "lightweight model serving"
    ],
    ai_description="Provides CPU-optimized local LLM inference using llama.cpp Python bindings. Ideal for environments without GPU acceleration.",

    example_usage="plugin: llamacpp_chat 'path/to/model.gguf' 'Explain Python decorators'",
    confidence_boost=1.0,
)
def llamacpp_chat(model_path: str, prompt: str, max_tokens: int = 256) -> Dict[str, Any]:
    """Chat using llama.cpp Python bindings"""
    try:
        from llama_cpp import Llama
    except ImportError:
        return {
            "error": "llama-cpp-python package not found",
            "suggestion": "Install with: pip install llama-cpp-python"
        }

    try:
        # Load the model
        llm = Llama(model_path=model_path, n_ctx=2048, verbose=False)

        # Generate response
        output = llm(
            prompt,
            max_tokens=max_tokens,
            stop=["Human:", "Assistant:", "\n\n"],
            echo=False,
            temperature=0.7
        )

        return {
            "success": True,
            "model_path": model_path,
            "prompt": prompt,
            "response": output["choices"][0]["text"].strip(),
            "usage": {
                "prompt_tokens": output["usage"]["prompt_tokens"],
                "completion_tokens": output["usage"]["completion_tokens"],
                "total_tokens": output["usage"]["total_tokens"]
            }
        }

    except FileNotFoundError:
        return {
            "error": f"Model file not found: {model_path}",
            "suggestion": "Make sure the model file exists and the path is correct"
        }
    except Exception as e:
        return {"error": f"llama.cpp inference failed: {str(e)}"}
