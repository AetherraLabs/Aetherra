#!/usr/bin/env python3
"""
🧠 Natural-to-NeuroCode Translator
=================================

Revolutionary AI-powered translator that converts natural language
into executable NeuroCode, making AI-native programming accessible
to everyone.

Examples:
- "Fix any recurring memory errors" → memory.pattern("memory error"); suggest fix; apply fix
- "Remember this conversation" → remember("conversation content") as "dialogue,important"
- "Find patterns in my data" → detect patterns; memory summary

This is the bridge between human intent and AI-native execution.
"""

import json
import re
import sys
from pathlib import Path
from typing import Callable, Dict, List, Tuple, Union

# Add core modules to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "core"))

try:
    from memory import AetherraMemory
except ImportError:
    print("⚠️ Memory module not available, running in limited mode")
    AetherraMemory = None


class NaturalToNeuroTranslator:
    """Translates natural language to NeuroCode"""

    def __init__(self):
        self.memory = AetherraMemory() if AetherraMemory else None
        self.translation_patterns = self._load_translation_patterns()
        self.context_memory = []  # Store conversation context

    def _load_translation_patterns(self) -> Dict[str, Union[str, Callable]]:
        """Load patterns for natural language to NeuroCode translation"""
        return {
            # Memory operations
            r"remember (?:this |that |the )?(.+?)(?:\s+as\s+(.+))?": lambda m: f'remember("{m.group(1)}") as "{m.group(2) or "general"}"',

            r"(?:recall|find|get) (?:memories )?(?:about |with |tagged )?(.+)": lambda m: f'recall tag: "{m.group(1)}"',
            r"forget (?:about )?(.+)": lambda m: f'forget tag: "{m.group(1)}"',
            # Pattern detection
            r"(?:find|detect|look for) patterns?(?:\s+in\s+(.+))?": lambda m: "detect patterns"
            + (f' in "{m.group(1)}"' if m.group(1) else ""),
            r"(?:analyze|examine|study) (?:my )?(?:memory|memories|data)": lambda m: "memory summary; detect patterns",
            # Problem solving
            r"fix (?:any )?(?:recurring )?(.+?)(?:\s+errors?)?": lambda m: f'if memory.pattern("{m.group(1)} error"): suggest fix; apply fix',

            r"solve (?:the )?(.+?)(?:\s+problem)?": lambda m: f'analyze problem: "{m.group(1)}"; suggest solution; execute solution',

            r"debug (?:the )?(.+)": lambda m: f'debug "{m.group(1)}"; suggest fix',
            # Learning and improvement
            r"learn (?:from )?(.+)": lambda m: f'remember("{m.group(1)}") as "learning,
                experience"; reflect on tags="learning"',

            r"improve (?:my )?(.+)": lambda m: f'analyze "{m.group(1)}"; suggest improvements; apply improvements',
            # Reflection and analysis
            r"(?:think about|reflect on|consider) (.+)": lambda m: f'reflect on tags="{m.group(1)}"',
            r"what (?:do I know|have I learned) about (.+)": lambda m: f'recall tag: "{m.group(1)}"; memory summary',
            r"show me (?:my )?(?:memories about |everything about )?(.+)": lambda m: f'recall tag: "{m.group(1)}"; display results',

            # Automation and actions
            r"automatically (.+)": lambda m: f"auto_execute: {self._translate_action(m.group(1))}",
            r"when (.+?) (?:happens|occurs),
                (.+)": lambda m: f'when "{m.group(1)}": {self._translate_action(m.group(2))}',

            r"if (.+?), (?:then )?(.+)": lambda m: f'if "{m.group(1)}": {self._translate_action(m.group(2))}',
            # Plugin operations
            r"use (?:the )?(.+?) plugin (?:to )?(.+)": lambda m: f'call plugin: "{m.group(1)}" with task: "{m.group(2)}"',

            r"calculate (.+)": lambda m: f'call plugin: "math_plugin" with expression: "{m.group(1)}"',
            # Meta-operations
            r"explain (?:what )?(?:you )?(?:just )?did": lambda m: "memory summary; reflection_summary",
            r"show (?:me )?(?:your )?status": lambda m: "system status; memory stats; agent status",
        }

    def _translate_action(self, action: str) -> str:
        """Translate a natural language action to NeuroCode"""
        # Simple action translations
        action_map = {
            "remember": "remember(this)",
            "save": "remember(this)",
            "store": "remember(this)",
            "alert": "notify('alert')",
            "notify": "notify(this)",
            "log": "remember(this) as 'log'",
            "analyze": "reflect on tags=this",
            "fix": "suggest fix; apply fix",
        }

        for key, value in action_map.items():
            if key in action.lower():
                return value.replace("this", f'"{action}"')

        return f'execute: "{action}"'

    def translate(self, natural_input: str) -> str:
        """Translate natural language to NeuroCode with comprehensive error handling"""
        # Input validation
        if not natural_input or not isinstance(natural_input, str):
            raise ValueError("Input must be a non-empty string")

        if len(natural_input.strip()) == 0:
            raise ValueError("Input cannot be empty or whitespace only")

        if len(natural_input) > 1000:  # Reasonable limit
            raise ValueError("Input too long (max 1000 characters)")

        try:
            # Store context
            self.context_memory.append(natural_input)

            # Clean input
            cleaned_input = natural_input.strip().lower()

            # Try each pattern
            for pattern, transformer in self.translation_patterns.items():
                try:
                    match = re.search(pattern, cleaned_input, re.IGNORECASE)
                    if match:
                        if callable(transformer):
                            neurocode = transformer(match)
                        else:
                            neurocode = str(transformer)

                        # Validate generated NeuroCode
                        if not neurocode or len(neurocode.strip()) == 0:
                            continue  # Try next pattern

                        # Add translation to memory for learning
                        if self.memory:
                            try:
                                self.memory.remember(
                                    f"Translated '{natural_input}' to '{neurocode}'",
                                    ["translation", "natural-language", "neurocode"],
                                )
                            except Exception as e:
                                print(f"⚠️ Failed to store translation in memory: {e}")

                        return neurocode

                except re.error as e:
                    print(f"⚠️ Regex error in pattern '{pattern}': {e}")
                    continue
                except Exception as e:
                    print(f"⚠️ Translation error with pattern '{pattern}': {e}")
                    continue

            # If no pattern matches, try AI-assisted translation
            return self._ai_assisted_translation(natural_input)

        except Exception as e:
            print(f"❌ Critical translation error: {e}")
            return f'# Translation failed for: "{natural_input}"\n# Error: {str(e)}\n# Fallback: remember("{natural_input}") as "general"'

    def _ai_assisted_translation(self, input_text: str) -> str:
        """Fallback AI-assisted translation for complex inputs"""
        # For now, provide a generic translation
        # In the future, this could use an LLM for more sophisticated translation

        # Extract key concepts
        concepts = self._extract_concepts(input_text)

        if not concepts:
            return f'# Natural input: "{input_text}"\n# TODO: Add specific NeuroCode translation'

        # Build NeuroCode based on concepts
        if "remember" in concepts or "save" in concepts or "store" in concepts:
            return f'remember("{input_text}") as "general"'
        elif "find" in concepts or "search" in concepts or "recall" in concepts:
            return 'recall tag: "general"'
        elif "analyze" in concepts or "pattern" in concepts:
            return "detect patterns; memory summary"
        else:
            return f'# Natural input: "{input_text}"\n# Suggested NeuroCode:\nremember("{input_text}") as "general"'

    def _extract_concepts(self, text: str) -> List[str]:
        """Extract key concepts from natural language"""
        # Simple keyword extraction
        keywords = [
            "remember",
            "save",
            "store",
            "keep",
            "record",
            "find",
            "search",
            "recall",
            "get",
            "retrieve",
            "analyze",
            "pattern",
            "detect",
            "discover",
            "fix",
            "solve",
            "debug",
            "repair",
            "improve",
            "learn",
            "understand",
            "study",
            "explore",
            "think",
            "reflect",
            "consider",
            "ponder",
        ]

        found_concepts = []
        text_lower = text.lower()

        for keyword in keywords:
            if keyword in text_lower:
                found_concepts.append(keyword)

        return found_concepts

    def interactive_translate(self):
        """Interactive translation session"""
        print("🧠 Natural-to-NeuroCode Translator")
        print("=" * 50)
        print("Type natural language and I'll convert it to NeuroCode!")
        print("Examples:")
        print("  • 'Remember this conversation'")
        print("  • 'Fix any recurring memory errors'")
        print("  • 'Find patterns in my data'")
        print("Type 'quit' to exit.\n")

        while True:
            try:
                user_input = input("🗣️  Natural: ").strip()

                if user_input.lower() in ["quit", "exit", "q"]:
                    print("👋 Translation session ended!")
                    break

                if not user_input:
                    continue

                neurocode = self.translate(user_input)
                print(f"🧬 NeuroCode: {neurocode}")

                # Ask if user wants to execute
                execute = input("🚀 Execute this NeuroCode? (y/n): ").strip().lower()
                if execute in ["y", "yes"]:
                    self._execute_neurocode(neurocode)

                print()  # Empty line for readability

            except KeyboardInterrupt:
                print("\n👋 Translation session ended!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

    def _execute_neurocode(self, neurocode: str):
        """Execute the generated NeuroCode"""
        try:
            # Import the standalone runner
            from scripts.aether_runner_standalone import StandaloneNeuroRunner

            runner = StandaloneNeuroRunner(verbose=True)

            # Create temporary file
            temp_file = Path(__file__).parent / "temp_translation.aether"
            temp_file.write_text(neurocode, encoding="utf-8")

            # Execute
            print("⚡ Executing...")
            results = runner.run_file(str(temp_file))

            # Clean up
            if temp_file.exists():
                temp_file.unlink()

            if results.get("success"):
                print("✅ Execution successful!")
            else:
                print("❌ Execution failed")

        except Exception as e:
            print(f"❌ Execution error: {e}")

    def batch_translate(self, natural_inputs: List[str]) -> List[Tuple[str, str]]:
        """Translate multiple natural language inputs"""
        results = []
        for input_text in natural_inputs:
            neurocode = self.translate(input_text)
            results.append((input_text, neurocode))
        return results

    def save_translations(self, filename: str = "translations.json"):
        """Save translation history"""
        if self.memory:
            translations = self.memory.recall(tags=["translation"])
            with open(filename, "w") as f:
                json.dump(translations, f, indent=2)
            print(f"💾 Saved {len(translations)} translations to {filename}")


def main():
    """Main function for CLI usage"""
    import argparse

    parser = argparse.ArgumentParser(description="Natural-to-NeuroCode Translator")
    parser.add_argument(
        "--interactive",
        "-i",
        action="store_true",
        help="Start interactive translation session",
    )
    parser.add_argument(
        "--translate", "-t", type=str, help="Translate a single natural language input"
    )
    parser.add_argument(
        "--batch", "-b", type=str, help="Batch translate from file (one input per line)"
    )
    parser.add_argument(
        "--execute", "-e", action="store_true", help="Execute the translated NeuroCode"
    )

    args = parser.parse_args()

    translator = NaturalToNeuroTranslator()

    if args.interactive:
        translator.interactive_translate()
    elif args.translate:
        neurocode = translator.translate(args.translate)
        print(f"🧬 NeuroCode: {neurocode}")
        if args.execute:
            translator._execute_neurocode(neurocode)
    elif args.batch:
        try:
            with open(args.batch) as f:
                inputs = [line.strip() for line in f if line.strip()]

            results = translator.batch_translate(inputs)
            for natural, neurocode in results:
                print(f"🗣️  {natural}")
                print(f"🧬 {neurocode}\n")
        except FileNotFoundError:
            print(f"❌ File not found: {args.batch}")
    else:
        print("🧠 Natural-to-NeuroCode Translator")
        print("Use --help for options or --interactive for live translation")


if __name__ == "__main__":
    main()
