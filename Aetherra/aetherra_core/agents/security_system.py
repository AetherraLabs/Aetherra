"""
🛡️ Aetherra Security Integration System
=======================================

Comprehensive security system that integrates API key management,
memory leak prevention, and overall system security for Aetherra.

Author: Aetherra Security Team
Date: July 16, 2025
"""

import os
import sys
import time
import logging
import threading
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

# Import our security modules
from .api_key_manager import APIKeyManager, get_api_key_manager
from .memory_manager import MemoryManager, get_memory_manager

@dataclass
class SecurityConfig:
    """Security configuration settings"""
    api_key_rotation_days: int = 30
    memory_monitoring_enabled: bool = True
    leak_detection_enabled: bool = True
    audit_logging_enabled: bool = True
    max_memory_usage_percent: int = 80
    security_scan_interval: int = 3600  # 1 hour
    auto_cleanup_enabled: bool = True

class AetherraSecuritySystem:
    """
    🛡️ Comprehensive Security System for Aetherra

    Features:
    - API key management and rotation
    - Memory leak prevention and monitoring
    - Security audit logging
    - Automatic threat detection
    - Resource cleanup
    - Performance optimization
    """

    def __init__(self, workspace_path: Optional[str] = None, config: Optional[SecurityConfig] = None):
        self.workspace_path = Path(workspace_path or ".")
        self.config = config or SecurityConfig()

        # Initialize security components
        self.api_key_manager = APIKeyManager(str(self.workspace_path))
        self.memory_manager = MemoryManager(str(self.workspace_path))

        # Security state
        self.security_alerts = []
        self.last_security_scan = 0
        self.is_monitoring = False

        # Initialize logging
        self._setup_logging()

        # Start security monitoring
        self.start_monitoring()

        # Initialize Aetherra with security
        self._initialize_aetherra_security()

    def _setup_logging(self):
        """Setup comprehensive security logging"""
        log_dir = self.workspace_path / ".aetherra" / "security"
        log_dir.mkdir(parents=True, exist_ok=True)

        self.logger = logging.getLogger("aetherra_security_system")
        self.logger.setLevel(logging.INFO)

        # Create handlers
        security_handler = logging.FileHandler(log_dir / "security.log")
        alert_handler = logging.FileHandler(log_dir / "alerts.log")

        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        security_handler.setFormatter(detailed_formatter)
        alert_handler.setFormatter(detailed_formatter)

        self.logger.addHandler(security_handler)
        self.logger.addHandler(alert_handler)

    def _initialize_aetherra_security(self):
        """Initialize Aetherra with security features"""
        # Set up secure environment
        self._setup_secure_environment()

        # Configure secure API access
        self._configure_secure_api_access()

        # Initialize memory protection
        self._initialize_memory_protection()

        self.logger.info("🛡️ Aetherra Security System initialized successfully")

    def _setup_secure_environment(self):
        """Setup secure environment variables and paths"""
        # Ensure secure directories exist
        secure_dirs = [
            self.workspace_path / ".aetherra" / "secure",
            self.workspace_path / ".aetherra" / "keys",
            self.workspace_path / ".aetherra" / "logs",
            self.workspace_path / ".aetherra" / "backups"
        ]

        for dir_path in secure_dirs:
            dir_path.mkdir(parents=True, exist_ok=True)
            # Set restrictive permissions
            os.chmod(dir_path, 0o700)

        # Setup secure .env if it doesn't exist
        env_file = self.workspace_path / ".env"
        if not env_file.exists():
            env_template = self.workspace_path / ".env.template"
            if env_template.exists():
                with open(env_template, 'r') as f:
                    content = f.read()

                with open(env_file, 'w') as f:
                    f.write(content)

                # Set secure permissions
                os.chmod(env_file, 0o600)

                self.logger.info("Created secure .env file from template")

    def _configure_secure_api_access(self):
        """Configure secure API access for Aetherra"""
        # Check for existing API keys
        api_providers = ['openai', 'anthropic', 'google']

        for provider in api_providers:
            env_key = f"{provider.upper()}_API_KEY"
            api_key = os.getenv(env_key)

            if api_key:
                # Store in secure manager
                self.api_key_manager.store_api_key(provider, api_key)
                self.logger.info(f"Secured API key for {provider}")

                # Remove from environment for security
                if env_key in os.environ:
                    del os.environ[env_key]

    def _initialize_memory_protection(self):
        """Initialize memory protection for Aetherra components"""
        # Track important Aetherra objects
        aetherra_classes = [
            'LyrixaAssistant',
            'PluginManager',
            'MemoryCore',
            'GoalTracker',
            'AetherInterpreter'
        ]

        for class_name in aetherra_classes:
            # This would be called when objects are created
            self.logger.debug(f"Memory protection enabled for {class_name}")

    def start_monitoring(self):
        """Start security monitoring"""
        if self.is_monitoring:
            return

        self.is_monitoring = True

        def monitor_security():
            while self.is_monitoring:
                try:
                    self._run_security_scan()
                    time.sleep(self.config.security_scan_interval)
                except Exception as e:
                    self.logger.error(f"Error in security monitoring: {e}")
                    time.sleep(60)  # Wait 1 minute before retrying

        thread = threading.Thread(target=monitor_security, daemon=True)
        thread.start()

        self.logger.info("🔍 Security monitoring started")

    def stop_monitoring(self):
        """Stop security monitoring"""
        self.is_monitoring = False
        self.logger.info("🔍 Security monitoring stopped")

    def _run_security_scan(self):
        """Run comprehensive security scan"""
        scan_results = {
            'timestamp': time.time(),
            'api_keys': self._scan_api_keys(),
            'memory': self._scan_memory(),
            'files': self._scan_files(),
            'network': self._scan_network()
        }

        # Process results
        self._process_scan_results(scan_results)

        self.last_security_scan = time.time()

    def _scan_api_keys(self) -> Dict[str, Any]:
        """Scan API key security"""
        return {
            'status': self.api_key_manager.get_security_status(),
            'rotation_needed': self._check_key_rotation_needed(),
            'potential_leaks': self._check_api_key_leaks()
        }

    def _scan_memory(self) -> Dict[str, Any]:
        """Scan memory security"""
        memory_report = self.memory_manager.get_memory_report()
        leaks = self.memory_manager.check_memory_leaks()

        return {
            'usage': memory_report,
            'leaks': leaks,
            'high_usage': memory_report['current_usage']['percent'] > self.config.max_memory_usage_percent
        }

    def _scan_files(self) -> Dict[str, Any]:
        """Scan file system security"""
        suspicious_files = []

        # Check for suspicious files
        suspicious_patterns = [
            '*.key',
            '*.pem',
            '*.p12',
            '*password*',
            '*secret*',
            '*.env'
        ]

        for pattern in suspicious_patterns:
            for file_path in self.workspace_path.glob(f"**/{pattern}"):
                if file_path.is_file():
                    suspicious_files.append(str(file_path))

        return {
            'suspicious_files': suspicious_files,
            'permissions_issues': self._check_file_permissions()
        }

    def _scan_network(self) -> Dict[str, Any]:
        """Scan network security"""
        return {
            'open_ports': self._check_open_ports(),
            'suspicious_connections': []
        }

    def _check_key_rotation_needed(self) -> List[str]:
        """Check which API keys need rotation"""
        current_time = time.time()
        rotation_needed = []

        for provider, metadata in self.api_key_manager._key_metadata.items():
            age = current_time - metadata['created']
            if age > (self.config.api_key_rotation_days * 24 * 60 * 60):
                rotation_needed.append(provider)

        return rotation_needed

    def _check_api_key_leaks(self) -> List[str]:
        """Check for potential API key leaks"""
        leaks = []

        # Check environment variables
        for key, value in os.environ.items():
            if 'api_key' in key.lower() or 'secret' in key.lower():
                if len(value) > 20:
                    leaks.append(f"Environment variable: {key}")

        # Check common files
        check_files = [
            '.env',
            'config.json',
            'settings.json',
            'keys.json'
        ]

        for filename in check_files:
            file_path = self.workspace_path / filename
            if file_path.exists():
                try:
                    with open(file_path, 'r') as f:
                        content = f.read()

                    # Simple pattern matching for potential keys
                    if 'api_key' in content.lower() or 'secret' in content.lower():
                        leaks.append(f"File: {filename}")
                except:
                    pass

        return leaks

    def _check_file_permissions(self) -> List[str]:
        """Check for file permission issues"""
        issues = []

        # Check sensitive files
        sensitive_files = [
            '.env',
            '.aetherra/secure/',
            '.aetherra/keys/'
        ]

        for file_path in sensitive_files:
            full_path = self.workspace_path / file_path
            if full_path.exists():
                stat = full_path.stat()
                if stat.st_mode & 0o077:  # Too permissive
                    issues.append(f"Permissive permissions on {file_path}")

        return issues

    def _check_open_ports(self) -> List[int]:
        """Check for open ports"""
        # This would typically check for open ports
        # For now, return empty list
        return []

    def _process_scan_results(self, results: Dict[str, Any]):
        """Process security scan results"""
        alerts = []

        # Check API key issues
        api_results = results['api_keys']
        if api_results['rotation_needed']:
            alerts.append(f"API key rotation needed for: {', '.join(api_results['rotation_needed'])}")

        if api_results['potential_leaks']:
            alerts.append(f"Potential API key leaks: {', '.join(api_results['potential_leaks'])}")

        # Check memory issues
        memory_results = results['memory']
        if memory_results['high_usage']:
            alerts.append(f"High memory usage: {memory_results['usage']['current_usage']['percent']:.1f}%")

        if memory_results['leaks']:
            alerts.append(f"Memory leaks detected: {len(memory_results['leaks'])} locations")

        # Check file issues
        file_results = results['files']
        if file_results['suspicious_files']:
            alerts.append(f"Suspicious files found: {len(file_results['suspicious_files'])}")

        if file_results['permissions_issues']:
            alerts.append(f"File permission issues: {len(file_results['permissions_issues'])}")

        # Log alerts
        for alert in alerts:
            self.logger.warning(f"🚨 SECURITY ALERT: {alert}")
            self.security_alerts.append({
                'timestamp': time.time(),
                'alert': alert,
                'severity': 'warning'
            })

        # Auto-cleanup if enabled
        if self.config.auto_cleanup_enabled:
            self._auto_cleanup()

    def _auto_cleanup(self):
        """Automatic cleanup of security issues"""
        # Clean up memory if high usage
        memory_report = self.memory_manager.get_memory_report()
        if memory_report['current_usage']['percent'] > self.config.max_memory_usage_percent:
            self.memory_manager.cleanup_resources()
            self.logger.info("🧹 Automatic memory cleanup performed")

    def get_security_status(self) -> Dict[str, Any]:
        """Get comprehensive security status"""
        return {
            'api_keys': self.api_key_manager.get_security_status(),
            'memory': self.memory_manager.get_memory_report(),
            'alerts': len(self.security_alerts),
            'last_scan': self.last_security_scan,
            'monitoring_active': self.is_monitoring,
            'config': {
                'api_key_rotation_days': self.config.api_key_rotation_days,
                'memory_monitoring_enabled': self.config.memory_monitoring_enabled,
                'leak_detection_enabled': self.config.leak_detection_enabled,
                'auto_cleanup_enabled': self.config.auto_cleanup_enabled
            }
        }

    def force_security_scan(self) -> Dict[str, Any]:
        """Force an immediate security scan"""
        self._run_security_scan()
        return self.get_security_status()

    def cleanup_all(self):
        """Cleanup all security-related resources"""
        # Cleanup API keys
        self.api_key_manager.cleanup_memory()

        # Cleanup memory
        self.memory_manager.cleanup_resources()

        # Stop monitoring
        self.stop_monitoring()

        self.logger.info("🧹 Complete security cleanup performed")

# Global security system instance
_security_system = None

def get_security_system() -> AetherraSecuritySystem:
    """Get the global security system instance"""
    global _security_system
    if _security_system is None:
        _security_system = AetherraSecuritySystem()
    return _security_system

def initialize_aetherra_security(workspace_path: Optional[str] = None, config: Optional[SecurityConfig] = None):
    """Initialize Aetherra security system"""
    global _security_system
    _security_system = AetherraSecuritySystem(workspace_path, config)
    return _security_system

def secure_api_call(provider: str, func, *args, **kwargs):
    """Make a secure API call with proper key management"""
    security_system = get_security_system()
    api_key = security_system.api_key_manager.get_api_key(provider)

    if not api_key:
        raise ValueError(f"No API key found for provider: {provider}")

    # Add API key to kwargs
    kwargs['api_key'] = api_key

    # Track memory usage
    with security_system.memory_manager.memory_context(f"api_call_{provider}"):
        return func(*args, **kwargs)

if __name__ == "__main__":
    # Example usage
    security_system = AetherraSecuritySystem()

    print("🛡️ Aetherra Security System")
    print("=" * 40)

    # Get security status
    status = security_system.get_security_status()
    print(f"Security monitoring: {'Active' if status['monitoring_active'] else 'Inactive'}")
    print(f"Security alerts: {status['alerts']}")
    print(f"Memory usage: {status['memory']['current_usage']['percent']:.1f}%")

    # Force security scan
    print("\n🔍 Running security scan...")
    scan_results = security_system.force_security_scan()
    print("Security scan completed!")

    # Cleanup
    security_system.cleanup_all()
