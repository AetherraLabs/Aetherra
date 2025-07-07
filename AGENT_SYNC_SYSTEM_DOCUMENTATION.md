# Agent Sync System Documentation

## Overview

The Agent Sync System ensures all system agents are correctly defined, up to date, and aware of relevant plugins. It runs automatically every hour to maintain system consistency.

## Files Structure

```
Aetherra/system/
├── agent_sync.aether      # Main sync plugin
├── agents.aether          # Agent management functions
└── logger.aether          # Event logging system
```

## Agent Sync Plugin (`agent_sync.aether`)

### Configuration
- **Schedule**: Runs every 1 hour
- **Memory Access**: Read-write
- **Tags**: [os, sync, agents]

### Settings
```plaintext
config: {
    log_all_actions: true,
    sync_roles: true,
    allow_agent_regeneration: true
}
```

### Expected Agents
1. **core_agent** (role: core)
   - Plugins: ["goal_autopilot", "memory_cleanser"]

2. **escalation_mgr** (role: escalator)
   - Plugins: ["goal_autopilot", "logger"]

3. **reflection_ai** (role: reflector)
   - Plugins: ["summarizer_plugin"]

### Sync Process
1. **Find Agent**: Check if agent exists using `find_agent()`
2. **Create Missing**: If missing and regeneration allowed, create with `create_agent()`
3. **Update Role**: If role differs, update with `update_agent_role()`
4. **Sync Plugins**: If plugins differ, update with `update_agent_plugins()`
5. **Log Events**: Record all actions for audit trail

## Supporting Functions (`agents.aether`)

### find_agent(agent_id)
```plaintext
fn find_agent(agent_id) {
    return search_memory_one({ type: "agent", id: agent_id })
}
```
- **Purpose**: Find a specific agent by ID
- **Returns**: Agent object or null if not found

### create_agent(agent_def)
```plaintext
fn create_agent(agent_def) {
    store_memory({
        type: "agent",
        id: agent_def.id,
        role: agent_def.role,
        plugins: agent_def.plugins,
        created: now(),
        status: "active",
        health: "healthy",
        current_tasks: [],
        last_activity: now()
    })
}
```
- **Purpose**: Create a new agent with the given definition
- **Parameters**: Agent definition object with id, role, and plugins
- **Creates**: Complete agent record in memory

### update_agent_role(agent_id, new_role)
```plaintext
fn update_agent_role(agent_id, new_role) {
    update_memory(agent_id, { 
        role: new_role,
        last_activity: now()
    })
}
```
- **Purpose**: Update an agent's role
- **Updates**: Role field and last activity timestamp

### update_agent_plugins(agent_id, plugins)
```plaintext
fn update_agent_plugins(agent_id, plugins) {
    update_memory(agent_id, { 
        plugins: plugins,
        last_activity: now()
    })
}
```
- **Purpose**: Update an agent's plugin list
- **Updates**: Plugins array and last activity timestamp

## Event Logging (`logger.aether`)

### log_event(event_type, data, level)
```plaintext
fn log_event(event_type, data, level = "info") {
    let log_entry = {
        type: "system_log",
        event_type: event_type,
        level: level,
        timestamp: now(),
        data: data,
        source: "system_logger",
        session_id: get_session_id()
    }
    
    store_memory(log_entry)
    log "{level_icon} [{event_type}] {format_log_data(data)}"
    
    return log_entry.id
}
```

### Log Event Types
- **agent_created**: New agent was created
- **agent_missing**: Expected agent not found
- **agent_role_updated**: Agent role was changed
- **agent_plugins_synced**: Agent plugins were updated

### Example Log Events

#### Agent Created
```json
{
    "type": "system_log",
    "event_type": "agent_created",
    "data": {
        "id": "core_agent",
        "role": "core",
        "plugins": ["goal_autopilot", "memory_cleanser"]
    },
    "timestamp": "2025-07-07T15:00:00Z",
    "level": "info"
}
```

#### Agent Plugins Synced
```json
{
    "type": "system_log",
    "event_type": "agent_plugins_synced",
    "data": {
        "id": "core_agent",
        "plugins": ["goal_autopilot", "memory_cleanser"]
    },
    "timestamp": "2025-07-07T15:00:00Z",
    "level": "info"
}
```

## Agent Data Structure

### Complete Agent Record
```json
{
    "type": "agent",
    "id": "core_agent",
    "role": "core",
    "plugins": ["goal_autopilot", "memory_cleanser"],
    "created": "2025-07-07T15:00:00Z",
    "status": "active",
    "health": "healthy",
    "current_tasks": [],
    "last_activity": "2025-07-07T15:00:00Z"
}
```

### Agent Status Values
- **active**: Agent is operational
- **inactive**: Agent is disabled
- **maintenance**: Agent is being updated

### Agent Health Values
- **healthy**: Agent is functioning normally
- **degraded**: Agent has performance issues
- **unhealthy**: Agent has critical issues

## Usage Examples

### Manual Sync Trigger
```plaintext
call system/agent_sync.on_run()
```

### Check Agent Status
```plaintext
let agent = call system/agents.find_agent("core_agent")
if agent {
    log "Agent {agent.id} is {agent.status}"
}
```

### Update Agent Plugins
```plaintext
call system/agents.update_agent_plugins("core_agent", ["goal_autopilot", "memory_cleanser", "new_plugin"])
```

### View Sync Logs
```plaintext
let sync_logs = call system/logger.get_logs_by_type("agent_plugins_synced", 10)
```

## Error Handling

### Missing Agent (with regeneration disabled)
```plaintext
if not config.allow_agent_regeneration {
    call system/logger.log_event("agent_missing", expected)
}
```

### Role Update Failure
```plaintext
try {
    call system/agents.update_agent_role(agent_id, new_role)
} catch (error) {
    call system/logger.log_error("agent_role_update_failed", error)
}
```

## Monitoring

### Check Sync Status
```plaintext
let last_sync = call system/logger.get_logs_by_type("agent_sync_complete", 1)[0]
```

### Agent Health Check
```plaintext
let agent_stats = call system/agents.get_agent_statistics()
log "Active agents: {agent_stats.active_agents}/{agent_stats.total_agents}"
```

## Best Practices

1. **Regular Monitoring**: Check sync logs for any recurring issues
2. **Plugin Validation**: Ensure all referenced plugins exist
3. **Graceful Degradation**: Handle missing agents appropriately
4. **Audit Trail**: Keep comprehensive logs of all changes
5. **Performance**: Monitor sync execution time and resource usage

## Security Considerations

- Agent creation requires proper permissions
- Plugin assignments should be validated
- Audit logs should be protected from tampering
- Role changes should be authorized

---

*This documentation covers the complete Agent Sync System implementation for Aetherra OS.*
