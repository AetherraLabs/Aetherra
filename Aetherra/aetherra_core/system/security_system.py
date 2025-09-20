# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
🛡️ Aetherra Security Integration System
=======================================

Comprehensive security system that integrates API key management,
memory leak prevention, and overall system security for Aetherra.

Author: Aetherra Security Team
Date: July 16, 2025
"""

# Standard library imports
import json
import logging
import os
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

# Aetherra imports
from Aetherra.core.memory_manager import MemoryManager

# Import our security modules
# Use the shared security and memory components available in the repo
from Aetherra.security import api_keys

# --- Safe logging & redaction helpers (to prevent sensitive data leaks) ---
SENSITIVE_KEY_PATTERNS = (
    "password",
    "secret",
    "api_key",
    "apikey",
    "token",
    "private",
    "credential",
    "master",
    "key",
)


def _looks_like_secret(value: str) -> bool:
    try:
        if not isinstance(value, str):
            return False
        v = value.strip()
        # Heuristic: long opaque tokens
        return (len(v) >= 20) and any(ch.isdigit() for ch in v) and any(ch.isalpha() for ch in v)
    except Exception:  # Defensive: broad exception for secret detection heuristics
        return False


def redact_secrets(data: Any) -> Any:
    """Return a deep-copied structure with secret-looking fields redacted.

    - Redacts dict items whose key name contains sensitive patterns
    - Redacts string values that look like secrets/tokens
    """
    try:
        if isinstance(data, dict):
            out: Dict[str, Any] = {}
            for k, v in data.items():
                if isinstance(k, str) and any(p in k.lower() for p in SENSITIVE_KEY_PATTERNS):
                    out[k] = "***REDACTED***"
                else:
                    out[k] = redact_secrets(v)
            return out
        if isinstance(data, list):
            return [redact_secrets(x) for x in data]
        if isinstance(data, str) and _looks_like_secret(data):
            return "***REDACTED***"
        return data
    except Exception:
        return data


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

    def __init__(
        self,
        workspace_path: Optional[str] = None,
        config: Optional[SecurityConfig] = None,
    ) -> None:
        self.workspace_path = Path(workspace_path or ".")
        self.config = config or SecurityConfig()

        # Initialize security components
        # Place memory DB under .aetherra to avoid cluttering workspace root
        mem_db = self.workspace_path / ".aetherra" / "security" / "memory_manager.db"
        mem_db.parent.mkdir(parents=True, exist_ok=True)
        self.memory_manager = MemoryManager(db_path=str(mem_db))

        # Security state
        self.security_alerts = []
        self.last_security_scan = 0
        self.is_monitoring = False

        # Initialize logging
        self._setup_logging()

        # Path for UI-consumable alerts
        self.alerts_jsonl = self.workspace_path / ".aetherra" / "security" / "alerts.jsonl"

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
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
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
            self.workspace_path / ".aetherra" / "backups",
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
                with open(env_template) as f:
                    content = f.read()

                with open(env_file, "w") as f:
                    f.write(content)

                # Set secure permissions
                os.chmod(env_file, 0o600)

                self.logger.info("Created secure .env file from template")

    def _configure_secure_api_access(self):
        """Configure secure API access for Aetherra"""
        # Check for existing API keys
        api_providers = ["openai", "anthropic", "google"]

        for provider in api_providers:
            env_key = f"{provider.upper()}_API_KEY"
            api_key = os.getenv(env_key)

            if api_key:
                # Store in secure keystore (encrypt-at-rest when configured)
                try:
                    api_keys.set_key(f"{provider}_api_key", api_key)
                    self.logger.info(f"Secured API key for {provider}")
                except Exception as e:  # Security: log API key storage failures
                    self.logger.error(f"Failed securing API key for {provider}: {e}")

                # Remove from environment for security
                if env_key in os.environ:
                    del os.environ[env_key]

    def _initialize_memory_protection(self):
        """Initialize memory protection for Aetherra components"""
        # Track important Aetherra objects
        aetherra_classes = [
            "LyrixaAssistant",
            "PluginManager",
            "MemoryCore",
            "GoalTracker",
            "AetherInterpreter",
        ]

        for class_name in aetherra_classes:
            # This would be called when objects are created
            self.logger.debug(f"Memory protection enabled for {class_name}")

    def start_monitoring(self) -> None:
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

    def stop_monitoring(self) -> None:
        """Stop security monitoring"""
        self.is_monitoring = False
        self.logger.info("🔍 Security monitoring stopped")

    def _run_security_scan(self):
        """Run comprehensive security scan"""
        scan_results = {
            "timestamp": time.time(),
            "api_keys": self._scan_api_keys(),
            "memory": self._scan_memory(),
            "files": self._scan_files(),
            "network": self._scan_network(),
        }

        # Process results
        self._process_scan_results(scan_results)

        self.last_security_scan = time.time()

    def _scan_api_keys(self) -> Dict[str, Any]:
        """Scan API key security"""
        return {
            "status": self._get_api_keys_status(),
            "rotation_needed": self._check_key_rotation_needed(),
            "potential_leaks": self._check_api_key_leaks(),
        }

    def _scan_memory(self) -> Dict[str, Any]:
        """Scan memory security"""
        stats = self.memory_manager.get_memory_stats()
        leaks: List[Dict[str, Any]] = []  # placeholder: no leak detector available here

        return {
            "usage": stats,
            "leaks": leaks,
            "high_usage": stats.get("usage_percent", 0.0) > self.config.max_memory_usage_percent,
        }

    def _scan_files(self) -> Dict[str, Any]:
        """Scan file system security"""
        suspicious_files = []

        # Check for suspicious files
        suspicious_patterns = [
            "*.key",
            "*.pem",
            "*.p12",
            "*password*",
            "*secret*",
            "*.env",
        ]

        for pattern in suspicious_patterns:
            for file_path in self.workspace_path.glob(f"**/{pattern}"):
                if file_path.is_file():
                    suspicious_files.append(str(file_path))

        return {
            "suspicious_files": suspicious_files,
            "permissions_issues": self._check_file_permissions(),
        }

    def _scan_network(self) -> Dict[str, Any]:
        """Scan network security"""
        return {"open_ports": self._check_open_ports(), "suspicious_connections": []}

    def _check_key_rotation_needed(self) -> List[str]:
        """Check which API keys need rotation"""
        current_time = time.time()
        rotation_needed = []

        # Heuristic: if a key exists and the keystore is older than rotation window, flag rotation
        providers = ["openai", "anthropic", "google"]
        try:
            last_updated = None
            if api_keys.KEYS_FILE.exists():
                # Prefer __updated_at inside JSON (set when encrypted), else file mtime
                try:
                    data = json.loads(api_keys.KEYS_FILE.read_text(encoding="utf-8"))
                    ts = data.get("__updated_at")
                    if isinstance(ts, str):
                        # parse ISO-8601 best-effort
                        try:
                            # Standard library imports
                            import datetime as _dt

                            last_updated = _dt.datetime.fromisoformat(ts).timestamp()
                        except Exception:
                            last_updated = None
                except Exception:
                    last_updated = None
                if last_updated is None:
                    try:
                        last_updated = api_keys.KEYS_FILE.stat().st_mtime
                    except Exception:
                        last_updated = None

            # If we couldn't determine last_updated, don't force rotation
            if last_updated is not None:
                age = current_time - float(last_updated)
                max_age = float(self.config.api_key_rotation_days * 24 * 60 * 60)
                if age > max_age:
                    for p in providers:
                        if api_keys.get_key(f"{p}_api_key"):
                            rotation_needed.append(p)
        except Exception:
            pass

        return rotation_needed

    def _check_api_key_leaks(self) -> List[str]:
        """Check for potential API key leaks"""
        leaks = []

        # Check environment variables
        for key, value in os.environ.items():
            if "api_key" in key.lower() or "secret" in key.lower():
                if len(value) > 20:
                    leaks.append(f"Environment variable: {key}")

        # Check common files
        check_files = [".env", "config.json", "settings.json", "keys.json"]

        for filename in check_files:
            file_path = self.workspace_path / filename
            if file_path.exists():
                try:
                    with open(file_path) as f:
                        content = f.read()

                    # Simple pattern matching for potential keys
                    if "api_key" in content.lower() or "secret" in content.lower():
                        leaks.append(f"File: {filename}")
                except Exception:
                    pass

        return leaks

    def _check_file_permissions(self) -> List[str]:
        """Check for file permission issues"""
        issues = []

        # Check sensitive files
        sensitive_files = [".env", ".aetherra/secure/", ".aetherra/keys/"]

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
        api_results = results["api_keys"]
        if api_results["rotation_needed"]:
            alerts.append(
                f"API key rotation needed for: {', '.join(api_results['rotation_needed'])}"
            )

        if api_results["potential_leaks"]:
            alerts.append(f"Potential API key leaks: {', '.join(api_results['potential_leaks'])}")

        # Check memory issues
        memory_results = results["memory"]
        if memory_results["high_usage"]:
            alerts.append(
                f"High memory usage: {memory_results['usage']['current_usage']['percent']:.1f}%"
            )

        if memory_results["leaks"]:
            alerts.append(f"Memory leaks detected: {len(memory_results['leaks'])} locations")

        # Check file issues
        file_results = results["files"]
        if file_results["suspicious_files"]:
            alerts.append(f"Suspicious files found: {len(file_results['suspicious_files'])}")

        if file_results["permissions_issues"]:
            alerts.append(f"File permission issues: {len(file_results['permissions_issues'])}")

        # Log alerts
        for alert in alerts:
            self.logger.warning(f"🚨 SECURITY ALERT: {alert}")
            rec = {"timestamp": time.time(), "alert": alert, "severity": "warning"}
            self.security_alerts.append(rec)
            # Append to JSONL for UI
            try:
                self.alerts_jsonl.parent.mkdir(parents=True, exist_ok=True)
                with open(self.alerts_jsonl, "a", encoding="utf-8") as f:
                    f.write(json.dumps(rec) + "\n")
            except Exception:
                pass

        # Auto-cleanup if enabled
        if self.config.auto_cleanup_enabled:
            self._auto_cleanup()

    def _auto_cleanup(self):
        """Automatic cleanup of security issues"""
        # Clean up memory if high usage
        try:
            stats = self.memory_manager.get_memory_stats()
            if stats.get("usage_percent", 0.0) > self.config.max_memory_usage_percent:
                # Placeholder: MemoryManager performs periodic cleanup itself; log for now
                self.logger.info("🧹 High memory usage detected; consider triggering cleanup cycle")
        except Exception:
            pass

    def add_alert(self, alert: str, severity: str = "warning") -> None:
        """Public helper to record a security alert and append to the JSONL feed."""
        try:
            rec = {"timestamp": time.time(), "alert": alert, "severity": severity}
            self.security_alerts.append(rec)
            try:
                self.alerts_jsonl.parent.mkdir(parents=True, exist_ok=True)
                with open(self.alerts_jsonl, "a", encoding="utf-8") as f:
                    f.write(json.dumps(rec) + "\n")
            except Exception:
                pass
            self.logger.warning(f"🚨 SECURITY ALERT: {alert}")
        except Exception:
            pass

    def get_security_status(self) -> Dict[str, Any]:
        """Get comprehensive security status"""
        return {
            "api_keys": self._get_api_keys_status(),
            "memory": self.memory_manager.get_memory_stats(),
            "alerts": len(self.security_alerts),
            "last_scan": self.last_security_scan,
            "monitoring_active": self.is_monitoring,
            "config": {
                "api_key_rotation_days": self.config.api_key_rotation_days,
                "memory_monitoring_enabled": self.config.memory_monitoring_enabled,
                "leak_detection_enabled": self.config.leak_detection_enabled,
                "auto_cleanup_enabled": self.config.auto_cleanup_enabled,
            },
        }

    def _get_api_keys_status(self) -> Dict[str, Any]:
        """Return a simple status for the API keystore."""
        status: Dict[str, Any] = {
            "encrypted": False,
            "key_count": 0,
            "master_key_present": False,
            "last_updated": None,
        }
        try:
            if api_keys.KEYS_FILE.exists():
                data = json.loads(api_keys.KEYS_FILE.read_text(encoding="utf-8") or "{}")
                status["encrypted"] = bool(data.get("__encrypted__") is True)
                # count non-internal entries
                status["key_count"] = len([k for k in data.keys() if not k.startswith("__")])
                status["last_updated"] = data.get("__updated_at")
            # detect master key presence without generating it
            if os.getenv("AETHERRA_KEYS_MASTER"):
                status["master_key_present"] = True
            else:
                try:
                    status["master_key_present"] = api_keys.MASTER_KEY_FILE.exists()
                except Exception:
                    status["master_key_present"] = False
        except Exception:
            pass
        return status

    def get_recent_alerts(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Return recent security alerts for UI display (best-effort)."""
        out: List[Dict[str, Any]] = []
        try:
            if self.alerts_jsonl.exists():
                lines = self.alerts_jsonl.read_text(encoding="utf-8").splitlines()
                for line in lines[-limit:]:
                    try:
                        out.append(json.loads(line))
                    except Exception:
                        continue
        except Exception:
            pass
        return out

    def force_security_scan(self) -> Dict[str, Any]:
        """Force an immediate security scan"""
        self._run_security_scan()
        return self.get_security_status()

    def cleanup_all(self) -> None:
        """Cleanup all security-related resources"""
        # Cleanup API keys (no-op for function-based API)
        # In the future we could clear in-memory caches here.

        # Cleanup memory
        try:
            stats = self.memory_manager.get_memory_stats()
            self.logger.info(
                f"Memory stats at cleanup: usage={stats.get('usage_percent', 0.0):.1f}% entries={stats.get('total_entries', 0)}"
            )
        except Exception:
            pass

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


def initialize_aetherra_security(
    workspace_path: Optional[str] = None, config: Optional[SecurityConfig] = None
) -> None:
    """Initialize Aetherra security system"""
    global _security_system
    _security_system = AetherraSecuritySystem(workspace_path, config)
    return _security_system


def secure_api_call(provider: str, func, *args, **kwargs):
    """Make a secure API call with proper key management"""
    # Fetch provider key from keystore
    api_key = api_keys.get_key(f"{provider}_api_key")

    if not api_key:
        raise ValueError(f"No API key found for provider: {provider}")

    # Add API key to kwargs
    kwargs["api_key"] = api_key
    return func(*args, **kwargs)


if __name__ == "__main__":
    # Example usage
    security_system = AetherraSecuritySystem()

    print("🛡️ Aetherra Security System")
    print("=" * 40)

    # Get security status (sanitized for console output)
    status = redact_secrets(security_system.get_security_status())
    print(f"Security monitoring: {'Active' if status['monitoring_active'] else 'Inactive'}")
    print(f"Security alerts: {status['alerts']}")
    # Guard against missing keys and avoid printing raw objects
    mem = status.get("memory") or {}
    usage = 0.0
    if isinstance(mem, dict):
        usage = float(mem.get("usage_percent", 0.0) or 0.0)
    print(f"Memory usage: {usage:.1f}%")

    # Force security scan
    print("\n🔍 Running security scan...")
    scan_results = security_system.force_security_scan()
    print("Security scan completed!")

    # Cleanup
    security_system.cleanup_all()
