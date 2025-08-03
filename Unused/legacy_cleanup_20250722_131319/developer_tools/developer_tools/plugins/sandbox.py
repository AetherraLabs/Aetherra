"""
Plugin Sandbox Environment - Isolated Plugin Testing

This module provides a safe, isolated environment for testing plugins
without affecting the live Aetherra & Lyrixa system. Features include
memory simulation, step-through debugging, resource monitoring,
and complete isolation from the production environment.

Key Features:
- Complete isolation from live system
- Memory simulation and mocking
- Step-through debugging capabilities
- Resource usage monitoring
- Plugin dependency management
- Safe execution context
- Test result reporting
"""

import os
import sys
import json
import time
import psutil
import threading
import traceback
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable, TYPE_CHECKING, Union
from contextlib import contextmanager
import tempfile
import shutil

GUI_AVAILABLE = False

if TYPE_CHECKING:
    import tkinter as tk
    from tkinter import ttk, messagebox, scrolledtext
else:
    # Runtime imports
    try:
        import tkinter as tk
        from tkinter import ttk, messagebox, scrolledtext
        GUI_AVAILABLE = True
    except ImportError:
        GUI_AVAILABLE = False
        # Create placeholder variables for runtime
        tk = ttk = messagebox = scrolledtext = None

class SandboxConfig:
    """Configuration for plugin sandbox"""

    def __init__(self):
        self.max_execution_time = 30  # seconds
        self.max_memory_usage = 100 * 1024 * 1024  # 100MB
        self.max_cpu_percent = 50  # 50% CPU
        self.allow_network = False
        self.allow_file_system = False
        self.allow_subprocesses = False
        self.sandbox_directory = Path("sandbox")
        self.log_file = "sandbox.log"
        self.enable_step_debugging = True
        self.capture_stdout = True
        self.capture_stderr = True

class MockMemorySystem:
    """Mock memory system for sandbox testing"""

    def __init__(self):
        self.memories = {}
        self.access_log = []
        self._locked = False

    def store_memory(self, key: str, value: Any) -> bool:
        """Store memory in sandbox"""
        self.access_log.append(('store', key, datetime.now()))
        if not self._locked:
            self.memories[key] = value
            return True
        return False

    def get_memory(self, key: str) -> Any:
        """Get memory from sandbox"""
        self.access_log.append(('get', key, datetime.now()))
        return self.memories.get(key)

    def delete_memory(self, key: str) -> bool:
        """Delete memory from sandbox"""
        self.access_log.append(('delete', key, datetime.now()))
        if key in self.memories:
            del self.memories[key]
            return True
        return False

    def list_memories(self) -> List[str]:
        """List all memory keys"""
        self.access_log.append(('list', None, datetime.now()))
        return list(self.memories.keys())

    def clear_memories(self):
        """Clear all memories"""
        self.access_log.append(('clear', None, datetime.now()))
        self.memories.clear()

    def lock(self):
        """Lock memory system (simulate read-only mode)"""
        self._locked = True

    def unlock(self):
        """Unlock memory system"""
        self._locked = False

    def get_access_log(self) -> List[tuple]:
        """Get memory access log"""
        return self.access_log.copy()

class MockAgentSystem:
    """Mock agent system for sandbox testing"""

    def __init__(self):
        self.agents = {}
        self.messages = []
        self.active_agents = set()

    def create_agent(self, agent_id: str, config: Dict) -> bool:
        """Create mock agent"""
        self.agents[agent_id] = {
            'config': config,
            'created_at': datetime.now(),
            'status': 'created'
        }
        return True

    def start_agent(self, agent_id: str) -> bool:
        """Start mock agent"""
        if agent_id in self.agents:
            self.agents[agent_id]['status'] = 'running'
            self.active_agents.add(agent_id)
            return True
        return False

    def stop_agent(self, agent_id: str) -> bool:
        """Stop mock agent"""
        if agent_id in self.agents:
            self.agents[agent_id]['status'] = 'stopped'
            self.active_agents.discard(agent_id)
            return True
        return False

    def send_message(self, agent_id: str, message: str) -> bool:
        """Send message to mock agent"""
        if agent_id in self.active_agents:
            self.messages.append({
                'agent_id': agent_id,
                'message': message,
                'timestamp': datetime.now()
            })
            return True
        return False

    def get_agent_status(self, agent_id: str) -> Optional[str]:
        """Get agent status"""
        return self.agents.get(agent_id, {}).get('status')

    def list_agents(self) -> List[str]:
        """List all agents"""
        return list(self.agents.keys())

class ResourceMonitor:
    """Monitor resource usage during plugin execution"""

    def __init__(self, config: SandboxConfig):
        self.config = config
        self.process = None
        self.monitoring = False
        self.stats: Dict[str, float] = {
            'max_memory': 0.0,
            'max_cpu': 0.0,
            'execution_time': 0.0,
            'network_calls': 0.0,
            'file_operations': 0.0
        }
        self.violations = []

    def start_monitoring(self, process_id: int):
        """Start monitoring process"""
        try:
            self.process = psutil.Process(process_id)
            self.monitoring = True
            self._monitor_loop()
        except psutil.NoSuchProcess:
            pass

    def stop_monitoring(self):
        """Stop monitoring"""
        self.monitoring = False

    def _monitor_loop(self):
        """Main monitoring loop"""
        start_time = time.time()

        while self.monitoring and self.process and self.process.is_running():
            try:
                # Memory usage
                memory_info = self.process.memory_info()
                memory_mb = memory_info.rss / 1024 / 1024
                self.stats['max_memory'] = max(self.stats['max_memory'], memory_mb)

                # CPU usage
                cpu_percent = self.process.cpu_percent()
                self.stats['max_cpu'] = max(self.stats['max_cpu'], cpu_percent)

                # Execution time
                self.stats['execution_time'] = time.time() - start_time

                # Check violations
                if memory_mb > self.config.max_memory_usage / 1024 / 1024:
                    self.violations.append(f"Memory limit exceeded: {memory_mb:.1f}MB")

                if cpu_percent > self.config.max_cpu_percent:
                    self.violations.append(f"CPU limit exceeded: {cpu_percent:.1f}%")

                if self.stats['execution_time'] > self.config.max_execution_time:
                    self.violations.append(f"Execution time limit exceeded: {self.stats['execution_time']:.1f}s")
                    break

                time.sleep(0.1)  # Monitor every 100ms

            except (psutil.NoSuchProcess, psutil.AccessDenied):
                break

    def get_stats(self) -> Dict[str, Any]:
        """Get monitoring statistics"""
        return {
            **self.stats,
            'violations': self.violations.copy()
        }

class PluginSandbox:
    """Main plugin sandbox class"""

    def __init__(self, config: Optional[SandboxConfig] = None):
        self.config = config or SandboxConfig()
        self.sandbox_dir = self.config.sandbox_directory
        self.sandbox_dir.mkdir(exist_ok=True)

        # Mock systems
        self.mock_memory = MockMemorySystem()
        self.mock_agents = MockAgentSystem()

        # Monitoring
        self.resource_monitor = ResourceMonitor(self.config)

        # Test results
        self.test_results = []
        self.current_test = None

        # Step debugging
        self.debug_mode = False
        self.breakpoints = set()
        self.step_callback = None

        print(f"Plugin Sandbox initialized in {self.sandbox_dir}")

    def load_plugin(self, plugin_path: str) -> bool:
        """Load plugin into sandbox"""
        try:
            plugin_path_obj = Path(plugin_path)
            if not plugin_path_obj.exists():
                raise FileNotFoundError(f"Plugin not found: {plugin_path}")

            # Copy plugin to sandbox
            sandbox_plugin_path = self.sandbox_dir / plugin_path_obj.name
            shutil.copy2(plugin_path_obj, sandbox_plugin_path)

            print(f"Plugin loaded: {sandbox_plugin_path}")
            return True

        except Exception as e:
            print(f"Failed to load plugin: {e}")
            return False

    def run_plugin(self, plugin_name: str, function_name: str = "main",
                   args: Optional[List] = None, kwargs: Optional[Dict] = None) -> Dict[str, Any]:
        """Run plugin function in sandbox"""
        args = args or []
        kwargs = kwargs or {}

        test_result = {
            'plugin_name': plugin_name,
            'function_name': function_name,
            'start_time': datetime.now(),
            'success': False,
            'output': None,
            'error': None,
            'resource_stats': {},
            'memory_access_log': [],
            'agent_operations': []
        }

        self.current_test = test_result

        try:
            # Prepare sandbox environment
            self._setup_sandbox_environment()

            # Create isolated execution script
            script_path = self._create_execution_script(plugin_name, function_name, args, kwargs)

            # Run in subprocess for isolation
            process = subprocess.Popen(
                [sys.executable, "execute_plugin.py"],
                cwd=self.sandbox_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # Start monitoring
            if process.pid:
                monitor_thread = threading.Thread(
                    target=self.resource_monitor.start_monitoring,
                    args=(process.pid,)
                )
                monitor_thread.start()

            # Wait for completion with timeout
            try:
                stdout, stderr = process.communicate(timeout=self.config.max_execution_time)
                test_result['success'] = process.returncode == 0
                test_result['output'] = stdout
                if stderr:
                    test_result['error'] = stderr
            except subprocess.TimeoutExpired:
                process.kill()
                test_result['error'] = "Execution timeout"

            # Stop monitoring
            self.resource_monitor.stop_monitoring()

            # Collect results
            test_result['resource_stats'] = self.resource_monitor.get_stats()
            test_result['memory_access_log'] = self.mock_memory.get_access_log()
            test_result['end_time'] = datetime.now()
            test_result['duration'] = (test_result['end_time'] - test_result['start_time']).total_seconds()

        except Exception as e:
            test_result['error'] = str(e)
            test_result['end_time'] = datetime.now()

        self.test_results.append(test_result)
        self.current_test = None

        return test_result

    def _setup_sandbox_environment(self):
        """Setup sandbox environment"""
        # Clear previous state
        self.mock_memory.clear_memories()
        self.mock_agents = MockAgentSystem()

        # Create mock modules file
        mock_modules = {
            'memory_system': self.mock_memory,
            'agent_system': self.mock_agents
        }

        with open(self.sandbox_dir / 'mock_modules.py', 'w') as f:
            f.write("# Mock modules for sandbox testing\n")
            f.write("import json\n")
            f.write("from datetime import datetime\n\n")

            # Write mock classes
            f.write(self._generate_mock_code())

    def _generate_mock_code(self) -> str:
        """Generate mock module code"""
        return '''
class MemorySystem:
    def __init__(self):
        self.memories = {}

    def store_memory(self, key, value):
        self.memories[key] = value
        return True

    def get_memory(self, key):
        return self.memories.get(key)

    def delete_memory(self, key):
        if key in self.memories:
            del self.memories[key]
            return True
        return False

class AgentSystem:
    def __init__(self):
        self.agents = {}

    def create_agent(self, agent_id, config):
        self.agents[agent_id] = config
        return True

    def start_agent(self, agent_id):
        return agent_id in self.agents

# Global instances
memory_system = MemorySystem()
agent_system = AgentSystem()
'''

    def _create_execution_script(self, plugin_name: str, function_name: str,
                                args: List, kwargs: Dict) -> Path:
        """Create script for isolated plugin execution"""
        script_content = f'''
import sys
import json
import importlib.util
from pathlib import Path

# Import mock modules
sys.path.insert(0, str(Path(__file__).parent))
import mock_modules

# Load plugin
plugin_path = Path("{plugin_name}")
if not plugin_path.exists():
    print(f"Error: Plugin file {{plugin_path}} not found")
    sys.exit(1)

spec = importlib.util.spec_from_file_location(plugin_path.stem, plugin_path)
plugin_module = importlib.util.module_from_spec(spec)

# Replace real modules with mocks
plugin_module.memory_system = mock_modules.memory_system
plugin_module.agent_system = mock_modules.agent_system

try:
    spec.loader.exec_module(plugin_module)

    # Execute function
    if hasattr(plugin_module, "{function_name}"):
        func = getattr(plugin_module, "{function_name}")
        result = func(*{args}, **{kwargs})
        print(f"Result: {{result}}")
    else:
        print(f"Function '{function_name}' not found in plugin")

except Exception as e:
    import traceback
    print(f"Error: {{e}}")
    traceback.print_exc()
'''

        script_path = self.sandbox_dir / "execute_plugin.py"
        script_path.parent.mkdir(parents=True, exist_ok=True)
        with open(script_path, 'w') as f:
            f.write(script_content)

        return script_path

    def run_test_suite(self, test_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Run a complete test suite"""
        results = []

        for test_case in test_config.get('test_cases', []):
            plugin_name = test_case['plugin']
            function_name = test_case.get('function', 'main')
            args = test_case.get('args', [])
            kwargs = test_case.get('kwargs', {})

            print(f"Running test: {plugin_name}.{function_name}")
            result = self.run_plugin(plugin_name, function_name, args, kwargs)
            results.append(result)

        return results

    def enable_step_debugging(self, callback: Optional[Callable] = None):
        """Enable step-by-step debugging"""
        self.debug_mode = True
        self.step_callback = callback

    def disable_step_debugging(self):
        """Disable step debugging"""
        self.debug_mode = False
        self.step_callback = None

    def add_breakpoint(self, line_number: int):
        """Add breakpoint for debugging"""
        self.breakpoints.add(line_number)

    def remove_breakpoint(self, line_number: int):
        """Remove breakpoint"""
        self.breakpoints.discard(line_number)

    def generate_test_report(self) -> str:
        """Generate comprehensive test report"""
        if not self.test_results:
            return "No test results available."

        report = []
        report.append("# Plugin Sandbox Test Report")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Total Tests: {len(self.test_results)}")

        successful_tests = sum(1 for result in self.test_results if result['success'])
        report.append(f"Successful Tests: {successful_tests}")
        report.append(f"Failed Tests: {len(self.test_results) - successful_tests}")
        report.append("")

        for i, result in enumerate(self.test_results, 1):
            report.append(f"## Test {i}: {result['plugin_name']}.{result['function_name']}")
            report.append(f"Status: {'✅ PASSED' if result['success'] else '❌ FAILED'}")
            report.append(f"Duration: {result.get('duration', 0):.2f} seconds")

            if result.get('resource_stats'):
                stats = result['resource_stats']
                report.append(f"Max Memory: {stats.get('max_memory', 0):.1f} MB")
                report.append(f"Max CPU: {stats.get('max_cpu', 0):.1f}%")

                if stats.get('violations'):
                    report.append("[WARN] Resource Violations:")
                    for violation in stats['violations']:
                        report.append(f"  - {violation}")

            if result.get('error'):
                report.append(f"Error: {result['error']}")

            if result.get('output'):
                report.append(f"Output: {result['output']}")

            report.append("")

        return "\n".join(report)

    def cleanup(self):
        """Clean up sandbox environment"""
        try:
            # Remove sandbox files
            for item in self.sandbox_dir.iterdir():
                if item.is_file():
                    item.unlink()
                elif item.is_dir():
                    shutil.rmtree(item)

            print("Sandbox cleaned up successfully")

        except Exception as e:
            print(f"Error during sandbox cleanup: {e}")

class SandboxGUI:
    """GUI interface for plugin sandbox"""

    def __init__(self, sandbox: PluginSandbox):
        if not GUI_AVAILABLE:
            raise RuntimeError("GUI not available - tkinter not installed")

        self.sandbox = sandbox
        self.root = tk.Tk()
        self.root.title("Plugin Sandbox Environment")
        self.root.geometry("1000x700")

        self._setup_gui()

    def _setup_gui(self):
        """Setup GUI components"""
        # Main notebook
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Plugin testing tab
        test_frame = ttk.Frame(notebook)
        notebook.add(test_frame, text="Plugin Testing")
        self._setup_test_tab(test_frame)

        # Results tab
        results_frame = ttk.Frame(notebook)
        notebook.add(results_frame, text="Test Results")
        self._setup_results_tab(results_frame)

        # Monitoring tab
        monitor_frame = ttk.Frame(notebook)
        notebook.add(monitor_frame, text="Resource Monitor")
        self._setup_monitor_tab(monitor_frame)

    def _setup_test_tab(self, parent):
        """Setup plugin testing tab"""
        # Plugin selection
        ttk.Label(parent, text="Plugin File:").pack(anchor='w', pady=5)

        plugin_frame = ttk.Frame(parent)
        plugin_frame.pack(fill=tk.X, pady=5)

        self.plugin_path_var = tk.StringVar()
        plugin_entry = ttk.Entry(plugin_frame, textvariable=self.plugin_path_var, width=50)
        plugin_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        ttk.Button(plugin_frame, text="Browse", command=self._browse_plugin).pack(side=tk.RIGHT, padx=5)

        # Function name
        ttk.Label(parent, text="Function to Test:").pack(anchor='w', pady=(10, 5))
        self.function_var = tk.StringVar(value="main")
        ttk.Entry(parent, textvariable=self.function_var).pack(fill=tk.X, pady=5)

        # Arguments
        ttk.Label(parent, text="Arguments (JSON format):").pack(anchor='w', pady=(10, 5))
        self.args_text = tk.Text(parent, height=3)
        self.args_text.pack(fill=tk.X, pady=5)
        self.args_text.insert('1.0', '{"args": [], "kwargs": {}}')

        # Test buttons
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=10)

        ttk.Button(button_frame, text="Load Plugin", command=self._load_plugin).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Run Test", command=self._run_test).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear Results", command=self._clear_results).pack(side=tk.LEFT, padx=5)

        # Output
        ttk.Label(parent, text="Test Output:").pack(anchor='w', pady=(10, 5))
        self.output_text = scrolledtext.ScrolledText(parent, height=15)
        self.output_text.pack(fill=tk.BOTH, expand=True, pady=5)

    def _setup_results_tab(self, parent):
        """Setup test results tab"""
        # Results tree
        columns = ('Test', 'Plugin', 'Function', 'Status', 'Duration', 'Memory', 'CPU')
        self.results_tree = ttk.Treeview(parent, columns=columns, show='headings')

        for col in columns:
            self.results_tree.heading(col, text=col)
            self.results_tree.column(col, width=100)

        # Scrollbars
        v_scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.results_tree.yview)
        h_scrollbar = ttk.Scrollbar(parent, orient=tk.HORIZONTAL, command=self.results_tree.xview)
        self.results_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        self.results_tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')

        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)

        # Buttons
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=2, column=0, columnspan=2, sticky='ew', pady=10)

        ttk.Button(button_frame, text="Refresh", command=self._refresh_results).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Generate Report", command=self._generate_report).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Export Results", command=self._export_results).pack(side=tk.LEFT, padx=5)

    def _setup_monitor_tab(self, parent):
        """Setup resource monitoring tab"""
        # Configuration
        config_frame = ttk.LabelFrame(parent, text="Sandbox Configuration")
        config_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(config_frame, text="Max Execution Time (s):").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.max_time_var = tk.StringVar(value=str(self.sandbox.config.max_execution_time))
        ttk.Entry(config_frame, textvariable=self.max_time_var, width=10).grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(config_frame, text="Max Memory (MB):").grid(row=0, column=2, sticky='w', padx=5, pady=5)
        self.max_memory_var = tk.StringVar(value=str(self.sandbox.config.max_memory_usage // 1024 // 1024))
        ttk.Entry(config_frame, textvariable=self.max_memory_var, width=10).grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(config_frame, text="Max CPU (%):").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.max_cpu_var = tk.StringVar(value=str(self.sandbox.config.max_cpu_percent))
        ttk.Entry(config_frame, textvariable=self.max_cpu_var, width=10).grid(row=1, column=1, padx=5, pady=5)

        ttk.Button(config_frame, text="Update Config", command=self._update_config).grid(row=1, column=3, padx=5, pady=5)

        # Current statistics
        stats_frame = ttk.LabelFrame(parent, text="Current Test Statistics")
        stats_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.stats_text = scrolledtext.ScrolledText(stats_frame, height=20)
        self.stats_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def _browse_plugin(self):
        """Browse for plugin file"""
        from tkinter import filedialog
        filename = filedialog.askopenfilename(
            title="Select Plugin File",
            filetypes=[("Python files", "*.py"), ("All files", "*.*")]
        )
        if filename:
            self.plugin_path_var.set(filename)

    def _load_plugin(self):
        """Load selected plugin"""
        plugin_path = self.plugin_path_var.get()
        if not plugin_path:
            messagebox.showerror("Error", "Please select a plugin file")
            return

        success = self.sandbox.load_plugin(plugin_path)
        if success:
            messagebox.showinfo("Success", "Plugin loaded successfully")
        else:
            messagebox.showerror("Error", "Failed to load plugin")

    def _run_test(self):
        """Run plugin test"""
        plugin_path = self.plugin_path_var.get()
        function_name = self.function_var.get()

        if not plugin_path:
            messagebox.showerror("Error", "Please select a plugin file")
            return

        try:
            # Parse arguments
            args_data = json.loads(self.args_text.get('1.0', tk.END))
            args = args_data.get('args', [])
            kwargs = args_data.get('kwargs', {})

            # Run test
            plugin_name = Path(plugin_path).name
            result = self.sandbox.run_plugin(plugin_name, function_name, args, kwargs)

            # Display output
            output = f"Test Result for {plugin_name}.{function_name}\n"
            output += f"Status: {'PASSED' if result['success'] else 'FAILED'}\n"
            output += f"Duration: {result.get('duration', 0):.2f} seconds\n"

            if result.get('output'):
                output += f"Output:\n{result['output']}\n"

            if result.get('error'):
                output += f"Error:\n{result['error']}\n"

            if result.get('resource_stats'):
                stats = result['resource_stats']
                output += f"Max Memory: {stats.get('max_memory', 0):.1f} MB\n"
                output += f"Max CPU: {stats.get('max_cpu', 0):.1f}%\n"

            self.output_text.delete('1.0', tk.END)
            self.output_text.insert('1.0', output)

            # Refresh results
            self._refresh_results()

        except json.JSONDecodeError:
            messagebox.showerror("Error", "Invalid JSON format in arguments")
        except Exception as e:
            messagebox.showerror("Error", f"Test execution failed: {e}")

    def _clear_results(self):
        """Clear test results"""
        self.sandbox.test_results.clear()
        self.output_text.delete('1.0', tk.END)
        self._refresh_results()

    def _refresh_results(self):
        """Refresh results tree"""
        # Clear existing items
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)

        # Add test results
        for i, result in enumerate(self.sandbox.test_results, 1):
            status = "PASSED" if result['success'] else "FAILED"
            duration = f"{result.get('duration', 0):.2f}s"

            stats = result.get('resource_stats', {})
            memory = f"{stats.get('max_memory', 0):.1f}MB"
            cpu = f"{stats.get('max_cpu', 0):.1f}%"

            self.results_tree.insert('', tk.END, values=(
                i, result['plugin_name'], result['function_name'],
                status, duration, memory, cpu
            ))

    def _generate_report(self):
        """Generate and display test report"""
        report = self.sandbox.generate_test_report()

        # Show in new window
        report_window = tk.Toplevel(self.root)
        report_window.title("Test Report")
        report_window.geometry("800x600")

        text_widget = scrolledtext.ScrolledText(report_window)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text_widget.insert('1.0', report)

    def _export_results(self):
        """Export test results"""
        from tkinter import filedialog
        filename = filedialog.asksaveasfilename(
            title="Export Test Results",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )

        if filename:
            try:
                with open(filename, 'w') as f:
                    json.dump(self.sandbox.test_results, f, indent=2, default=str)
                messagebox.showinfo("Success", f"Results exported to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export results: {e}")

    def _update_config(self):
        """Update sandbox configuration"""
        try:
            self.sandbox.config.max_execution_time = int(self.max_time_var.get())
            self.sandbox.config.max_memory_usage = int(self.max_memory_var.get()) * 1024 * 1024
            self.sandbox.config.max_cpu_percent = int(self.max_cpu_var.get())
            messagebox.showinfo("Success", "Configuration updated")
        except ValueError:
            messagebox.showerror("Error", "Invalid configuration values")

    def run(self):
        """Run the GUI"""
        self.root.mainloop()

def main():
    """Main function for testing"""
    print("Plugin Sandbox Environment")

    # Create sandbox
    config = SandboxConfig()
    sandbox = PluginSandbox(config)

    print("Available commands:")
    print("1. gui - Launch GUI interface")
    print("2. test <plugin_path> - Test a plugin")
    print("3. report - Generate test report")
    print("4. cleanup - Clean sandbox")
    print("5. quit - Exit")

    while True:
        command = input("\n> ").strip().lower()

        if command == 'quit':
            break
        elif command == 'gui':
            if GUI_AVAILABLE:
                gui = SandboxGUI(sandbox)
                gui.run()
            else:
                print("GUI not available - tkinter not installed")
        elif command.startswith('test '):
            plugin_path = command[5:]
            if sandbox.load_plugin(plugin_path):
                result = sandbox.run_plugin(Path(plugin_path).name)
                print(f"Test result: {'PASSED' if result['success'] else 'FAILED'}")
                if result.get('error'):
                    print(f"Error: {result['error']}")
        elif command == 'report':
            print(sandbox.generate_test_report())
        elif command == 'cleanup':
            sandbox.cleanup()
        else:
            print("Unknown command")

    sandbox.cleanup()

if __name__ == "__main__":
    main()
