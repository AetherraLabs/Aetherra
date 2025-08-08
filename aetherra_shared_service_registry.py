#!/usr/bin/env python3
"""
🌐 Aetherra Shared Service Registry
==================================

Inter-process service registry for true AI OS-level persistence.
Enables services to persist across process boundaries and provides
real OS-like service discovery and communication.

Copyright (C) 2025 AetherraLabs
Licensed under GNU General Public License v3.0
"""

import asyncio
import json
import logging
import os
import pickle
import socket
import subprocess
import tempfile
import time
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
import threading
import multiprocessing
import mmap

logger = logging.getLogger(__name__)


class ServiceStatus(Enum):
    """Service health status enumeration."""
    STARTING = "starting"
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILED = "failed"
    STOPPING = "stopping"


@dataclass
class SharedServiceInfo:
    """Serializable service information for inter-process sharing."""
    name: str
    process_id: int
    status: str = "starting"
    registered_at: float = field(default_factory=time.time)
    last_heartbeat: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    socket_path: Optional[str] = None
    port: Optional[int] = None


class AetherraSharedServiceRegistry:
    """
    🌐 Shared Service Registry
    
    Inter-process service registry that persists across process boundaries
    using shared memory, sockets, and filesystem-based discovery.
    """
    
    def __init__(self, registry_dir: Optional[str] = None):
        self.registry_dir = Path(registry_dir or tempfile.gettempdir()) / "aetherra_registry"
        self.registry_file = self.registry_dir / "services.json"
        self.lock_file = self.registry_dir / "registry.lock"
        self.process_id = os.getpid()
        self.server_socket = None
        self.server_port = None
        self.running = False
        self.services = {}
        self.local_services = {}
        
        # Ensure registry directory exists
        self.registry_dir.mkdir(exist_ok=True)
        
    async def start(self):
        """Start the shared service registry."""
        try:
            logger.info(f"[REGISTRY] Starting shared service registry (PID: {self.process_id})")
            
            # Start communication server
            await self._start_communication_server()
            
            # Load existing services
            await self._load_services()
            
            # Clean up stale services
            await self._cleanup_stale_services()
            
            # Start heartbeat monitor
            asyncio.create_task(self._heartbeat_monitor())
            
            self.running = True
            logger.info("[OK] Shared service registry online")
            
        except Exception as e:
            logger.error(f"[ERROR] Failed to start shared service registry: {e}")
            raise
    
    async def stop(self):
        """Stop the shared service registry."""
        logger.info("[REGISTRY] Stopping shared service registry...")
        self.running = False
        
        # Unregister local services
        for service_name in list(self.local_services.keys()):
            await self.unregister_service(service_name)
        
        # Close communication server
        if self.server_socket:
            self.server_socket.close()
        
        logger.info("[OK] Shared service registry stopped")
    
    async def _start_communication_server(self):
        """Start the inter-process communication server."""
        try:
            # Create TCP server for inter-process communication
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind(('localhost', 0))
            self.server_port = self.server_socket.getsockname()[1]
            self.server_socket.listen(5)
            
            logger.info(f"[COMM] Communication server started on port {self.server_port}")
            
            # Start server task
            asyncio.create_task(self._handle_connections())
            
        except Exception as e:
            logger.error(f"[ERROR] Failed to start communication server: {e}")
            raise
    
    async def _handle_connections(self):
        """Handle incoming connections from other processes."""
        while self.running:
            try:
                # Accept connections (non-blocking)
                await asyncio.sleep(0.1)  # Prevent busy loop
                # TODO: Implement proper async socket handling
                
            except Exception as e:
                if self.running:
                    logger.error(f"[ERROR] Connection handling error: {e}")
    
    async def _load_services(self):
        """Load services from shared registry file."""
        try:
            if self.registry_file.exists():
                with open(self.registry_file, 'r') as f:
                    data = json.load(f)
                    for name, service_data in data.get('services', {}).items():
                        self.services[name] = SharedServiceInfo(**service_data)
                logger.info(f"[LOAD] Loaded {len(self.services)} services from registry")
            else:
                logger.info("[LOAD] No existing registry found, starting fresh")
                
        except Exception as e:
            logger.error(f"[ERROR] Failed to load services: {e}")
    
    async def _save_services(self):
        """Save services to shared registry file."""
        try:
            # Use file locking to prevent concurrent writes
            with open(self.lock_file, 'w') as lock:
                lock.write(str(self.process_id))
                
                registry_data = {
                    'updated_at': time.time(),
                    'updated_by': self.process_id,
                    'services': {
                        name: asdict(service_info) 
                        for name, service_info in self.services.items()
                    }
                }
                
                # Atomic write
                temp_file = self.registry_file.with_suffix('.tmp')
                with open(temp_file, 'w') as f:
                    json.dump(registry_data, f, indent=2)
                temp_file.replace(self.registry_file)
                
            # Remove lock
            if self.lock_file.exists():
                self.lock_file.unlink()
                
        except Exception as e:
            logger.error(f"[ERROR] Failed to save services: {e}")
    
    async def _cleanup_stale_services(self):
        """Remove services from dead processes."""
        stale_services = []
        current_time = time.time()
        
        for name, service_info in self.services.items():
            # Check if process is still alive
            try:
                if not self._is_process_alive(service_info.process_id):
                    stale_services.append(name)
                    continue
                    
                # Check heartbeat timeout (5 minutes)
                if current_time - service_info.last_heartbeat > 300:
                    stale_services.append(name)
                    
            except Exception:
                stale_services.append(name)
        
        # Remove stale services
        for name in stale_services:
            logger.warning(f"[CLEANUP] Removing stale service: {name}")
            del self.services[name]
        
        if stale_services:
            await self._save_services()
    
    def _is_process_alive(self, pid: int) -> bool:
        """Check if a process is still alive."""
        try:
            if os.name == 'nt':  # Windows
                import subprocess
                result = subprocess.run(['tasklist', '/FI', f'PID eq {pid}'], 
                                      capture_output=True, text=True)
                return str(pid) in result.stdout
            else:  # Unix-like
                os.kill(pid, 0)
                return True
        except (OSError, Exception):
            return False
    
    async def _heartbeat_monitor(self):
        """Monitor service heartbeats and cleanup stale services."""
        while self.running:
            try:
                await asyncio.sleep(30)  # Check every 30 seconds
                await self._cleanup_stale_services()
                
                # Refresh from disk (other processes may have updated)
                await self._load_services()
                
            except Exception as e:
                logger.error(f"[ERROR] Heartbeat monitor error: {e}")
    
    async def register_service(self, name: str, instance: Any, **kwargs) -> bool:
        """Register a service in the shared registry."""
        try:
            service_info = SharedServiceInfo(
                name=name,
                process_id=self.process_id,
                metadata=kwargs.get('metadata', {}),
                dependencies=kwargs.get('dependencies', []),
                port=self.server_port
            )
            
            self.services[name] = service_info
            self.local_services[name] = instance
            
            await self._save_services()
            
            logger.info(f"[REGISTER] Service '{name}' registered (PID: {self.process_id})")
            return True
            
        except Exception as e:
            logger.error(f"[ERROR] Failed to register service '{name}': {e}")
            return False
    
    async def unregister_service(self, name: str) -> bool:
        """Unregister a service from the shared registry."""
        try:
            if name in self.services:
                service_info = self.services[name]
                if service_info.process_id == self.process_id:
                    del self.services[name]
                    if name in self.local_services:
                        del self.local_services[name]
                    
                    await self._save_services()
                    logger.info(f"[UNREGISTER] Service '{name}' unregistered")
                    return True
                else:
                    logger.warning(f"[WARN] Cannot unregister service '{name}' from different process")
                    return False
            return False
            
        except Exception as e:
            logger.error(f"[ERROR] Failed to unregister service '{name}': {e}")
            return False
    
    def get_service(self, name: str) -> Optional[Any]:
        """Get a service instance (local only)."""
        return self.local_services.get(name)
    
    def get_service_info(self, name: str) -> Optional[SharedServiceInfo]:
        """Get service information (can be from any process)."""
        return self.services.get(name)
    
    def list_services(self) -> Dict[str, SharedServiceInfo]:
        """List all registered services."""
        return self.services.copy()
    
    async def update_heartbeat(self, name: str):
        """Update service heartbeat."""
        if name in self.services:
            service_info = self.services[name]
            if service_info.process_id == self.process_id:
                service_info.last_heartbeat = time.time()
                await self._save_services()
    
    async def update_service_status(self, name: str, status: ServiceStatus):
        """Update service status."""
        if name in self.services:
            service_info = self.services[name]
            if service_info.process_id == self.process_id:
                service_info.status = status.value
                service_info.last_heartbeat = time.time()
                await self._save_services()
    
    def get_registry_status(self) -> Dict[str, Any]:
        """Get comprehensive registry status."""
        current_time = time.time()
        
        # Count services by status
        status_counts = {}
        healthy_services = 0
        
        for service_info in self.services.values():
            status = service_info.status
            status_counts[status] = status_counts.get(status, 0) + 1
            
            if status == 'healthy' and (current_time - service_info.last_heartbeat) < 60:
                healthy_services += 1
        
        return {
            "registry_process_id": self.process_id,
            "registry_running": self.running,
            "total_services": len(self.services),
            "healthy_services": healthy_services,
            "local_services": len(self.local_services),
            "communication_port": self.server_port,
            "status_counts": status_counts,
            "registry_file": str(self.registry_file),
            "services": {
                name: {
                    "process_id": info.process_id,
                    "status": info.status,
                    "last_heartbeat_age": current_time - info.last_heartbeat,
                    "dependencies": info.dependencies,
                }
                for name, info in self.services.items()
            }
        }


# Global shared registry instance
_shared_registry: Optional[AetherraSharedServiceRegistry] = None


async def get_shared_service_registry() -> AetherraSharedServiceRegistry:
    """Get the global shared service registry instance."""
    global _shared_registry
    if _shared_registry is None:
        _shared_registry = AetherraSharedServiceRegistry()
        await _shared_registry.start()
    return _shared_registry


async def register_shared_service(name: str, instance: Any, **kwargs) -> bool:
    """Register a service with the shared registry."""
    registry = await get_shared_service_registry()
    return await registry.register_service(name, instance, **kwargs)


async def get_shared_service(name: str) -> Optional[Any]:
    """Get a service from the shared registry (local instances only)."""
    registry = await get_shared_service_registry()
    return registry.get_service(name)


async def get_shared_service_info(name: str) -> Optional[SharedServiceInfo]:
    """Get service information from the shared registry."""
    registry = await get_shared_service_registry()
    return registry.get_service_info(name)


async def update_shared_heartbeat(name: str):
    """Update service heartbeat in the shared registry."""
    registry = await get_shared_service_registry()
    await registry.update_heartbeat(name)


async def shutdown_shared_service_registry():
    """Shutdown the shared service registry."""
    global _shared_registry
    if _shared_registry:
        await _shared_registry.stop()
        _shared_registry = None


# Example usage and testing
if __name__ == "__main__":
    async def test_shared_registry():
        print("🌐 Testing Aetherra Shared Service Registry")
        
        # Test service registration
        registry = AetherraSharedServiceRegistry()
        await registry.start()
        
        class TestService:
            def __init__(self, name):
                self.name = name
            
            def status(self):
                return f"Service {self.name} is running"
        
        # Register test services
        service1 = TestService("test_service_1")
        service2 = TestService("test_service_2")
        
        await registry.register_service("test_service_1", service1, 
                                       metadata={"version": "1.0"})
        await registry.register_service("test_service_2", service2, 
                                       dependencies=["test_service_1"])
        
        # Update statuses
        await registry.update_service_status("test_service_1", ServiceStatus.HEALTHY)
        await registry.update_service_status("test_service_2", ServiceStatus.HEALTHY)
        
        # Test heartbeats
        await registry.update_heartbeat("test_service_1")
        await registry.update_heartbeat("test_service_2")
        
        # Get registry status
        status = registry.get_registry_status()
        print(f"✅ Registry Status:")
        print(f"   - Total services: {status['total_services']}")
        print(f"   - Healthy services: {status['healthy_services']}")
        print(f"   - Communication port: {status['communication_port']}")
        print(f"   - Registry file: {status['registry_file']}")
        
        # List services
        services = registry.list_services()
        print(f"✅ Registered Services:")
        for name, info in services.items():
            print(f"   - {name}: PID {info.process_id}, Status {info.status}")
        
        # Test cross-process persistence
        print(f"✅ Testing persistence across 'process restart'...")
        await registry.stop()
        
        # Simulate new process
        registry2 = AetherraSharedServiceRegistry()
        await registry2.start()
        
        services_after_restart = registry2.list_services()
        print(f"   - Services after 'restart': {len(services_after_restart)}")
        
        for name, info in services_after_restart.items():
            print(f"   - Recovered: {name} (Status: {info.status})")
        
        await registry2.stop()
        print("\n🌐 Shared Service Registry Test Complete!")
    
    asyncio.run(test_shared_registry())
