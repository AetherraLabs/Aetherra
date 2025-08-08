#!/usr/bin/env python3
"""
Aetherra Hub Connector for Lyrixa
Connects Lyrixa to the existing Aetherra Hub infrastructure
"""

import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import Any, Callable, Dict, Optional

import aiohttp
import websockets

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

logger = logging.getLogger(__name__)


class AetherraHubConnector:
    """
    Connects Lyrixa to the Aetherra Hub for centralized coordination
    """

    def __init__(self):
        self.hub_host = "localhost"
        self.hub_port = 3001  # Aetherra Hub port - updated to match main OS
        self.hub_ws_port = 3002  # WebSocket port
        self.connected = False
        self.session = None
        self.websocket = None
        self.message_handlers = {}
        self.status_callbacks = []

    async def connect(self) -> bool:
        """Connect to Aetherra Hub"""
        try:
            # Test HTTP connection first
            self.session = aiohttp.ClientSession()
            async with self.session.get(
                f"http://{self.hub_host}:{self.hub_port}/status"
            ) as response:
                if response.status == 200:
                    hub_status = await response.json()
                    logger.info(f"[HUB] Connected to Aetherra Hub: {hub_status}")

                    # Establish WebSocket connection
                    try:
                        self.websocket = await websockets.connect(
                            f"ws://{self.hub_host}:{self.hub_ws_port}/lyrixa"
                        )

                        # Register Lyrixa with the Hub
                        await self._register_with_hub()

                        # Start message handler
                        asyncio.create_task(self._handle_messages())

                        self.connected = True
                        logger.info(
                            "[HUB] Lyrixa successfully connected to Aetherra Hub"
                        )
                        await self._notify_status_change("connected")
                        return True

                    except Exception as ws_error:
                        logger.warning(f"[HUB] WebSocket connection failed: {ws_error}")
                        # HTTP-only mode
                        self.connected = True
                        await self._notify_status_change("http_only")
                        return True

        except Exception as e:
            logger.warning(f"[HUB] Failed to connect to Aetherra Hub: {e}")
            await self._notify_status_change("disconnected")
            return False

    async def _register_with_hub(self):
        """Register Lyrixa with the Aetherra Hub"""
        registration_data = {
            "type": "registration",
            "service": "lyrixa",
            "capabilities": [
                "ai_assistance",
                "consciousness_orchestration",
                "gui_interface",
                "agent_management",
                "personality_system",
            ],
            "status": "active",
            "version": "2.0",
            "interfaces": {"gui": True, "api": True, "consciousness": True},
        }

        if self.websocket:
            await self.websocket.send(json.dumps(registration_data))
            logger.info("[HUB] Registered Lyrixa with Aetherra Hub")

    async def _handle_messages(self):
        """Handle incoming messages from the Hub"""
        try:
            async for message in self.websocket:
                try:
                    data = json.loads(message)
                    message_type = data.get("type", "unknown")

                    if message_type in self.message_handlers:
                        await self.message_handlers[message_type](data)
                    else:
                        logger.debug(f"[HUB] Unhandled message type: {message_type}")

                except json.JSONDecodeError:
                    logger.warning(f"[HUB] Invalid JSON message: {message}")

        except websockets.exceptions.ConnectionClosed:
            logger.info("[HUB] WebSocket connection closed")
            self.connected = False
            await self._notify_status_change("disconnected")
        except Exception as e:
            logger.error(f"[HUB] Message handling error: {e}")

    def register_message_handler(self, message_type: str, handler: Callable):
        """Register a handler for specific message types"""
        self.message_handlers[message_type] = handler
        logger.debug(f"[HUB] Registered handler for {message_type}")

    def register_status_callback(self, callback: Callable):
        """Register callback for status changes"""
        self.status_callbacks.append(callback)

    async def _notify_status_change(self, status: str):
        """Notify all callbacks of status change"""
        for callback in self.status_callbacks:
            try:
                await callback(status)
            except Exception as e:
                logger.error(f"[HUB] Status callback error: {e}")

    async def send_message(self, message_type: str, data: Dict[str, Any]) -> bool:
        """Send a message to the Hub"""
        if not self.connected:
            return False

        message = {
            "type": message_type,
            "source": "lyrixa",
            "timestamp": asyncio.get_event_loop().time(),
            **data,
        }

        try:
            if self.websocket:
                await self.websocket.send(json.dumps(message))
                return True
            elif self.session:
                async with self.session.post(
                    f"http://{self.hub_host}:{self.hub_port}/message", json=message
                ) as response:
                    return response.status == 200
        except Exception as e:
            logger.error(f"[HUB] Failed to send message: {e}")
            return False

    async def request_aetherra_os_status(self) -> Optional[Dict[str, Any]]:
        """Request status information from Aetherra OS"""
        if not self.connected:
            return None

        try:
            if self.session:
                async with self.session.get(
                    f"http://{self.hub_host}:{self.hub_port}/services/aetherra_os/status"
                ) as response:
                    if response.status == 200:
                        return await response.json()
        except Exception as e:
            logger.error(f"[HUB] Failed to get Aetherra OS status: {e}")

        return None

    async def request_service_list(self) -> Optional[Dict[str, Any]]:
        """Get list of all services connected to the Hub"""
        if not self.connected:
            return None

        try:
            if self.session:
                async with self.session.get(
                    f"http://{self.hub_host}:{self.hub_port}/services"
                ) as response:
                    if response.status == 200:
                        return await response.json()
        except Exception as e:
            logger.error(f"[HUB] Failed to get service list: {e}")

        return None

    async def coordinate_with_aetherra_os(
        self, action: str, params: Dict[str, Any] = None
    ) -> Optional[Dict[str, Any]]:
        """Coordinate an action with Aetherra OS through the Hub"""
        if not self.connected:
            return None

        coordination_message = {
            "action": action,
            "target": "aetherra_os",
            "params": params or {},
        }

        success = await self.send_message("coordination_request", coordination_message)
        if success:
            logger.info(f"[HUB] Coordination request sent to Aetherra OS: {action}")
            return {"status": "sent", "action": action}

        return None

    async def disconnect(self):
        """Disconnect from the Hub"""
        self.connected = False

        if self.websocket:
            await self.websocket.close()

        if self.session:
            await self.session.close()

        logger.info("[HUB] Disconnected from Aetherra Hub")
        await self._notify_status_change("disconnected")


class AetherraOSDetector:
    """
    Detects if Aetherra OS is running and provides status information
    """

    @staticmethod
    async def detect_aetherra_os() -> Dict[str, Any]:
        """Detect if Aetherra OS is running and get its status"""
        detection_result = {
            "running": False,
            "services": [],
            "hub_connected": False,
            "backend_port": None,
            "capabilities": [],
        }

        # Check for Aetherra Hub
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("http://localhost:8888/status") as response:
                    if response.status == 200:
                        hub_status = await response.json()
                        detection_result["hub_connected"] = True
                        logger.info(f"[DETECT] Aetherra Hub detected: {hub_status}")

                        # Get service list from Hub
                        async with session.get(
                            "http://localhost:8888/services"
                        ) as services_response:
                            if services_response.status == 200:
                                services = await services_response.json()
                                detection_result["services"] = services.get(
                                    "services", []
                                )

                                # Check if Aetherra OS backend is in the service list
                                for service in detection_result["services"]:
                                    if service.get("name") == "aetherra_os":
                                        detection_result["running"] = True
                                        detection_result["capabilities"] = service.get(
                                            "capabilities", []
                                        )
                                        break

        except Exception as e:
            logger.debug(f"[DETECT] Hub detection failed: {e}")

        # Direct port detection for Aetherra OS backend
        for port in [5000, 5001, 8000, 8080, 9000]:
            try:
                reader, writer = await asyncio.wait_for(
                    asyncio.open_connection("localhost", port), timeout=1.0
                )
                writer.close()
                await writer.wait_closed()
                detection_result["backend_port"] = port
                if not detection_result["running"]:
                    detection_result["running"] = True
                logger.info(f"[DETECT] Aetherra OS backend detected on port {port}")
                break
            except Exception:
                continue

        return detection_result


# Global instance
hub_connector = AetherraHubConnector()
os_detector = AetherraOSDetector()


async def initialize_hub_connection():
    """Initialize the hub connection and OS detection"""
    logger.info("[HUB] Initializing Aetherra Hub connection...")

    # Detect Aetherra OS first
    os_status = await os_detector.detect_aetherra_os()
    logger.info(f"[DETECT] Aetherra OS Status: {os_status}")

    # Connect to Hub
    connected = await hub_connector.connect()

    if connected and os_status["running"]:
        logger.info("[HUB] Successfully connected to Aetherra ecosystem")

        # Request coordination with Aetherra OS
        await hub_connector.coordinate_with_aetherra_os(
            "lyrixa_integration",
            {"component": "consciousness_orchestrator", "status": "online"},
        )

    return {"hub_connected": connected, "aetherra_os": os_status}


if __name__ == "__main__":

    async def main():
        result = await initialize_hub_connection()
        print(f"Connection result: {result}")

        if hub_connector.connected:
            # Keep connection alive for testing
            await asyncio.sleep(10)
            await hub_connector.disconnect()

    asyncio.run(main())
