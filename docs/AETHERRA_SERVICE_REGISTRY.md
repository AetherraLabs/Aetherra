# Aetherra Service Registry System

> Maintained and officially operated by **Aetherra Labs**.
> **Powered by Aetherra Labs.**

Updated: 2025-11-01

This guide explains the Aetherra Service Registry, which provides service discovery, health monitoring, and inter-service communication for all Aetherra components.

## Purpose and scope

- Understand service registration and discovery
- Register and manage services
- Send messages between services
- Monitor service health and availability
- Implement health checks and heartbeats
- Handle service dependencies
- Troubleshoot service communication issues

## What is the Service Registry?

The **Service Registry** is the central coordination system for Aetherra OS. It enables services to:

- **Register themselves** and become discoverable
- **Discover other services** without hard dependencies
- **Send messages** to specific services
- **Broadcast events** to multiple services
- **Monitor health** via heartbeats
- **Handle failures** gracefully with degradation

### Key Features

- **Service discovery** - Find services by name
- **Health monitoring** - Track service status and heartbeats
- **Inter-service messaging** - Point-to-point and broadcast
- **Dependency tracking** - Manage service dependencies
- **Event system** - React to service lifecycle events
- **Graceful degradation** - Handle unavailable services

---

## Guardian enforcement

Guardian protects the registry trust-state mutation paths that decide whether a service exists, is healthy, or owns its own heartbeat:

- `AetherraServiceRegistry.register_service` declares `service_registry.register` before adding or replacing a service registration.
- `AetherraServiceRegistry.unregister_service` declares `service_registry.unregister` before moving a service to stopping state and removing it from the registry.
- `AetherraServiceRegistry.update_service_status` declares `service_registry.status_update` before mutating service status, heartbeat timestamp, or metadata.
- `AetherraServiceRegistry.update_heartbeat` declares `service_registry.heartbeat_update` before refreshing heartbeat timestamps.
- `AetherraServiceRegistry.mark_service_self_heartbeat` declares `service_registry.self_heartbeat_flag` before changing heartbeat ownership metadata.
- `AetherraServiceRegistry.send_message` declares `service_registry.send_message` before dispatching to a service message handler.
- `AetherraServiceRegistry.broadcast_message` declares `service_registry.broadcast_message` before iterating healthy broadcast targets.
- `AetherraServiceRegistry.subscribe_to_events` and `unsubscribe_from_events` declare Guardian intents before mutating event handler lists.
- `aetherra_registry_client.http_get_status`, `http_register_service`, `http_update`, and `http_heartbeat` declare Guardian intents before outbound HTTP forwarding to an external registry daemon.
- Internal registry bootstrap and maintenance use the internal `service_registry` requester so the system can start and self-monitor safely.
- Explicit external callers are capability-checked in strict mode for registry register, unregister, status, heartbeat, message, broadcast, subscription, and outbound daemon-forwarding capabilities.
- Audit metadata records service names, statuses, metadata keys, dependency names, instance types, message types, payload shapes, handler types, daemon host hashes, endpoint keys, and daemon operations without storing raw metadata values, message payload values, endpoint values, or daemon URLs.

Remaining Guardian scope:

- Keep future registry admin APIs, daemon mutation endpoints, or cross-process service-control messages behind Guardian before enabling them.

## Architecture

### Service Lifecycle

```
┌──────────────────────────────────────────────────────────┐
│                  Service Lifecycle                        │
└──────────────────────────────────────────────────────────┘

STARTING ──register──▶ HEALTHY ──heartbeat──▶ HEALTHY
   │                      │                       │
   │                      │ miss heartbeat        │
   │                      ├──────────────────────▶│
   │                      │                       │
   │                      │                   DEGRADED
   │                      │                       │
   │                      │ stale threshold       │
   │                      ├──────────────────────▶│
   │                      │                       │
   │                      │                    FAILED
   │                      │                       │
   │                      │ unregister            │
   │                      └──────────────────────▶│
   │                                              │
   └──────────────────────────────────────────┴─▶STOPPING
```

### Service Status

```python
class ServiceStatus(Enum):
    STARTING = "starting"    # Initial state
    HEALTHY = "healthy"      # Operating normally
    DEGRADED = "degraded"    # Partial functionality
    FAILED = "failed"        # Not responding
    STOPPING = "stopping"    # Shutting down
```

### Components

#### 1. ServiceInfo

Metadata about registered services:

```python
@dataclass
class ServiceInfo:
    name: str                    # Service name
    instance: Any                # Service instance reference
    status: ServiceStatus        # Current status
    registered_at: datetime      # Registration timestamp
    last_heartbeat: datetime     # Last heartbeat timestamp
    metadata: dict               # Custom metadata
    dependencies: list[str]      # Required services
```

#### 2. AetherraServiceRegistry

Central registry managing all services:

```python
class AetherraServiceRegistry:
    def __init__(self):
        self._services: dict[str, ServiceInfo] = {}
        self._event_handlers: dict[str, list[Callable]] = {}
        self._heartbeat_interval_sec = 60  # Heartbeat check interval
        self._stale_sec = 180              # Stale threshold (3x heartbeat)
```

---

## Basic Usage

### Registering a Service

**Simple registration:**

```python
from aetherra_service_registry import AetherraServiceRegistry

# Create registry instance
registry = AetherraServiceRegistry()
await registry.start()

# Register a service
class MyService:
    def get_status(self):
        return {"healthy": True}

service = MyService()
await registry.register_service(
    name="my_service",
    instance=service
)
```

**With metadata and dependencies:**

```python
await registry.register_service(
    name="memory_adapter",
    instance=memory_adapter,
    metadata={
        "type": "adapter",
        "version": "2.0",
        "self_heartbeat": True  # Service manages own heartbeat
    },
    dependencies=["kernel", "storage"]
)
```

**With status check:**

```python
await registry.register_service(
    name="engine",
    instance=engine,
    status=ServiceStatus.HEALTHY,
    metadata={"capabilities": ["reasoning", "learning"]}
)
```

### Discovering Services

**Get service instance:**

```python
# Get service by name
service = await registry.get_service("my_service")
if service:
    result = await service.do_something()
else:
    print("Service not available")
```

**Check service status:**

```python
status = await registry.get_service_status("my_service")
print(f"Status: {status}")  # ServiceStatus.HEALTHY
```

**List all services:**

```python
services = await registry.list_services()
for name in services:
    print(f"Service: {name}")
```

**Get service info:**

```python
info = registry._services.get("my_service")
if info:
    print(f"Registered: {info.registered_at}")
    print(f"Last heartbeat: {info.last_heartbeat}")
    print(f"Dependencies: {info.dependencies}")
```

### Sending Messages

**Point-to-point messaging:**

```python
# Send message to specific service
result = await registry.send_message(
    service_name="memory_adapter",
    message_type="query",
    data={
        "query": "SELECT * FROM events",
        "limit": 10
    }
)

if result["ok"]:
    print(f"Response: {result['data']}")
```

**Broadcasting to all services:**

```python
# Broadcast to all services with handlers
await registry.broadcast_message(
    message_type="system.shutdown",
    data={"reason": "maintenance"}
)
```

**Broadcasting events:**

```python
# Broadcast event to subscribed handlers
await registry._broadcast_event(
    event_type="service.registered",
    event_data={
        "service": "new_service",
        "timestamp": time.time()
    }
)
```

### Implementing Message Handlers

**Services should implement `handle_message` method:**

```python
class MyService:
    async def handle_message(self, message_type: str, data: Any) -> Any:
        """Handle incoming messages from Service Registry."""
        if message_type == "query":
            # Handle query
            return await self.execute_query(data.get("query"))

        elif message_type == "status_check":
            # Return status
            return {"healthy": True, "load": 0.45}

        elif message_type == "system.shutdown":
            # Handle shutdown
            await self.cleanup()
            return {"ok": True}

        else:
            return {"ok": False, "error": "unknown_message_type"}
```

---

## Health Monitoring

### Heartbeat System

The Registry monitors service health via heartbeats:

**Configuration:**

```bash
# Heartbeat check interval (default: 60 seconds)
export AETHERRA_REGISTRY_HEARTBEAT_SEC=60

# Stale threshold (default: 3x heartbeat interval = 180 seconds)
export AETHERRA_REGISTRY_STALE_SEC=180
```

**How it works:**

1. **Registration:** Service registers with initial heartbeat timestamp
2. **Monitoring:** Registry checks heartbeats every `HEARTBEAT_SEC` seconds
3. **Staleness:** If `last_heartbeat` exceeds `STALE_SEC`, service marked `DEGRADED` or `FAILED`
4. **Recovery:** Service can recover by updating heartbeat

### Self-Heartbeat Services

Services can manage their own heartbeats:

```python
await registry.register_service(
    name="my_service",
    instance=service,
    metadata={"self_heartbeat": True}  # Service manages heartbeat
)

# Service updates its own heartbeat
class MyService:
    async def run(self):
        while self.running:
            # Do work
            await self.do_work()

            # Update heartbeat
            await self.update_heartbeat()

            await asyncio.sleep(30)

    async def update_heartbeat(self):
        await registry.heartbeat("my_service")
```

### Automatic Heartbeats

Registry can automatically monitor services via `get_status()`:

```python
class MyService:
    def get_status(self):
        """Called by Registry during heartbeat checks."""
        return {
            "healthy": True,
            "uptime": self.get_uptime(),
            "metrics": self.get_metrics()
        }

# Registry will call get_status() every heartbeat interval
```

### Health Check Status

```python
# Manual health check
status = await registry.check_service_health("my_service")

if status == ServiceStatus.HEALTHY:
    print("Service is healthy")
elif status == ServiceStatus.DEGRADED:
    print("Service is degraded")
elif status == ServiceStatus.FAILED:
    print("Service has failed")
```

---

## Service Dependencies

### Declaring Dependencies

```python
await registry.register_service(
    name="engine",
    instance=engine,
    dependencies=["memory_adapter", "plugin_manager"]
)
```

### Checking Dependencies

```python
# Check if all dependencies are available
async def check_dependencies(service_name: str):
    info = registry._services.get(service_name)
    if not info:
        return False

    for dep in info.dependencies:
        dep_service = await registry.get_service(dep)
        if not dep_service:
            logger.warning(f"{service_name} missing dependency: {dep}")
            return False

    return True
```

### Waiting for Dependencies

```python
async def wait_for_dependencies(service_name: str, timeout: int = 60):
    """Wait for service dependencies to become available."""
    info = registry._services.get(service_name)
    if not info:
        return False

    start = time.time()
    while time.time() - start < timeout:
        all_available = True
        for dep in info.dependencies:
            if not await registry.get_service(dep):
                all_available = False
                break

        if all_available:
            return True

        await asyncio.sleep(1)

    return False
```

---

## Event System

### Subscribing to Events

```python
# Subscribe to service lifecycle events
async def on_service_registered(event_data):
    service_name = event_data.get("service")
    print(f"New service registered: {service_name}")

registry.subscribe_event("service.registered", on_service_registered)
```

### Event Types

**Service lifecycle events:**

| Event                  | When                     | Data                                        |
| ---------------------- | ------------------------ | ------------------------------------------- |
| `service.registered`   | Service registers        | `{"service": "name", "timestamp": ...}`     |
| `service.unregistered` | Service unregisters      | `{"service": "name", "timestamp": ...}`     |
| `service.degraded`     | Service becomes degraded | `{"service": "name", "status": "degraded"}` |
| `service.failed`       | Service fails            | `{"service": "name", "status": "failed"}`   |
| `service.recovered`    | Service recovers         | `{"service": "name", "status": "healthy"}`  |

**Custom events:**

```python
# Broadcast custom event
await registry._broadcast_event(
    event_type="custom.event",
    event_data={"key": "value"}
)
```

---

## Advanced Usage

### Legacy Service Aliases

Support for legacy service names:

```python
# Legacy aliases map to canonical names
self._legacy_alias_map = {
    "quantum_consciousness": "quantum_cognition",
    "cosmic_consciousness": "universal_cognition",
    "beyond_transcendence": "meta_cognition"
}

# Access via legacy name
service = await registry.get_service("quantum_consciousness")
# Returns the same as: quantum_cognition
```

**Disable legacy aliases:**

```bash
export AETHERRA_DISABLE_LEGACY_ALIASES=1
```

### Message Handler Warnings

Control warning behavior for missing handlers:

```bash
# Warn once per service (no repeated warnings)
export AETHERRA_REGISTRY_WARN_NO_HANDLER=1

# Completely silent (no warnings)
export AETHERRA_REGISTRY_NO_HANDLER_SILENT=1

# Rate-limit warnings (seconds between logs)
export AETHERRA_REGISTRY_NO_HANDLER_RATE_SEC=60
```

### Graceful Service Shutdown

```python
async def shutdown_service(service_name: str):
    """Gracefully shutdown a service."""
    # 1. Mark as stopping
    info = registry._services.get(service_name)
    if info:
        info.status = ServiceStatus.STOPPING

    # 2. Notify service
    await registry.send_message(
        service_name,
        "system.shutdown",
        {}
    )

    # 3. Wait for cleanup
    await asyncio.sleep(2)

    # 4. Unregister
    await registry.unregister_service(service_name)
```

### Service Status Monitoring

```python
async def monitor_services():
    """Monitor all registered services."""
    while True:
        for name, info in registry._services.items():
            age = (datetime.now() - info.last_heartbeat).total_seconds()

            if age > registry._stale_sec:
                logger.warning(f"Service {name} is stale ({age}s)")
                info.status = ServiceStatus.FAILED
            elif age > registry._stale_sec / 2:
                logger.info(f"Service {name} heartbeat delayed ({age}s)")
                info.status = ServiceStatus.DEGRADED

        await asyncio.sleep(registry._heartbeat_interval_sec)
```

---

## Best Practices

### Service Registration

✅ **Register early in service lifecycle:**

```python
class MyService:
    async def start(self):
        # Register as first step
        await registry.register_service("my_service", self)

        # Then initialize
        await self.initialize()
```

✅ **Declare dependencies explicitly:**

```python
await registry.register_service(
    "engine",
    engine,
    dependencies=["memory_adapter", "plugin_manager"]
)
```

✅ **Provide metadata for discoverability:**

```python
await registry.register_service(
    "my_service",
    service,
    metadata={
        "version": "2.0",
        "capabilities": ["query", "index"],
        "api_version": "v1"
    }
)
```

❌ **Don't register the same service multiple times**

### Message Handling

✅ **Implement async message handlers:**

```python
async def handle_message(self, message_type: str, data: Any) -> Any:
    # Process message asynchronously
    result = await self.process(data)
    return {"ok": True, "result": result}
```

✅ **Return meaningful responses:**

```python
async def handle_message(self, message_type: str, data: Any):
    if message_type == "query":
        results = await self.query(data)
        return {"ok": True, "results": results}

    return {"ok": False, "error": "unknown_message_type"}
```

✅ **Handle errors gracefully:**

```python
async def handle_message(self, message_type: str, data: Any):
    try:
        result = await self.process(data)
        return {"ok": True, "result": result}
    except Exception as e:
        logger.error(f"Message handling failed: {e}")
        return {"ok": False, "error": str(e)}
```

❌ **Don't block in message handlers**

### Health Monitoring

✅ **Update heartbeats regularly:**

```python
async def background_task(self):
    while self.running:
        await self.do_work()

        # Update heartbeat every 30 seconds
        await registry.heartbeat("my_service")
        await asyncio.sleep(30)
```

✅ **Implement informative status checks:**

```python
def get_status(self):
    return {
        "healthy": self.is_healthy(),
        "uptime_seconds": self.get_uptime(),
        "requests_processed": self.request_count,
        "error_rate": self.get_error_rate()
    }
```

✅ **Handle service unavailability:**

```python
async def call_service(service_name: str):
    service = await registry.get_service(service_name)
    if not service:
        # Fallback or graceful degradation
        logger.warning(f"Service {service_name} not available")
        return await self.use_fallback()

    return await service.do_work()
```

---

## Troubleshooting

### Common Issues

#### 1. Service Not Found

**Symptoms:**
- `get_service()` returns `None`
- "Service not found" errors

**Causes:**
- Service not registered
- Service name typo
- Service failed and unregistered

**Solutions:**

```python
# List all registered services
services = await registry.list_services()
print(f"Available services: {services}")

# Check if service was ever registered
info = registry._services.get("service_name")
if not info:
    print("Service never registered")
```

#### 2. Service Marked as Failed

**Symptoms:**
- Service status is `FAILED`
- Heartbeat warnings in logs

**Causes:**
- Service not updating heartbeat
- Service crashed
- Heartbeat threshold too aggressive

**Solutions:**

```python
# Check last heartbeat
info = registry._services.get("service_name")
if info:
    age = (datetime.now() - info.last_heartbeat).total_seconds()
    print(f"Last heartbeat: {age} seconds ago")

# Manually update heartbeat
await registry.heartbeat("service_name")

# Adjust threshold
export AETHERRA_REGISTRY_STALE_SEC=300  # 5 minutes
```

#### 3. Messages Not Delivered

**Symptoms:**
- `send_message()` returns error
- No response from service

**Causes:**
- Service doesn't implement `handle_message`
- Handler raising exceptions
- Service not registered

**Solutions:**

```python
# Verify service has handler
service = await registry.get_service("service_name")
if not hasattr(service, 'handle_message'):
    print("Service missing handle_message method")

# Enable handler warnings
export AETHERRA_REGISTRY_WARN_NO_HANDLER=1

# Check service status
status = await registry.get_service_status("service_name")
print(f"Service status: {status}")
```

#### 4. Circular Dependencies

**Symptoms:**
- Services waiting for each other
- Startup hangs

**Solution:**

```python
# Avoid circular dependencies in registration
# Instead, use lazy discovery:

class ServiceA:
    async def use_service_b(self):
        # Discover at call time, not at registration
        service_b = await registry.get_service("service_b")
        if service_b:
            return await service_b.do_work()
```

---

## Performance Considerations

### Service Discovery

- **Fast:** O(1) service lookup by name
- **Cached:** Service references cached after discovery
- **Lightweight:** Minimal memory overhead per service

### Message Delivery

- **Async:** Non-blocking message delivery
- **Direct:** No message queue overhead
- **Fanout:** Broadcast scales with handler count

### Heartbeat Overhead

- **Configurable:** Adjust heartbeat interval based on needs
- **Lightweight:** Simple timestamp update
- **Batched:** All services checked in single pass

---

## Related Documentation

- [AETHERRA_EVENT_BUS_SYSTEM.md](./AETHERRA_EVENT_BUS_SYSTEM.md) - Event Bus integration
- [AETHERRA_HMR_GUIDE.md](./AETHERRA_HMR_GUIDE.md) - HMR uses Service Registry
- [AETHERRA_KERNEL_SYSTEM.md](./AETHERRA_KERNEL_SYSTEM.md) - Kernel integration
- [TROUBLESHOOTING_GUIDE.md](./TROUBLESHOOTING_GUIDE.md) - Service Registry troubleshooting
- [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) - Production configuration

---

Status: ✅ Complete - Comprehensive Service Registry documentation

<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->
