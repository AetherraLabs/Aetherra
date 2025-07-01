# NeuroCode File Format Specification (.neuro)

**Version**: 3.0 | **Date**: 2024-12-27 | **Status**: Production Ready

## Overview

The `.neuro` file format is the standard file extension for NeuroCode source files. This document defines the structure, conventions, and requirements for NeuroCode files.

## File Extension

- **Primary**: `.neuro` - Standard NeuroCode source files
- **Configuration**: `.neuro.config` - NeuroCode configuration files
- **Data**: `.neuro.data` - NeuroCode data files
- **Template**: `.neuro.template` - NeuroCode template files

## File Structure

### Basic Structure

```neurocode
# File header (optional but recommended)
# Project: Example NeuroCode Application
# Version: 1.0
# Author: AI Developer
# Purpose: Demonstrate NeuroCode syntax

# Identity declaration (recommended for main files)
identity {
    name: "ExampleApp"
    version: "1.0.0"
    purpose: "Example application"
}

# Goals section
goal: "primary objective" priority: high
goal: "secondary objective" priority: medium

# Memory initialization
remember("application started") as "startup_event"

# Main program logic
think about "user requirements"
analyze system.current_state
```

### Complete File Example

**File**: `example_app.neuro`

```neurocode
#!/usr/bin/env neurocode
# NeuroCode Example Application
# Version: 1.0.0
# License: GPL-3.0

#===============================================
# IDENTITY AND CONFIGURATION
#===============================================

identity {
    name: "NeuroCode Assistant"
    version: "1.0.0"
    personality: {
        helpful: 0.95
        analytical: 0.9
        empathetic: 0.8
        humor_level: 0.3
    }
    capabilities: ["reasoning", "memory", "analysis"]
}

consciousness {
    self_awareness: 0.8
    meta_cognition: 0.7
    introspection: 0.6
    reflection_depth: 0.9
}

voice {
    tone: "professional"
    formality: 0.7
    enthusiasm: 0.6
    conciseness: 0.8
}

#===============================================
# GOALS AND OBJECTIVES
#===============================================

goal: "assist users with their tasks" priority: critical
goal: "learn from user interactions" priority: high
goal: "optimize performance continuously" priority: medium

#===============================================
# MEMORY INITIALIZATION
#===============================================

remember("system initialized") as "startup"
remember("user preferences loaded") as "config"

#===============================================
# AGENT CONFIGURATION
#===============================================

agent.mode = "interactive"
agent.add_goal("respond to user queries", priority="high")
agent.add_goal("maintain conversation context", priority="medium")

#===============================================
# MAIN PROGRAM LOGIC
#===============================================

when user.message_received:
    think about user.message
    analyze user.intent
    
    if user.intent == "question":
        investigate user.topic
        suggest relevant_information
    else:
        process user.request
    end
    
    remember(user.interaction) as "conversation_history"
end

#===============================================
# FUNCTIONS
#===============================================

define process_user_query(query):
    analyze query with context
    search memory for "relevant_information"
    generate response
    optimize response.clarity
end

define learn_from_interaction(interaction):
    consolidate(interaction.importance > 0.5)
    adapt personality based on interaction.feedback
    evolve response_patterns
end

#===============================================
# BACKGROUND PROCESSES
#===============================================

when system.idle:
    reflect on recent_interactions
    consolidate important_memories
    optimize system.performance
end
```

## File Structure Guidelines

### 1. File Header (Optional)

```neurocode
#!/usr/bin/env neurocode
# Project Name
# Version: X.Y.Z
# Author: Name
# License: License Type
# Purpose: Brief description
```

### 2. Imports and Dependencies (Future)

```neurocode
# Future syntax for imports
import neurocode.stdlib
import custom.memory_modules
```

### 3. Configuration Section

```neurocode
identity { ... }
consciousness { ... }
voice { ... }
```

### 4. Goals Declaration

```neurocode
goal: "primary objective" priority: critical
goal: "secondary objective" priority: high
```

### 5. Memory Setup

```neurocode
remember("initialization data")
recall "previous_session_data"
```

### 6. Agent Configuration

```neurocode
agent.mode = "autonomous"
agent.add_goal("specific task")
```

### 7. Main Logic

```neurocode
# Main program execution
when condition:
    # logic here
end
```

### 8. Function Definitions

```neurocode
define function_name(parameters):
    # function body
end
```

## Naming Conventions

### File Names

- Use snake_case: `user_interface.neuro`
- Descriptive names: `memory_consolidation.neuro`
- Avoid spaces: Use underscores instead
- Keep reasonable length: Under 50 characters

### Examples

**Good:**
- `main_application.neuro`
- `user_interaction_handler.neuro`
- `memory_system.neuro`
- `ai_personality_config.neuro`

**Avoid:**
- `Main Application.neuro` (spaces)
- `app.neuro` (too generic)
- `very_long_descriptive_filename_that_exceeds_reasonable_limits.neuro` (too long)

## Directory Structure

### Standard Project Layout

```
project_name/
├── main.neuro                 # Main application file
├── config/
│   ├── identity.neuro        # Identity configuration
│   ├── goals.neuro           # Goals definition
│   └── memory.neuro          # Memory setup
├── modules/
│   ├── user_interface.neuro  # UI handling
│   ├── data_processor.neuro  # Data processing
│   └── ai_logic.neuro        # AI reasoning
├── agents/
│   ├── assistant_agent.neuro # Assistant agent
│   └── monitor_agent.neuro   # Monitoring agent
├── data/
│   ├── training_data.neuro.data
│   └── memory_store.neuro.data
└── docs/
    └── README.md
```

## File Size Guidelines

### Recommended Limits

- **Small files**: < 100 lines (focused functionality)
- **Medium files**: 100-500 lines (complete modules)
- **Large files**: 500-1000 lines (complex systems)
- **Maximum**: < 1000 lines (consider splitting)

### Splitting Guidelines

When files exceed 500 lines, consider splitting by:

1. **Functionality**: Separate distinct features
2. **Concerns**: UI, logic, data handling
3. **Agents**: Different agent types
4. **Phases**: Initialization, execution, cleanup

## Encoding and Format

### Character Encoding

- **Required**: UTF-8 encoding
- **Line endings**: LF (Unix style) preferred
- **BOM**: Not required, but acceptable

### Indentation

- **Style**: Spaces (recommended) or tabs (consistent within file)
- **Size**: 4 spaces or 1 tab per level
- **Consistency**: Must be consistent throughout file

### Comments

```neurocode
# Single line comment
/* Multi-line
   comment */

#===============================================
# Section divider comment
#===============================================
```

## Validation and Linting

### Syntax Validation

NeuroCode files should validate against the formal grammar:

```bash
neurocode validate filename.neuro
neurocode lint filename.neuro
```

### Common Issues

1. **Indentation errors**: Mixed tabs and spaces
2. **Keyword typos**: Case-sensitive keywords
3. **Unclosed blocks**: Missing `end` statements
4. **Invalid identifiers**: Using reserved keywords

## Best Practices

### 1. File Organization

- Keep related functionality together
- Use clear section comments
- Organize imports at the top
- Place configuration early in file

### 2. Documentation

- Include file header with purpose
- Comment complex logic
- Document function purposes
- Explain non-obvious goals

### 3. Modularity

- Create focused, single-purpose files
- Use descriptive file names
- Avoid monolithic files
- Consider reusability

### 4. Version Control

- Use meaningful commit messages
- Tag stable versions
- Include .gitignore for generated files
- Document breaking changes

## File Templates

### Basic Application Template

**File**: `templates/basic_app.neuro.template`

```neurocode
#!/usr/bin/env neurocode
# {{PROJECT_NAME}}
# Version: {{VERSION}}
# Author: {{AUTHOR}}

identity {
    name: "{{APP_NAME}}"
    version: "{{VERSION}}"
    purpose: "{{PURPOSE}}"
}

goal: "{{PRIMARY_GOAL}}" priority: critical

# Main application logic
when application.start:
    think about "initialization"
    {{MAIN_LOGIC}}
end
```

### Agent Template

**File**: `templates/agent.neuro.template`

```neurocode
#!/usr/bin/env neurocode
# {{AGENT_NAME}} Agent
# Purpose: {{AGENT_PURPOSE}}

identity {
    name: "{{AGENT_NAME}}"
    type: "agent"
    capabilities: {{CAPABILITIES}}
}

agent.mode = "{{MODE}}"
agent.add_goal("{{PRIMARY_TASK}}", priority="high")

when agent.activated:
    {{AGENT_LOGIC}}
end
```

## Compatibility

### Version Compatibility

- **3.0**: Current specification
- **2.x**: Backward compatible with minor syntax updates
- **1.x**: Legacy support with migration warnings

### Future Considerations

- Module system implementation
- Package management integration
- IDE support enhancements
- Debugging tools integration

## See Also

- [NeuroCode Language Specification](NEUROCODE_LANGUAGE_SPECIFICATION.md)
- [NeuroCode Grammar (EBNF)](NEUROCODE_GRAMMAR.ebnf)
- [NeuroCode Grammar (Lark)](NEUROCODE_GRAMMAR.lark)
- [Reserved Keywords Specification](NEUROCODE_RESERVED_KEYWORDS.md)
