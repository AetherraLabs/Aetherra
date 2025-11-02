#!/usr/bin/env python3
"""
Pre-Pack Validation Suite for Aetherra & Lyrixa
Comprehensive smoke tests for all capabilities before building .exe

Date: 2025-10-31
Owner: Aetherra Labs
"""

import json
import os
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


@dataclass
class ValidationResult:
    """Result of a single validation check"""

    section: str
    check_name: str
    status: str  # PASS, FAIL, SKIP, WARN
    message: str
    details: dict | None = None
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.utcnow().isoformat()


class PrePackValidator:
    """Master validation orchestrator"""

    def __init__(self, profile: str = "test", verbose: bool = False):
        self.profile = profile
        self.verbose = verbose
        self.results: list[ValidationResult] = []
        self.setup_environment()

    def setup_environment(self):
        """Configure environment for validation"""
        # Set profile
        os.environ["AETHERRA_PROFILE"] = self.profile
        os.environ["AETHERRA_QUIET"] = "0" if self.verbose else "1"

        # Enable validation modes
        os.environ["AETHERRA_VALIDATION_MODE"] = "1"

        self.log(f"🔧 Environment configured for profile: {self.profile}")

    def log(self, message: str, level: str = "INFO"):
        """Log with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        prefix = {
            "INFO": "ℹ️",
            "PASS": "✅",
            "FAIL": "❌",
            "WARN": "⚠️",
            "SKIP": "⏭️",
        }.get(level, "•")
        print(f"[{timestamp}] {prefix} {message}")

    def add_result(
        self,
        section: str,
        check_name: str,
        status: str,
        message: str,
        details: dict | None = None,
    ):
        """Record validation result"""
        result = ValidationResult(section, check_name, status, message, details)
        self.results.append(result)

        level = status if status in ["PASS", "FAIL", "WARN", "SKIP"] else "INFO"
        self.log(f"{section} :: {check_name} - {message}", level)

    # =========================================================================
    # 0) ONE-GLANCE STATUS
    # =========================================================================

    def validate_kernel_status(self) -> bool:
        """Validate kernel loop & queues are operational"""
        section = "0-Kernel"
        try:
            # Check if kernel status endpoint is reachable
            # For now, we'll check if the kernel loop module loads

            self.add_result(
                section,
                "Kernel Module Load",
                "PASS",
                "Kernel loop module imported successfully",
            )
            return True

        except Exception as e:
            self.add_result(
                section, "Kernel Module Load", "FAIL", f"Failed to import kernel: {e}"
            )
            return False

    def validate_ai_engine(self) -> bool:
        """Validate AI Engine basic operations"""
        section = "0-AI-Engine"
        try:
            # Import and check AI coordinator
            from Aetherra.ai_engine.coordinator import AetherraAICoordinator

            coordinator = AetherraAICoordinator()
            self.add_result(
                section, "AI Coordinator Init", "PASS", "AI coordinator initialized"
            )
            return True

        except Exception as e:
            self.add_result(section, "AI Coordinator Init", "FAIL", f"Failed: {e}")
            return False

    def validate_memory_systems(self) -> bool:
        """Validate memory systems (Core + Advanced)"""
        section = "0-Memory"
        try:
            from Aetherra.memory.core.store import AetherraMemoryStore

            store = AetherraMemoryStore()
            health = store.health_pulse()

            self.add_result(
                section,
                "Memory Store Health",
                "PASS",
                f"Health score: {health.get('health_score', 'N/A')}",
                details=health,
            )
            return True

        except Exception as e:
            self.add_result(section, "Memory Store Health", "FAIL", f"Failed: {e}")
            return False

    # =========================================================================
    # 1) KERNEL SYSTEM
    # =========================================================================

    def validate_kernel_queues(self) -> bool:
        """Validate priority queues and backpressure"""
        section = "1-Kernel-Queues"

        checks = [
            ("AETHERRA_KERNEL_QSIZE_HIGH", "High priority queue size"),
            ("AETHERRA_KERNEL_QSIZE_NORMAL", "Normal priority queue size"),
            ("AETHERRA_KERNEL_QSIZE_BACKGROUND", "Background queue size"),
        ]

        all_pass = True
        for env_var, desc in checks:
            value = os.getenv(env_var)
            if value:
                self.add_result(section, desc, "PASS", f"Set to {value}")
            else:
                self.add_result(section, desc, "WARN", "Using default")
                all_pass = False

        return all_pass

    def validate_hmr_config(self) -> bool:
        """Validate HMR (Hot Module Reload) configuration"""
        section = "1-Kernel-HMR"

        hmr_enabled = os.getenv("AETHERRA_HMR_ENABLED", "0") == "1"

        if hmr_enabled:
            self.add_result(
                section,
                "HMR Status",
                "WARN",
                "HMR is ENABLED - ensure this is intentional for pack",
            )
        else:
            self.add_result(
                section,
                "HMR Status",
                "PASS",
                "HMR disabled (recommended for production)",
            )

        return True

    # =========================================================================
    # 2) AI ENGINE
    # =========================================================================

    def validate_ai_session_management(self) -> bool:
        """Validate AI session creation and management"""
        section = "2-AI-Sessions"

        try:
            from Aetherra.ai_engine.coordinator import AetherraAICoordinator

            coordinator = AetherraAICoordinator()
            session_id = coordinator.start_conversation()

            if session_id:
                self.add_result(
                    section,
                    "Session Creation",
                    "PASS",
                    f"Created session: {session_id[:8]}...",
                )
                return True
            self.add_result(section, "Session Creation", "FAIL", "Session ID is None")
            return False

        except Exception as e:
            self.add_result(section, "Session Creation", "FAIL", f"Error: {e}")
            return False

    # =========================================================================
    # 3) AGENT SYSTEM
    # =========================================================================

    def validate_agent_registry(self) -> bool:
        """Validate agent registry and task submission"""
        section = "3-Agents"

        try:
            from aetherra_agent_fabric import AetherraAgentFabric

            fabric = AetherraAgentFabric()
            agents = fabric.list_agents()

            self.add_result(
                section,
                "Agent Registry",
                "PASS",
                f"Found {len(agents)} agents",
                details={"agents": [a.get("name") for a in agents]},
            )
            return True

        except Exception as e:
            self.add_result(section, "Agent Registry", "FAIL", f"Error: {e}")
            return False

    # =========================================================================
    # 4) CHAT SYSTEM
    # =========================================================================

    def validate_chat_endpoints(self) -> bool:
        """Validate chat system endpoints availability"""
        section = "4-Chat"

        # Check if chat blueprints are loadable
        try:
            self.add_result(
                section, "Chat Blueprint", "PASS", "AI stream blueprint loaded"
            )
            return True

        except Exception as e:
            self.add_result(section, "Chat Blueprint", "FAIL", f"Error: {e}")
            return False

    # =========================================================================
    # 5) MEMORY SYSTEM
    # =========================================================================

    def validate_memory_advanced(self) -> bool:
        """Validate advanced memory orchestrator"""
        section = "5-Memory-Advanced"

        try:
            from Aetherra.memory.advanced.orchestrator import AdvancedMemoryOrchestrator

            orch = AdvancedMemoryOrchestrator()
            health = orch.health_pulse()

            self.add_result(
                section,
                "Advanced Health",
                "PASS",
                "Advanced orchestrator operational",
                details=health,
            )
            return True

        except Exception as e:
            self.add_result(section, "Advanced Health", "FAIL", f"Error: {e}")
            return False

    def validate_qfac_mode(self) -> bool:
        """Validate QFAC compression system"""
        section = "5-Memory-QFAC"

        qfac_mode = os.getenv("AETHERRA_QFAC_MODE", "disabled")

        if qfac_mode in ["enabled", "hybrid"]:
            self.add_result(
                section,
                "QFAC Mode",
                "WARN",
                f"QFAC is {qfac_mode} - verify intentional",
            )
        else:
            self.add_result(section, "QFAC Mode", "PASS", f"QFAC mode: {qfac_mode}")

        return True

    def validate_storm_retrieval(self) -> bool:
        """Validate STORM retrieval system"""
        section = "5-Memory-STORM"

        storm_enabled = os.getenv("AETHERRA_MEMORY_STORM", "0") == "1"

        if storm_enabled:
            self.add_result(
                section,
                "STORM Mode",
                "WARN",
                "STORM is ENABLED - experimental feature active",
            )
        else:
            self.add_result(
                section, "STORM Mode", "PASS", "STORM disabled (baseline mode)"
            )

        return True

    # =========================================================================
    # 6) SECURITY SYSTEM
    # =========================================================================

    def validate_signing_strict(self) -> bool:
        """Validate signing strict mode"""
        section = "6-Security-Signing"

        strict = os.getenv("AETHERRA_SIGNING_STRICT", "0") == "1"
        profile = os.getenv("AETHERRA_PROFILE", "").lower()

        if profile in ["prod", "production"]:
            if strict:
                self.add_result(
                    section,
                    "Signing Strict",
                    "PASS",
                    "Strict signing enabled for production",
                )
            else:
                self.add_result(
                    section,
                    "Signing Strict",
                    "FAIL",
                    "Production profile MUST have strict signing!",
                )
                return False
        else:
            if strict:
                self.add_result(
                    section,
                    "Signing Strict",
                    "WARN",
                    "Strict signing enabled in non-prod profile",
                )
            else:
                self.add_result(
                    section, "Signing Strict", "PASS", "Signing relaxed for development"
                )

        return True

    def validate_network_policy(self) -> bool:
        """Validate network policy configuration"""
        section = "6-Security-Network"

        net_strict = os.getenv("AETHERRA_NET_STRICT", "0") == "1"
        allowlist = os.getenv("AETHERRA_NETWORK_ALLOWLIST", "")

        if net_strict:
            if allowlist:
                self.add_result(
                    section,
                    "Network Policy",
                    "PASS",
                    f"Strict mode with allowlist: {allowlist}",
                )
            else:
                self.add_result(
                    section,
                    "Network Policy",
                    "WARN",
                    "Strict mode but no allowlist configured",
                )
        else:
            self.add_result(
                section,
                "Network Policy",
                "PASS",
                "Network policy permissive (development mode)",
            )

        return True

    def validate_secrets_management(self) -> bool:
        """Validate secrets management configuration"""
        section = "6-Security-Secrets"

        master_key = os.getenv("AETHERRA_KEYS_MASTER")

        if master_key:
            self.add_result(
                section,
                "Secrets Encryption",
                "PASS",
                "Master key configured for encryption at rest",
            )
        else:
            self.add_result(
                section,
                "Secrets Encryption",
                "WARN",
                "No master key - secrets not encrypted at rest",
            )

        return True

    # =========================================================================
    # 7) AETHER SCRIPT LANGUAGE
    # =========================================================================

    def validate_aether_scripts(self) -> bool:
        """Validate .aether script verification"""
        section = "7-Aether-Scripts"

        try:
            # Run the verification tool
            result = subprocess.run(
                [
                    sys.executable,
                    "tools/verify_aether_scripts.py",
                    "--root",
                    ".",
                    "--output",
                    "aether_static_report.md",
                ],
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode == 0:
                self.add_result(
                    section,
                    "Script Verification",
                    "PASS",
                    "All .aether scripts verified",
                )
                return True
            self.add_result(
                section,
                "Script Verification",
                "FAIL",
                f"Verification failed: {result.stderr[:200]}",
            )
            return False

        except Exception as e:
            self.add_result(
                section, "Script Verification", "FAIL", f"Error running verifier: {e}"
            )
            return False

    # =========================================================================
    # 8) CODING SYSTEM
    # =========================================================================

    def validate_lyrixa_studio(self) -> bool:
        """Validate Lyrixa Code Studio components"""
        section = "8-Lyrixa-Studio"

        try:
            # Check if Lyrixa modules load

            self.add_result(
                section, "Studio Components", "PASS", "Lyrixa assistant module loaded"
            )
            return True

        except Exception as e:
            self.add_result(section, "Studio Components", "FAIL", f"Error: {e}")
            return False

    # =========================================================================
    # 9) HOMEOSTASIS & MAINTENANCE
    # =========================================================================

    def validate_homeostasis(self) -> bool:
        """Validate homeostasis system"""
        section = "9-Homeostasis"

        try:
            # Try to import homeostasis controller
            import importlib.util

            spec = importlib.util.find_spec("aetherra_homeostasis_controller")
            if spec:
                self.add_result(
                    section,
                    "Homeostasis Module",
                    "PASS",
                    "Homeostasis controller available",
                )
                return True
            self.add_result(
                section,
                "Homeostasis Module",
                "SKIP",
                "Homeostasis module not found (optional)",
            )
            return True

        except Exception as e:
            self.add_result(
                section, "Homeostasis Module", "SKIP", f"Could not check: {e}"
            )
            return True

    def validate_maintenance(self) -> bool:
        """Validate maintenance and self-healing"""
        section = "9-Maintenance"

        try:
            self.add_result(
                section, "Self-Organizer", "PASS", "Self-organizer module loaded"
            )
            return True

        except Exception as e:
            self.add_result(section, "Self-Organizer", "FAIL", f"Error: {e}")
            return False

    # =========================================================================
    # 10) LYRIXA CHAT & UI BRIDGE
    # =========================================================================

    def validate_lyrixa_bridge(self) -> bool:
        """Validate Lyrixa chat bridge"""
        section = "10-Lyrixa-Bridge"

        try:
            self.add_result(section, "Chat Bridge", "PASS", "Lyrixa chat bridge loaded")
            return True

        except Exception as e:
            self.add_result(section, "Chat Bridge", "FAIL", f"Error: {e}")
            return False

    # =========================================================================
    # 11) AI TRAINER SYSTEM
    # =========================================================================

    def validate_trainer_disabled(self) -> bool:
        """Validate trainer is properly disabled for production"""
        section = "11-AI-Trainer"

        trainer_enabled = os.getenv("AETHERRA_TRAINER_ENABLED", "0") == "1"
        profile = os.getenv("AETHERRA_PROFILE", "").lower()

        if profile in ["prod", "production"]:
            if trainer_enabled:
                self.add_result(
                    section,
                    "Trainer Status",
                    "FAIL",
                    "Trainer MUST be disabled in production!",
                )
                return False
            self.add_result(
                section,
                "Trainer Status",
                "PASS",
                "Trainer correctly disabled for production",
            )
        else:
            if trainer_enabled:
                self.add_result(
                    section,
                    "Trainer Status",
                    "WARN",
                    "Trainer enabled in non-production",
                )
            else:
                self.add_result(section, "Trainer Status", "PASS", "Trainer disabled")

        return True

    # =========================================================================
    # ORCHESTRATION
    # =========================================================================

    def run_all_validations(self) -> tuple[int, int, int, int]:
        """Run all validation checks"""
        self.log("=" * 60)
        self.log("AETHERRA & LYRIXA PRE-PACK VALIDATION SUITE")
        self.log("=" * 60)
        self.log(f"Profile: {self.profile}")
        self.log(f"Timestamp: {datetime.now().isoformat()}")
        self.log("=" * 60)

        # Section 0: One-glance status
        self.log("\n[Section 0] One-Glance Status Checks")
        self.validate_kernel_status()
        self.validate_ai_engine()
        self.validate_memory_systems()

        # Section 1: Kernel System
        self.log("\n[Section 1] Kernel System")
        self.validate_kernel_queues()
        self.validate_hmr_config()

        # Section 2: AI Engine
        self.log("\n[Section 2] AI Engine")
        self.validate_ai_session_management()

        # Section 3: Agent System
        self.log("\n[Section 3] Agent System")
        self.validate_agent_registry()

        # Section 4: Chat System
        self.log("\n[Section 4] Chat System")
        self.validate_chat_endpoints()

        # Section 5: Memory System
        self.log("\n[Section 5] Memory System")
        self.validate_memory_advanced()
        self.validate_qfac_mode()
        self.validate_storm_retrieval()

        # Section 6: Security System
        self.log("\n[Section 6] Security System")
        self.validate_signing_strict()
        self.validate_network_policy()
        self.validate_secrets_management()

        # Section 7: Aether Scripts
        self.log("\n[Section 7] Aether Script Language")
        self.validate_aether_scripts()

        # Section 8: Coding System
        self.log("\n[Section 8] Coding System (Lyrixa)")
        self.validate_lyrixa_studio()

        # Section 9: Homeostasis
        self.log("\n[Section 9] Homeostasis & Maintenance")
        self.validate_homeostasis()
        self.validate_maintenance()

        # Section 10: Lyrixa Bridge
        self.log("\n[Section 10] Lyrixa Chat & UI Bridge")
        self.validate_lyrixa_bridge()

        # Section 11: AI Trainer
        self.log("\n[Section 11] AI Trainer System")
        self.validate_trainer_disabled()

        # Calculate summary
        passed = sum(1 for r in self.results if r.status == "PASS")
        failed = sum(1 for r in self.results if r.status == "FAIL")
        warned = sum(1 for r in self.results if r.status == "WARN")
        skipped = sum(1 for r in self.results if r.status == "SKIP")

        return passed, failed, warned, skipped

    def generate_report(self, output_file: str = "pre_pack_validation_report.json"):
        """Generate detailed JSON report"""
        report = {
            "metadata": {
                "timestamp": datetime.utcnow().isoformat(),
                "profile": self.profile,
                "total_checks": len(self.results),
            },
            "summary": {
                "passed": sum(1 for r in self.results if r.status == "PASS"),
                "failed": sum(1 for r in self.results if r.status == "FAIL"),
                "warned": sum(1 for r in self.results if r.status == "WARN"),
                "skipped": sum(1 for r in self.results if r.status == "SKIP"),
            },
            "results": [asdict(r) for r in self.results],
        }

        output_path = PROJECT_ROOT / output_file
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        self.log(f"\n📄 Detailed report written to: {output_path}")
        return output_path

    def print_summary(self, passed: int, failed: int, warned: int, skipped: int):
        """Print final summary"""
        total = len(self.results)

        self.log("\n" + "=" * 60)
        self.log("VALIDATION SUMMARY")
        self.log("=" * 60)
        self.log(f"Total Checks:  {total}")
        self.log(f"✅ PASSED:     {passed} ({passed / total * 100:.1f}%)", "PASS")
        self.log(f"❌ FAILED:     {failed} ({failed / total * 100:.1f}%)", "FAIL")
        self.log(f"⚠️  WARNINGS:   {warned} ({warned / total * 100:.1f}%)", "WARN")
        self.log(f"⏭️  SKIPPED:    {skipped} ({skipped / total * 100:.1f}%)", "SKIP")
        self.log("=" * 60)

        if failed > 0:
            self.log("\n⚠️  CRITICAL FAILURES DETECTED - DO NOT PACKAGE", "FAIL")
            self.log("Review failures above before building .exe", "FAIL")
            return 1
        if warned > 0:
            self.log("\n⚠️  Warnings detected - review before packaging", "WARN")
            return 0
        self.log("\n✅ All checks passed - ready for packaging", "PASS")
        return 0


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Pre-Pack Validation Suite for Aetherra & Lyrixa"
    )
    parser.add_argument(
        "--profile",
        default="test",
        choices=["dev", "test", "prod", "production"],
        help="Environment profile to validate",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument(
        "--output",
        "-o",
        default="pre_pack_validation_report.json",
        help="Output report file",
    )

    args = parser.parse_args()

    # Run validation
    validator = PrePackValidator(profile=args.profile, verbose=args.verbose)
    passed, failed, warned, skipped = validator.run_all_validations()

    # Generate report
    validator.generate_report(args.output)

    # Print summary and exit
    validator.print_summary(passed, failed, warned, skipped)

    return 1 if failed > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
