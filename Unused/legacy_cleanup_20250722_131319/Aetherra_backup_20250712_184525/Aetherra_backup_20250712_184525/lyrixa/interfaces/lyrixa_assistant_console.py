#!/usr/bin/env python3
"""
🖥️ LYRIXA ASSISTANT CONSOLE
============================

Console interface for Lyrixa AI Assistant.
Provides command-line interaction with the assistant including:
- Interactive chat mode
- Command execution
- Task management
- System status monitoring
- Batch processing
"""

import argparse
import asyncio
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Import Lyrixa assistant
try:
    from .lyrixa_assistant import LyrixaAssistant

    ASSISTANT_AVAILABLE = True
except ImportError as e:
    logger.warning(f"[WARN] Lyrixa Assistant not available: {e}")
    LyrixaAssistant = None
    ASSISTANT_AVAILABLE = False


class LyrixaConsole:
    """
    🖥️ Lyrixa Assistant Console

    Command-line interface for interacting with Lyrixa AI Assistant.
    Provides interactive chat, command execution, and system management.
    """

    def __init__(
        self,
        workspace_path: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize Lyrixa Console

        Args:
            workspace_path: Path to the workspace directory
            config: Configuration dictionary
        """
        self.workspace_path = workspace_path or str(Path.cwd())
        self.config = config or {}
        self.assistant = None
        self.is_running = False
        self.command_history = []
        self.session_start = datetime.now()

        # Console commands
        self.commands = {
            "/help": self._show_help,
            "/status": self._show_status,
            "/history": self._show_history,
            "/clear": self._clear_history,
            "/tasks": self._show_tasks,
            "/capabilities": self._show_capabilities,
            "/execute": self._execute_task,
            "/analyze": self._analyze_code,
            "/quit": self._quit,
            "/exit": self._quit,
        }

        logger.info(f"🖥️ Lyrixa Console initialized in: {self.workspace_path}")

    async def initialize(self) -> bool:
        """
        Initialize the console and assistant

        Returns:
            bool: True if initialization successful
        """
        try:
            if not ASSISTANT_AVAILABLE:
                print("[ERROR] Lyrixa Assistant not available")
                return False

            if not LyrixaAssistant:
                print("[ERROR] Lyrixa Assistant class not available")
                return False

            # Initialize assistant
            self.assistant = LyrixaAssistant(self.workspace_path, self.config)
            await self.assistant.initialize()

            print("✅ Lyrixa Assistant Console initialized")
            print(f"📁 Workspace: {self.workspace_path}")
            print(
                f"🕐 Session started: {self.session_start.strftime('%Y-%m-%d %H:%M:%S')}"
            )
            print("Type '/help' for available commands or start chatting!")
            print("-" * 60)

            return True

        except Exception as e:
            logger.error(f"[ERROR] Failed to initialize console: {e}")
            print(f"[ERROR] Initialization failed: {e}")
            return False

    async def run_interactive(self):
        """Run interactive console mode"""
        if not await self.initialize():
            return

        self.is_running = True
        print("🎙️ Lyrixa Assistant Console - Interactive Mode")
        print("Type your message or use /help for commands")

        while self.is_running:
            try:
                # Get user input
                user_input = input("\n🔵 You: ").strip()

                if not user_input:
                    continue

                # Add to command history
                self.command_history.append(
                    {
                        "timestamp": datetime.now().isoformat(),
                        "input": user_input,
                        "type": "command" if user_input.startswith("/") else "chat",
                    }
                )

                # Process command or chat
                if user_input.startswith("/"):
                    await self._process_command(user_input)
                else:
                    await self._process_chat(user_input)

            except KeyboardInterrupt:
                print("\n\n🔄 Shutting down...")
                break
            except EOFError:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                logger.error(f"[ERROR] Error in interactive mode: {e}")
                print(f"[ERROR] Error: {e}")

        await self._shutdown()

    async def _process_command(self, command_input: str):
        """Process console command"""
        parts = command_input.split()
        command = parts[0]
        args = parts[1:] if len(parts) > 1 else []

        if command in self.commands:
            await self.commands[command](args)
        else:
            print(f"[ERROR] Unknown command: {command}")
            print("Type '/help' for available commands")

    async def _process_chat(self, message: str):
        """Process chat message"""
        try:
            if not self.assistant:
                print("[ERROR] Assistant not initialized")
                return

            print("🟡 Lyrixa: Thinking...")

            # Send to assistant
            response = await self.assistant.chat(message)

            # Display response
            print(f"🟢 Lyrixa: {response}")

        except Exception as e:
            logger.error(f"[ERROR] Chat processing failed: {e}")
            print(f"[ERROR] Error processing message: {e}")

    async def _show_help(self, args: List[str]):
        """Show help information"""
        print("\n🆘 Lyrixa Assistant Console - Help")
        print("=" * 50)
        print("Available commands:")
        print("  /help          - Show this help message")
        print("  /status        - Show assistant status")
        print("  /history       - Show command history")
        print("  /clear         - Clear conversation history")
        print("  /tasks         - Show active tasks")
        print("  /capabilities  - Show assistant capabilities")
        print("  /execute <task> - Execute a task")
        print("  /analyze <code> - Analyze code")
        print("  /quit, /exit   - Exit the console")
        print("\nFor regular chat, just type your message without '/'")
        print("Example: 'Hello, how can you help me?'")
        print("-" * 50)

    async def _show_status(self, args: List[str]):
        """Show assistant status"""
        try:
            if not self.assistant:
                print("[ERROR] Assistant not initialized")
                return

            status = await self.assistant.get_status()

            print("\n📊 Assistant Status")
            print("=" * 30)
            print(f"Session ID: {status['session_id']}")
            print(f"Initialized: {status['initialized']}")
            print(f"Workspace: {status['workspace_path']}")
            print(
                f"Conversation History: {status['conversation_history_size']} messages"
            )
            print(f"Active Tasks: {status['active_tasks']}")
            print(f"Components: {status['components']}")
            print(f"Timestamp: {status['timestamp']}")

        except Exception as e:
            logger.error(f"[ERROR] Failed to get status: {e}")
            print(f"[ERROR] Error getting status: {e}")

    async def _show_history(self, args: List[str]):
        """Show command history"""
        print("\n📜 Command History")
        print("=" * 30)

        if not self.command_history:
            print("No commands in history")
            return

        # Show last 10 commands
        recent_history = self.command_history[-10:]
        for i, entry in enumerate(recent_history, 1):
            timestamp = entry["timestamp"]
            input_text = entry["input"]
            cmd_type = entry["type"]
            print(f"{i:2d}. [{timestamp}] ({cmd_type}) {input_text}")

    async def _clear_history(self, args: List[str]):
        """Clear conversation history"""
        if not self.assistant:
            print("[ERROR] Assistant not initialized")
            return

        await self.assistant.clear_conversation_history()
        print("✅ Conversation history cleared")

    async def _show_tasks(self, args: List[str]):
        """Show active tasks"""
        try:
            if not self.assistant:
                print("[ERROR] Assistant not initialized")
                return

            tasks = self.assistant.get_active_tasks()

            print("\n📋 Active Tasks")
            print("=" * 30)

            if not tasks:
                print("No active tasks")
                return

            for task_id, task in tasks.items():
                print(f"Task ID: {task_id}")
                print(f"  Type: {task.get('type', 'unknown')}")
                print(f"  Description: {task.get('description', 'No description')}")
                print(f"  Status: {task.get('status', 'unknown')}")
                print(f"  Created: {task.get('created_at', 'unknown')}")
                print("-" * 30)

        except Exception as e:
            logger.error(f"[ERROR] Failed to get tasks: {e}")
            print(f"[ERROR] Error getting tasks: {e}")

    async def _show_capabilities(self, args: List[str]):
        """Show assistant capabilities"""
        try:
            if not self.assistant:
                print("[ERROR] Assistant not initialized")
                return

            capabilities = await self.assistant.get_capabilities()

            print("\n🎯 Assistant Capabilities")
            print("=" * 30)

            for i, capability in enumerate(capabilities, 1):
                print(f"{i}. {capability}")

        except Exception as e:
            logger.error(f"[ERROR] Failed to get capabilities: {e}")
            print(f"[ERROR] Error getting capabilities: {e}")

    async def _execute_task(self, args: List[str]):
        """Execute a task"""
        if not args:
            print("[ERROR] Please provide a task description")
            print("Example: /execute Analyze the current project structure")
            return

        if not self.assistant:
            print("[ERROR] Assistant not initialized")
            return

        task_description = " ".join(args)

        try:
            print(f"🔄 Executing task: {task_description}")

            result = await self.assistant.execute_task(task_description)

            print("✅ Task completed!")
            print(f"Result: {result}")

        except Exception as e:
            logger.error(f"[ERROR] Task execution failed: {e}")
            print(f"[ERROR] Error executing task: {e}")

    async def _analyze_code(self, args: List[str]):
        """Analyze code"""
        if not args:
            print("[ERROR] Please provide code to analyze")
            print("Example: /analyze def hello(): print('Hello, world!')")
            return

        if not self.assistant:
            print("[ERROR] Assistant not initialized")
            return

        code = " ".join(args)

        try:
            print(f"🔍 Analyzing code: {code}")

            result = await self.assistant.analyze_code(code)

            print("✅ Code analysis completed!")
            print(f"Analysis: {result}")

        except Exception as e:
            logger.error(f"[ERROR] Code analysis failed: {e}")
            print(f"[ERROR] Error analyzing code: {e}")

    async def _quit(self, args: List[str]):
        """Quit the console"""
        print("👋 Goodbye!")
        self.is_running = False

    async def _shutdown(self):
        """Shutdown the console"""
        try:
            if self.assistant:
                await self.assistant.shutdown()

            session_duration = datetime.now() - self.session_start
            print("\n📊 Session Summary")
            print(f"Duration: {session_duration}")
            print(f"Commands processed: {len(self.command_history)}")
            print("✅ Console shutdown complete")

        except Exception as e:
            logger.error(f"[ERROR] Shutdown failed: {e}")

    async def run_batch_command(self, command: str, args: List[str]) -> Dict[str, Any]:
        """
        Run a single batch command

        Args:
            command: Command to execute
            args: Command arguments

        Returns:
            Dict: Command result
        """
        if not await self.initialize():
            return {"error": "Failed to initialize assistant"}

        try:
            if not self.assistant:
                return {"error": "Assistant not initialized"}

            if command == "chat":
                message = " ".join(args)
                response = await self.assistant.chat(message)
                return {"response": response}

            elif command == "execute":
                task = " ".join(args)
                result = await self.assistant.execute_task(task)
                return {"result": result}

            elif command == "analyze":
                code = " ".join(args)
                result = await self.assistant.analyze_code(code)
                return {"analysis": result}

            elif command == "status":
                status = await self.assistant.get_status()
                return {"status": status}

            else:
                return {"error": f"Unknown command: {command}"}

        except Exception as e:
            logger.error(f"[ERROR] Batch command failed: {e}")
            return {"error": str(e)}
        finally:
            await self._shutdown()


async def main():
    """Main console entry point"""
    parser = argparse.ArgumentParser(description="Lyrixa Assistant Console")
    parser.add_argument("--workspace", "-w", help="Workspace directory path")
    parser.add_argument("--command", "-c", help="Single command to execute")
    parser.add_argument("--batch", "-b", help="Batch mode with command file")
    parser.add_argument(
        "--debug", "-d", action="store_true", help="Enable debug logging"
    )

    args = parser.parse_args()

    # Set logging level
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    # Create console
    console = LyrixaConsole(workspace_path=args.workspace)

    try:
        if args.command:
            # Single command mode
            parts = args.command.split()
            command = parts[0]
            command_args = parts[1:] if len(parts) > 1 else []

            result = await console.run_batch_command(command, command_args)
            print(f"Result: {result}")

        elif args.batch:
            # Batch mode (placeholder for future implementation)
            print("Batch mode not yet implemented")

        else:
            # Interactive mode
            await console.run_interactive()

    except KeyboardInterrupt:
        print("\n\n🔄 Interrupted by user")
    except Exception as e:
        logger.error(f"[ERROR] Console error: {e}")
        print(f"[ERROR] Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())


# Export main class
__all__ = ["LyrixaConsole"]
