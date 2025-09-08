#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
🌌 Quantum Dashboard Launcher
============================

Launch the quantum memory monitoring web dashboard as part of the Aetherra ecosystem.
This script integrates with existing Aetherra components and provides a unified
interface for monitoring quantum-enhanced memory operations.

Usage:
    python quantum_dashboard_launcher.py [--port 8080] [--mode web]
"""

import argparse
import asyncio
import sys
from pathlib import Path

# Add Aetherra to path
aetherra_path = Path(__file__).parent / "Aetherra"
sys.path.insert(0, str(aetherra_path))

try:
    # ARCHITECTURAL FIX: Removed Lyrixa import -     from lyrixa.memory.quantum_web_dashboard import QuantumWebDashboard, WEB_AVAILABLE
    # ARCHITECTURAL FIX: Removed Lyrixa import -     from lyrixa.memory.quantum_memory_integration import create_quantum_enhanced_memory_engine
    QUANTUM_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Quantum components not available: {e}")
    QUANTUM_AVAILABLE = False

try:
    # ARCHITECTURAL FIX: Removed Lyrixa import -     from lyrixa.memory.qfac_dashboard import QFACDashboard
    QFAC_AVAILABLE = True
except ImportError:
    QFAC_AVAILABLE = False


async def launch_quantum_dashboard(port: int = 8080, mode: str = "web"):
    """Launch the quantum dashboard in specified mode"""

    print("🌌 Aetherra Quantum Dashboard Launcher")
    print("=" * 50)

    if mode == "web" and not WEB_AVAILABLE:
        print("❌ Web mode not available - missing aiohttp dependency")
        print("💡 Install with: pip install aiohttp")
        mode = "text"

    if mode == "web":
        print("🚀 Starting Quantum Web Dashboard...")

        # Create quantum-enhanced memory engine
        quantum_engine = None
        if QUANTUM_AVAILABLE:
            try:
                quantum_engine = create_quantum_enhanced_memory_engine()

                # Add some initial test data for demonstration
                print("📝 Adding initial test memories...")
                await quantum_engine.remember(
                    "Quantum superposition enables parallel memory processing",
                    tags=["quantum", "superposition", "memory"],
                    category="quantum_concepts",
                )
                await quantum_engine.remember(
                    "Quantum coherence is essential for stable memory operations",
                    tags=["quantum", "coherence", "stability"],
                    category="quantum_concepts",
                )
                await quantum_engine.remember(
                    "Aetherra integrates classical and quantum memory systems",
                    tags=["aetherra", "integration", "hybrid"],
                    category="system_architecture",
                )

                print("[OK] Quantum memory engine initialized with test data")

                # Check quantum system status
                status = quantum_engine.get_quantum_system_status()
                print("🔍 Quantum System Status:")
                print(f"   • Quantum Available: {status['quantum_available']}")
                print(f"   • Backend: {status['configuration']['quantum_backend']}")
                print(f"   • Max Qubits: {status['configuration']['max_qubits']}")
                print(f"   • Quantum States: {status['quantum_states_count']}")

            except Exception as e:
                print(f"⚠️ Failed to initialize quantum engine: {e}")
                print("🔄 Dashboard will run with mock data")
        else:
            print("⚠️ Quantum integration not available - using mock data")

        # Start web dashboard
        try:
            dashboard = QuantumWebDashboard(quantum_engine, port)
            dashboard_url = await dashboard.start()

            print("\n🎉 SUCCESS!")
            print(f"🌐 Quantum Dashboard URL: {dashboard_url}")
            print("📱 Features Available:")
            print("   • ⚛️  Real-time quantum coherence monitoring")
            print("   • 📊 Quantum vs classical performance comparison")
            print("   • 🔗 Interactive quantum circuit visualization")
            print("   • 🚨 System health alerts and recommendations")
            print("   • 📈 Live performance metrics and statistics")

            if quantum_engine:
                print("\n🧪 Try these actions:")
                print("   • Store new memories to see quantum encoding in action")
                print("   • Query memories to test quantum-enhanced recall")
                print("   • Monitor coherence levels and error correction")

            print("\n⌨️  Press Ctrl+C to stop the dashboard")

            # Keep dashboard running
            try:
                while True:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                print("\n🛑 Shutting down dashboard...")
                await dashboard.stop()
                print("[OK] Dashboard stopped successfully")

        except Exception as e:
            print(f"❌ Failed to start web dashboard: {e}")
            return False

    elif mode == "integrated" and QFAC_AVAILABLE:
        print("🎯 Starting Integrated QFAC Dashboard with Quantum Support...")

        # Use the existing QFAC dashboard with quantum integration
        try:
            # We'll need to create a mock analyzer for the QFAC dashboard
            # ARCHITECTURAL FIX: Removed Lyrixa import -             from lyrixa.memory.compression_analyzer import MemoryCompressionAnalyzer

            analyzer = MemoryCompressionAnalyzer()
            dashboard = QFACDashboard(analyzer)

            await dashboard.start_dashboard(mode="web")

        except Exception as e:
            print(f"❌ Failed to start integrated dashboard: {e}")
            return False

    else:
        print("📟 Text mode dashboard not implemented in this launcher")
        print("💡 Use the full QFAC dashboard for text mode")
        return False

    return True


def main():
    """Main launcher function"""
    parser = argparse.ArgumentParser(
        description="Launch Aetherra Quantum Memory Dashboard"
    )
    parser.add_argument(
        "--port", type=int, default=8080, help="Port for web dashboard (default: 8080)"
    )
    parser.add_argument(
        "--mode",
        choices=["web", "integrated", "text"],
        default="web",
        help="Dashboard mode (default: web)",
    )
    parser.add_argument(
        "--test-data",
        action="store_true",
        help="Add additional test data for demonstration",
    )

    args = parser.parse_args()

    # Check dependencies
    missing_deps = []
    if args.mode == "web" and not WEB_AVAILABLE:
        missing_deps.append("aiohttp (for web interface)")
    if not QUANTUM_AVAILABLE:
        missing_deps.append("quantum components")

    if missing_deps:
        print("⚠️ Missing dependencies:")
        for dep in missing_deps:
            print(f"   • {dep}")
        print("\n💡 Dashboard will run in compatibility mode")

    # Run dashboard
    try:
        success = asyncio.run(launch_quantum_dashboard(args.port, args.mode))
        if success:
            print("🎉 Dashboard session completed successfully")
        else:
            print("❌ Dashboard failed to start")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Dashboard launcher interrupted by user")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
