# Aetherra Kernel Event Bus (KEB) System

> Maintained and officially operated by **Aetherra Labs**.
> **Powered by Aetherra Labs.**

Updated: 2025-11-01

This guide explains the Kernel Event Bus (KEB), Aetherra's lightweight in-memory pub/sub messaging system for inter-service communication within the OS.

## Purpose and scope

- Understand event-driven architecture in Aetherra
- Publish and subscribe to system events
- Handle event delivery and acknowledgment
- Monitor event bus metrics
- Implement best practices for event-driven services
- Troubleshoot event delivery issues

## What is the Kernel Event Bus?

The **Kernel Event Bus (KEB)** is a lightweight, in-memory publish-subscribe messaging system that enables loosely-coupled communication between Aetherra services.

### Key Features

- **Asynchronous messaging** - Non-blocking event delivery
- **Topic-based routing** - Services subscribe to specific topics
- **Backpressure handling** - Rate limiting and burst control
- **Best-effort delivery** - Fan-out to all subscribers
- **Minimal durability** - In-memory with optional persistence hooks
- **Observable** - Metrics for monitoring and debugging

### When to Use KEB

**Use KEB for:**

- Service-to-service notifications
- System event broadcasting (homeostasis, HMR, etc.)
- Decoupling service dependencies
- Event-driven workflows

**Don't use KEB for:**

- Long-term event storage (use Memory System)
- Guaranteed delivery (no persistence by default)
- External system integration (use API endpoints)
- High-volume data streams (consider dedicated queues)

---

## Architecture

### Event Flow

```
┌──────────────────────────────────────────────────────────┐
│                   Event Bus Architecture                  │
└──────────────────────────────────────────────────────────┘

   Publisher                Event Bus               Subscribers
   ─────────                ─────────               ───────────

┌──────────┐              ┌──────────┐            ┌───────────┐
│ Service  │   publish    │  Topic:  │  fanout    │ Service A │
│    A     ├─────────────▶│homeostasis│───────────▶│           │
└──────────┘              │          │            └───────────┘
                          │ Backlog: │                  │
┌──────────┐              │ [evt1,   │            ┌─────▼─────┐
│ Service  │   publish    │  evt2,   │  fanout    │ Service B │
│    B     ├─────────────▶│  evt3]   ├───────────▶│           │
└──────────┘              │          │            └───────────┘
                          │Subscribers│                  │
                          │ [A, B, C] │            ┌─────▼─────┐
                          └──────────┘  fanout    │ Service C │
                                       ───────────▶│           │
                                                   └───────────┘
                                                         │
                                                         │ ack
                                                         ▼
                                                   Backlog advances
```

### Components

#### 1. Topics

**Topics** are named channels for events:

```python
@dataclass
class Topic:
    name: str                    # Topic identifier
    backlog: Deque[Dict]        # Event queue (FIFO)
    subscribers: Set[str]       # Subscribed service names
```

**Common topics:**

- `homeostasis` - Health check events
- `hmr` - Hot Module Reload events
- `self_improvement` - Self-improvement proposals
- `memory` - Memory system events
- `plugins` - Plugin lifecycle events
- `kernel` - Kernel lifecycle events

#### 2. Event Bus

**EventBus** manages topics, delivery, and backpressure:

```python
class EventBus:
    def __init__(self, service_registry):
        self.registry = service_registry
        self._topics: Dict[str, Topic] = {}
        self._rate_per_sec = 100.0      # Per-topic rate limit
        self._max_backlog = 1000        # Max events per topic
```

#### 3. Token Bucket Rate Limiting

Events are rate-limited per topic using token bucket algorithm:

- **Rate:** 100 events/second per topic (default)
- **Burst tolerance:** Accumulates tokens when idle
- **Overflow:** Excess events dropped with metric increment

---

## Basic Usage

### Publishing Events

**Via EventBus API:**

```python
from aetherra_event_bus import EventBus

async def publish_homeostasis_event():
    event_bus = get_event_bus()  # Get EventBus instance

    result = await event_bus.publish(
        topic="homeostasis",
        event={
            "type": "health_check",
            "health_score": 0.92,
            "timestamp": time.time()
        }
    )

    if result["ok"]:
        print("Event published successfully")
    else:
        print(f"Failed: {result.get('error')}")
```

**Via Service Registry:**

```python
async def publish_via_registry():
    registry = get_service_registry()

    result = await registry.send_message(
        "event_bus",
        "event.publish",
        {
            "topic": "homeostasis",
            "event": {
                "type": "health_check",
                "health_score": 0.92
            }
        }
    )
```

### Subscribing to Events

**Subscribe to topic:**

```python
async def subscribe_to_homeostasis():
    event_bus = get_event_bus()

    result = await event_bus.subscribe(
        topic="homeostasis",
        service_name="my_service"
    )

    if result["ok"]:
        print("Subscribed successfully")
```

**Receive events via Service Registry:**

```python
class MyService:
    async def handle_message(self, message_type: str, data: Any):
        """Handle incoming messages from Service Registry."""
        if message_type == "keb.event.homeostasis":
            # Handle homeostasis event
            event = data
            print(f"Received event: {event}")

            # Process event
            await self.process_homeostasis_event(event)

            # Acknowledge event
            await self.ack_event("homeostasis")
```

### Acknowledging Events

After processing events, acknowledge to advance the backlog:

```python
async def ack_events():
    event_bus = get_event_bus()

    # Acknowledge 1 event (head of backlog)
    result = await event_bus.ack(topic="homeostasis", count=1)

    if result["ok"]:
        print("Event acknowledged")
```

---

## Event Structure

### Standard Event Format

```python
{
    "ts": "2025-11-01T12:00:00.123456",  # Auto-added timestamp
    "type": "health_check",               # Event type
    "source": "homeostasis_service",      # Event source
    "data": {                             # Event-specific data
        "health_score": 0.92,
        "metrics": {...}
    }
}
```

### Event Types by Topic

**homeostasis:**

```python
{
    "type": "health_check",
    "health_score": 0.92,
    "degraded": False,
    "metrics": {
        "cpu_usage": 0.45,
        "memory_usage": 0.60
    }
}
```

**hmr:**

```python
{
    "type": "HMR_PREPARE",
    "target": "engine",
    "source": "Aetherra.engine_v2"
}
```

**self_improvement:**

```python
{
    "type": "proposal_created",
    "proposal_id": "prop_12345",
    "priority": "high",
    "summary": "Optimize memory query performance"
}
```

**memory:**

```python
{
    "type": "event_stored",
    "event_id": "evt_abc123",
    "event_type": "user_interaction",
    "indexed": True
}
```

**plugins:**

```python
{
    "type": "plugin_loaded",
    "plugin_id": "sample_plugin",
    "version": "1.0.0",
    "capabilities": ["transform"]
}
```

---

## Service Registry Integration

The Event Bus integrates with the Service Registry for message routing:

### Message Types

**Publish event:**

```python
message_type = "event.publish"
data = {
    "topic": "homeostasis",
    "event": {"type": "health_check", "health_score": 0.92}
}
```

**Subscribe to topic:**

```python
message_type = "event.subscribe"
data = {
    "topic": "homeostasis",
    "service": "my_service"
}
```

**Acknowledge events:**

```python
message_type = "event.ack"
data = {
    "topic": "homeostasis",
    "count": 1
}
```

**Get status:**

```python
message_type = "event.status"
data = {}
```

### Broadcasting Events

The Event Bus broadcasts to subscribers using Service Registry:

```python
# Internal EventBus fanout
await self.registry.broadcast_message(
    f"keb.event.{topic}",  # Message type: "keb.event.homeostasis"
    event                   # Event data
)
```

Subscribers receive messages via their `handle_message` method.

---

## Rate Limiting and Backpressure

### Token Bucket Algorithm

Each topic has a token bucket for rate limiting:

**Configuration:**

```python
self._rate_per_sec = 100.0  # 100 events/second per topic
```

**How it works:**

1. Topic starts with 0 tokens
2. Tokens accumulate at `rate_per_sec` (100/sec)
3. Max tokens = `rate_per_sec` (100)
4. Each publish consumes 1 token
5. If tokens < 1, publish fails with `"error": "burst"`

**Example:**

```python
# Rapid publishing
for i in range(150):
    result = await event_bus.publish("test", {"index": i})
    if not result["ok"]:
        print(f"Event {i} dropped: {result['error']}")  # "burst"
```

### Backlog Management

Each topic maintains a bounded backlog:

**Configuration:**

```python
self._max_backlog = 1000  # Max 1000 events per topic
```

**Overflow behavior:**

- When backlog reaches `max_backlog`
- Oldest event is dropped (FIFO)
- New event is enqueued

**Best practices:**

- **Subscribers should ack regularly** to prevent backlog buildup
- **Monitor backlog metrics** to detect slow consumers
- **Increase ack frequency** for high-volume topics

---

## Monitoring and Observability

### Metrics

**Event Bus metrics (Prometheus):**

```python
{
    "events_published_total": 15234,      # Total events published
    "events_delivered_total": 30468,      # Total deliveries (fanout)
    "events_dropped_burst": 12,           # Events dropped due to burst
    "topic_backlog": {                    # Per-topic backlog size
        "homeostasis": 5,
        "hmr": 0,
        "self_improvement": 2
    }
}
```

**Get metrics:**

```python
metrics = event_bus.get_metrics()
print(f"Published: {metrics['events_published_total']}")
print(f"Dropped: {metrics['events_dropped_burst']}")
print(f"Backlogs: {metrics['topic_backlog']}")
```

**Prometheus queries:**

```promql
# Event publish rate
rate(aetherra_keb_events_published_total[5m])

# Event drop rate
rate(aetherra_keb_events_dropped_burst[5m])

# Backlog size
aetherra_keb_topic_backlog{topic="homeostasis"}

# Delivery rate
rate(aetherra_keb_events_delivered_total[5m])
```

### Status Endpoint

Get comprehensive Event Bus status:

```python
status = event_bus.get_status()
```

**Response:**

```json
{
  "topics": {
    "homeostasis": {
      "subscribers": ["health_monitor", "metrics_collector"],
      "backlog": 5
    },
    "hmr": {
      "subscribers": ["hmr_controller"],
      "backlog": 0
    }
  },
  "metrics": {
    "events_published_total": 15234,
    "events_delivered_total": 30468,
    "events_dropped_burst": 12,
    "topic_backlog": {
      "homeostasis": 5,
      "hmr": 0
    }
  }
}
```

---

## Best Practices

### Publisher Best Practices

✅ **Keep events small**

```python
# Good: Minimal event
await event_bus.publish("homeostasis", {
    "type": "health_check",
    "health_score": 0.92
})

# Bad: Large payload
await event_bus.publish("homeostasis", {
    "type": "health_check",
    "full_metrics": {... 10 KB of data ...}
})
```

✅ **Use meaningful event types**

```python
# Good
{"type": "health_check_completed", "score": 0.92}

# Bad
{"type": "event", "status": "done"}
```

✅ **Handle publish failures**

```python
result = await event_bus.publish("topic", event)
if not result["ok"]:
    if result["error"] == "burst":
        # Implement backoff
        await asyncio.sleep(0.1)
        await event_bus.publish("topic", event)
```

✅ **Use appropriate topics**

```python
# Good: Specific topic
await event_bus.publish("homeostasis.health_check", event)

# Bad: Generic topic
await event_bus.publish("system", event)
```

### Subscriber Best Practices

✅ **Acknowledge events promptly**

```python
async def handle_event(event):
    # Process event
    await process(event)

    # Acknowledge immediately
    await event_bus.ack("homeostasis", count=1)
```

✅ **Handle errors gracefully**

```python
async def handle_event(event):
    try:
        await process(event)
        await event_bus.ack("homeostasis", count=1)
    except Exception as e:
        logger.error(f"Failed to process event: {e}")
        # Don't ack on error - will be redelivered
```

✅ **Batch acknowledgments for high volume**

```python
# Process multiple events
events_processed = 0
for event in batch:
    await process(event)
    events_processed += 1

# Batch ack
await event_bus.ack("homeostasis", count=events_processed)
```

❌ **Don't block in event handlers**

```python
# Bad: Blocking operation
async def handle_event(event):
    time.sleep(5)  # Blocks event loop!
    await event_bus.ack("topic", count=1)

# Good: Async operation
async def handle_event(event):
    await asyncio.sleep(5)
    await event_bus.ack("topic", count=1)
```

---

## Advanced Usage

### Custom Topics

Create domain-specific topics:

```python
# Plugin lifecycle events
await event_bus.publish("plugins.lifecycle", {
    "type": "plugin_loaded",
    "plugin_id": "my_plugin"
})

# Memory system events
await event_bus.publish("memory.query", {
    "type": "query_completed",
    "duration_ms": 45
})

# User interaction events
await event_bus.publish("user.interaction", {
    "type": "message_received",
    "user_id": "user_123"
})
```

### Event Filtering

Subscribers can filter events by type:

```python
class MyService:
    async def handle_message(self, message_type: str, data: Any):
        if message_type == "keb.event.homeostasis":
            event = data

            # Filter by event type
            if event.get("type") == "health_check":
                await self.handle_health_check(event)
            elif event.get("type") == "degraded":
                await self.handle_degradation(event)
```

### Event Enrichment

Add metadata to events before publishing:

```python
async def publish_enriched_event(event: dict):
    enriched = {
        **event,
        "source": "my_service",
        "environment": os.getenv("AETHERRA_ENV", "dev"),
        "version": "1.0.0",
        "correlation_id": generate_correlation_id()
    }

    await event_bus.publish("topic", enriched)
```

### Multi-Topic Subscription

Subscribe to multiple topics:

```python
async def subscribe_multiple():
    for topic in ["homeostasis", "hmr", "self_improvement"]:
        await event_bus.subscribe(topic, "my_service")
```

---

## Troubleshooting

### Common Issues

#### 1. Events Not Delivered

**Symptoms:**

- Subscriber not receiving events
- Backlog growing

**Causes:**

- Service not subscribed to topic
- Service not registered in Service Registry
- `handle_message` not implemented

**Solutions:**

```python
# Verify subscription
status = event_bus.get_status()
subscribers = status["topics"]["homeostasis"]["subscribers"]
print(f"Subscribers: {subscribers}")

# Check if service is subscribed
if "my_service" not in subscribers:
    await event_bus.subscribe("homeostasis", "my_service")

# Verify Service Registry registration
services = await registry.list_services()
print(f"Registered services: {services}")
```

#### 2. Events Dropped (Burst)

**Symptoms:**

- `events_dropped_burst` increasing
- Publish returns `{"ok": False, "error": "burst"}`

**Causes:**

- Publishing too fast (> 100 events/sec per topic)
- Burst traffic

**Solutions:**

```python
# Implement backoff
async def publish_with_backoff(topic, event):
    for attempt in range(3):
        result = await event_bus.publish(topic, event)
        if result["ok"]:
            return result

        # Exponential backoff
        await asyncio.sleep(0.1 * (2 ** attempt))

    return result

# Or batch events
events = [...]
for event in events:
    await event_bus.publish(topic, event)
    await asyncio.sleep(0.01)  # 10ms delay = 100/sec
```

#### 3. Backlog Growing

**Symptoms:**

- `topic_backlog` increasing
- Events piling up

**Causes:**

- Subscribers not acknowledging events
- Slow event processing
- No subscribers for topic

**Solutions:**

```python
# Increase ack frequency
async def process_batch():
    batch_size = 10
    for i in range(batch_size):
        event = await get_next_event()
        await process(event)

    # Ack entire batch
    await event_bus.ack("topic", count=batch_size)

# Monitor backlog
metrics = event_bus.get_metrics()
if metrics["topic_backlog"]["homeostasis"] > 100:
    logger.warning("Backlog too high!")
```

#### 4. Missing Events After Restart

**Cause:** Event Bus is in-memory (not persisted)

**Solution:**

- Events are lost on restart by design
- Use Memory System for persistence
- Republish critical events after restart

```python
async def republish_after_restart():
    """Republish critical state after OS restart."""
    if just_restarted():
        # Republish system state
        await event_bus.publish("homeostasis", {
            "type": "health_check",
            "health_score": get_current_health()
        })
```

---

## Performance Considerations

### Throughput

**Per-topic limits:**

- **100 events/second** (rate limit)
- **1000 events** backlog capacity

**System limits:**

- Unlimited topics (bounded by memory)
- Fanout scales with subscriber count

### Memory Usage

**Memory per event:** ~1 KB (estimated)

**Memory per topic:**

- Metadata: ~100 bytes
- Backlog: ~1 KB per event × backlog size

**Example:**

- 10 topics × 100 events backlog = ~1 MB

### Optimization Tips

✅ **Keep events small** (< 1 KB)

✅ **Ack frequently** to reduce backlog

✅ **Use specific topics** to reduce fanout overhead

✅ **Monitor backlog** and adjust ack strategy

---

## Related Documentation

- [AETHERRA_SERVICE_REGISTRY.md](./AETHERRA_SERVICE_REGISTRY.md) - Service Registry integration
- [AETHERRA_HMR_GUIDE.md](./AETHERRA_HMR_GUIDE.md) - HMR events
- [AETHERRA_HOMEOSTASIS_SYSTEM.md](./AETHERRA_HOMEOSTASIS_SYSTEM.md) - Homeostasis events
- [AETHERRA_SELF_IMPROVEMENT_API.md](./AETHERRA_SELF_IMPROVEMENT_API.md) - Self-improvement events
- [TROUBLESHOOTING_GUIDE.md](./TROUBLESHOOTING_GUIDE.md) - Event Bus troubleshooting

---

Status: ✅ Complete - Comprehensive Kernel Event Bus documentation

<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->
