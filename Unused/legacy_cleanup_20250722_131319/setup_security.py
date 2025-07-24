"""
🛡️ Aetherra Security Initialization Script
===========================================

This script initializes the Aetherra security system and provides
an easy way to set up security for your projects.

Author: Aetherra Security Team
Date: July 16, 2025
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional

def create_security_directories(workspace_path: str) -> None:
    """Create necessary security directories"""
    base_path = Path(workspace_path)

    # Create Aetherra directory structure
    aetherra_dir = base_path / "Aetherra"
    aetherra_dir.mkdir(exist_ok=True)

    # Create security directory
    security_dir = aetherra_dir / "security"
    security_dir.mkdir(exist_ok=True)

    # Create secure data directories
    secure_dirs = [
        base_path / ".aetherra" / "secure",
        base_path / ".aetherra" / "keys",
        base_path / ".aetherra" / "logs",
        base_path / ".aetherra" / "backups"
    ]

    for dir_path in secure_dirs:
        dir_path.mkdir(parents=True, exist_ok=True)
        # Set restrictive permissions
        os.chmod(dir_path, 0o700)

    print(f"✅ Security directories created in {workspace_path}")

def create_security_init_file(security_dir: Path) -> None:
    """Create __init__.py file for security module"""
    init_content = '''"""
Aetherra Security Module
========================

This module provides comprehensive security features for Aetherra:
- API key management with encryption
- Memory leak detection and monitoring
- Security auditing and logging
- Automatic cleanup and optimization
"""

from .api_key_manager import APIKeyManager, get_api_key_manager
from .memory_manager import MemoryManager, get_memory_manager
from .security_system import (
    AetherraSecuritySystem,
    SecurityConfig,
    secure_api_call,
    get_security_system,
    initialize_aetherra_security
)

__all__ = [
    'APIKeyManager',
    'get_api_key_manager',
    'MemoryManager',
    'get_memory_manager',
    'AetherraSecuritySystem',
    'SecurityConfig',
    'secure_api_call',
    'get_security_system',
    'initialize_aetherra_security'
]

__version__ = "1.0.0"
'''

    init_file = security_dir / "__init__.py"
    with open(init_file, 'w') as f:
        f.write(init_content)

    print(f"✅ Security module __init__.py created")

def create_security_config_file(workspace_path: str) -> None:
    """Create security configuration file"""
    config_data = {
        "api_key_rotation_days": 30,
        "memory_monitoring_enabled": True,
        "leak_detection_enabled": True,
        "audit_logging_enabled": True,
        "max_memory_usage_percent": 80,
        "security_scan_interval": 3600,
        "auto_cleanup_enabled": True,
        "encryption_enabled": True,
        "backup_keys": True,
        "log_api_calls": True,
        "monitor_file_permissions": True,
        "check_suspicious_files": True
    }

    config_file = Path(workspace_path) / ".aetherra" / "security_config.json"
    with open(config_file, 'w') as f:
        json.dump(config_data, f, indent=2)

    # Set secure permissions
    os.chmod(config_file, 0o600)

    print(f"✅ Security configuration file created")

def create_env_template(workspace_path: str) -> None:
    """Create .env template file"""
    env_template = """# Aetherra API Keys Configuration
# Copy this file to .env and fill in your actual API keys
# Never commit .env to version control!

# OpenAI API Key
OPENAI_API_KEY=your_openai_api_key_here

# Anthropic API Key
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Google API Key
GOOGLE_API_KEY=your_google_api_key_here

# Discord Bot Token
DISCORD_BOT_TOKEN=your_discord_bot_token_here

# Other API Keys
# Add your other API keys here following the same pattern
"""

    template_file = Path(workspace_path) / ".env.template"
    with open(template_file, 'w') as f:
        f.write(env_template)

    print(f"✅ .env template created")

def create_gitignore_security_rules(workspace_path: str) -> None:
    """Add security rules to .gitignore"""
    gitignore_file = Path(workspace_path) / ".gitignore"

    security_rules = """
# Aetherra Security Files
.aetherra/
.env
*.key
*.pem
*.p12
*secret*
*password*
api_keys.json
security_config.json
*.log

# Discord Bot
lyrixa_bot.py
discord_bot/
bot_token.txt

# Database Files
*.db
*.sqlite
*.sqlite3

# Backup Files
*.backup
*.bak

# Temporary Files
*.tmp
*.temp
temp/
tmp/

# OS Files
.DS_Store
Thumbs.db

# IDE Files
.vscode/
.idea/
*.swp
*.swo
"""

    if gitignore_file.exists():
        with open(gitignore_file, 'r') as f:
            existing_content = f.read()

        if "# Aetherra Security Files" not in existing_content:
            with open(gitignore_file, 'a') as f:
                f.write(security_rules)
            print(f"✅ Security rules added to existing .gitignore")
        else:
            print(f"ℹ️  Security rules already exist in .gitignore")
    else:
        with open(gitignore_file, 'w') as f:
            f.write(security_rules)
        print(f"✅ .gitignore created with security rules")

def create_security_readme(workspace_path: str) -> None:
    """Create security README file"""
    readme_content = """# Aetherra Security System

## Overview

The Aetherra Security System provides comprehensive security features for your AI applications:

- **API Key Management**: Encrypted storage and automatic rotation
- **Memory Monitoring**: Leak detection and performance optimization
- **Security Auditing**: Continuous monitoring and alerting
- **Automatic Cleanup**: Resource management and optimization

## Quick Start

### 1. Initialize Security System

```python
from Aetherra.security import initialize_aetherra_security, SecurityConfig

# Initialize with default configuration
security_system = initialize_aetherra_security()

# Or with custom configuration
config = SecurityConfig(
    api_key_rotation_days=30,
    memory_monitoring_enabled=True,
    auto_cleanup_enabled=True
)
security_system = initialize_aetherra_security(config=config)
```

### 2. Store API Keys Securely

```python
# Store API keys
security_system.api_key_manager.store_api_key("openai", "your_openai_key")
security_system.api_key_manager.store_api_key("anthropic", "your_anthropic_key")
```

### 3. Make Secure API Calls

```python
from Aetherra.security import secure_api_call

# Make secure API calls
result = secure_api_call("openai", your_api_function, prompt="Hello!")
```

### 4. Monitor Memory Usage

```python
# Monitor memory in context
with security_system.memory_manager.memory_context("my_operation"):
    # Your memory-intensive code here
    pass

# Check for memory leaks
leaks = security_system.memory_manager.check_memory_leaks()
```

## Configuration

Edit `.aetherra/security_config.json` to customize security settings:

```json
{
  "api_key_rotation_days": 30,
  "memory_monitoring_enabled": true,
  "leak_detection_enabled": true,
  "max_memory_usage_percent": 80,
  "auto_cleanup_enabled": true
}
```

## Security Features

### API Key Security
- ✅ Encrypted storage using Fernet encryption
- ✅ Automatic key rotation
- ✅ Leak detection and prevention
- ✅ Secure memory handling

### Memory Management
- ✅ Memory leak detection
- ✅ Automatic garbage collection
- ✅ Performance monitoring
- ✅ Resource cleanup

### Security Monitoring
- ✅ Continuous security scanning
- ✅ File permission monitoring
- ✅ Suspicious activity detection
- ✅ Audit logging

## Important Security Notes

1. **Never commit sensitive files**: The `.gitignore` includes security patterns
2. **Use environment variables**: Store secrets in `.env` file (not committed)
3. **Regular updates**: Keep security system updated
4. **Monitor alerts**: Check security alerts regularly

## Troubleshooting

### Common Issues

1. **Permission Errors**: Ensure proper file permissions on security directories
2. **Memory Issues**: Monitor memory usage and enable auto-cleanup
3. **API Key Issues**: Check key rotation and encryption settings

### Getting Help

- Check the security logs in `.aetherra/logs/`
- Run security diagnostics: `python -m Aetherra.security.security_system`
- Review security alerts in the monitoring dashboard

## License

This security system is part of the Aetherra project and follows the same license terms.
"""

    readme_file = Path(workspace_path) / "SECURITY.md"
    with open(readme_file, 'w', encoding='utf-8') as f:
        f.write(readme_content)

    print(f"✅ Security README created")

def initialize_aetherra_security_setup(workspace_path: Optional[str] = None) -> None:
    """Initialize complete Aetherra security setup"""
    if workspace_path is None:
        workspace_path = "."

    workspace_path = os.path.abspath(workspace_path)

    print(f"🛡️ Initializing Aetherra Security System")
    print(f"📁 Workspace: {workspace_path}")
    print("=" * 60)

    try:
        # Create security directories
        create_security_directories(workspace_path)

        # Create security module init file
        security_dir = Path(workspace_path) / "Aetherra" / "security"
        create_security_init_file(security_dir)

        # Create security configuration
        create_security_config_file(workspace_path)

        # Create .env template
        create_env_template(workspace_path)

        # Update .gitignore
        create_gitignore_security_rules(workspace_path)

        # Create security README
        create_security_readme(workspace_path)

        print("\n✅ Aetherra Security System initialized successfully!")
        print("\n📋 Next Steps:")
        print("1. Copy .env.template to .env and add your API keys")
        print("2. Review security configuration in .aetherra/security_config.json")
        print("3. Run: python demo_security_integration.py to test")
        print("4. Read SECURITY.md for detailed documentation")

    except Exception as e:
        print(f"\n❌ Error initializing security system: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description="Initialize Aetherra Security System")
    parser.add_argument("--workspace", "-w", help="Workspace directory", default=".")

    args = parser.parse_args()

    initialize_aetherra_security_setup(args.workspace)

if __name__ == "__main__":
    main()
