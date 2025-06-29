<<<<<<< HEAD
#!/usr/bin/env python3
"""
🧬 NeuroCode Input Utilities
Robust input handling with EOF protection for all NeuroCode interfaces
"""

import sys
from typing import Optional, List, Callable, Any

def safe_input(prompt: str = "", fallback_message: str = "Input stream closed.") -> Optional[str]:
    """
    Safe input function that handles EOF gracefully
    
    Args:
        prompt: The input prompt to display
        fallback_message: Message to show when EOF is encountered
        
    Returns:
        User input string, or None if EOF is encountered
    """
    try:
        return input(prompt)
    except EOFError:
        print(f"\n{fallback_message}")
        return None
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        return None

def interactive_loop(prompt: str, process_func: Callable[[str], Any], 
                    exit_commands: Optional[List[str]] = None, 
                    eof_message: str = "Session ended.",
                    welcome_message: Optional[str] = None):
    """
    Generic interactive loop with robust input handling
    
    Args:
        prompt: Input prompt to display
        process_func: Function to process user input (takes string, returns result)
        exit_commands: List of commands that exit the loop (default: ['exit', 'quit'])
        eof_message: Message to show on EOF
        welcome_message: Optional welcome message to display
    """
    if exit_commands is None:
        exit_commands = ['exit', 'quit', 'bye']
    
    if welcome_message:
        print(welcome_message)
    
    while True:
        try:
            user_input = safe_input(prompt)
            
            # Handle EOF
            if user_input is None:
                print(f"👋 {eof_message}")
                break
                
            # Handle exit commands
            if user_input.lower().strip() in exit_commands:
                print("👋 Goodbye!")
                break
                
            # Skip empty input
            if not user_input.strip():
                continue
                
            # Process the input
            try:
                result = process_func(user_input.strip())
                if result is not None:
                    print(result)
            except Exception as e:
                print(f"❌ Error processing input: {e}")
                
        except KeyboardInterrupt:
            print(f"\n\n👋 {eof_message}")
            break
        except Exception as e:
            print(f"❌ Unexpected error: {e}")

def check_interactive_mode() -> bool:
    """
    Check if we're running in an interactive environment
    
    Returns:
        True if interactive, False if running in script/pipe mode
    """
    return sys.stdin.isatty() and sys.stdout.isatty()

def get_yes_no(prompt: str, default: bool = False) -> bool:
    """
    Get a yes/no response from user with EOF handling
    
    Args:
        prompt: Question to ask user
        default: Default value if user just presses enter or EOF occurs
        
    Returns:
        Boolean response from user
    """
    default_str = "Y/n" if default else "y/N"
    full_prompt = f"{prompt} ({default_str}): "
    
    response = safe_input(full_prompt)
    
    if response is None:  # EOF
        return default
        
    response = response.strip().lower()
    
    if not response:  # Empty input
        return default
        
    return response in ['y', 'yes', 'true', '1']

if __name__ == "__main__":
    # Demo of the utility functions
    print("🧬 NeuroCode Input Utilities Demo")
    print("=" * 40)
    
    def demo_processor(text):
        return f"You said: {text}"
    
    interactive_loop(
        prompt="Demo> ",
        process_func=demo_processor,
        welcome_message="Type anything to test robust input handling!\nType 'exit' to quit.",
        eof_message="Demo session ended."
    )
=======
#!/usr/bin/env python3
"""
🧬 NeuroCode Input Utilities
Robust input handling with EOF protection for all NeuroCode interfaces
"""

import sys
from typing import Optional, List, Callable, Any

def safe_input(prompt: str = "", fallback_message: str = "Input stream closed.") -> Optional[str]:
    """
    Safe input function that handles EOF gracefully
    
    Args:
        prompt: The input prompt to display
        fallback_message: Message to show when EOF is encountered
        
    Returns:
        User input string, or None if EOF is encountered
    """
    try:
        return input(prompt)
    except EOFError:
        print(f"\n{fallback_message}")
        return None
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        return None

def interactive_loop(prompt: str, process_func: Callable[[str], Any], 
                    exit_commands: Optional[List[str]] = None, 
                    eof_message: str = "Session ended.",
                    welcome_message: Optional[str] = None):
    """
    Generic interactive loop with robust input handling
    
    Args:
        prompt: Input prompt to display
        process_func: Function to process user input (takes string, returns result)
        exit_commands: List of commands that exit the loop (default: ['exit', 'quit'])
        eof_message: Message to show on EOF
        welcome_message: Optional welcome message to display
    """
    if exit_commands is None:
        exit_commands = ['exit', 'quit', 'bye']
    
    if welcome_message:
        print(welcome_message)
    
    while True:
        try:
            user_input = safe_input(prompt)
            
            # Handle EOF
            if user_input is None:
                print(f"👋 {eof_message}")
                break
                
            # Handle exit commands
            if user_input.lower().strip() in exit_commands:
                print("👋 Goodbye!")
                break
                
            # Skip empty input
            if not user_input.strip():
                continue
                
            # Process the input
            try:
                result = process_func(user_input.strip())
                if result is not None:
                    print(result)
            except Exception as e:
                print(f"❌ Error processing input: {e}")
                
        except KeyboardInterrupt:
            print(f"\n\n👋 {eof_message}")
            break
        except Exception as e:
            print(f"❌ Unexpected error: {e}")

def check_interactive_mode() -> bool:
    """
    Check if we're running in an interactive environment
    
    Returns:
        True if interactive, False if running in script/pipe mode
    """
    return sys.stdin.isatty() and sys.stdout.isatty()

def get_yes_no(prompt: str, default: bool = False) -> bool:
    """
    Get a yes/no response from user with EOF handling
    
    Args:
        prompt: Question to ask user
        default: Default value if user just presses enter or EOF occurs
        
    Returns:
        Boolean response from user
    """
    default_str = "Y/n" if default else "y/N"
    full_prompt = f"{prompt} ({default_str}): "
    
    response = safe_input(full_prompt)
    
    if response is None:  # EOF
        return default
        
    response = response.strip().lower()
    
    if not response:  # Empty input
        return default
        
    return response in ['y', 'yes', 'true', '1']

if __name__ == "__main__":
    # Demo of the utility functions
    print("🧬 NeuroCode Input Utilities Demo")
    print("=" * 40)
    
    def demo_processor(text):
        return f"You said: {text}"
    
    interactive_loop(
        prompt="Demo> ",
        process_func=demo_processor,
        welcome_message="Type anything to test robust input handling!\nType 'exit' to quit.",
        eof_message="Demo session ended."
    )
>>>>>>> 20a510e90c83aa50461841f557e9447d03056c8d
