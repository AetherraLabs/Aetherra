# Memory Cleanser System Documentation

## Overview

The Memory Cleanser System automatically maintains memory health by removing outdated, low-confidence, and orphaned memory entries. It runs every 12 hours to ensure optimal system performance and data quality.

## Core Components

### Main Plugin: `memory_cleanser.aether`

**Schedule**: Every 12 hours  
**Memory Access**: Read-write  
**Tags**: [os, memory, maintenance]

#### Configuration
```plaintext
config: {
    min_confidence: 0.4,         # Delete entries below this confidence
    max_age_days: 30,            # Delete entries older than this
    enable_orphan_check: true,   # Remove entries linked to deleted goals/plugins
    log_cleaned_entries: true    # Log each deletion for audit trail
}
```

#### Deletion Criteria
1. **Low Confidence**: Entries with confidence < `min_confidence`
2. **Expired**: Entries older than `max_age_days`
3. **Orphaned**: Entries linked to non-existent plugins/goals/agents
4. **Protected Entries**: Entries with `locked=true` or `protected=true` are skipped

## Supporting Modules

### 1. Memory Operations (`memory_ops.aether`)

Core memory management functions:

```plaintext
fn get_all_memory_entries() {
    return search_memory({})  # Optionally batch/paginate later
}

fn delete_memory(id) {
    delete_memory_entry(id)
}

fn get_memory_by_type(type) {
    return search_memory({ type: type })
}

fn get_memory_by_confidence(min_confidence = 0.0, max_confidence = 1.0) {
    return search_memory({
        confidence_gte: min_confidence,
        confidence_lte: max_confidence
    })
}

fn get_memory_older_than(timestamp) {
    return search_memory({
        timestamp_lt: timestamp
    })
}

fn batch_delete_memory(ids) {
    let deleted_count = 0
    for id in ids {
        try {
            delete_memory_entry(id)
            deleted_count += 1
        } catch (error) {
            log "❌ Failed to delete memory entry {id}: {error.message}"
        }
    }
    return deleted_count
}

fn get_memory_stats() {
    # Returns comprehensive memory statistics
}
```

### 2. Time Utilities (`utils.aether`)

Time calculation functions:

```plaintext
fn days_ago(n) {
    return now() - (n * 86400)
}

fn hours_ago(n) {
    return now() - (n * 3600)
}

fn minutes_ago(n) {
    return now() - (n * 60)
}
```

### 3. Existence Checkers

#### Plugins (`plugins.aether`)
```plaintext
fn exists(id_or_name) {
    return search_memory_one({ 
        type: "plugin", 
        name: id_or_name 
    }) != null || search_memory_one({ 
        type: "plugin", 
        id: id_or_name 
    }) != null
}
```

#### Goals (`goals.aether`)
```plaintext
fn exists(id_or_name) {
    return search_memory_one({ 
        type: "goal", 
        id: id_or_name 
    }) != null
}
```

#### Agents (`agents.aether`)
```plaintext
fn exists(id_or_name) {
    return search_memory_one({ 
        type: "agent", 
        id: id_or_name 
    }) != null
}
```

## Workflow Process

### 1. Initialization
```plaintext
let threshold_time = call system/utils.days_ago(config.max_age_days)
let entries = call system/memory_ops.get_all_memory_entries()
```

### 2. Entry Processing
For each memory entry:

```plaintext
# Skip protected entries
if entry.locked or entry.protected {
    continue
}

# Check confidence level
if entry.confidence < config.min_confidence {
    call delete_and_log(entry, "low_confidence")
    continue
}

# Check age
if entry.timestamp < threshold_time {
    call delete_and_log(entry, "expired")
    continue
}

# Check for orphaned references
if config.enable_orphan_check and call is_orphan(entry) {
    call delete_and_log(entry, "orphaned")
}
```

### 3. Orphan Detection
```plaintext
fn is_orphan(entry) {
    if entry.type == "plugin" {
        return not call system/plugins.exists(entry.name)
    }
    if entry.type == "goal" {
        return not call system/goals.exists(entry.id)
    }
    if entry.type == "agent" {
        return not call system/agents.exists(entry.id)
    }
    
    return false  # Default: not orphaned
}
```

### 4. Deletion and Logging
```plaintext
fn delete_and_log(entry, reason) {
    call system/memory_ops.delete_memory(entry.id)
    state.deleted_count += 1

    if config.log_cleaned_entries {
        call system/logger.log_event("memory_deleted", {
            id: entry.id,
            reason: reason,
            type: entry.type,
            confidence: entry.confidence
        })
    }
}
```

## Event Logging

### Memory Deleted Event
```json
{
    "event_type": "memory_deleted",
    "reason": "low_confidence",
    "id": "entry_93481",
    "type": "thought",
    "confidence": 0.21,
    "timestamp": "2025-07-07T23:00:00Z"
}
```

**Deletion Reasons:**
- `low_confidence` - Entry confidence below threshold
- `expired` - Entry older than max age
- `orphaned` - Entry linked to non-existent resource

### Memory Cleanser Complete Event
```json
{
    "event_type": "memory_cleanser_complete",
    "deleted_count": 83,
    "timestamp": "2025-07-07T23:00:00Z"
}
```

## Memory Entry Types

The system handles various memory entry types:

| Type | Description | Orphan Check |
|------|-------------|--------------|
| `plugin` | Plugin-related entries | Check `plugins.exists(entry.name)` |
| `goal` | Goal-related entries | Check `goals.exists(entry.id)` |
| `agent` | Agent-related entries | Check `agents.exists(entry.id)` |
| `thought` | General thoughts and ideas | No orphan check |
| `fact` | Stored facts and information | No orphan check |
| `context` | Contextual information | No orphan check |
| `session` | Session-specific data | No orphan check |

## Configuration Options

### Performance Tuning
```plaintext
config: {
    min_confidence: 0.4,         # Lower = more aggressive cleaning
    max_age_days: 30,            # Lower = more frequent cleanup
    enable_orphan_check: true,   # Disable for performance if needed
    log_cleaned_entries: true    # Disable for reduced logging
}
```

### Memory Protection
Entries with these flags are never deleted:
- `locked: true` - Temporarily protected
- `protected: true` - Permanently protected

## Usage Examples

### Manual Trigger
```plaintext
call system/memory_cleanser.on_run()
```

### Check Memory Statistics
```plaintext
let stats = call system/memory_ops.get_memory_stats()
log "Total entries: {stats.total_entries}"
log "Average confidence: {stats.avg_confidence}"
```

### Get Low Confidence Entries
```plaintext
let low_conf = call system/memory_ops.get_memory_by_confidence(0.0, 0.3)
```

### Get Old Entries
```plaintext
let old_time = call system/utils.days_ago(60)
let old_entries = call system/memory_ops.get_memory_older_than(old_time)
```

## Monitoring and Maintenance

### View Cleanup Logs
```plaintext
let cleanup_logs = call system/logger.get_logs_by_type("memory_cleanser_complete", 10)
let deletion_logs = call system/logger.get_logs_by_type("memory_deleted", 50)
```

### Memory Health Check
```plaintext
let stats = call system/memory_ops.get_memory_stats()
let health_score = stats.avg_confidence
let entry_count = stats.total_entries

if health_score < 0.5 {
    log "⚠️ Low memory quality detected"
}

if entry_count > 10000 {
    log "⚠️ High memory usage detected"
}
```

## Best Practices

1. **Regular Monitoring**: Check cleanup logs for patterns
2. **Confidence Calibration**: Adjust `min_confidence` based on data quality
3. **Age Management**: Set `max_age_days` based on memory patterns
4. **Protection Usage**: Use `locked` and `protected` flags judiciously
5. **Performance Monitoring**: Monitor cleanup execution time

## Security Considerations

- Protected entries cannot be deleted
- All deletions are logged for audit trail
- Orphan checks prevent data integrity issues
- Batch operations include error handling

## Error Handling

### Failed Deletions
```plaintext
try {
    delete_memory_entry(id)
    deleted_count += 1
} catch (error) {
    log "❌ Failed to delete memory entry {id}: {error.message}"
}
```

### Missing References
```plaintext
if not entry.id {
    log "⚠️ Entry missing ID, skipping"
    continue
}
```

---

*This documentation covers the complete Memory Cleanser System for Aetherra OS maintenance operations.*
