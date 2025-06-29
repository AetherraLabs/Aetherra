#!/usr/bin/env python3
"""
🧬 NeuroCode Standard Library - System Monitor Plugin
Built-in plugin for NeuroCode to monitor system statistics
"""

import os
import platform
import json
import subprocess
from datetime import datetime

class SystemMonitorPlugin:
    """System monitoring capabilities for NeuroCode"""
    
    def __init__(self):
        self.name = "sysmon"
        self.description = "System performance monitoring"
        self.available_actions = ["check_health", "get_status", "status"]
        
    def get_system_info(self):
        """Get basic system information"""
        return {
            'platform': platform.system(),
            'release': platform.release(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'python_version': platform.python_version()
        }
    
    def get_process_count(self):
        """Get number of running processes (simple approach)"""
        try:
            if platform.system() == "Windows":
                result = subprocess.run(['tasklist'], capture_output=True, text=True)
                return len(result.stdout.split('\n')) - 3  # Subtract header lines
            else:
                result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
                return len(result.stdout.split('\n')) - 1
        except:
            return -1  # Unknown
    
    def check_disk_space(self, path="."):
        """Check available disk space"""
        try:
            # Use shutil.disk_usage (available in Python 3.3+, cross-platform)
            import shutil
            total, used, free = shutil.disk_usage(path)
            return {
                'total': total,
                'used': used,
                'available': free,
                'percent_used': (used / total) * 100 if total > 0 else 0
            }
        except ImportError:
            # shutil.disk_usage not available, use platform-specific method
            import platform
            if platform.system() == 'Windows':
                # Windows fallback with mock data
                return {
                    'total': 1000000000,  # Mock values
                    'used': 500000000,
                    'available': 500000000,
                    'percent_used': 50,
                    'note': 'Using mock disk space data on Windows'
                }
            else:
                # Unix-like systems - dynamic import to avoid linting issues
                try:
                    statvfs_func = getattr(__import__('os'), 'statvfs', None)
                    if statvfs_func:
                        statvfs = statvfs_func(path)
                        total = statvfs.f_frsize * statvfs.f_blocks
                        available = statvfs.f_frsize * statvfs.f_available
                        used = total - available
                        return {
                            'total': total,
                            'used': used,
                            'available': available,
                            'percent_used': (used / total) * 100 if total > 0 else 0
                        }
                except:
                    pass
                # Final fallback
                return {
                    'total': 1000000000,
                    'used': 500000000,
                    'available': 500000000,
                    'percent_used': 50,
                    'note': 'Using mock disk space data'
                }
        except Exception as e:
            return {
                'total': 0,
                'used': 0, 
                'available': 0,
                'percent_used': 0,
                'error': str(e)
            }
    
    def get_system_status(self):
        """Get comprehensive system status"""
        status = {
            'timestamp': datetime.now().isoformat(),
            'system_info': self.get_system_info(),
            'process_count': self.get_process_count(),
            'disk_space': self.check_disk_space(),
            'monitoring_active': True
        }
        return status
    
    def check_system_health(self):
        """Analyze system health and return recommendations"""
        status = self.get_system_status()
        recommendations = []
        
        if status['disk_space']['percent_used'] > 90:
            recommendations.append("Low disk space - consider cleanup")
        
        if status['process_count'] > 200:
            recommendations.append("High process count - system may be overloaded")
        
        return {
            'status': status,
            'recommendations': recommendations,
            'health_score': self._calculate_health_score(status)
        }
    
    def _calculate_health_score(self, status):
        """Calculate overall system health score (0-100)"""
        disk_score = max(0, 100 - status['disk_space']['percent_used'])
        process_score = max(0, 100 - (status['process_count'] / 5)) if status['process_count'] > 0 else 100
        
        return (disk_score + process_score) / 2
    
    def execute_action(self, action, memory_system=None):
        """Execute system monitoring actions for NeuroCode"""
        if action == "check_health":
            health = self.check_system_health()
            if memory_system:
                memory_system.remember(
                    f"System health check: Process count {health['status']['process_count']}, "
                    f"Disk usage {health['status']['disk_space']['percent_used']:.1f}%, "
                    f"Health score: {health['health_score']:.1f}",
                    tags=['sysmon', 'health_check'],
                    category='system'
                )
            return health
        
        elif action == "get_status" or action == "status":
            status = self.get_system_status()
            if memory_system:
                memory_system.remember(
                    f"System status: {status['system_info']['platform']} "
                    f"{status['system_info']['release']}, "
                    f"Process count: {status['process_count']}",
                    tags=['sysmon', 'status'],
                    category='system'
                )
            return status
        
        else:
            return {
                'error': f"Unknown sysmon action: {action}",
                'available_actions': ['check_health', 'get_status', 'status'],
                'usage': [
                    'sysmon check_health  # Full health check with recommendations',
                    'sysmon status        # Get system information and metrics'
                ]
            }


# Register plugin
PLUGIN_CLASS = SystemMonitorPlugin
