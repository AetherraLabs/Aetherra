#!/usr/bin/env python3
"""
Aetherra v2 Enhanced Launcher with Web Interface
Launches the integrated system with your working web interface.
"""

import asyncio
import logging
import sys
import subprocess
from pathlib import Path

# Add clean architecture to path
sys.path.insert(0, str(Path(__file__).parent))

from Aetherra.integration.bridges.aetherra_lyrixa_bridge import bridge
from Aetherra.web.server.web_adapter import web_adapter

async def main():
    """Enhanced launcher with web interface integration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger = logging.getLogger(__name__)
    logger.info("🚀 Starting Aetherra v2 with Web Interface")
    
    try:
        # Initialize integration systems
        await bridge.start()
        await web_adapter.initialize_web_systems()
        
        # Start your web interface server
        logger.info("🌐 Starting web interface server...")
        web_server_path = Path(__file__).parent / "web" / "server" / "web_interface_server.py"
        
        if web_server_path.exists():
            # Start web interface in background
            web_process = subprocess.Popen([
                sys.executable, str(web_server_path), "--no-browser"
            ], cwd=str(Path(__file__).parent.parent))
            
            logger.info("✅ Web interface started on port 8686")
            logger.info("🌟 Aetherra v2 system fully operational!")
            logger.info("🌐 Access your web interface at: http://localhost:8686")
            
            # Keep running
            while True:
                await asyncio.sleep(1)
        else:
            logger.error("❌ Web interface server not found")
            
    except KeyboardInterrupt:
        logger.info("🛑 Shutting down...")
        await bridge.stop()
        if 'web_process' in locals():
            web_process.terminate()
    except Exception as e:
        logger.error(f"❌ System error: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
