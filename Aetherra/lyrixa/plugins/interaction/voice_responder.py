#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors
"""
🔊 Lyrixa Voice Responder Plugin
================================

Subscribes to lyrixa.expression events and plays non-verbal audio cues
based on Lyrixa's emotional state and confidence levels.

This plugin is OPTIONAL and user-toggleable. When enabled, it provides
subtle audio feedback that enhances Lyrixa's interactive presence without
being intrusive.

Audio Cues:
- Calm: Soft ambient hum
- Focused: Gentle pulse tone
- Concerned: Warning chime
- Delighted: Pleasant bell
- Thoughtful: Contemplative note
- Confident: Bright affirming tone

All audio is generated synthetically or uses royalty-free samples.
"""

import asyncio
import contextlib
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class AudioCue(Enum):
    """Available audio cue types."""

    AMBIENT_HUM = "ambient_hum"
    GENTLE_PULSE = "gentle_pulse"
    WARNING_CHIME = "warning_chime"
    PLEASANT_BELL = "pleasant_bell"
    CONTEMPLATIVE_NOTE = "contemplative_note"
    BRIGHT_TONE = "bright_affirming"
    ALERT_TONE = "alert_tone"
    SILENCE = "silence"


@dataclass
class AudioConfig:
    """Configuration for audio playback."""

    enabled: bool = False
    volume: float = 0.5  # 0.0-1.0
    rate_limit_ms: int = 1000  # Min time between cues
    cue_duration_ms: int = 500
    fade_in_ms: int = 50
    fade_out_ms: int = 50


class VoiceResponderPlugin:
    """
    Plugin that provides non-verbal audio feedback based on Lyrixa's expressions.

    Subscribes to lyrixa.expression events from KEB and plays appropriate
    audio cues. Respects user settings and system load.
    """

    def __init__(self, event_bus=None, config: Optional[AudioConfig] = None):
        """
        Initialize the voice responder plugin.

        Args:
            event_bus: Kernel Event Bus for subscribing to expressions
            config: Audio configuration
        """
        self.event_bus = event_bus
        self.config = config or AudioConfig()

        # State tracking
        self.last_cue_time = 0.0
        self.current_cue: Optional[AudioCue] = None

        # Running state
        self.running = False
        self.subscription_task: Optional[asyncio.Task] = None

        # Audio backend (placeholder — would use actual audio library)
        self.audio_backend = None  # e.g., sounddevice, pygame, pydub

        # Expression to audio cue mapping
        self.expression_to_cue = {
            "calm": AudioCue.AMBIENT_HUM,
            "focused": AudioCue.GENTLE_PULSE,
            "concerned": AudioCue.WARNING_CHIME,
            "delighted": AudioCue.PLEASANT_BELL,
            "thoughtful": AudioCue.CONTEMPLATIVE_NOTE,
            "confident": AudioCue.BRIGHT_TONE,
            "pensive": AudioCue.CONTEMPLATIVE_NOTE,
            "on_edge": AudioCue.ALERT_TONE,
            "resting": AudioCue.SILENCE,
        }

        # Statistics
        self.stats = {
            "cues_played": 0,
            "cues_rate_limited": 0,
            "cues_skipped_disabled": 0,
        }

        logger.info("🔊 Voice Responder Plugin initialized")

    async def start(self):
        """Start the voice responder plugin."""
        if self.running:
            logger.warning("Voice Responder already running")
            return

        if not self.config.enabled:
            logger.info("Voice Responder disabled by config")
            return

        self.running = True
        logger.info("🚀 Starting Voice Responder Plugin")

        # Subscribe to lyrixa.expression events
        if self.event_bus:
            await self._subscribe_to_expressions()

        # Start audio playback loop
        self.subscription_task = asyncio.create_task(self._playback_loop())

        logger.info("✅ Voice Responder Plugin started")

    async def stop(self):
        """Stop the voice responder plugin."""
        if not self.running:
            return

        logger.info("🛑 Stopping Voice Responder Plugin")
        self.running = False

        if self.subscription_task and not self.subscription_task.done():
            self.subscription_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self.subscription_task

        # Stop any playing audio
        await self._stop_audio()

        logger.info("✅ Voice Responder Plugin stopped")

    async def _subscribe_to_expressions(self):
        """Subscribe to expression events from KEB."""
        if not self.event_bus:
            return

        try:
            await self.event_bus.subscribe("lyrixa.expression", "voice_responder_plugin")
            logger.debug("📡 Subscribed to lyrixa.expression events")
        except Exception as e:
            logger.warning(f"Failed to subscribe to expressions: {e}")

    async def _playback_loop(self):
        """Main playback loop."""
        while self.running:
            try:
                # Placeholder for actual audio playback logic
                # In reality, this would poll the event bus or use callbacks
                await asyncio.sleep(0.1)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in playback loop: {e}", exc_info=True)
                await asyncio.sleep(1.0)

    async def handle_expression_event(self, event: Dict[str, Any]):
        """
        Handle an expression event and play appropriate audio cue.

        Args:
            event: Expression event data from KEB
        """
        if not self.config.enabled:
            self.stats["cues_skipped_disabled"] += 1
            return

        try:
            expression_state = event.get("state", "calm")
            intensity = event.get("intensity", 0.5)

            # Get appropriate audio cue
            cue = self.expression_to_cue.get(expression_state, AudioCue.SILENCE)

            if cue == AudioCue.SILENCE:
                return

            # Check rate limiting
            import time

            current_time = time.time()
            time_since_last = (current_time - self.last_cue_time) * 1000  # ms

            if time_since_last < self.config.rate_limit_ms:
                self.stats["cues_rate_limited"] += 1
                logger.debug(f"Rate limited audio cue: {cue.value}")
                return

            # Play the cue
            await self._play_cue(cue, intensity)

            self.last_cue_time = current_time
            self.current_cue = cue
            self.stats["cues_played"] += 1

            logger.debug(f"🔊 Played audio cue: {cue.value} (intensity={intensity:.2f})")

        except Exception as e:
            logger.error(f"Error handling expression event: {e}", exc_info=True)

    async def _play_cue(self, cue: AudioCue, intensity: float):
        """
        Play an audio cue.

        Args:
            cue: Audio cue type
            intensity: Playback intensity (affects volume)
        """
        # PLACEHOLDER: This would integrate with actual audio backend

        # Example with sounddevice (requires: pip install sounddevice numpy):
        # import sounddevice as sd
        # import numpy as np
        #
        # duration = self.config.cue_duration_ms / 1000.0
        # volume = self.config.volume * intensity
        #
        # # Generate simple tone based on cue type
        # frequency_map = {
        #     AudioCue.AMBIENT_HUM: 110,  # Low A
        #     AudioCue.GENTLE_PULSE: 220,  # A3
        #     AudioCue.WARNING_CHIME: 440,  # A4
        #     AudioCue.PLEASANT_BELL: 880,  # A5
        #     AudioCue.CONTEMPLATIVE_NOTE: 330,  # E4
        #     AudioCue.BRIGHT_TONE: 660,  # E5
        #     AudioCue.ALERT_TONE: 1000,  # High warning
        # }
        #
        # freq = frequency_map.get(cue, 440)
        # samples = np.sin(2 * np.pi * freq * np.linspace(0, duration, int(44100 * duration)))
        # samples = samples * volume
        #
        # # Apply fade in/out
        # fade_samples_in = int(44100 * self.config.fade_in_ms / 1000.0)
        # fade_samples_out = int(44100 * self.config.fade_out_ms / 1000.0)
        # samples[:fade_samples_in] *= np.linspace(0, 1, fade_samples_in)
        # samples[-fade_samples_out:] *= np.linspace(1, 0, fade_samples_out)
        #
        # # Play async
        # sd.play(samples, 44100, blocking=False)

        # For now, just log
        logger.debug(
            f"[AUDIO BACKEND PLACEHOLDER] Would play {cue.value} at {intensity:.2f} volume"
        )

    async def _stop_audio(self):
        """Stop any currently playing audio."""
        # PLACEHOLDER: Stop audio backend
        # Example: sd.stop()
        pass

    # Configuration API

    def enable(self):
        """Enable audio cues."""
        self.config.enabled = True
        logger.info("🔊 Voice Responder enabled")

    def disable(self):
        """Disable audio cues."""
        self.config.enabled = False
        logger.info("🔇 Voice Responder disabled")

    def set_volume(self, volume: float):
        """Set playback volume (0.0-1.0)."""
        self.config.volume = max(0.0, min(1.0, volume))
        logger.debug(f"🔊 Volume set to {self.config.volume:.2f}")

    def set_rate_limit(self, milliseconds: int):
        """Set minimum time between cues."""
        self.config.rate_limit_ms = max(0, milliseconds)
        logger.debug(f"⏱️ Rate limit set to {self.config.rate_limit_ms}ms")

    # Status API

    def get_status(self) -> Dict[str, Any]:
        """Get plugin status."""
        return {
            "running": self.running,
            "enabled": self.config.enabled,
            "volume": self.config.volume,
            "rate_limit_ms": self.config.rate_limit_ms,
            "current_cue": self.current_cue.value if self.current_cue else None,
            "stats": self.stats,
        }

    def get_stats(self) -> Dict[str, Any]:
        """Get playback statistics."""
        return self.stats.copy()


# Plugin metadata for Aetherra plugin system
PLUGIN_METADATA = {
    "name": "voice_responder",
    "version": "1.0.0",
    "description": "Non-verbal audio cues for Lyrixa expressions",
    "author": "Aetherra Labs",
    "requires": ["lyrixa.expression"],
    "optional_dependencies": ["sounddevice", "numpy"],
    "config_schema": {
        "enabled": {"type": "boolean", "default": False},
        "volume": {"type": "number", "default": 0.5, "min": 0.0, "max": 1.0},
        "rate_limit_ms": {"type": "integer", "default": 1000, "min": 0},
    },
}


# Plugin factory function
async def create_plugin(event_bus, config: Optional[Dict[str, Any]] = None):
    """Factory function for plugin instantiation."""
    audio_config = AudioConfig(
        enabled=config.get("enabled", False) if config else False,
        volume=config.get("volume", 0.5) if config else 0.5,
        rate_limit_ms=config.get("rate_limit_ms", 1000) if config else 1000,
    )

    plugin = VoiceResponderPlugin(event_bus=event_bus, config=audio_config)
    await plugin.start()

    return plugin
