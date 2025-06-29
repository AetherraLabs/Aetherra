#!/usr/bin/env python3
"""
🧬 NeuroCode Playground - Interactive Web Interface
================================================

A Streamlit-based playground for NeuroCode that allows users to:
- Write and execute NeuroCode programs in real-time
- Explore the standard library with live examples
- Learn through interactive tutorials
- Share and experiment with NeuroCode code

This creates a "PythonAnywhere/Replit" experience for NeuroCode!
"""

import sys
from datetime import datetime
from pathlib import Path

import streamlit as st

# Add the project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import NeuroCode components
try:
    from core.neurocode_grammar import create_neurocode_parser
    from neurocode_engine import neurocode_engine  # NEW: Multi-LLM engine
    from stdlib import stdlib_manager

    LLM_SUPPORT = True
except ImportError as e:
    st.error(f"Error importing NeuroCode components: {e}")
    LLM_SUPPORT = False

# Page configuration
st.set_page_config(
    page_title="NeuroCode Playground",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for better styling
st.markdown(
    """
<style>
.main-header {
    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    padding: 1rem;
    border-radius: 10px;
    color: white;
    text-align: center;
    margin-bottom: 2rem;
}

.plugin-card {
    background: #f8f9fa;
    padding: 1rem;
    border-radius: 8px;
    border-left: 4px solid #667eea;
    margin: 0.5rem 0;
}

.success-box {
    background: #d4edda;
    border: 1px solid #c3e6cb;
    color: #155724;
    padding: 1rem;
    border-radius: 5px;
    margin: 1rem 0;
}

.error-box {
    background: #f8d7da;
    border: 1px solid #f5c6cb;
    color: #721c24;
    padding: 1rem;
    border-radius: 5px;
    margin: 1rem 0;
}

.example-code {
    background: #f8f9fa;
    border: 1px solid #e9ecef;
    border-radius: 5px;
    padding: 1rem;
    font-family: 'Courier New', monospace;
}
</style>
""",
    unsafe_allow_html=True,
)


def main():
    """Main application function"""

    # Header
    st.markdown(
        """
    <div class="main-header">
        <h1>🧬 NeuroCode Playground</h1>
        <p>Interactive environment for the NeuroCode programming language</p>
        <p><strong>Try NeuroCode instantly - No installation required!</strong></p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Sidebar navigation
    st.sidebar.title("🎮 Playground Menu")
    page = st.sidebar.selectbox(
        "Choose your experience:",
        [
            "🚀 Quick Start",
            "📚 Standard Library",
            "🎓 Tutorials",
            "🧪 Code Editor",
            "📖 Examples",
            "ℹ️ About",
        ],
    )

    if page == "🚀 Quick Start":
        show_quick_start()
    elif page == "📚 Standard Library":
        show_standard_library()
    elif page == "🎓 Tutorials":
        show_tutorials()
    elif page == "🧪 Code Editor":
        show_code_editor()
    elif page == "📖 Examples":
        show_examples()
    elif page == "ℹ️ About":
        show_about()


def show_quick_start():
    """Quick start page with basic NeuroCode introduction"""
    st.header("🚀 Welcome to NeuroCode!")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("What is NeuroCode?")
        st.write("""
        NeuroCode is a **true programming language** designed for AI-driven development:
        
        ✅ **Syntax-Native**: Formal grammar with `.neuro` files  
        ✅ **AI-Centric**: Goals, agents, memory, and intent constructs  
        ✅ **Standard Library**: 7 powerful plugins for real-world tasks  
        ✅ **Extensible**: Plugin architecture for custom functionality  
        """)

        st.subheader("🎯 Key Features")
        st.write("""
        - **Goals**: Define what you want to achieve
        - **Agents**: AI entities that execute tasks
        - **Memory**: Persistent storage and recall
        - **Plugins**: Rich standard library (sysmon, coretools, executor, etc.)
        - **Intent Actions**: Natural language task descriptions
        """)

    with col2:
        st.subheader("🧬 Try NeuroCode Now!")

        # Simple interactive example
        sample_code = """# Your first NeuroCode program!
goal: "system_check" priority: high
agent: "system_admin"

# Check system health with stdlib
status = plugin("sysmon.status")
files = plugin("coretools.list_files")

# Remember the results
remember("system_checked") as "health_check"
"""

        st.code(sample_code, language="neuro")

        if st.button("▶️ Run This Example", key="quick_start_run"):
            run_neurocode_sample(sample_code)

    # Quick stats
    st.subheader("📊 NeuroCode Status")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Language Status", "✅ Complete", "Syntax-Native")
    with col2:
        st.metric("Standard Library", "7 Plugins", "All Functional")
    with col3:
        st.metric("Parser", "✅ Working", "Lark Grammar")
    with col4:
        st.metric("Real-World Ready", "✅ Yes", "Practical Tasks")


def show_standard_library():
    """Standard library exploration page"""
    st.header("📚 NeuroCode Standard Library")
    st.write("Explore the 7 core plugins that make NeuroCode powerful for real-world tasks!")

    # Get plugin information
    plugins = stdlib_manager.list_plugins()

    st.subheader(f"🔌 {len(plugins)} Core Plugins Available")

    # Plugin selection
    plugin_names = list(plugins.keys())
    selected_plugin = st.selectbox("Choose a plugin to explore:", plugin_names)

    if selected_plugin:
        show_plugin_details(selected_plugin)

    # Plugin overview grid
    st.subheader("🎯 Plugin Overview")

    plugin_info = {
        "sysmon": {
            "icon": "🔍",
            "purpose": "System performance monitoring",
            "example": 'status = plugin("sysmon.check_health")',
        },
        "optimizer": {
            "icon": "⚡",
            "purpose": "Performance optimization",
            "example": 'analysis = plugin("optimizer.analyze_performance")',
        },
        "coretools": {
            "icon": "🛠️",
            "purpose": "File & data management",
            "example": 'files = plugin("coretools.list_files")',
        },
        "executor": {
            "icon": "🚀",
            "purpose": "Command execution & scheduling",
            "example": 'plugin("executor.execute_now", "echo test")',
        },
        "reflector": {
            "icon": "🧠",
            "purpose": "Behavior analysis & AI reflection",
            "example": 'patterns = plugin("reflector.analyze_behavior")',
        },
        "selfrepair": {
            "icon": "🔧",
            "purpose": "Automated debugging & repair",
            "example": 'errors = plugin("selfrepair.detect_errors")',
        },
        "whisper": {
            "icon": "🎤",
            "purpose": "Audio transcription & speech",
            "example": 'transcript = plugin("whisper.transcribe")',
        },
    }

    col1, col2, col3 = st.columns(3)

    for i, (plugin_name, info) in enumerate(plugin_info.items()):
        col = [col1, col2, col3][i % 3]
        with col:
            with st.container():
                st.markdown(
                    f"""
                <div class="plugin-card">
                    <h4>{info["icon"]} {plugin_name}</h4>
                    <p><strong>Purpose:</strong> {info["purpose"]}</p>
                    <code>{info["example"]}</code>
                </div>
                """,
                    unsafe_allow_html=True,
                )


def show_plugin_details(plugin_name):
    """Show detailed information about a specific plugin"""
    st.subheader(f"🔌 {plugin_name} Plugin Details")

    # Get plugin info
    plugin_info = stdlib_manager.get_plugin_info(plugin_name)

    if plugin_info:
        col1, col2 = st.columns(2)

        with col1:
            st.write(f"**Description:** {plugin_info['description']}")
            st.write(f"**Status:** {'✅ Loaded' if plugin_info['loaded'] else '❌ Not Loaded'}")
            st.write(f"**Available Actions:** {len(plugin_info['available_actions'])}")

        with col2:
            st.write("**Actions:**")
            for action in plugin_info["available_actions"][:10]:  # Show first 10
                st.write(f"• `{action}`")
            if len(plugin_info["available_actions"]) > 10:
                st.write(f"• ... and {len(plugin_info['available_actions']) - 10} more")

        # Test the plugin
        st.subheader(f"🧪 Test {plugin_name}")

        if st.button(f"Test {plugin_name}.status()", key=f"test_{plugin_name}"):
            try:
                result = stdlib_manager.execute_plugin_action(plugin_name, "status")
                st.markdown(
                    f"""
                <div class="success-box">
                    <strong>✅ Plugin Test Successful!</strong><br>
                    Result: {result}
                </div>
                """,
                    unsafe_allow_html=True,
                )
            except Exception as e:
                st.markdown(
                    f"""
                <div class="error-box">
                    <strong>❌ Plugin Test Failed</strong><br>
                    Error: {str(e)}
                </div>
                """,
                    unsafe_allow_html=True,
                )


def show_tutorials():
    """Interactive tutorials page"""
    st.header("🎓 NeuroCode Tutorials")
    st.write("Learn NeuroCode step by step with interactive examples!")

    tutorial = st.selectbox(
        "Choose a tutorial:",
        [
            "1. 🎯 Basic Syntax - Goals & Agents",
            "2. 🧠 Memory Operations",
            "3. 🔌 Using Plugins",
            "4. 🚀 Real-World Example - System Monitoring",
            "5. 🛠️ File Processing Pipeline",
            "6. 🤖 AI Behavior Analysis",
        ],
    )

    if "Basic Syntax" in tutorial:
        show_tutorial_basic_syntax()
    elif "Memory Operations" in tutorial:
        show_tutorial_memory()
    elif "Using Plugins" in tutorial:
        show_tutorial_plugins()
    elif "System Monitoring" in tutorial:
        show_tutorial_system_monitoring()
    elif "File Processing" in tutorial:
        show_tutorial_file_processing()
    elif "AI Behavior" in tutorial:
        show_tutorial_ai_behavior()


def show_tutorial_basic_syntax():
    """Basic syntax tutorial"""
    st.subheader("🎯 Tutorial 1: Basic Syntax - Goals & Agents")

    st.write("""
    NeuroCode programs are built around **Goals** and **Agents**:
    - **Goals** define what you want to achieve
    - **Agents** are AI entities that execute tasks
    """)

    code = """# NeuroCode Basic Syntax
goal: "learn_neurocode" priority: high
agent: "tutorial_assistant"

# Variables
task_name = "syntax_tutorial"
progress = 0

# Memory operations
remember("started_tutorial") as "learning_progress"
"""

    st.code(code, language="neuro")

    if st.button("▶️ Try Basic Syntax", key="tutorial_basic"):
        run_neurocode_sample(code)


def show_tutorial_memory():
    """Memory operations tutorial"""
    st.subheader("🧠 Tutorial 2: Memory Operations")

    st.write("""
    NeuroCode has built-in memory operations:
    - `remember()` - Store information
    - `recall()` - Retrieve information  
    - `forget()` - Remove information
    """)

    code = """# Memory Operations Example
goal: "memory_demo" priority: medium
agent: "memory_manager"

# Store information
remember("NeuroCode is awesome!") as "opinion"
remember("2025-06-29") as "tutorial_date"

# Retrieve information
user_opinion = recall("opinion")
date_info = recall("tutorial_date")
"""

    st.code(code, language="neuro")

    if st.button("▶️ Try Memory Operations", key="tutorial_memory"):
        run_neurocode_sample(code)


def show_tutorial_plugins():
    """Plugin usage tutorial"""
    st.subheader("🔌 Tutorial 3: Using Plugins")

    st.write("""
    Plugins extend NeuroCode with powerful capabilities:
    - Use `plugin("name.action")` to call plugin functions
    - 7 core plugins available: sysmon, coretools, executor, etc.
    """)

    code = """# Plugin Usage Example
goal: "test_plugins" priority: high
agent: "plugin_explorer"

# System monitoring
health = plugin("sysmon.status")

# File operations
files = plugin("coretools.list_files")

# Command execution  
result = plugin("executor.execute_now")

# Remember the results
remember(health) as "system_health"
"""

    st.code(code, language="neuro")

    if st.button("▶️ Try Plugin Usage", key="tutorial_plugins"):
        run_neurocode_sample(code)


def show_tutorial_system_monitoring():
    """System monitoring tutorial"""
    st.subheader("🚀 Tutorial 4: Real-World Example - System Monitoring")

    st.write("""
    Build a real system monitoring script with NeuroCode!
    This example shows practical usage with multiple plugins.
    """)

    code = """# System Monitoring Dashboard
goal: "monitor_system" priority: critical
agent: "sysadmin_bot"

# Check system health
system_status = plugin("sysmon.check_health")
performance = plugin("optimizer.analyze_performance")

# Log the results
plugin("coretools.write_file", "system_log.txt", system_status)

# Schedule regular checks
plugin("executor.schedule_command", "health_check", "+1h")

# Analyze patterns
plugin("reflector.analyze_behavior", "monitoring_session")

# Remember this monitoring session
remember("monitoring_complete") as "session_status"
"""

    st.code(code, language="neuro")

    if st.button("▶️ Run System Monitor", key="tutorial_sysmon"):
        run_neurocode_sample(code)


def show_tutorial_file_processing():
    """File processing tutorial"""
    st.subheader("🛠️ Tutorial 5: File Processing Pipeline")

    code = """# File Processing Pipeline
goal: "process_data" priority: high
agent: "data_processor"

# List available files
files = plugin("coretools.list_files")

# Process each file type
csv_data = plugin("coretools.read_csv", "data.csv")
json_data = plugin("coretools.read_json", "config.json")

# Transform and save results
processed = plugin("coretools.transform_data", csv_data)
plugin("coretools.write_json", "results.json", processed)

# Track processing
remember("files_processed") as "pipeline_status"
"""

    st.code(code, language="neuro")

    if st.button("▶️ Run File Pipeline", key="tutorial_files"):
        run_neurocode_sample(code)


def show_tutorial_ai_behavior():
    """AI behavior analysis tutorial"""
    st.subheader("🤖 Tutorial 6: AI Behavior Analysis")

    code = """# AI Behavior Analysis
goal: "analyze_ai_behavior" priority: high
agent: "behavior_analyst"

# Analyze current behavior patterns
patterns = plugin("reflector.analyze_behavior", "tutorial_session")
performance = plugin("reflector.reflect_on_performance")

# Get usage insights
insights = plugin("reflector.usage_insights")

# Detect any issues
errors = plugin("selfrepair.detect_errors")
suggestions = plugin("selfrepair.suggest_fixes")

# Store analysis results
remember(patterns) as "behavior_analysis"
remember(insights) as "usage_patterns"
"""

    st.code(code, language="neuro")

    if st.button("▶️ Analyze AI Behavior", key="tutorial_ai"):
        run_neurocode_sample(code)


def show_code_editor():
    """Interactive code editor page"""
    st.header("🧪 NeuroCode Interactive Editor")
    st.write("Write and execute your own NeuroCode programs!")

    # Code editor
    default_code = """# Write your NeuroCode program here!
goal: "my_program" priority: medium
agent: "my_assistant"

# Example: Check system and create a report
system_info = plugin("sysmon.status")
file_count = plugin("coretools.list_files")

# Remember the results
remember("program_executed") as "execution_status"

# Your code here...
"""

    code = st.text_area(
        "✏️ NeuroCode Editor",
        value=default_code,
        height=400,
        help="Write NeuroCode syntax here. Use goals, agents, plugins, and memory operations!",
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("▶️ Execute Code", key="execute_custom"):
            if code.strip():
                run_neurocode_sample(code)
            else:
                st.warning("Please enter some NeuroCode to execute!")

    with col2:
        if st.button("🔍 Validate Syntax", key="validate_custom"):
            validate_neurocode_syntax(code)

    with col3:
        if st.button("💾 Save Example", key="save_custom"):
            save_user_example(code)

    # Syntax reference
    with st.expander("📖 Quick Syntax Reference"):
        st.markdown("""
        **Basic Constructs:**
        ```neuro
        # Goals
        goal: "task_name" priority: high
        
        # Agents  
        agent: "agent_name"
        
        # Variables
        variable_name = "value"
        number_var = 42
        
        # Memory
        remember("data") as "memory_key"
        data = recall("memory_key")
        
        # Plugins
        result = plugin("plugin_name.action")
        plugin("coretools.write_file", "filename.txt", "content")
        
        # Comments
        # This is a comment
        ```
        """)


def show_examples():
    """Example gallery page"""
    st.header("📖 NeuroCode Example Gallery")
    st.write("Explore practical NeuroCode programs for real-world tasks!")

    examples = {
        "🧠 Multi-LLM AI Analysis": {
            "description": "Demonstrate NeuroCode's multi-LLM capabilities with different AI models",
            "code": '''# Multi-LLM NeuroCode Demo
# Switch between different AI models for specialized tasks

goal: "multi_model_analysis" priority: high

# Use local Mistral for privacy-focused analysis
model: "mistral"
assistant: "analyze system architecture for potential security issues"

# Switch to GPT-4 for complex reasoning
model: "gpt-4"
assistant: "generate comprehensive improvement recommendations based on analysis"

# Use LLaMA for code generation
model: "llama2"
assistant: "create Python implementation for the suggested improvements"

# Use Mixtral for synthesis
model: "mixtral"
assistant: "combine all insights into actionable development plan"

# Remember insights
remember("Multi-LLM analysis provides specialized expertise") as "ai_architecture"
remember("Different models excel at different tasks") as "model_specialization"

# Set agent for continuous monitoring
agent: "multi_model_coordinator"

# Recall insights for final decision
recall "ai_architecture"
recall "model_specialization"''',
        },
        "🔍 System Health Monitor": {
            "description": "Complete system monitoring with health checks and reporting",
            "code": '''goal: "system_health_monitor" priority: critical
agent: "health_monitor"

# Comprehensive health check
cpu_status = plugin("sysmon.check_health")
system_info = plugin("sysmon.get_status")

# Performance analysis
performance_data = plugin("optimizer.analyze_performance")
optimization_tips = plugin("optimizer.suggest_optimizations")

# Error detection
potential_errors = plugin("selfrepair.detect_errors")

# Generate report
health_report = {
    "timestamp": now(),
    "cpu_status": cpu_status,
    "performance": performance_data,
    "errors": potential_errors
}

# Save and schedule
plugin("coretools.write_json", "health_report.json", health_report)
plugin("executor.schedule_command", "health_check", "+6h")

remember("health_check_complete") as "monitoring_session"''',
        },
        "📁 Automated File Organizer": {
            "description": "Organize files by type and create a structured directory",
            "code": '''goal: "organize_files" priority: medium
agent: "file_organizer"

# Get all files in current directory
all_files = plugin("coretools.list_files")

# Create organization directories
plugin("coretools.create_directory", "documents")
plugin("coretools.create_directory", "images") 
plugin("coretools.create_directory", "archives")

# Organize files by extension
for file in all_files:
    file_info = plugin("coretools.file_info", file)
    
    if file.endswith(".txt") or file.endswith(".pdf"):
        plugin("coretools.move_file", file, "documents/")
    elif file.endswith(".jpg") or file.endswith(".png"):
        plugin("coretools.move_file", file, "images/")
    elif file.endswith(".zip") or file.endswith(".tar"):
        plugin("coretools.move_file", file, "archives/")

# Generate organization report
organization_log = plugin("coretools.list_files", ".")
plugin("coretools.write_file", "organization_log.txt", organization_log)

remember("files_organized") as "organization_complete"''',
        },
        "🤖 AI Behavior Tracker": {
            "description": "Track and analyze AI decision patterns and performance",
            "code": '''goal: "ai_behavior_analysis" priority: high
agent: "behavior_analyst"

# Analyze recent behavior patterns
behavior_data = plugin("reflector.analyze_behavior", "daily_operations")
performance_metrics = plugin("reflector.reflect_on_performance")

# Get detailed insights
usage_patterns = plugin("reflector.usage_insights")
decision_tracking = plugin("reflector.decision_tracking")

# Pattern analysis
pattern_analysis = plugin("reflector.pattern_analysis")

# Create comprehensive behavior report
behavior_report = {
    "analysis_date": now(),
    "behavior_patterns": behavior_data,
    "performance_metrics": performance_metrics,
    "usage_insights": usage_patterns,
    "decision_patterns": decision_tracking
}

# Save analysis
plugin("coretools.write_json", "ai_behavior_report.json", behavior_report)

# Schedule regular analysis
plugin("executor.schedule_command", "behavior_analysis", "+24h")

# Self-improvement suggestions
if performance_metrics.efficiency < 0.8:
    plugin("selfrepair.suggest_fixes")
    plugin("optimizer.suggest_optimizations")

remember("behavior_analysis_complete") as "analysis_session"''',
        },
        "⚡ Performance Optimizer": {
            "description": "Automated system performance optimization and monitoring",
            "code": '''goal: "optimize_system_performance" priority: high
agent: "performance_optimizer"

# Current performance baseline
current_performance = plugin("optimizer.analyze_performance")
system_health = plugin("sysmon.check_health")

# Get optimization recommendations
optimization_suggestions = plugin("optimizer.suggest_optimizations")

# Detect performance bottlenecks
performance_issues = plugin("selfrepair.detect_errors")

# Apply safe optimizations
for suggestion in optimization_suggestions:
    if suggestion.safety_level == "safe":
        plugin("executor.execute_now", suggestion.command)

# Monitor optimization results
plugin("executor.schedule_command", "performance_check", "+30m")

# Create optimization report
optimization_report = {
    "baseline_performance": current_performance,
    "applied_optimizations": optimization_suggestions,
    "post_optimization_health": plugin("sysmon.check_health")
}

plugin("coretools.write_json", "optimization_report.json", optimization_report)

# Track optimization effectiveness
plugin("reflector.analyze_behavior", "optimization_session")

remember("optimization_complete") as "performance_session"''',
        },
    }

    # Example selection
    selected_example = st.selectbox("Choose an example to explore:", list(examples.keys()))

    if selected_example:
        example = examples[selected_example]

        st.subheader(selected_example)
        st.write(example["description"])

        # Show code
        st.code(example["code"], language="neuro")

        # Run button
        if st.button(f"▶️ Run {selected_example}", key=f"run_example_{selected_example}"):
            run_neurocode_sample(example["code"])


def show_about():
    """About page with NeuroCode information"""
    st.header("ℹ️ About NeuroCode")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🧬 What is NeuroCode?")
        st.write("""
        NeuroCode is a **true programming language** designed specifically for AI-driven development and intelligent automation.
        
        **Key Characteristics:**
        - **Syntax-Native**: Real programming language with formal grammar
        - **AI-Centric Design**: Built around goals, agents, and intent
        - **Rich Standard Library**: 7 powerful plugins for real-world tasks
        - **Memory Operations**: Built-in persistent storage and recall
        - **Plugin Architecture**: Extensible through standardized plugins
        """)

        st.subheader("🎯 Design Philosophy")
        st.write("""
        NeuroCode bridges the gap between natural language intent and executable code:
        
        - **Goal-Oriented**: Programs express what you want to achieve
        - **Agent-Based**: AI entities execute complex tasks
        - **Memory-Aware**: Built-in knowledge persistence
        - **Plugin-Powered**: Extensive capabilities through modular plugins
        """)

    with col2:
        st.subheader("📊 Technical Specifications")

        # Language stats
        st.metric("Language Status", "✅ Complete")
        st.metric("Grammar", "Lark EBNF")
        st.metric("File Extension", ".neuro")
        st.metric("Standard Library", "7 Core Plugins")

        st.subheader("🔌 Standard Library Plugins")
        plugins_info = [
            ("sysmon", "System monitoring & health"),
            ("optimizer", "Performance optimization"),
            ("coretools", "File & data operations"),
            ("executor", "Command execution & scheduling"),
            ("reflector", "AI behavior analysis"),
            ("selfrepair", "Automated debugging"),
            ("whisper", "Audio transcription"),
        ]

        for name, desc in plugins_info:
            st.write(f"**{name}**: {desc}")

    st.subheader("🚀 Language Evolution")

    col1, col2 = st.columns(2)

    with col1:
        st.write("**BEFORE** (Framework):")
        st.code(
            """
# Python-wrapped simulation
neurocode.goal("task")
neurocode.agent("assistant")
neurocode.remember("data")
        """,
            language="python",
        )

    with col2:
        st.write("**AFTER** (True Language):")
        st.code(
            """
# Native NeuroCode syntax
goal: "task" priority: high
agent: "assistant"
remember("data") as "key"
        """,
            language="neuro",
        )

    st.subheader("🌟 Use Cases")

    use_cases = [
        "🖥️ **System Administration**: Automated monitoring, optimization, and maintenance",
        "📊 **Data Processing**: File operations, format conversion, and data analysis",
        "🤖 **AI Automation**: Intelligent task scheduling and decision making",
        "🔧 **DevOps**: Deployment automation and infrastructure management",
        "📈 **Performance Optimization**: System tuning and bottleneck analysis",
        "🧠 **AI Behavior Analysis**: Self-improvement and pattern recognition",
    ]

    for use_case in use_cases:
        st.write(use_case)


def run_neurocode_sample(code):
    """Execute a NeuroCode sample and display results"""
    st.subheader("🔄 Execution Results")

    try:
        # Show LLM availability status
        if LLM_SUPPORT:
            available_models = neurocode_engine.list_available_models()
            current_model = neurocode_engine.get_current_model()

            with st.expander("🧠 Multi-LLM Status"):
                st.write(f"**Available Models:** {len(available_models)}")
                for name, info in available_models.items():
                    status = "🟢" if name == current_model else "⚫"
                    local_badge = " 🏠" if info.get("is_local") else " ☁️"
                    st.write(f"{status} {name} ({info['provider']}){local_badge}")

                if current_model:
                    st.success(f"Current model: {current_model}")
                else:
                    st.warning("No model selected")

        # Execute with enhanced engine if available
        if LLM_SUPPORT:
            with st.spinner("Executing NeuroCode with multi-LLM support..."):
                execution_result = neurocode_engine.execute_neurocode(code)

            if execution_result["status"] == "success":
                st.markdown(
                    """
                <div class="success-box">
                    <strong>✅ Execution Successful!</strong><br>
                    Your NeuroCode program executed successfully with multi-LLM support.
                </div>
                """,
                    unsafe_allow_html=True,
                )

                # Display execution results
                st.subheader("📋 Execution Output")

                # Show individual statement results
                for i, stmt_result in enumerate(execution_result["results"], 1):
                    if stmt_result.get("type") == "model":
                        if stmt_result["status"] == "success":
                            st.success(f"Statement {i}: {stmt_result['message']}")
                        else:
                            st.error(f"Statement {i}: {stmt_result['message']}")
                    elif stmt_result.get("type") == "assistant":
                        if stmt_result["status"] == "success":
                            st.info("🤖 **Assistant Response:**")
                            st.write(stmt_result["response"])
                        else:
                            st.error(f"Assistant Error: {stmt_result['message']}")
                    else:
                        st.write(f"Statement {i}: {stmt_result.get('message', stmt_result)}")

                # Show execution context
                with st.expander("🔍 Execution Context"):
                    context = execution_result.get("context", {})
                    st.json(context)

            else:
                st.markdown(
                    f"""
                <div class="error-box">
                    <strong>❌ Execution Failed</strong><br>
                    {execution_result["message"]}<br>
                    Status: {execution_result["status"]}
                </div>
                """,
                    unsafe_allow_html=True,
                )

                if "errors" in execution_result:
                    st.subheader("📋 Parse Errors")
                    for error in execution_result["errors"]:
                        st.error(error)
        else:
            # Fallback to basic validation without LLM support
            parser = create_neurocode_parser()

            with st.spinner("Validating NeuroCode syntax..."):
                result = parser.validate_syntax(code)

            if result["valid"]:
                st.markdown(
                    """
                <div class="success-box">
                    <strong>✅ Syntax Validation Successful!</strong><br>
                    Your NeuroCode program has valid syntax.
                    <br><em>Note: LLM features not available - install dependencies for full execution.</em>
                </div>
                """,
                    unsafe_allow_html=True,
                )

                # Simulate basic execution
                with st.spinner("Simulating NeuroCode execution..."):
                    execution_result = simulate_execution(code)

                st.subheader("📋 Simulated Output")
                st.json(execution_result)

            else:
                st.markdown(
                    f"""
                <div class="error-box">
                    <strong>❌ Syntax Validation Failed</strong><br>
                    Errors found: {len(result["errors"])}<br>
                    {", ".join(result["errors"])}
                </div>
                """,
                    unsafe_allow_html=True,
                )

    except Exception as e:
        st.markdown(
            f"""
        <div class="error-box">
            <strong>❌ Execution Error</strong><br>
            {str(e)}
        </div>
        """,
            unsafe_allow_html=True,
        )


def validate_neurocode_syntax(code):
    """Validate NeuroCode syntax only"""
    try:
        parser = create_neurocode_parser()
        result = parser.validate_syntax(code)

        if result["valid"]:
            st.success("✅ Syntax is valid! Your NeuroCode program follows proper grammar rules.")
        else:
            st.error(f"❌ Syntax errors found: {', '.join(result['errors'])}")

    except Exception as e:
        st.error(f"❌ Validation error: {str(e)}")


def simulate_execution(code):
    """Simulate NeuroCode execution for demo purposes"""
    # This is a safe simulation for the playground
    # In a real implementation, this would execute the actual NeuroCode

    execution_log = {
        "timestamp": datetime.now().isoformat(),
        "status": "simulated_execution",
        "code_lines": len(code.split("\n")),
        "detected_constructs": [],
        "plugin_calls": [],
        "memory_operations": [],
    }

    # Analyze code for constructs
    if "goal:" in code:
        execution_log["detected_constructs"].append("goal_declaration")
    if "agent:" in code:
        execution_log["detected_constructs"].append("agent_activation")
    if "plugin(" in code:
        execution_log["detected_constructs"].append("plugin_usage")
        # Count plugin calls
        import re

        plugins = re.findall(r'plugin\("([^"]+)"', code)
        execution_log["plugin_calls"] = plugins
    if "remember(" in code:
        execution_log["detected_constructs"].append("memory_storage")
        execution_log["memory_operations"].append("remember")
    if "recall(" in code:
        execution_log["detected_constructs"].append("memory_retrieval")
        execution_log["memory_operations"].append("recall")

    # Simulate plugin results
    simulated_results = {}
    for plugin_call in execution_log["plugin_calls"]:
        if "sysmon" in plugin_call:
            simulated_results[plugin_call] = "System healthy - CPU: 45%, Memory: 60%"
        elif "coretools" in plugin_call:
            simulated_results[plugin_call] = "Operation completed - 15 files processed"
        elif "executor" in plugin_call:
            simulated_results[plugin_call] = "Command scheduled successfully"
        elif "reflector" in plugin_call:
            simulated_results[plugin_call] = "Behavior analysis complete - 3 patterns found"
        elif "optimizer" in plugin_call:
            simulated_results[plugin_call] = (
                "Performance analysis complete - 2 optimizations suggested"
            )
        elif "selfrepair" in plugin_call:
            simulated_results[plugin_call] = "System scan complete - No errors detected"
        elif "whisper" in plugin_call:
            simulated_results[plugin_call] = "Audio service ready - No files to process"
        else:
            simulated_results[plugin_call] = "Plugin executed successfully"

    execution_log["simulated_results"] = simulated_results
    execution_log["execution_status"] = "completed_successfully"

    return execution_log


def save_user_example(code):
    """Save user's code example"""
    st.success("💾 Example saved! (Note: This is a demo - saving is simulated)")
    st.info(
        "In a full implementation, this would save your code to a personal gallery or share it with the community!"
    )


if __name__ == "__main__":
    main()
