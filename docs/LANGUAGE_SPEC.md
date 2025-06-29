# 🧬 NeuroCode Language Specification
**Version 1.0.0** | **AI-Native Programming Language**

---

## Table of Contents
1. [Language Overview](#language-overview)
2. [Basic Syntax](#basic-syntax)
3. [Data Types](#data-types)
4. [Variables and Assignments](#variables-and-assignments)
5. [Control Flow](#control-flow)
6. [Functions](#functions)
7. [AI Integration](#ai-integration)
8. [Memory System](#memory-system)
9. [Goal System](#goal-system)
10. [Agent System](#agent-system)
11. [Standard Library](#standard-library)
12. [Multi-LLM Support](#multi-llm-support)
13. [Grammar Definition](#grammar-definition)

---

## Language Overview

NeuroCode is the world's first **AI-native programming language** designed for cognitive computing and AI-human collaboration. Unlike traditional programming languages that focus on explicit instructions, NeuroCode emphasizes **intentions**, **goals**, and **AI-assisted problem solving**.

### Key Principles
- **Intent-driven**: Express what you want to achieve, not how to achieve it
- **AI-augmented**: Built-in AI assistance and reasoning capabilities
- **Multi-model**: Seamless switching between different AI models (OpenAI, Ollama, local models)
- **Memory-aware**: Persistent learning and contextual memory
- **Self-reflective**: Code that can analyze and improve itself

### File Extension
NeuroCode programs use the `.neuro` file extension.

---

## Basic Syntax

### Comments
```neurocode
# This is a single-line comment

# Multi-line comments use multiple # symbols
# Each line needs its own # symbol
# Like this example
```

### Statements
Statements in NeuroCode end with newlines. No semicolons required.

```neurocode
goal: "improve system performance"
remember("optimization completed") as "performance"
agent: on
```

---

## Data Types

NeuroCode supports the following data types:

### Primitives
```neurocode
# Strings (quoted)
name = "NeuroCode"
description = "AI-native programming language"

# Numbers (integers and floats)
version = 1
accuracy = 95.7

# Booleans
enabled = true
debug_mode = false

# Lists
models = ["gpt-4", "mistral", "llama2"]
priorities = [1, 2, 3, 4, 5]
```

### Special Types
```neurocode
# Goals (intent expressions)
goal: "optimize database queries" priority: high

# Memory references
memory.pattern("crash", frequency="daily")

# Agent references
agent: "performance_monitor"
```

---

## Variables and Assignments

### Basic Assignment
```neurocode
# Simple assignment
x = 42
name = "neural_network"
enabled = true

# List assignment
models = ["gpt-4", "mistral", "claude"]
scores = [0.95, 0.87, 0.92]
```

### Variable References
```neurocode
# Use variables in expressions
current_model = models[0]
total_score = scores[0] + scores[1]

# String interpolation
message = "Using model: " + current_model
```

---

## Control Flow

### Conditional Statements
```neurocode
# Basic if statement
if performance < 80%:
    suggest fix for "performance issues"
end

# If-else statement
if memory.contains("optimization"):
    apply previous_optimization
else:
    run performance_analysis
end

# Multiple conditions
if error_rate > 5% and uptime < 99%:
    goal: "improve system reliability" priority: critical
    agent: on
end
```

### Loops
```neurocode
# For loop with list
for model in ["gpt-4", "mistral", "llama2"]:
    test model_performance with model
end

# For loop with range
for i in range(1, 10):
    optimize component[i]
end

# While loop
while system_load > 80%:
    reduce_background_tasks()
    wait 5 seconds
end
```

### Pattern Matching
```neurocode
# Memory pattern matching
if memory.pattern("crash", frequency="daily"):
    goal: "eliminate daily crashes" priority: high
    suggest fix for "stability issues"
end

# Event pattern matching
when system_startup:
    load user_preferences
    initialize monitoring
end
```

---

## Functions

### Function Definition
```neurocode
# Basic function
define greet(name)
    return "Hello, " + name + "!"
end

# Function with multiple parameters
define optimize_system(target_performance, max_iterations)
    for i in range(1, max_iterations):
        current_perf = measure_performance()
        if current_perf >= target_performance:
            break
        end
        apply_optimization(i)
    end
    return current_perf
end

# Function with AI assistance
define analyze_code(filename)
    load filename
    assistant: "analyze this code for potential issues"
    remember(assistant_response) as "code_analysis"
    return analysis_report
end
```

### Function Calls
```neurocode
# Simple function call
greeting = greet("NeuroCode")

# Function call with multiple arguments
final_performance = optimize_system(95.0, 10)

# Function call in expressions
if optimize_system(90.0, 5) > 90.0:
    remember("optimization successful") as "results"
end
```

---

## AI Integration

### Model Selection
```neurocode
# Switch AI models
model: "gpt-4"              # OpenAI GPT-4
model: "mistral"            # Local Mistral via Ollama
model: "llama2"             # Local LLaMA via Ollama
model: "claude-3"           # Anthropic Claude
model: "gemini-pro"         # Google Gemini

# Model with specific configuration
model: "gpt-4" temperature: 0.7 max_tokens: 1000
```

### Assistant Interactions
```neurocode
# Basic assistant request
assistant: "explain this algorithm"

# Assistant with context
load "complex_algorithm.py"
assistant: "optimize this code for performance"

# Assistant with variable interpolation
error_msg = "NullPointer at line 42"
assistant: "fix this error: " + error_msg

# Assistant with conditional logic
if bug_detected:
    assistant: "analyze and suggest fix for the detected bug"
end
```

### AI-Powered Operations
```neurocode
# Code analysis
analyze "myfile.py"
suggest fix for "performance bottleneck"

# Automatic improvements
refactor "myfile.py" "readability"
optimize "database_query.sql"

# Learning from data
learn from "usage_logs.txt"
learn from "error_reports.json"
```

---

## Memory System

### Storing Memories
```neurocode
# Basic memory storage
remember("user prefers dark theme") as "preferences"
remember("optimization improved speed by 40%") as "performance"

# Contextual memory
remember("bug fixed in authentication module") as "debugging"
remember("user workflow: login -> dashboard -> reports") as "behavior"
```

### Retrieving Memories
```neurocode
# Simple recall
user_prefs = recall "preferences"

# Pattern-based recall
optimization_history = recall "performance"
crash_patterns = memory.pattern("crash", frequency="weekly")
```

### Memory Queries
```neurocode
# Check memory contents
if memory.contains("optimization"):
    apply_learned_optimization()
end

# Memory statistics
crash_frequency = memory.frequency("crash")
last_optimization = memory.last("performance")
```

---

## Goal System

### Goal Definition
```neurocode
# Basic goal
goal: "improve system performance"

# Goal with priority
goal: "fix security vulnerabilities" priority: critical

# Goal with metrics
goal: "reduce response time" target: "<200ms" priority: high

# Goal with conditions
goal: "optimize database" if load > 80% priority: medium
```

### Goal Management
```neurocode
# Check goal status
if goal.status("improve performance") == "active":
    continue optimization_process
end

# Goal completion
complete goal "fix security issues"
archive goal "legacy_cleanup"
```

---

## Agent System

### Agent Activation
```neurocode
# Basic agent
agent: on

# Named agent
agent: "performance_monitor"

# Agent with specific role
agent: "security_auditor" scope: "authentication"

# Conditional agent
if system_load > 90%:
    agent: "load_balancer"
end
```

### Agent Configuration
```neurocode
# Agent with parameters
agent: "monitor" interval: 30s actions: ["alert", "optimize"]

# Agent lifecycle
agent: start "backup_manager"
agent: stop "old_process"
agent: restart "web_server"
```

---

## Standard Library

### System Monitoring (sysmon)
```neurocode
# System performance
cpu_usage = sysmon.cpu()
memory_usage = sysmon.memory()
disk_space = sysmon.disk()

# Process monitoring
process_list = sysmon.processes()
top_processes = sysmon.top(5)
```

### Optimizer
```neurocode
# Performance optimization
optimizer.cpu_optimize()
optimizer.memory_cleanup()
optimizer.disk_defrag()

# Code optimization
optimizer.refactor("myfile.py")
optimizer.suggest_improvements("algorithm.py")
```

### Self-Repair (selfrepair)
```neurocode
# Automatic debugging
selfrepair.scan_errors()
selfrepair.suggest_fixes()
selfrepair.apply_fix("syntax_error_line_42")

# System healing
selfrepair.health_check()
selfrepair.auto_repair()
```

### Audio Processing (whisper)
```neurocode
# Speech transcription
text = whisper.transcribe("audio.wav")
real_time_text = whisper.live_transcribe()

# Audio analysis
language = whisper.detect_language("speech.mp3")
confidence = whisper.confidence_score()
```

---

## Multi-LLM Support

NeuroCode supports seamless switching between multiple AI models within the same program:

### Supported Providers
```neurocode
# OpenAI Models
model: "gpt-4"
model: "gpt-3.5-turbo"

# Local Models via Ollama
model: "mistral"
model: "llama2"
model: "mixtral"
model: "codellama"

# Anthropic Models
model: "claude-3"
model: "claude-instant"

# Google Models
model: "gemini-pro"
model: "gemini-1.5"

# Local GGUF Models
model: "local_model.gguf"
```

### Multi-Model Workflows
```neurocode
# Privacy-first analysis with local model
model: "mistral"
assistant: "analyze this sensitive data locally"

# Switch to cloud model for complex reasoning
model: "gpt-4"
assistant: "develop optimization strategy based on analysis"

# Use specialized model for code generation
model: "codellama"
assistant: "generate implementation code"

# Final review with another model
model: "claude-3"
assistant: "review and validate the complete solution"
```

### Model-Specific Features
```neurocode
# Model with configuration
model: "gpt-4" temperature: 0.3 max_tokens: 2000
model: "mistral" context_length: 8192
model: "llama2" top_p: 0.9

# Conditional model selection
if privacy_required:
    model: "mistral"  # Local model
else:
    model: "gpt-4"    # Cloud model for better performance
end
```

---

## Grammar Definition

NeuroCode uses a formal EBNF grammar implemented with the Lark parser. Here are the key grammar rules:

### Core Program Structure
```ebnf
program: statement*

statement: goal_statement
         | remember_statement
         | agent_statement
         | model_statement
         | assistant_statement
         | assignment
         | if_statement
         | for_statement
         | while_statement
         | function_definition
         | function_call
         | comment
```

### AI-Specific Statements
```ebnf
model_statement: "model:" (STRING | IDENTIFIER) model_params?
assistant_statement: "assistant:" value
goal_statement: "goal:" value goal_params?
remember_statement: "remember" "(" value ")" "as" STRING
agent_statement: "agent:" (value | "on" | "off")
```

### Control Flow
```ebnf
if_statement: "if" expression ":" statement* ("else:" statement*)? "end"
for_statement: "for" IDENTIFIER "in" expression ":" statement* "end"
while_statement: "while" expression ":" statement* "end"
function_definition: "define" IDENTIFIER "(" parameters? ")" statement* "end"
```

### Expressions and Values
```ebnf
expression: logical_or
logical_or: logical_and ("or" logical_and)*
logical_and: equality ("and" equality)*
equality: comparison (("==" | "!=") comparison)*
comparison: addition ((">" | "<" | ">=" | "<=") addition)*
addition: multiplication (("+" | "-") multiplication)*
multiplication: primary (("*" | "/" | "%") primary)*

value: STRING | NUMBER | BOOLEAN | IDENTIFIER | list_literal
list_literal: "[" (value ("," value)*)? "]"
```

### Lexical Rules
```ebnf
STRING: "\"" /[^"]*/ "\""
NUMBER: /\d+(\.\d+)?/
BOOLEAN: "true" | "false"
IDENTIFIER: /[a-zA-Z_][a-zA-Z0-9_]*/
COMMENT: /#[^\n]*/
```

---

## Error Handling

NeuroCode includes built-in error handling and self-correction capabilities:

### Automatic Error Detection
```neurocode
# Syntax errors are caught by the parser
# Runtime errors trigger the self-repair system
if error_detected:
    selfrepair.suggest_fix()
    if confidence > 80%:
        selfrepair.apply_fix()
    end
end
```

### Manual Error Handling
```neurocode
try:
    risky_operation()
catch error:
    remember(error) as "error_log"
    assistant: "help fix this error: " + error
end
```

---

## Best Practices

### Code Organization
```neurocode
# Start with goals
goal: "process user data efficiently" priority: high

# Set up AI model
model: "gpt-4"

# Define functions
define process_data(input_file)
    load input_file
    assistant: "analyze data structure and suggest processing strategy"
    # Implementation based on AI suggestions
end

# Main execution
agent: "data_processor"
result = process_data("user_data.csv")
remember(result) as "processing_results"
```

### AI Collaboration
```neurocode
# Use different models for different tasks
model: "mistral"          # Privacy-sensitive analysis
assistant: "analyze user behavior patterns"

model: "gpt-4"            # Complex reasoning
assistant: "develop optimization recommendations"

model: "codellama"        # Code generation
assistant: "implement the recommended optimizations"
```

### Memory Management
```neurocode
# Store important insights
remember("users prefer mobile interface") as "ux_insights"
remember("authentication bug fixed") as "bug_fixes"

# Use memory in decision making
if memory.contains("performance_issues"):
    goal: "optimize performance" priority: high
end
```

---

## Version History

- **v1.0.0** (2024): Initial release with formal grammar, multi-LLM support, and standard library
- **v0.9.0** (2024): Added function definitions, loops, and conditionals  
- **v0.8.0** (2024): Implemented self-repair and debugging system
- **v0.7.0** (2024): Added goal and agent systems
- **v0.6.0** (2024): Introduced memory system
- **v0.5.0** (2024): Basic AI integration and assistant statements

---

*NeuroCode: Where code thinks, learns, and evolves* 🧬✨
