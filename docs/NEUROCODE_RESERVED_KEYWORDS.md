# NeuroCode Reserved Keywords Specification
**Version**: 3.0 | **Date**: 2024-12-27 | **Status**: Production Ready

## Overview

This document defines all reserved keywords in the NeuroCode programming language. These keywords have special meaning in the language and cannot be used as identifiers (variable names, function names, etc.).

## Core Language Keywords

### Program Structure
- `goal` - Declares an AI goal or objective
- `identity` - Defines persistent AI identity
- `consciousness` - Configures consciousness parameters
- `memory` - Memory system operations
- `voice` - Voice and personality settings
- `agent` - Agent control and management

### Control Flow
- `when` - Conditional execution based on state
- `if` - Standard conditional statement
- `else` - Alternative branch for conditionals
- `end` - Block terminator (alternative syntax)
- `for` - Iteration over collections
- `while` - Loop with condition
- `in` - Iterator/membership operator

### Function System
- `define` - Function definition
- `run` - Function invocation
- `return` - Function return (implicit in NeuroCode)

### Memory Operations
- `remember` - Store information in memory
- `recall` - Retrieve information from memory
- `forget` - Remove information from memory
- `consolidate` - Memory consolidation process
- `search` - Search memory content
- `pattern` - Pattern recognition in memory

### Intent Actions
- `think` - Cognitive processing
- `analyze` - Data analysis operation
- `optimize` - Optimization process
- `learn` - Learning operation
- `investigate` - Investigation process
- `suggest` - Suggestion generation
- `reflect` - Self-reflection operation
- `adapt` - Adaptation process
- `evolve` - Evolution/improvement process
- `process` - General processing
- `understand` - Comprehension operation
- `create` - Creation operation
- `modify` - Modification operation
- `delete` - Deletion operation

### Priority Levels
- `critical` - Critical priority level
- `high` - High priority level
- `medium` - Medium priority level
- `low` - Low priority level

### Boolean Values
- `true` - Boolean true value
- `false` - Boolean false value

### Logical Operators
- `and` - Logical AND operator
- `or` - Logical OR operator
- `not` - Logical NOT operator

### Agent Control
- `mode` - Agent operating mode
- `start` - Start agent operation
- `stop` - Stop agent operation
- `pause` - Pause agent operation
- `resume` - Resume agent operation
- `status` - Get agent status
- `add_goal` - Add goal to agent
- `remove_goal` - Remove goal from agent
- `clear_goals` - Clear all agent goals
- `list_goals` - List agent goals

### Memory Modifiers
- `as` - Alias or categorization
- `since` - Time-based filtering
- `category` - Category-based organization
- `frequency` - Pattern frequency

### Intent Modifiers
- `about` - Topic specification
- `for` - Purpose specification
- `from` - Source specification
- `on` - Subject specification
- `with` - Tool/method specification
- `using` - Instrument specification
- `through` - Means specification

### Time and Scheduling
- `deadline` - Goal deadline specification
- `priority` - Priority specification

### System Properties
- `name` - Identity name
- `version` - Version identifier
- `personality` - Personality configuration
- `traits` - Character traits
- `capabilities` - System capabilities
- `self_awareness` - Self-awareness level
- `meta_cognition` - Meta-cognitive level
- `introspection` - Introspection depth
- `reflection_depth` - Reflection capability
- `tone` - Communication tone
- `formality` - Formality level
- `enthusiasm` - Enthusiasm level
- `conciseness` - Conciseness level

## Keyword Categories

### 1. Core Constructs (14 keywords)
```
goal, identity, consciousness, memory, voice, agent, when, if, else, 
end, define, run, for, while
```

### 2. Memory System (6 keywords)
```
remember, recall, forget, consolidate, search, pattern
```

### 3. Intent Actions (15 keywords)
```
think, analyze, optimize, learn, investigate, suggest, reflect, 
adapt, evolve, process, understand, create, modify, delete, search
```

### 4. Agent System (10 keywords)
```
mode, start, stop, pause, resume, status, add_goal, remove_goal, 
clear_goals, list_goals
```

### 5. Logical Operations (8 keywords)
```
and, or, not, true, false, in, ==, !=
```

### 6. Priority System (4 keywords)
```
critical, high, medium, low
```

### 7. Modifiers and Prepositions (12 keywords)
```
as, since, category, frequency, about, for, from, on, with, 
using, through, deadline
```

### 8. System Properties (13 keywords)
```
name, version, personality, traits, capabilities, self_awareness,
meta_cognition, introspection, reflection_depth, tone, formality,
enthusiasm, conciseness
```

## Total Reserved Keywords: 82

## Usage Rules

### 1. Case Sensitivity
All NeuroCode keywords are case-sensitive and must be written in lowercase.

**Valid:**
```neurocode
goal: "optimize performance"
```

**Invalid:**
```neurocode
GOAL: "optimize performance"  # Error: GOAL is not recognized
Goal: "optimize performance"  # Error: Goal is not recognized
```

### 2. Keyword Context
Some words may appear as both keywords and property names depending on context:

**As keyword:**
```neurocode
identity {
    name: "Assistant"
}
```

**As property (allowed):**
```neurocode
my_identity = {
    name: "Custom Name"
}
```

### 3. Future Keyword Reservation
The following words are reserved for future language expansion:
```
async, await, class, import, export, module, package, namespace,
try, catch, finally, throw, yield, async, sync, parallel, sequential
```

## Compatibility Notes

### Version 3.0 Changes
- Added agent control keywords: `pause`, `resume`, `list_goals`, `remove_goal`
- Added memory modifiers: `frequency`, `category`
- Added intent modifiers: `with`, `using`, `through`
- Added system properties: `enthusiasm`, `conciseness`

### Backward Compatibility
All keywords from NeuroCode 2.x remain valid in 3.0. New code should use the updated syntax where available.

## Best Practices

### 1. Variable Naming
Avoid using reserved keywords as variable names:

**Good:**
```neurocode
user_name = "Alice"
priority_level = "high"
```

**Bad:**
```neurocode
name = "Alice"      # Conflicts with identity property
priority = "high"   # Conflicts with goal priority
```

### 2. Future-Proofing
Avoid using reserved future keywords in your code to ensure compatibility with future NeuroCode versions.

### 3. Contextual Usage
When in doubt about keyword usage, refer to the formal grammar specification in `NEUROCODE_GRAMMAR.ebnf` and `NEUROCODE_GRAMMAR.lark`.

## See Also

- [NeuroCode Language Specification](NEUROCODE_LANGUAGE_SPECIFICATION.md)
- [NeuroCode Grammar (EBNF)](NEUROCODE_GRAMMAR.ebnf)
- [NeuroCode Grammar (Lark)](NEUROCODE_GRAMMAR.lark)
- [File Format Specification](NEUROCODE_FILE_FORMAT.md)
