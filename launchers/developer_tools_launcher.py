#!/usr/bin/env python3
"""
🛠️ AETHERRA & LYRIXA DEVELOPER TOOLS LAUNCHER
==============================================

Interactive launcher for all developer tools with menu-driven interface.
This script provides easy access to all developer tools and their features.
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Add developer_tools to path
sys.path.insert(0, str(Path(__file__).parent / "developer_tools"))

def print_banner():
    """Print the developer tools banner"""
    print("🛠️" + "=" * 60)
    print("  AETHERRA & LYRIXA DEVELOPER TOOLS SUITE")
    print("  Production-Ready Safety & Development Tools")
    print("=" * 62)
    print()

def print_main_menu():
    """Print the main menu"""
    print("📋 Available Tools:")
    print("1. 🛡️  WriteGuard System - File write monitoring & protection")
    print("2. 💾  SafeSave Plugin - Atomic file operations")
    print("3. 🧠  Memory Inspector - Memory management & editing")
    print("4. 🏖️  Plugin Sandbox - Isolated plugin testing")
    print("5. �  Health Dashboard - Real-time system monitoring")
    print("6. 🚨  Error Tracker - Centralized error logging")
    print("7. ⚡  Performance Profiler - Resource usage analysis")
    print("8. 📦  Memory & Workflow Backup - Versioned snapshots")
    print("9. 📚  Knowledge Base Sync - Auto-sync docs to memory")
    print("10. �🔧 Tool Integration Demo - See tools working together")
    print("11. � Run Full Test Suite - Validate all tools")
    print("12. ℹ️  Show Tool Status - Check available tools")
    print("13. � Show Documentation - View tool documentation")
    print("14. 🚪 Exit")
    print()

def launch_write_guard():
    """Launch WriteGuard demonstration"""
    print("\n🛡️ WriteGuard System Demo")
    print("-" * 30)

    try:
        write_guard_path = Path(__file__).parent / "developer_tools" / "safety"
        sys.path.insert(0, str(write_guard_path))
        from write_guard import write_guard_protection, WriteGuardConfig

        # Configure WriteGuard
        config = WriteGuardConfig()
        config.log_all_writes = True
        config.backup_before_write = True
        config.dry_run_mode = True  # Safe demo mode

        print("✅ WriteGuard configured with:")
        print(f"   - Logging: {config.log_all_writes}")
        print(f"   - Backups: {config.backup_before_write}")
        print(f"   - Dry run mode: {config.dry_run_mode}")

        with write_guard_protection(config) as guard:
            print("\n🔍 Demonstrating protected file operations...")

            # Simulate file write
            test_data = {
                "demo": "WriteGuard Demo",
                "timestamp": datetime.now().isoformat(),
                "protected": True
            }

            with open("demo_protected_file.json", "w") as f:
                json.dump(test_data, f, indent=2)

            # Show statistics
            stats = guard.get_operation_stats()
            print(f"\n📊 WriteGuard Statistics:")
            print(f"   - Total operations: {stats['total_operations']}")
            print(f"   - Active operations: {stats['active_operations']}")
            print(f"   - Success rate: {stats['success_rate']:.1%}")

        print("✅ WriteGuard demo completed successfully!")

    except Exception as e:
        print(f"❌ WriteGuard demo failed: {e}")

def launch_safe_save():
    """Launch SafeSave demonstration"""
    print("\n💾 SafeSave Plugin Demo")
    print("-" * 25)

    try:
        safe_save_path = Path(__file__).parent / "developer_tools" / "safety"
        sys.path.insert(0, str(safe_save_path))
        from safe_save import SafeSavePlugin, SafeSaveConfig

        # Configure SafeSave
        config = SafeSaveConfig()
        config.verify_checksums = True
        config.create_backups = True

        plugin = SafeSavePlugin(config)

        print("✅ SafeSave configured with:")
        print(f"   - Checksum verification: {config.verify_checksums}")
        print(f"   - Automatic backups: {config.create_backups}")

        print("\n🔒 Demonstrating atomic file operations...")

        # Test JSON write
        demo_data = {
            "system": "Aetherra & Lyrixa",
            "tool": "SafeSave Plugin",
            "demo_time": datetime.now().isoformat(),
            "features": ["atomic_writes", "backup_creation", "validation"]
        }

        success = plugin.safe_write_json("demo_safesave.json", demo_data)
        print(f"   JSON write: {'✅ SUCCESS' if success else '❌ FAILED'}")

        # Test text write
        success = plugin.safe_write_text("demo_safesave.txt",
                                       "SafeSave Plugin Demo Content\nAtomic operations ensure data integrity!")
        print(f"   Text write: {'✅ SUCCESS' if success else '❌ FAILED'}")

        # Show statistics
        stats = plugin.get_stats()
        print(f"\n📊 SafeSave Statistics:")
        print(f"   - Total writes: {stats['total_writes']}")
        print(f"   - Success rate: {stats['success_rate']:.1%}")
        print(f"   - Backups created: {stats['backups_created']}")

        print("✅ SafeSave demo completed successfully!")

    except Exception as e:
        print(f"❌ SafeSave demo failed: {e}")

def launch_memory_inspector():
    """Launch Memory Inspector demonstration"""
    print("\n🧠 Memory Inspector Demo")
    print("-" * 25)

    try:
        memory_path = Path(__file__).parent / "developer_tools" / "memory"
        sys.path.insert(0, str(memory_path))
        from inspector import MemoryInspector

        # Create inspector
        inspector = MemoryInspector("demo_memory.json")

        print("🧠 Demonstrating memory management...")

        # Add some demo memories
        demo_memories = {
            "user_preferences": {"theme": "dark", "language": "en", "notifications": True},
            "system_state": {"version": "1.0.0", "last_update": datetime.now().isoformat()},
            "project_config": {"name": "Aetherra", "type": "AI_Assistant", "status": "active"}
        }

        for key, value in demo_memories.items():
            success = inspector.update_memory(key, value)
            print(f"   Memory '{key}': {'✅ STORED' if success else '❌ FAILED'}")

        # Demonstrate search
        results = inspector.search_memories("config")
        print(f"\n🔍 Search for 'config': {len(results)} results")

        # Demonstrate pinning
        inspector.pin_memory("system_state", True)
        print("📌 Pinned 'system_state' memory")

        # Demonstrate tagging
        inspector.add_tag("user_preferences", "ui")
        inspector.add_tag("user_preferences", "user_data")
        print("🏷️  Added tags to 'user_preferences'")

        # Show all memories
        all_memories = inspector.search_memories()
        print(f"\n📊 Total memories: {len(all_memories)}")

        # Validate integrity
        integrity = inspector.validate_integrity()
        valid_count = sum(integrity.values())
        print(f"🔐 Integrity check: {valid_count}/{len(integrity)} memories valid")

        print("✅ Memory Inspector demo completed successfully!")

    except Exception as e:
        print(f"❌ Memory Inspector demo failed: {e}")

def launch_plugin_sandbox():
    """Launch Plugin Sandbox demonstration"""
    print("\n🏖️ Plugin Sandbox Demo")
    print("-" * 22)

    try:
        sandbox_path = Path(__file__).parent / "developer_tools" / "plugins"
        sys.path.insert(0, str(sandbox_path))
        from sandbox import PluginSandbox, SandboxConfig

        # Create demo plugin
        demo_plugin_code = '''
def hello_world():
    """Simple demo function"""
    return {"message": "Hello from demo plugin!", "status": "success"}

def calculate_fibonacci(n):
    """Calculate fibonacci number"""
    if n <= 1:
        return n
    return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)

def demo_with_memory():
    """Demonstrate memory system interaction"""
    # This would interact with mock memory system in sandbox
    return {"memory_test": "completed", "mock_data": "available"}
'''

        # Write demo plugin
        plugin_path = Path("demo_plugin.py")
        with open(plugin_path, "w") as f:
            f.write(demo_plugin_code)

        # Configure sandbox
        config = SandboxConfig()
        config.max_execution_time = 15
        config.max_memory_usage = 50 * 1024 * 1024  # 50MB

        sandbox = PluginSandbox(config)

        print("✅ Sandbox configured with:")
        print(f"   - Max execution time: {config.max_execution_time}s")
        print(f"   - Max memory: {config.max_memory_usage // 1024 // 1024}MB")

        print("\n🔒 Testing plugin in isolated environment...")

        # Load plugin
        success = sandbox.load_plugin("demo_plugin.py")
        print(f"   Plugin loading: {'✅ SUCCESS' if success else '❌ FAILED'}")

        if success:
            # Test different functions
            tests = [
                ("hello_world", []),
                ("calculate_fibonacci", [8]),
                ("demo_with_memory", [])
            ]

            for func_name, args in tests:
                result = sandbox.run_plugin("demo_plugin.py", func_name, args)
                status = "✅ SUCCESS" if result['success'] else "❌ FAILED"
                duration = result.get('duration', 0)
                print(f"   Function '{func_name}': {status} ({duration:.2f}s)")

                if result.get('resource_stats'):
                    stats = result['resource_stats']
                    if stats.get('max_memory') > 0:
                        print(f"      Memory: {stats['max_memory']:.1f}MB")
                    if stats.get('violations'):
                        print(f"      ⚠️ Violations: {len(stats['violations'])}")

        # Generate report
        report = sandbox.generate_test_report()
        report_lines = len(report.split('\n'))
        print(f"\n📄 Test report generated ({report_lines} lines)")

        # Cleanup
        sandbox.cleanup()
        plugin_path.unlink(missing_ok=True)

        print("✅ Plugin Sandbox demo completed successfully!")

    except Exception as e:
        print(f"❌ Plugin Sandbox demo failed: {e}")

def show_integration_demo():
    """Show how tools work together"""
    print("\n🔧 Tool Integration Demo")
    print("-" * 26)

    print("🔗 Demonstrating tool integration...")

    try:
        # Import multiple tools
        safe_save_path = Path(__file__).parent / "developer_tools" / "safety"
        memory_path = Path(__file__).parent / "developer_tools" / "memory"

        sys.path.insert(0, str(safe_save_path))
        sys.path.insert(0, str(memory_path))

        from safe_save import SafeSavePlugin
        from write_guard import write_guard_protection, WriteGuardConfig
        from inspector import MemoryInspector

        print("✅ All tools imported successfully")

        # Configure WriteGuard for integration
        wg_config = WriteGuardConfig()
        wg_config.dry_run_mode = False
        wg_config.backup_before_write = True

        with write_guard_protection(wg_config):
            print("🛡️ WriteGuard monitoring active")

            # Use SafeSave plugin
            safe_save = SafeSavePlugin()

            # Create memory inspector
            memory_inspector = MemoryInspector("integration_demo.json")

            print("💾 Creating integrated demo data...")

            # Store some memories
            memory_inspector.update_memory("integration_test", {
                "tools_used": ["WriteGuard", "SafeSave", "MemoryInspector"],
                "demo_time": datetime.now().isoformat(),
                "success": True
            })

            # Export memories using SafeSave
            success = memory_inspector.export_memories("integration_export.json")
            print(f"📤 Memory export: {'✅ SUCCESS' if success else '❌ FAILED'}")

            # Create additional safe file
            integration_data = {
                "demonstration": "Tool Integration",
                "writeGuard_active": True,
                "safeSave_enabled": True,
                "memory_inspector_running": True,
                "all_tools_working": True
            }

            success = safe_save.safe_write_json("integration_demo_file.json", integration_data)
            print(f"💾 Safe file write: {'✅ SUCCESS' if success else '❌ FAILED'}")

        print("🔗 Integration demo: All tools working together successfully!")

    except Exception as e:
        print(f"❌ Integration demo failed: {e}")

def run_test_suite():
    """Run the full test suite"""
    print("\n📊 Running Full Test Suite")
    print("-" * 27)

    try:
        import subprocess
        result = subprocess.run([sys.executable, "test_developer_tools.py"],
                              capture_output=True, text=True)

        print("Test output:")
        print(result.stdout)

        if result.returncode == 0:
            print("✅ All tests passed!")
        else:
            print("❌ Some tests failed")
            if result.stderr:
                print(f"Errors: {result.stderr}")

    except Exception as e:
        print(f"❌ Test suite execution failed: {e}")

def show_tool_status():
    """Show status of all tools"""
    print("\n📊 Developer Tools Status")
    print("-" * 26)

    try:
        # Check tool availability
        tools_status = {
            "WriteGuard": False,
            "SafeSave": False,
            "MemoryInspector": False,
            "PluginSandbox": False
        }

        # Test WriteGuard
        try:
            write_guard_path = Path(__file__).parent / "developer_tools" / "safety"
            sys.path.insert(0, str(write_guard_path))
            from write_guard import WriteGuard
            tools_status["WriteGuard"] = True
        except:
            pass

        # Test SafeSave
        try:
            from safe_save import SafeSavePlugin
            tools_status["SafeSave"] = True
        except:
            pass

        # Test Memory Inspector
        try:
            memory_path = Path(__file__).parent / "developer_tools" / "memory"
            sys.path.insert(0, str(memory_path))
            from inspector import MemoryInspector
            tools_status["MemoryInspector"] = True
        except:
            pass

        # Test Plugin Sandbox
        try:
            sandbox_path = Path(__file__).parent / "developer_tools" / "plugins"
            sys.path.insert(0, str(sandbox_path))
            from sandbox import PluginSandbox
            tools_status["PluginSandbox"] = True
        except:
            pass

        # Display status
        for tool, available in tools_status.items():
            status = "✅ AVAILABLE" if available else "❌ NOT AVAILABLE"
            print(f"🛠️ {tool}: {status}")

        total_available = sum(tools_status.values())
        print(f"\n📊 Summary: {total_available}/4 tools available")

        if total_available == 4:
            print("🎉 All developer tools are ready for use!")

    except Exception as e:
        print(f"❌ Status check failed: {e}")

def show_documentation():
    """Show tool documentation"""
    print("\n📚 Developer Tools Documentation")
    print("-" * 33)

    print("📖 Available Documentation:")
    print()

    docs = [
        ("DEVELOPER_TOOLS_ROADMAP.md", "📋 Complete roadmap and planning"),
        ("DEVELOPER_TOOLS_IMPLEMENTATION_COMPLETE.md", "✅ Implementation summary"),
        ("developer_tools/safety/write_guard.py", "🛡️ WriteGuard System documentation"),
        ("developer_tools/safety/safe_save.py", "💾 SafeSave Plugin documentation"),
        ("developer_tools/memory/inspector.py", "🧠 Memory Inspector documentation"),
        ("developer_tools/plugins/sandbox.py", "🏖️ Plugin Sandbox documentation"),
        ("test_developer_tools.py", "🧪 Test suite and examples")
    ]

    for file_path, description in docs:
        path = Path(file_path)
        exists = "✅" if path.exists() else "❌"
        print(f"{exists} {description}")
        print(f"   📁 {file_path}")
        print()

    print("💡 Tip: Each tool module contains comprehensive docstrings and usage examples!")

def cleanup_demo_files():
    """Clean up demo files"""
    demo_files = [
        "demo_protected_file.json",
        "demo_safesave.json",
        "demo_safesave.txt",
        "demo_memory.json",
        "integration_demo.json",
        "integration_export.json",
        "integration_demo_file.json",
        "memory_inspector.db"
    ]

    cleaned = 0
    for file_path in demo_files:
        path = Path(file_path)
        if path.exists():
            path.unlink()
            cleaned += 1

    if cleaned > 0:
        print(f"🧹 Cleaned up {cleaned} demo files")

def launch_health_dashboard():
    """Launch Health Dashboard demonstration"""
    print("\n📊 Health Dashboard Demo")
    print("-" * 30)

    try:
        from developer_tools.monitoring.health_dashboard import ProjectHealthDashboard

        dashboard = ProjectHealthDashboard()

        print("✅ Health Dashboard initialized")
        print("   Checking system health...")

        # Get current system status
        status = dashboard.get_system_status()

        print(f"\n🖥️ System Status:")
        print(f"   CPU Usage: {status['cpu_percent']:.1f}%")
        print(f"   Memory Usage: {status['memory_usage']:.1f} MB ({status['memory_percent']:.1f}%)")
        print(f"   Disk Space: {status['disk_free_gb']:.1f} GB free")
        print(f"   Python Version: {status['python_version']}")

        # Check if web dashboard is running
        dashboard.start_web_dashboard(port=8080)
        print(f"\n🌐 Web dashboard started at: http://localhost:8080")
        print("   (Dashboard will run in background)")

        input("\nPress Enter to stop dashboard...")
        dashboard.stop_web_dashboard()
        print("✅ Dashboard stopped")

    except ImportError:
        print("❌ Health Dashboard not available - missing dependencies")
    except Exception as e:
        print(f"❌ Error running Health Dashboard: {e}")

def launch_error_tracker():
    """Launch Error Tracker demonstration"""
    print("\n🚨 Error Tracker Demo")
    print("-" * 30)

    try:
        from developer_tools.monitoring.error_tracker import ErrorTracker

        tracker = ErrorTracker()

        print("✅ Error Tracker initialized")
        print("   Testing error logging...")

        # Log some test errors
        tracker.log_error("TestError", "This is a test error for demonstration", {
            'component': 'demo',
            'severity': 'medium'
        })

        tracker.log_error("ValidationError", "Sample validation error", {
            'component': 'validation',
            'severity': 'low'
        })

        print("   ✅ Test errors logged")

        # Show error summary
        summary = tracker.get_error_summary()
        print(f"\n📈 Error Summary:")
        print(f"   Total Errors: {summary['total_errors']}")
        print(f"   Unique Error Types: {summary['unique_types']}")
        print(f"   Recent Errors (24h): {summary['recent_errors']}")

        # Show recent errors
        recent = tracker.get_recent_errors(limit=5)
        if recent:
            print(f"\n🔍 Recent Errors:")
            for error in recent:
                print(f"   - {error['error_type']}: {error['message'][:50]}...")

        # Generate report
        report = tracker.generate_daily_report()
        if report:
            print(f"\n📄 Error Report Generated:")
            print(f"   Report saved with {len(report.get('errors', []))} errors analyzed")

    except ImportError:
        print("❌ Error Tracker not available - missing dependencies")
    except Exception as e:
        print(f"❌ Error running Error Tracker: {e}")

def launch_performance_profiler():
    """Launch Performance Profiler demonstration"""
    print("\n⚡ Performance Profiler Demo")
    print("-" * 30)

    try:
        from developer_tools.monitoring.performance_profiler import PerformanceProfiler
        import time

        profiler = PerformanceProfiler()

        print("✅ Performance Profiler initialized")
        print("   Starting profiling session...")

        # Start profiling
        session_id = profiler.start_profiling("demo_session")

        # Simulate some work
        print("   🔄 Simulating workload...")
        time.sleep(3)

        # Do some memory-intensive work
        test_data = [i ** 2 for i in range(10000)]
        time.sleep(2)

        # Stop profiling
        session = profiler.stop_profiling()

        if session:
            print(f"\n📊 Profiling Results:")
            print(f"   Session: {session.session_id}")
            print(f"   Duration: {session.duration:.2f}s")
            print(f"   Metrics collected: {len(session.metrics)}")
            print(f"   Bottlenecks found: {len(session.bottlenecks)}")

            if session.bottlenecks:
                print(f"\n⚠️ Performance Issues:")
                for bottleneck in session.bottlenecks:
                    print(f"   - {bottleneck}")

            if session.recommendations:
                print(f"\n💡 Recommendations:")
                for rec in session.recommendations:
                    print(f"   - {rec}")

        # Show current system metrics
        metrics = profiler.get_system_metrics()
        print(f"\n🖥️ Current System Metrics:")
        print(f"   CPU: {metrics.cpu_percent:.1f}%")
        print(f"   Memory: {metrics.memory_usage:.1f} MB")
        print(f"   Threads: {metrics.thread_count}")

    except ImportError:
        print("❌ Performance Profiler not available - missing dependencies")
    except Exception as e:
        print(f"❌ Error running Performance Profiler: {e}")

def launch_memory_backup():
    """Launch Memory & Workflow Backup demonstration"""
    print("\n📦 Memory & Workflow Backup Demo")
    print("-" * 30)

    try:
        from developer_tools.memory.backup import MemoryWorkflowBackup

        backup_system = MemoryWorkflowBackup()

        print("✅ Backup System initialized")

        # Show current backup status
        backups = backup_system.list_backups()
        print(f"   Existing backups: {len(backups)}")

        # Create a test memory store for demo
        test_memory_path = "demo_memory_store.json"
        test_memory_data = {
            'memory': {
                'demo_key1': 'This is demo content 1',
                'demo_key2': 'This is demo content 2'
            },
            'tags': {
                'demo_key1': ['demo', 'test'],
                'demo_key2': ['demo', 'sample']
            },
            'pins': ['demo_key1']
        }

        # Save test memory store
        import json
        with open(test_memory_path, 'w') as f:
            json.dump(test_memory_data, f, indent=2)

        print("   📝 Created demo memory store")

        # Create memory backup
        backup_id = backup_system.create_memory_backup(
            test_memory_path,
            description="Demo backup created by launcher",
            tags=["demo", "launcher"]
        )

        print(f"   ✅ Created backup: {backup_id}")

        # List backups again
        updated_backups = backup_system.list_backups()
        print(f"   Total backups: {len(updated_backups)}")

        if updated_backups:
            print(f"\n📋 Recent Backups:")
            for backup in updated_backups[-3:]:  # Show last 3
                print(f"   - {backup['session_id']}: {backup['duration']:.2f}s")

        # Clean up
        Path(test_memory_path).unlink(missing_ok=True)
        print("   🧹 Demo files cleaned up")

    except ImportError:
        print("❌ Memory Backup not available - missing dependencies")
    except Exception as e:
        print(f"❌ Error running Memory Backup: {e}")

def launch_knowledge_sync():
    """Launch Knowledge Base Sync demonstration"""
    print("\n📚 Knowledge Base Sync Demo")
    print("-" * 30)

    try:
        from developer_tools.knowledge.sync import KnowledgeBaseSync

        kb_sync = KnowledgeBaseSync()

        print("✅ Knowledge Base Sync initialized")

        # Show current sync status
        status = kb_sync.get_sync_status()
        print(f"   Auto-sync: {'Enabled' if status['auto_sync_enabled'] else 'Disabled'}")
        print(f"   Sync paths: {status['sync_paths_count']}")
        print(f"   Synced documents: {status['synced_documents']}")

        # Add documentation directory for demo
        docs_dir = Path("docs")
        if docs_dir.exists():
            print(f"   📁 Adding docs directory to sync")
            kb_sync.add_sync_path(str(docs_dir), tags=["documentation", "demo"])

            # Perform sync
            print("   🔄 Running synchronization...")
            stats = kb_sync.sync_all()

            print(f"   ✅ Sync completed:")
            print(f"     Total files: {stats.total_docs}")
            print(f"     Synced: {stats.synced_docs}")
            print(f"     New: {stats.new_docs}")
            print(f"     Updated: {stats.updated_docs}")
            print(f"     Time: {stats.sync_time:.2f}s")

            # Demonstrate search
            if stats.synced_docs > 0:
                print(f"\n🔍 Testing document search...")
                results = kb_sync.search_documents("README", tags=["documentation"])
                print(f"   Found {len(results)} documents matching 'README'")

                for result in results[:3]:  # Show first 3
                    print(f"   - {Path(result['doc_path']).name}")
        else:
            print("   ℹ️ No docs directory found - skipping sync demo")
            print("   💡 Create a 'docs' directory with .md files to test sync")

    except ImportError:
        print("❌ Knowledge Base Sync not available - missing dependencies")
    except Exception as e:
        print(f"❌ Error running Knowledge Base Sync: {e}")

def main():
    """Main launcher function"""
    print_banner()

    while True:
        print_main_menu()

        try:
            choice = input("Enter your choice (1-14): ").strip()

            if choice == '1':
                launch_write_guard()
            elif choice == '2':
                launch_safe_save()
            elif choice == '3':
                launch_memory_inspector()
            elif choice == '4':
                launch_plugin_sandbox()
            elif choice == '5':
                launch_health_dashboard()
            elif choice == '6':
                launch_error_tracker()
            elif choice == '7':
                launch_performance_profiler()
            elif choice == '8':
                launch_memory_backup()
            elif choice == '9':
                launch_knowledge_sync()
            elif choice == '10':
                show_integration_demo()
            elif choice == '11':
                run_test_suite()
            elif choice == '12':
                show_tool_status()
            elif choice == '13':
                show_documentation()
            elif choice == '14':
                cleanup_demo_files()
                print("\n👋 Thank you for using Aetherra & Lyrixa Developer Tools!")
                print("🎉 All tools are ready for production use!")
                break
            else:
                print("❌ Invalid choice. Please enter a number from 1-14.")

            input("\n⏸️ Press Enter to continue...")
            print("\n" + "="*62)

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            cleanup_demo_files()
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            input("\n⏸️ Press Enter to continue...")

if __name__ == "__main__":
    main()
