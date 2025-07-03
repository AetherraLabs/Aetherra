#!/usr/bin/env python3
"""
Local AI Engine for Aetherra
Provides local model inference to reduce API dependency and increase performance
"""

import os
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Dict, List


@dataclass
class AIResponse:
    content: str
    confidence: float
    model_used: str
    processing_time: float
    tokens_used: int


class LocalAIEngine:
    """
    Advanced local AI engine supporting multiple models for 99% API independence
    """

    def __init__(self):
        self.local_models = {}
        self.embedding_model = None
        self.inference_pool = ThreadPoolExecutor(max_workers=4)
        self.model_cache = {}
        self.performance_metrics = {}

        # Try to initialize local models
        self._initialize_models()

    def _initialize_models(self):
        """Initialize local AI models with fallbacks"""
        print("[LocalAI] Initializing local AI models...")

        # Try Ollama first (most accessible)
        if self._init_ollama():
            print("✅ Ollama models available")

        # Try llama-cpp-python
        if self._init_llama_cpp():
            print("✅ LLaMA-cpp models available")

        # Try sentence transformers for embeddings
        if self._init_embeddings():
            print("✅ Embedding models available")

        # Fallback to lightweight models
        if not self.local_models:
            print("⚠️  No local models available, using mock AI")
            self.local_models["mock"] = self._mock_ai_response

    def _init_ollama(self) -> bool:
        """Initialize Ollama models if available"""
        try:
            import subprocess

            result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
            if result.returncode == 0:
                models = [
                    line.split()[0] for line in result.stdout.strip().split("\n")[1:]
                ]
                if models:
                    self.local_models["ollama"] = models
                    return True
        except Exception as e:
            print(f"[LocalAI] Ollama not available: {e}")
        return False

    def _init_llama_cpp(self) -> bool:
        """Initialize llama-cpp-python models"""
        try:
            from llama_cpp import Llama

            # Look for GGUF models in models directory
            models_dir = os.path.join(os.path.dirname(__file__), "..", "models")
            if os.path.exists(models_dir):
                for file in os.listdir(models_dir):
                    if file.endswith(".gguf"):
                        model_path = os.path.join(models_dir, file)
                        try:
                            model = Llama(
                                model_path=model_path,
                                n_ctx=2048,
                                n_threads=4,
                                verbose=False,
                            )
                            self.local_models[f"llama_cpp_{file}"] = model
                            print(f"✅ Loaded {file}")
                            return True
                        except Exception as e:
                            print(f"❌ Failed to load {file}: {e}")
        except ImportError:
            print("[LocalAI] llama-cpp-python not installed")
        except Exception as e:
            print(f"[LocalAI] LLaMA-cpp error: {e}")
        return False

    def _init_embeddings(self) -> bool:
        """Initialize embedding models"""
        try:
            from sentence_transformers import SentenceTransformer

            self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
            return True
        except Exception as e:
            print(f"[LocalAI] Embeddings not available: {e}")
        return False

    def generate_response(
        self, prompt: str, max_tokens: int = 512, temperature: float = 0.7
    ) -> AIResponse:
        """Generate response using best available local model"""
        start_time = time.time()

        # Try local models in order of preference
        for model_name, model in self.local_models.items():
            try:
                if model_name.startswith("ollama"):
                    response = self._ollama_generate(prompt, max_tokens, temperature)
                elif model_name.startswith("llama_cpp"):
                    response = self._llama_cpp_generate(
                        model, prompt, max_tokens, temperature
                    )
                elif model_name == "mock":
                    response = self._mock_ai_response(prompt)
                else:
                    continue

                processing_time = time.time() - start_time
                self._update_metrics(model_name, processing_time)

                return AIResponse(
                    content=response,
                    confidence=0.85,  # Local models get lower confidence
                    model_used=model_name,
                    processing_time=processing_time,
                    tokens_used=len(response.split()),
                )

            except Exception as e:
                print(f"[LocalAI] Model {model_name} failed: {e}")
                continue

        # Final fallback
        return AIResponse(
            content="[LocalAI] No models available for inference",
            confidence=0.0,
            model_used="none",
            processing_time=time.time() - start_time,
            tokens_used=0,
        )

    def _ollama_generate(self, prompt: str, max_tokens: int, temperature: float) -> str:
        """Generate using Ollama"""
        import subprocess

        # Use first available model
        model = (
            self.local_models["ollama"][0] if self.local_models["ollama"] else "llama2"
        )

        cmd = ["ollama", "run", model, "--num-ctx", str(max_tokens * 2), prompt]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return result.stdout.strip()

    def _llama_cpp_generate(
        self, model, prompt: str, max_tokens: int, temperature: float
    ) -> str:
        """Generate using llama-cpp-python"""
        response = model(
            prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            stop=["</s>", "\n\n"],
        )
        return response["choices"][0]["text"].strip()

    def _mock_ai_response(self, prompt: str) -> str:
        """Mock AI response when no models available"""
        responses = {
            "suggest fix": "Consider checking variable types and adding error handling.",
            "optimize": "This code could be optimized by caching results and reducing loop complexity.",
            "analyze": "The code appears to have good structure but could benefit from more documentation.",
            "explain": "This function processes data by iterating through items and applying transformations.",
        }

        # Simple keyword matching
        for key, response in responses.items():
            if key in prompt.lower():
                return response

        return "I understand your request. As a local AI model,
            I can help with code analysis,
            optimization suggestions,
            and general programming guidance."

    def create_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Create embeddings for semantic search"""
        if self.embedding_model:
            return self.embedding_model.encode(texts).tolist()
        else:
            # Simple fallback embedding (not semantic but functional)
            return [[hash(text) % 1000 / 1000.0 for _ in range(384)] for text in texts]

    def semantic_similarity(self, text1: str, text2: str) -> float:
        """Calculate semantic similarity between two texts"""
        if self.embedding_model:
            embeddings = self.embedding_model.encode([text1, text2])
            # Calculate cosine similarity
            import numpy as np

            return float(
                np.dot(embeddings[0], embeddings[1])
                / (np.linalg.norm(embeddings[0]) * np.linalg.norm(embeddings[1]))
            )
        else:
            # Simple word overlap fallback
            words1 = set(text1.lower().split())
            words2 = set(text2.lower().split())
            intersection = words1.intersection(words2)
            union = words1.union(words2)
            return len(intersection) / len(union) if union else 0.0

    def _update_metrics(self, model_name: str, processing_time: float):
        """Update performance metrics for model selection"""
        if model_name not in self.performance_metrics:
            self.performance_metrics[model_name] = []

        self.performance_metrics[model_name].append(processing_time)

        # Keep only last 100 measurements
        if len(self.performance_metrics[model_name]) > 100:
            self.performance_metrics[model_name] = self.performance_metrics[model_name][
                -100:
            ]

    def get_best_model(self) -> str:
        """Get the best performing model based on metrics"""
        if not self.performance_metrics:
            return list(self.local_models.keys())[0] if self.local_models else "none"

        avg_times = {}
        for model, times in self.performance_metrics.items():
            if times:  # Only include models with actual performance data
                avg_times[model] = sum(times) / len(times)

        if not avg_times:
            return list(self.local_models.keys())[0] if self.local_models else "none"

        return min(avg_times, key=lambda k: avg_times[k])

    def get_model_status(self) -> Dict:
        """Get status of all available models"""
        status = {
            "available_models": list(self.local_models.keys()),
            "embedding_available": self.embedding_model is not None,
            "best_model": self.get_best_model(),
            "performance_metrics": {
                model: {"avg_time": sum(times) / len(times), "samples": len(times)}
                for model, times in self.performance_metrics.items()
            },
        }
        return status

    def is_available(self) -> bool:
        """Check if any local AI models are available (excluding mock)."""
        return any(model != "mock" for model in self.local_models)

    def intent_to_code(self, intent: str) -> str:
        """Converts a natural language intent to Aetherra code using a local model."""
        if not self.is_available():
            return f"# [Local AI unavailable] Could not convert intent: {intent}"

        # This is a mock implementation.
        if "rest api" in intent.lower():
            return "http.server port: 8080, route: /api"
        else:
            return f"# TODO: Implement intent-to-code for: {intent}"


# Global instance
local_ai = LocalAIEngine()


def get_local_ai() -> LocalAIEngine:
    """Get the global local AI instance"""
    return local_ai


# Convenience functions for Aetherra integration
def local_ask_ai(prompt: str, max_tokens: int = 512, temperature: float = 0.7) -> str:
    """Ask local AI - convenience function"""
    response = local_ai.generate_response(prompt, max_tokens, temperature)
    return response.content


def local_analyze_code(code: str, filename: str = "") -> str:
    """Analyze code using local AI"""
    prompt = f"""
    Analyze this code for potential improvements, bugs, and optimization opportunities:

    Filename: {filename}
    Code:
    {code}

    Provide specific, actionable suggestions for improvement.
    """
    return local_ask_ai(prompt, max_tokens=1024, temperature=0.3)


def local_suggest_fix(error: str, context: str = "") -> str:
    """Suggest fix for error using local AI"""
    prompt = f"""
    Analyze this error and suggest a specific fix:

    Error: {error}
    Context: {context}

    Provide a clear, actionable solution.
    """
    return local_ask_ai(prompt, max_tokens=512, temperature=0.3)


def local_optimize_code(code: str, target: str = "performance") -> str:
    """Optimize code using local AI"""
    prompt = f"""
    Optimize this code for {target}:

    {code}

    Provide the optimized version with explanation of changes.
    """
    return local_ask_ai(prompt, max_tokens=1024, temperature=0.2)


if __name__ == "__main__":
    # Test the local AI engine
    print("🧠 Testing Local AI Engine")
    print("=" * 40)

    engine = get_local_ai()
    status = engine.get_model_status()

    print(f"Available models: {status['available_models']}")
    print(f"Best model: {status['best_model']}")
    print(f"Embeddings available: {status['embedding_available']}")

    # Test generation
    test_prompt = "Explain what makes Aetherra revolutionary"
    response = engine.generate_response(test_prompt)

    print("\nTest Response:")
    print(f"Model: {response.model_used}")
    print(f"Time: {response.processing_time:.2f}s")
    print(f"Content: {response.content[:200]}...")

    print("\n✅ Local AI Engine ready for Aetherra integration!")
