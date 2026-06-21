# 🚀 Interactive Lyrixa — Quick Start Integration Guide

## Prerequisites

- Aetherra OS must be running with:
  - Kernel Event Bus (KEB) initialized
  - Service Registry active
  - Homeostasis system loaded (optional but recommended)
  - Memory system loaded (optional but recommended)

## Step 1: Add to OS Launcher

Edit `aetherra_os_launcher.py` and add the Interactive Lyrixa initialization:

```python
async def _load_interactive_lyrixa_system(self):
    """Load Interactive Lyrixa system."""
    try:
        logger.info("[SYS] Loading Interactive Lyrixa System...")

        from Aetherra.lyrixa.interactive import initialize_interactive_system
        from aetherra_event_bus import get_event_bus

        # Get event bus
        event_bus = await get_event_bus(self.service_registry)

        # Initialize Interactive Lyrixa
        interactive_lyrixa = await initialize_interactive_system(
            event_bus=event_bus,
            service_registry=self.service_registry,
            config={
                "sample_interval": 5.0,  # Sample system health every 5 seconds
                "feature_flags": {
                    "expressions_enabled": True,
                    "voice_enabled": False,  # Optional voice plugin
                }
            }
        )

        # Register with systems dict
        self.systems["interactive_lyrixa"] = interactive_lyrixa

        logger.info("✅ Interactive Lyrixa System loaded successfully")

    except Exception as e:
        logger.error(f"❌ Failed to load Interactive Lyrixa: {e}", exc_info=True)
```

Then call it in your main load sequence:

```python
async def initialize(self):
    # ... existing initialization ...

    # Load Interactive Lyrixa (after KEB, memory, homeostasis)
    await self._load_interactive_lyrixa_system()
```

## Step 2: Feature Flag Configuration

Add to your config file (`config.json` or `config.production.json`):

```json
{
  "interactive_lyrixa": {
    "enabled": true,
    "sample_interval": 5.0,
    "expressions": {
      "calm": {"duration_ms": 5000, "intensity": 0.3},
      "focused": {"duration_ms": 3000, "intensity": 0.7},
      "concerned": {"duration_ms": 4000, "intensity": 0.8}
    },
    "voice_plugin": {
      "enabled": false,
      "volume": 0.5,
      "rate_limit_ms": 1000
    }
  }
}
```

## Step 3: GUI Integration (Optional)

If using the PySide6 GUI, wire expression events to visual feedback:

```python
from Aetherra.lyrixa.interactive import get_interactive_system

class LyrixaMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.interactive_lyrixa = None

    async def initialize_interactive_ui(self):
        """Initialize Interactive Lyrixa UI integration."""
        # Get the system instance
        self.interactive_lyrixa = await get_interactive_system()

        # Subscribe to expression events via KEB
        if self.interactive_lyrixa.expression_manager:
            self.interactive_lyrixa.expression_manager.register_enter_hook(
                ExpressionState.CONCERNED,
                self.on_lyrixa_concerned
            )

            self.interactive_lyrixa.expression_manager.register_enter_hook(
                ExpressionState.DELIGHTED,
                self.on_lyrixa_delighted
            )

    def on_lyrixa_concerned(self, state):
        """Update UI when Lyrixa becomes concerned."""
        # Change avatar glow to orange, show warning animation
        self.avatar.set_glow_color(QColor(255, 140, 0))
        self.avatar.start_animation("flicker")

    def on_lyrixa_delighted(self, state):
        """Update UI when Lyrixa is delighted."""
        # Change avatar glow to golden, show sparkle animation
        self.avatar.set_glow_color(QColor(255, 215, 0))
        self.avatar.start_animation("sparkle")
```

## Step 4: Track User Activity

Wire user interactions to activity tracking:

```python
class ChatInterface:
    def on_user_message(self, message):
        """Handle user message."""
        # Record activity
        if self.interactive_lyrixa:
            self.interactive_lyrixa.record_user_activity()

        # Process message...
```

## Step 5: Monitor & Observe

### Check Status

```python
status = interactive_lyrixa.get_status()
print(f"Running: {status['running']}")
print(f"Current Emotion: {status['current_emotion']['mood']}")
print(f"Current Expression: {status['expression_manager']['state']}")
```

### Access Metrics

Metrics are automatically exported via Hub at `/metrics`:

```
# HELP lyrixa_emotion_intensity_avg Current emotion intensity
lyrixa_emotion_intensity_avg 0.7

# HELP lyrixa_expression_state_transitions_total Total expression transitions
lyrixa_expression_state_transitions_total 42

# HELP lyrixa_expressions_emitted_total Total expressions emitted to KEB
lyrixa_expressions_emitted_total 38
```

## Step 6: Test the System

Run the smoke tests:

```powershell
pytest tests/smoke/test_interactive_lyrixa.py -v
```

Expected output:
```
tests/smoke/test_interactive_lyrixa.py::test_expression_manager_initializes PASSED
tests/smoke/test_interactive_lyrixa.py::test_expression_manager_starts_and_stops PASSED
tests/smoke/test_interactive_lyrixa.py::test_expression_manager_publishes_events PASSED
tests/smoke/test_interactive_lyrixa.py::test_interactive_loop_initializes PASSED
tests/smoke/test_interactive_lyrixa.py::test_interactive_loop_starts_and_stops PASSED
tests/smoke/test_interactive_lyrixa.py::test_emotion_mapper_rules PASSED
tests/smoke/test_interactive_lyrixa.py::test_keb_topics_registered PASSED
tests/smoke/test_interactive_lyrixa.py::test_integrated_system_starts PASSED
tests/smoke/test_interactive_lyrixa.py::test_user_activity_tracking PASSED
tests/smoke/test_interactive_lyrixa.py::test_error_burst_detection PASSED
tests/smoke/test_interactive_lyrixa.py::test_expression_hooks PASSED

============================== 11 passed in 15.23s ==============================
```

## Troubleshooting

### Problem: Expression Manager not publishing events

**Solution**: Check that KEB is properly initialized:
```python
event_bus = await get_event_bus(service_registry)
status = event_bus.get_status()
print(status)  # Should show lyrixa.* topics
```

### Problem: Interactive Loop not sampling health

**Solution**: Verify component discovery:
```python
loop = await get_interactive_loop(...)
print(f"Homeostasis: {loop.homeostasis is not None}")
print(f"Memory: {loop.memory_system is not None}")
print(f"Kernel: {loop.kernel is not None}")
```

### Problem: No emotion changes detected

**Solution**: Check thresholds and sample interval:
```python
config = {
    "sample_interval": 2.0,  # Sample more frequently
}
```

Also verify that health metrics are actually changing.

## Phase 1 Rollout: Minimal "Eyes Open" Mode

Start with just `calm` and `focused` states driven by memory coherence:

```python
config = {
    "enabled_states": ["calm", "focused"],
    "signal_sources": ["memory"],  # Only memory pulse
    "sample_interval": 10.0,  # Less frequent
}
```

## Phase 2+: Full Feature Activation

Once Phase 1 is stable, enable all features:

```python
config = {
    "enabled_states": "all",
    "signal_sources": ["memory", "homeostasis", "kernel", "storm", "chat"],
    "sample_interval": 5.0,
    "voice_plugin": {
        "enabled": True,
        "volume": 0.5
    }
}
```

## Need Help?

- Review `docs/INTERACTIVE_LYRIXA.md` for full architecture
- Check logs: `grep "Interactive Lyrixa" aetherra_system.log`
- Verify metrics: `curl http://localhost:3001/metrics | grep lyrixa`

## What's Next?

1. **GUI Visualization**: Create visual expression renderer
2. **Voice Integration**: Add actual audio backend (sounddevice, pygame)
3. **Mobile Support**: Adapt for touch/haptic feedback
4. **ML Tuning**: Train emotion mapper weights from user feedback

**Lyrixa is ready to come alive! 🌟**
