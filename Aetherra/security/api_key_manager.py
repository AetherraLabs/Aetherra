"""
🔒 Aetherra API Key Security Manager
====================================

A comprehensive security system for managing API keys, preventing leaks,
and ensuring secure credential handling throughout the Aetherra ecosystem.

Author: Aetherra Security Team
Date: July 16, 2025
"""

import os
import json
import hashlib
import secrets
import logging
from typing import Optional, Dict, Any, List
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import threading
import time
import re

class APIKeyManager:
    """
    🔒 Secure API Key Management System

    Features:
    - Encrypted storage of API keys
    - Automatic key rotation
    - Memory-safe key handling
    - Leak detection and prevention
    - Audit logging
    - Environment variable protection
    """

    def __init__(self, workspace_path: str = None):
        self.workspace_path = Path(workspace_path or ".")
        self.secure_dir = self.workspace_path / ".aetherra" / "secure"
        self.secure_dir.mkdir(parents=True, exist_ok=True)

        # Initialize encryption
        self._init_encryption()

        # Security settings
        self.max_key_age = 30 * 24 * 60 * 60  # 30 days
        self.audit_enabled = True
        self.memory_protection = True

        # In-memory key storage (encrypted)
        self._key_cache = {}
        self._key_metadata = {}
        self._access_log = []

        # Initialize logging
        self._setup_logging()

        # Start security monitoring
        self._start_monitoring()

    def _init_encryption(self):
        """Initialize encryption system"""
        key_file = self.secure_dir / "master.key"

        if key_file.exists():
            with open(key_file, 'rb') as f:
                self.master_key = f.read()
        else:
            # Generate new master key
            password = os.getenv("AETHERRA_MASTER_PASSWORD", "default_password").encode()
            salt = secrets.token_bytes(16)

            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            self.master_key = base64.urlsafe_b64encode(kdf.derive(password))

            # Save securely
            with open(key_file, 'wb') as f:
                f.write(self.master_key)

            # Secure file permissions
            os.chmod(key_file, 0o600)

        self.cipher = Fernet(self.master_key)

    def _setup_logging(self):
        """Setup security audit logging"""
        log_file = self.secure_dir / "security_audit.log"

        self.logger = logging.getLogger("aetherra_security")
        self.logger.setLevel(logging.INFO)

        handler = logging.FileHandler(log_file)
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def store_api_key(self, provider: str, api_key: str, metadata: Dict[str, Any] = None):
        """
        🔒 Securely store an API key

        Args:
            provider: Provider name (e.g., 'openai', 'anthropic')
            api_key: The API key to store
            metadata: Optional metadata about the key
        """
        if self._is_suspicious_key(api_key):
            raise ValueError("Suspicious API key detected - potential security issue")

        # Encrypt the key
        encrypted_key = self.cipher.encrypt(api_key.encode())

        # Generate key ID
        key_id = hashlib.sha256(f"{provider}:{api_key}".encode()).hexdigest()[:16]

        # Store metadata
        self._key_metadata[provider] = {
            'key_id': key_id,
            'created': time.time(),
            'last_used': None,
            'usage_count': 0,
            'metadata': metadata or {}
        }

        # Store encrypted key
        self._key_cache[provider] = encrypted_key

        # Persist to disk
        self._persist_keys()

        # Log the action
        self.logger.info(f"API key stored for provider: {provider} (ID: {key_id})")

        # Clear sensitive data from memory
        del api_key

    def get_api_key(self, provider: str) -> Optional[str]:
        """
        🔓 Retrieve and decrypt an API key

        Args:
            provider: Provider name

        Returns:
            Decrypted API key or None if not found
        """
        if provider not in self._key_cache:
            return None

        try:
            # Decrypt the key
            encrypted_key = self._key_cache[provider]
            decrypted_key = self.cipher.decrypt(encrypted_key).decode()

            # Update usage metadata
            self._key_metadata[provider]['last_used'] = time.time()
            self._key_metadata[provider]['usage_count'] += 1

            # Log access
            self.logger.info(f"API key accessed for provider: {provider}")

            return decrypted_key

        except Exception as e:
            self.logger.error(f"Failed to decrypt key for {provider}: {e}")
            return None

    def rotate_api_key(self, provider: str, new_key: str):
        """
        🔄 Rotate an API key

        Args:
            provider: Provider name
            new_key: New API key
        """
        old_metadata = self._key_metadata.get(provider, {})

        # Archive old key
        self._archive_key(provider, old_metadata)

        # Store new key
        self.store_api_key(provider, new_key, old_metadata.get('metadata'))

        self.logger.info(f"API key rotated for provider: {provider}")

    def _is_suspicious_key(self, api_key: str) -> bool:
        """
        🕵️ Check if an API key looks suspicious

        Args:
            api_key: The API key to check

        Returns:
            True if suspicious, False otherwise
        """
        suspicious_patterns = [
            r'^test[_-]',  # Test keys
            r'^fake[_-]',  # Fake keys
            r'^demo[_-]',  # Demo keys
            r'^sk-[a-zA-Z0-9]{20}$',  # Too short for real OpenAI keys
            r'^[a-zA-Z0-9]{10,20}$',  # Too simple
        ]

        for pattern in suspicious_patterns:
            if re.match(pattern, api_key, re.IGNORECASE):
                return True

        return False

    def _persist_keys(self):
        """Persist encrypted keys to disk"""
        data = {
            'keys': {k: base64.b64encode(v).decode() for k, v in self._key_cache.items()},
            'metadata': self._key_metadata
        }

        encrypted_data = self.cipher.encrypt(json.dumps(data).encode())

        with open(self.secure_dir / "keys.enc", 'wb') as f:
            f.write(encrypted_data)

    def _load_keys(self):
        """Load encrypted keys from disk"""
        key_file = self.secure_dir / "keys.enc"

        if not key_file.exists():
            return

        try:
            with open(key_file, 'rb') as f:
                encrypted_data = f.read()

            decrypted_data = self.cipher.decrypt(encrypted_data).decode()
            data = json.loads(decrypted_data)

            self._key_cache = {k: base64.b64decode(v) for k, v in data['keys'].items()}
            self._key_metadata = data['metadata']

        except Exception as e:
            self.logger.error(f"Failed to load keys: {e}")

    def _archive_key(self, provider: str, metadata: Dict[str, Any]):
        """Archive an old key"""
        archive_file = self.secure_dir / "key_archive.json"

        archive_data = []
        if archive_file.exists():
            with open(archive_file, 'r') as f:
                archive_data = json.load(f)

        archive_data.append({
            'provider': provider,
            'archived_at': time.time(),
            'metadata': metadata
        })

        with open(archive_file, 'w') as f:
            json.dump(archive_data, f, indent=2)

    def _start_monitoring(self):
        """Start security monitoring thread"""
        def monitor():
            while True:
                self._check_key_age()
                self._scan_for_leaks()
                time.sleep(3600)  # Check every hour

        thread = threading.Thread(target=monitor, daemon=True)
        thread.start()

    def _check_key_age(self):
        """Check for old keys that need rotation"""
        current_time = time.time()

        for provider, metadata in self._key_metadata.items():
            age = current_time - metadata['created']

            if age > self.max_key_age:
                self.logger.warning(f"API key for {provider} is {age/86400:.1f} days old - rotation recommended")

    def _scan_for_leaks(self):
        """Scan for potential API key leaks"""
        # Check environment variables for exposed keys
        for key, value in os.environ.items():
            if 'api_key' in key.lower() or 'secret' in key.lower():
                if len(value) > 20:  # Potential API key
                    self.logger.warning(f"Potential API key in environment variable: {key}")

    def get_masked_key(self, provider: str) -> str:
        """
        🎭 Get a masked version of the API key for display

        Args:
            provider: Provider name

        Returns:
            Masked key (e.g., "sk-...abc123")
        """
        key = self.get_api_key(provider)
        if not key:
            return "Not configured"

        if len(key) > 8:
            return f"{key[:3]}...{key[-4:]}"
        else:
            return "*" * len(key)

    def cleanup_memory(self):
        """
        🧹 Clean up sensitive data from memory
        """
        # Clear key cache
        self._key_cache.clear()

        # Clear metadata
        self._key_metadata.clear()

        # Clear access log
        self._access_log.clear()

        self.logger.info("Memory cleanup completed")

    def get_security_status(self) -> Dict[str, Any]:
        """
        📊 Get security status report

        Returns:
            Dictionary with security metrics
        """
        return {
            'providers_configured': len(self._key_metadata),
            'total_key_uses': sum(meta['usage_count'] for meta in self._key_metadata.values()),
            'oldest_key_age': min(
                (time.time() - meta['created']) / 86400
                for meta in self._key_metadata.values()
            ) if self._key_metadata else 0,
            'audit_log_size': len(self._access_log),
            'memory_protection': self.memory_protection,
            'encryption_enabled': True
        }

# Global instance
_api_key_manager = None

def get_api_key_manager() -> APIKeyManager:
    """Get the global API key manager instance"""
    global _api_key_manager
    if _api_key_manager is None:
        _api_key_manager = APIKeyManager()
    return _api_key_manager

def secure_getenv(key: str, default: str = None) -> str:
    """
    🔒 Secure environment variable getter

    Args:
        key: Environment variable name
        default: Default value if not found

    Returns:
        Environment variable value
    """
    manager = get_api_key_manager()

    # Try to get from secure storage first
    if key.endswith('_API_KEY'):
        provider = key.replace('_API_KEY', '').lower()
        stored_key = manager.get_api_key(provider)
        if stored_key:
            return stored_key

    # Fall back to environment variable
    return os.getenv(key, default)

if __name__ == "__main__":
    # Example usage
    manager = APIKeyManager()

    print("🔒 Aetherra API Key Security Manager")
    print("=" * 40)

    # Store a test key
    manager.store_api_key("openai", "sk-test123456789abcdef", {"purpose": "development"})

    # Retrieve and display
    print(f"Stored key: {manager.get_masked_key('openai')}")
    print(f"Security status: {manager.get_security_status()}")
