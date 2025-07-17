# Aetherra Security System

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
