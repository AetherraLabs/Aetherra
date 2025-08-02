"""
Web Interface Integration Adapter
Connects your existing web interface to the clean architecture.
"""

import logging
import sys
from pathlib import Path

# Add clean architecture paths
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from Aetherra.integration.bridges.aetherra_lyrixa_bridge import bridge
from Aetherra.integration.bridges.memory_adapter import memory_adapter

logger = logging.getLogger(__name__)


class WebInterfaceAdapter:
    """Adapter for integrating web interface with clean architecture"""

    def __init__(self):
        self.bridge = bridge
        self.memory_adapter = memory_adapter
        logger.info("🌐 Web Interface Adapter initialized")

    async def initialize_web_systems(self):
        """Initialize web interface systems with clean architecture"""
        logger.info("🚀 Initializing web systems...")

        # Connect to integration bridge
        await self.bridge.start()

        # Register web interface handlers
        self.bridge.register_aetherra_handler("web_request", self.handle_web_request)
        self.bridge.register_lyrixa_handler("web_response", self.handle_web_response)

        logger.info("✅ Web systems initialized")

    async def handle_web_request(self, request_data):
        """Handle requests from web interface"""
        logger.info(f"📨 Web request: {request_data.get('type', 'unknown')}")
        # Process web requests through clean architecture
        return {"status": "processed", "data": request_data}

    async def handle_web_response(self, response_data):
        """Handle responses to web interface"""
        logger.info(f"📤 Web response: {response_data.get('type', 'unknown')}")
        # Send responses back to web interface
        return response_data

    def get_memory_context(self, context_id):
        """Get memory context for web interface"""
        return self.memory_adapter.get_shared_context(context_id)

    def store_memory_context(self, context_id, data):
        """Store memory context from web interface"""
        self.memory_adapter.store_shared_context(context_id, data)


# Global web adapter instance
web_adapter = WebInterfaceAdapter()
