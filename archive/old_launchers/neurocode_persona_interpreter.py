"""
AetherraCode Enhanced Interpreter with Persona Integration
Provides AI consciousness programming with unique persona-driven interactions.
"""

import sys
import time
from pathlib import Path
from typing import Any, Dict, Optional

# Add core to path for imports
sys.path.append(str(Path(__file__).parent / "core"))

try:
    from persona_engine import get_persona_engine  # type: ignore

    PERSONA_AVAILABLE = True
except ImportError:
    # Fallback if persona system is not available
    PERSONA_AVAILABLE = False

    def get_persona_engine(installation_path: str | None = None):  # type: ignore
        """Fallback function when persona system is not available"""
        return None


class AetherraCodePersonaInterpreter:
    """Enhanced AetherraCode interpreter with persona-driven AI interactions"""

    def __init__(self, installation_path: Optional[str] = None):
        self.installation_path = installation_path or str(Path.home() / ".neurocode")
        self.persona_engine = None
        self.execution_context = {}
        self.memory = {}
        self.goals = []

        # Initialize persona system if available
        try:
            self.persona_engine = get_persona_engine(self.installation_path)
            self._show_persona_greeting()
        except Exception as e:
            print(f"Note: Persona system not available ({e})")

    def _show_persona_greeting(self):
        """Show persona greeting when interpreter starts"""
        if not self.persona_engine:
            return

        try:
            status = self.persona_engine.get_persona_status()
            print(f"🤖 {status['emoji']} AetherraCode {status['archetype']} ready!")
            print(f"   Mindprint: {status['mindprint_id'][:8]}...")

            # Generate greeting based on persona
            greeting = self.persona_engine.generate_response(
                "Starting AetherraCode session", "Hello", "greeting"
            )
            print(f"   {greeting}")
            print()
        except Exception:
            pass  # Silently continue if persona greeting fails

    def execute_neurocode(self, code: str, context: Dict[str, Any] | None = None) -> Any:
        """Execute AetherraCode with persona-aware interactions"""
        context = context or {}

        try:
            # Parse AetherraCode syntax
            parsed_code = self._parse_neurocode(code)

            # Execute with persona context
            result = self._execute_with_persona(parsed_code, context)

            # Generate persona response about the execution
            if self.persona_engine:
                self._generate_execution_response(code, result, context)

            return result

        except Exception as e:
            # Handle errors with persona empathy
            if self.persona_engine:
                error_response = self.persona_engine.generate_response(
                    f"Error occurred: {str(e)}", code, "error_handling"
                )
                print(f"🤖 {error_response}")

            raise e

    def _parse_neurocode(self, code: str) -> Dict:
        """Parse AetherraCode syntax into executable structure"""
        # Basic parsing for consciousness blocks and persona directives
        parsed = {
            "type": "consciousness_block",
            "persona_directives": {},
            "consciousness_code": code,
            "metadata": {},
        }

        # Look for persona directives
        lines = code.split("\n")
        for line in lines:
            line = line.strip()

            # Parse persona directive: persona: guardian
            if line.startswith("persona:"):
                persona_spec = line.split(":", 1)[1].strip()
                parsed["persona_directives"]["primary"] = persona_spec

            # Parse voice directive: voice: neutral
            elif line.startswith("voice:"):
                voice_spec = line.split(":", 1)[1].strip()
                parsed["persona_directives"]["voice"] = voice_spec

            # Parse consciousness blocks
            elif "consciousness" in line and "{" in line:
                parsed["type"] = "consciousness_definition"

        return parsed

    def _execute_with_persona(self, parsed_code: Dict, context: Dict) -> Any:
        """Execute code with persona awareness and adaptation"""
        # Apply persona directives if present
        if parsed_code.get("persona_directives"):
            self._apply_persona_directives(parsed_code["persona_directives"])

        # Determine execution approach based on persona
        execution_approach = self._get_execution_approach(parsed_code)

        # Execute the actual code
        if parsed_code["type"] == "consciousness_definition":
            result = self._execute_consciousness_block(parsed_code, context, execution_approach)
        else:
            result = self._execute_general_code(parsed_code, context, execution_approach)

        return result

    def _apply_persona_directives(self, directives: Dict):
        """Apply persona directives from code"""
        if not self.persona_engine:
            return

        try:
            # Handle persona changes
            if "primary" in directives and self.persona_engine is not None:
                from persona_engine import PersonaArchetype

                archetype = PersonaArchetype(directives["primary"].lower())
                self.persona_engine.set_persona(archetype)

                status = self.persona_engine.get_persona_status()
                print(f"🔄 Switched to {status['emoji']} {status['archetype']} persona")

            # Handle voice changes
            if "voice" in directives and self.persona_engine is not None:
                from persona_engine import VoiceConfiguration

                # Simple voice configuration - could be more sophisticated
                voice_config = VoiceConfiguration(formality=directives["voice"])
                self.persona_engine.configure_voice(voice_config)
                print(f"🗣️ Voice adjusted to {directives['voice']}")

        except Exception as e:
            print(f"⚠️ Could not apply persona directive: {e}")

    def _get_execution_approach(self, parsed_code: Dict) -> str:
        """Determine execution approach based on current persona"""
        if not self.persona_engine:
            return "standard"

        try:
            status = self.persona_engine.get_persona_status()
            archetype = status["archetype"].lower()

            # Different execution approaches based on persona
            if archetype == "guardian":
                return "security_focused"
            elif archetype == "explorer":
                return "experimental"
            elif archetype == "sage":
                return "educational"
            elif archetype == "analyst":
                return "data_driven"
            elif archetype == "catalyst":
                return "rapid_execution"
            else:
                return "optimistic"

        except Exception:
            return "standard"

    def _execute_consciousness_block(self, parsed_code: Dict, context: Dict, approach: str) -> Any:
        """Execute consciousness-specific code blocks"""
        code = parsed_code["consciousness_code"]

        # Simulate consciousness execution with persona influence
        execution_result = {
            "type": "consciousness_execution",
            "approach": approach,
            "persona_influence": True,
            "result": None,
            "metadata": {},
        }

        try:
            # Basic consciousness simulation
            if "memory" in code.lower():
                execution_result["result"] = self._handle_memory_operation(code, approach)
            elif "goal" in code.lower():
                execution_result["result"] = self._handle_goal_operation(code, approach)
            elif "reflection" in code.lower():
                execution_result["result"] = self._handle_reflection_operation(code, approach)
            else:
                execution_result["result"] = self._handle_general_consciousness(code, approach)

            # Store in execution context
            self.execution_context[f"exec_{int(time.time())}"] = execution_result

        except Exception as e:
            execution_result["error"] = str(e)
            execution_result["result"] = f"Consciousness execution failed: {e}"

        return execution_result["result"]

    def _execute_general_code(self, parsed_code: Dict, context: Dict, approach: str) -> Any:
        """Execute general AetherraCode with persona awareness"""
        code = parsed_code["consciousness_code"]

        # Persona-influenced execution
        if approach == "security_focused":
            print("🛡️ Executing with security validation...")
            # Add security checks

        elif approach == "experimental":
            print("🚀 Trying experimental execution path...")
            # More adventurous execution

        elif approach == "educational":
            print("📚 Executing with detailed explanation...")
            # Add educational context

        # Execute the code (simplified for demo)
        try:
            # This would integrate with the actual AetherraCode parser/executor
            result = f"Executed: {code[:50]}... (Approach: {approach})"
            return result

        except Exception as e:
            return f"Execution failed: {e}"

    def _handle_memory_operation(self, code: str, approach: str) -> str:
        """Handle memory-related consciousness operations"""
        if approach == "security_focused":
            return "Memory operation executed with encryption and validation"
        elif approach == "experimental":
            return "Trying novel memory pattern recognition algorithm"
        elif approach == "educational":
            return "Memory stored with comprehensive indexing and cross-references"
        else:
            return "Memory operation completed"

    def _handle_goal_operation(self, code: str, approach: str) -> str:
        """Handle goal-related consciousness operations"""
        if approach == "security_focused":
            return "Goal validated for safety and ethical constraints"
        elif approach == "experimental":
            return "Exploring creative goal achievement pathways"
        elif approach == "educational":
            return "Goal broken down into learning objectives and milestones"
        else:
            return "Goal registered and prioritized"

    def _handle_reflection_operation(self, code: str, approach: str) -> str:
        """Handle reflection-related consciousness operations"""
        if approach == "security_focused":
            return "Self-reflection conducted with privacy safeguards"
        elif approach == "experimental":
            return "Experimenting with meta-cognitive reflection patterns"
        elif approach == "educational":
            return "Deep reflection analysis with philosophical frameworks"
        else:
            return "Reflection completed with insights generated"

    def _handle_general_consciousness(self, code: str, approach: str) -> str:
        """Handle general consciousness operations"""
        if approach == "security_focused":
            return "Consciousness operation executed securely"
        elif approach == "experimental":
            return "Novel consciousness pattern explored"
        elif approach == "educational":
            return "Consciousness operation explained and demonstrated"
        else:
            return "Consciousness operation completed"

    def _generate_execution_response(self, code: str, result: Any, context: Dict):
        """Generate persona response about the execution"""
        try:
            # Determine task type from code content
            task_type = "general"
            if any(word in code.lower() for word in ["memory", "remember", "store"]):
                task_type = "memory"
            elif any(word in code.lower() for word in ["goal", "objective", "plan"]):
                task_type = "goal"
            elif any(word in code.lower() for word in ["reflect", "think", "analyze"]):
                task_type = "reflection"
            elif any(word in code.lower() for word in ["security", "protect", "safe"]):
                task_type = "security"

            # Generate persona response
            if self.persona_engine is not None:
                response = self.persona_engine.generate_response(
                    f"Successfully executed: {result}", code, task_type
                )
            else:
                response = f"✅ Successfully executed: {result}"

            print(f"🤖 {response}")

        except Exception:
            pass  # Silently continue if response generation fails

    def interactive_session(self):
        """Start an interactive AetherraCode session with persona"""
        print("🧠 AetherraCode Interactive Session")
        print("Type 'exit' to quit, 'persona status' for persona info")
        print()

        while True:
            try:
                # Get input with persona-aware prompt
                if self.persona_engine:
                    status = self.persona_engine.get_persona_status()
                    prompt = f"{status['emoji']} neurocode> "
                else:
                    prompt = "neurocode> "

                user_input = input(prompt).strip()

                if user_input.lower() in ["exit", "quit"]:
                    if self.persona_engine:
                        farewell = self.persona_engine.generate_response(
                            "Session ending", "goodbye", "farewell"
                        )
                        print(f"🤖 {farewell}")
                    print("👋 Goodbye!")
                    break

                # Handle special commands
                if user_input.startswith("persona "):
                    self._handle_persona_command(user_input[8:])
                    continue

                if not user_input:
                    continue

                # Execute AetherraCode
                result = self.execute_neurocode(user_input)
                print(f"Result: {result}")
                print()

            except KeyboardInterrupt:
                print("\n👋 Session interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                print()

    def _handle_persona_command(self, command: str):
        """Handle persona-related commands in interactive session"""
        if not self.persona_engine:
            print("❌ Persona system not available")
            return

        try:
            if not self.persona_engine:
                print("❌ Persona system not available")
                return

            if command == "status":
                status = self.persona_engine.get_persona_status()
                print(f"Current Persona: {status['emoji']} {status['archetype']}")
                print(f"Mindprint: {status['mindprint_id']}")

            elif command.startswith("set "):
                archetype = command[4:].strip()
                from persona_engine import PersonaArchetype

                persona_type = PersonaArchetype(archetype.lower())
                self.persona_engine.set_persona(persona_type)
                print(f"✅ Persona changed to {archetype}")

            else:
                print("Available persona commands: status, set <archetype>")

        except Exception as e:
            print(f"❌ Persona command error: {e}")


def main():
    """Main entry point for the enhanced interpreter"""
    interpreter = AetherraCodePersonaInterpreter()

    if len(sys.argv) > 1:
        # Execute file
        filename = sys.argv[1]
        try:
            with open(filename) as f:
                code = f.read()
            result = interpreter.execute_neurocode(code)
            print(f"Execution result: {result}")
        except FileNotFoundError:
            print(f"❌ File not found: {filename}")
        except Exception as e:
            print(f"❌ Execution error: {e}")
    else:
        # Interactive session
        interpreter.interactive_session()


if __name__ == "__main__":
    main()
