# Enhanced .aether Language Features

## Overview

The `.aether` language has been significantly enhanced with new control structures, error handling, and modern language features while maintaining backward compatibility with existing scripts.

## Phase 1: Core Control & Logic ✅

### 1. if/else Control Blocks

Enhanced conditional execution with modern `{}` block syntax:

```aether
if goal.status == "pending" {
    log "Goal is pending"
} else {
    log "Goal is in progress"
}

# Multiple conditions
if priority == "critical" {
    log "High priority goal"
} else if priority == "high" {
    log "Important goal"
} else {
    log "Standard goal"
}
```

### 2. For/While Loops

Powerful iteration capabilities:

```aether
# For loops with collections
for goal in goals {
    log f"Processing goal: {goal.title}"
}

# For loops with arrays
for item in [1, 2, 3, 4, 5] {
    call process_item(item)
}

# While loops
while incomplete_goals.length > 0 {
    let goal = incomplete_goals.pop()
    call process_goal(goal)
}
```

### 3. Wait/Delay Timing Control

Asynchronous orchestration for retries and pacing:

```aether
# Various time units supported
wait 5s          # 5 seconds
wait 2m          # 2 minutes
wait 1h          # 1 hour

# Use in retry logic
for attempt in [1, 2, 3] {
    try {
        call risky_operation()
        break
    } catch (error) {
        log f"Attempt {attempt} failed: {error}"
        if attempt < 3 {
            wait 30s  # Wait before retry
        }
    }
}
```

### 4. Function Return Values

Functions can now return values for composition and logic:

```aether
fn add(a, b) {
    return a + b
}

fn calculate_priority(urgency, importance) {
    let score = urgency * importance
    if score > 80 {
        return "critical"
    } else if score > 60 {
        return "high"
    } else {
        return "normal"
    }
}

# Usage
let result = add(5, 3)
let priority = calculate_priority(goal.urgency, goal.importance)
```

## Phase 2: Flow Control & Safety ✅

### 5. break/continue Flow Control

Enhanced loop control with early exits:

```aether
for goal in goals {
    if goal.status == "completed" {
        continue  # Skip completed goals
    }

    if goal.priority == "critical" {
        call handle_critical_goal(goal)
        break     # Stop processing after critical goal
    }

    call process_regular_goal(goal)
}
```

### 6. try/catch Error Handling

Robust error handling for resilient scripts:

```aether
try {
    call plugin.execute(goal)
    log "Plugin execution successful"
} catch (error) {
    log f"Plugin execution failed: {error.message}"
    call system/logger.log_event("plugin_error", {
        plugin: plugin.name,
        error: error.message,
        goal_id: goal.id
    })
}

# Multiple catch clauses
try {
    call risky_operation()
} catch (NetworkError as net_err) {
    log f"Network issue: {net_err}"
    wait 30s
    call retry_operation()
} catch (ValidationError as val_err) {
    log f"Validation failed: {val_err}"
    call fix_validation(val_err)
} catch (error) {
    log f"Unknown error: {error}"
}
```

## Phase 3: Clean Syntax & Scalability ✅

### 7. match/switch Pattern Matching

Clean branching logic for complex state handling:

```aether
match goal.status {
    case "pending": {
        log "Goal is waiting to start"
        call queue_for_execution(goal)
    }
    case "in_progress": {
        log "Goal is being processed"
        call monitor_progress(goal)
    }
    case "completed": {
        log "Goal finished successfully"
        call archive_goal(goal)
    }
    case "failed": {
        log "Goal failed"
        call handle_failure(goal)
    }
    default: {
        log f"Unknown status: {goal.status}"
        call escalate_unknown_status(goal)
    }
}

# Match with agent roles
match agent.role {
    case "supervisor": call assign_critical_tasks(agent)
    case "worker": call assign_regular_tasks(agent)
    case "specialist": call assign_specialized_tasks(agent)
    default: call assign_default_tasks(agent)
}
```

### 8. import/use Module System

Cleaner module referencing and organization:

```aether
# Import with alias
import "system/utils" as utils
import "system/logger" as log

# Direct use
use system/goals
use system/agents

# Usage
let time_diff = utils.time_since(goal.created_at)
log.log_event("goal_processed", {goal_id: goal.id})

# Imported functions are available directly
let incomplete = get_incomplete_goals()  # from system/goals
let agent = get_agent_by_role("supervisor")  # from system/agents
```

## Syntax Changes

### Block Delimiters

**Old Syntax:**
```aether
if condition:
    statement1
    statement2
end
```

**New Syntax:**
```aether
if condition {
    statement1
    statement2
}
```

### Function Definitions

**Old Syntax:**
```aether
define function_name(param1, param2):
    # function body
end
```

**New Syntax:**
```aether
fn function_name(param1, param2) {
    # function body
    return result
}
```

## Real-World Examples

### Enhanced Goal Autopilot

```aether
plugin enhanced_goal_autopilot {
    description: "Advanced goal autopilot with enhanced language features"

    fn process_goals() {
        let goals = get_incomplete_goals()
        let processed = 0
        let resumed = 0
        let escalated = 0

        for goal in goals {
            if goal.locked {
                continue  # Skip locked goals
            }

            processed = processed + 1

            try {
                match goal.status {
                    case "pending": {
                        if should_retry(goal) {
                            call resume_goal(goal)
                            resumed = resumed + 1
                        }
                    }
                    case "stalled": {
                        if should_escalate(goal) {
                            call escalate_goal(goal)
                            escalated = escalated + 1
                        }
                    }
                    default: {
                        log f"Unexpected goal status: {goal.status}"
                    }
                }
            } catch (error) {
                log f"Error processing goal {goal.id}: {error}"
                call mark_goal_failed(goal, error.message)
            }

            # Rate limiting
            wait 1s
        }

        return {
            processed: processed,
            resumed: resumed,
            escalated: escalated
        }
    }

    fn should_retry(goal) {
        let time_since_attempt = time_since(goal.last_attempt)
        let max_attempts = 3

        if goal.retry_count >= max_attempts {
            return false
        }

        match goal.priority {
            case "critical": return time_since_attempt > 300   # 5 minutes
            case "high": return time_since_attempt > 600      # 10 minutes
            case "normal": return time_since_attempt > 1800   # 30 minutes
            default: return time_since_attempt > 3600         # 1 hour
        }
    }
}
```

### Smart Plugin Manager

```aether
plugin smart_plugin_manager {
    description: "Advanced plugin management with error recovery"

    fn execute_plugin_safely(plugin_name, data) {
        let max_retries = 3

        for attempt in [1, 2, 3] {
            try {
                let result = call_plugin(plugin_name, data)
                log f"Plugin {plugin_name} executed successfully"
                return result

            } catch (NetworkError as net_err) {
                log f"Network error on attempt {attempt}: {net_err}"
                if attempt < max_retries {
                    wait 10s  # Wait before retry
                    continue
                } else {
                    throw net_err
                }

            } catch (ValidationError as val_err) {
                log f"Validation error: {val_err}"
                # Don't retry validation errors
                throw val_err

            } catch (error) {
                log f"Unknown error on attempt {attempt}: {error}"
                if attempt < max_retries {
                    wait 5s
                    continue
                } else {
                    throw error
                }
            }
        }
    }
}
```

## Migration Guide

### Updating Existing Scripts

1. **Change block syntax**: Replace `: ... end` with `{ ... }`
2. **Update function definitions**: Use `fn` instead of `define`
3. **Add return statements**: Explicitly return values from functions
4. **Enhance error handling**: Wrap risky operations in `try/catch`
5. **Optimize loops**: Use `break/continue` for better flow control

### Backward Compatibility

The enhanced language maintains compatibility with existing `.aether` scripts through:

- Legacy syntax support in the parser
- Automatic syntax migration hints
- Fallback execution modes
- Warning messages for deprecated patterns

## Testing

Use the comprehensive test script to validate enhanced features:

```aether
# Run all enhanced language tests
call system/test_enhanced_language.run_all_tests()

# Test only syntax parsing
call system/test_enhanced_language.test_syntax_only()
```

## Benefits

### 🚀 Improved Readability
- Modern block syntax with `{}`
- Clear function definitions with `fn`
- Explicit return statements

### 🛡️ Enhanced Reliability
- Comprehensive error handling with `try/catch`
- Safe loop controls with `break/continue`
- Pattern matching reduces conditional complexity

### ⚡ Better Performance
- Optimized execution engine
- Efficient loop constructs
- Smart timing controls

### 🔧 Greater Flexibility
- Function return values enable composition
- Module system improves organization
- Pattern matching simplifies complex logic

## Conclusion

The enhanced `.aether` language provides a modern, robust foundation for AI-native programming while preserving the unique characteristics that make Aetherra OS special. These improvements enable more sophisticated goal automation, better error handling, and cleaner code organization.

**Status: 🎉 IMPLEMENTATION COMPLETE**
