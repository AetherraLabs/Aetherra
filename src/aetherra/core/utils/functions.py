# core/functions.py
import json
import os


class AetherraFunctions:
    """Manages user-defined Aetherra functions"""

    def __init__(self, function_file="Aetherra_functions.json"):
        self.functions = {}
        self.function_file = function_file
        self.load_functions()

    def define_function(self, func_name, params, commands):
        """Define a new Aetherra function"""
        self.functions[func_name] = {"params": params, "commands": commands}
        self.save_functions()
        return f"[Function] Defined '{func_name}' with parameters: {', '.join(params) if params else 'none'}"

    def call_function(self, func_name, args, executor_callback):
        """Execute a user-defined function with given arguments"""
        if func_name not in self.functions:
            return f"[Function] Function '{func_name}' not defined"

        func = self.functions[func_name]
        params = func["params"]
        commands = func["commands"]

        # Check parameter count
        if len(args) != len(params):
            return f"[Function] Error: {func_name} expects {len(params)} arguments, got {len(args)}"

        # Create parameter substitution map
        param_map = dict(zip(params, args))

        # Substitute parameters in commands
        processed_commands = commands
        for param, arg in param_map.items():
            processed_commands = processed_commands.replace(f"${param}", arg)

        print(f"[Function] Executing '{func_name}' with args: {', '.join(args)}")

        # Execute each command in the function
        command_lines = [
            cmd.strip() for cmd in processed_commands.split(";") if cmd.strip()
        ]
        for cmd in command_lines:
            if cmd:
                print(f"  > {cmd}")
                executor_callback(cmd)

        return None

    def list_functions(self):
        """List all defined functions"""
        if not self.functions:
            return "[Functions] No functions defined"

        result = "[Functions] Defined functions:\n"
        for name, func in self.functions.items():
            params_str = ", ".join(func["params"]) if func["params"] else "none"
            result += f"  {name}({params_str})\n"
            result += f"    Commands: {func['commands'][:50]}{'...' if len(func['commands']) > 50 else ''}\n"
        return result.strip()

    def show_function(self, func_name):
        """Show details of a specific function"""
        if func_name not in self.functions:
            return f"[Function] Function '{func_name}' not found"

        func = self.functions[func_name]
        result = f"[Function] {func_name}({', '.join(func['params'])})\n"
        result += f"Commands: {func['commands']}"
        return result

    def delete_function(self, func_name):
        """Delete a function"""
        if func_name not in self.functions:
            return f"[Function] Function '{func_name}' not found"

        del self.functions[func_name]
        self.save_functions()
        return f"[Function] Deleted function '{func_name}'"

    def save_functions(self):
        """Save functions to persistent storage"""
        try:
            with open(self.function_file, "w") as f:
                json.dump(self.functions, f, indent=2)
        except Exception as e:
            print(f"[Function] Warning: Could not save functions: {e}")

    def load_functions(self):
        """Load functions from persistent storage"""
        try:
            if os.path.exists(self.function_file):
                with open(self.function_file, "r") as f:
                    self.functions = json.load(f)
                print(f"[Function] Loaded {len(self.functions)} saved functions")
        except Exception as e:
            print(f"[Function] Warning: Could not load functions: {e}")
            self.functions = {}

    def get_function_count(self):
        """Get the number of defined functions"""
        return len(self.functions)

    def get_function_names(self):
        """Get list of function names"""
        return list(self.functions.keys())
