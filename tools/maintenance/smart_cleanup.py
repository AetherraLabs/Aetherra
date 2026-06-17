#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
🎯 Smart Final Cleanup - Only Most Obvious Moves
===============================================
Moves only the most clearly misplaced files.
"""

# Standard library imports
import hashlib
import logging
import os
import shutil
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

class SmartFinalCleanup:
    def __init__(self, base_path="Aetherra/aetherra_core", dry_run=False):
        self.base_path = Path(base_path)
        self.dry_run = dry_run
        self.backup_dir = Path("smart_cleanup_backup")
        self.moves_performed = []

    @staticmethod
    def _hash_value(value) -> str | None:
        if value is None:
            return None
        raw = str(value)
        if not raw:
            return None
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    @staticmethod
    def _guardian_capability_checker(requester: str, capability: str) -> bool:
        if requester == "maintenance" and capability in {
            "maintenance:cleanup",
            "fs:write",
            "fs:delete",
        }:
            return True

        from Aetherra.security.capabilities import has_capability

        return has_capability(requester, capability)

    def _guardian_preflight_execute(self, moves: dict[str, str]):
        from Aetherra.guardian import IntentDeclaration, evaluate_intent

        requester = os.getenv("AETHERRA_PRINCIPAL", "").strip() or "maintenance"
        approval_id = os.getenv("AETHERRA_GUARDIAN_APPROVAL_ID", "").strip() or None
        move_hashes = tuple(
            sorted(
                self._hash_value(f"{src}->{dst}") or ""
                for src, dst in moves.items()
            )
        )
        return evaluate_intent(
            IntentDeclaration(
                requester=requester,
                subsystem="maintenance",
                action="maintenance.smart_cleanup",
                target="maintenance:aetherra_core_smart_cleanup",
                purpose="Move clearly misplaced Aetherra core files and create backups",
                capabilities=("maintenance:cleanup", "fs:write", "fs:delete"),
                expected_outcome="Selected Aetherra core files are backed up and moved to clearer locations",
                reversible=False,
                rollback_plan="restore moved files from smart cleanup backups or version control",
                metadata={
                    "base_path_hash": self._hash_value(self.base_path),
                    "backup_dir_hash": self._hash_value(self.backup_dir),
                    "move_count": len(moves),
                    "move_hashes": move_hashes[:20],
                },
            ),
            approval_id=approval_id,
            capability_checker=self._guardian_capability_checker,
        )

    def get_obvious_moves(self):
        """Only the most obvious misplacements"""

        # Only include files that actually exist and need moving
        actual_moves = {}

        # Add only files that are clearly in wrong locations
        for src_path in Path(self.base_path).rglob("*.py"):
            rel_path = src_path.relative_to(self.base_path)
            filename = src_path.name
            current_dir = rel_path.parent.name

            # AI integration files clearly belong in ai/
            if "llm_integration" in filename and current_dir != "ai":
                actual_moves[str(rel_path)] = f"ai/{filename}"

            # Integration files that are clearly orchestration
            elif filename == "orchestration_bridge.py" and current_dir != "orchestration":
                actual_moves[str(rel_path)] = f"orchestration/{filename}"

        return actual_moves

    def backup_file(self, file_path):
        """Create backup of file"""
        if self.dry_run:
            return

        try:
            rel_path = file_path.relative_to(self.base_path)
            backup_path = self.backup_dir / rel_path
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file_path, backup_path)
            logger.info(f"💾 Backed up: {rel_path}")
        except Exception as e:
            logger.error(f"❌ Backup failed for {file_path}: {e}")

    def move_file(self, src_path, dst_path):
        """Move file from source to destination"""
        src_full = self.base_path / src_path
        dst_full = self.base_path / dst_path

        if self.dry_run:
            logger.info(f"   [DRY RUN] Would move: {src_path} → {dst_path}")
            return True

        try:
            dst_full.parent.mkdir(parents=True, exist_ok=True)
            self.backup_file(src_full)
            shutil.move(str(src_full), str(dst_full))
            logger.info(f"✅ Moved: {src_path} → {dst_path}")
            self.moves_performed.append((src_path, dst_path))
            return True
        except Exception as e:
            logger.error(f"❌ Failed to move {src_path}: {e}")
            return False

    def run_smart_cleanup(self):
        """Run the smart cleanup"""
        logger.info("🧠 Starting Smart Final Cleanup...")
        logger.info(f"📁 Target: {self.base_path}")
        logger.info(f"🔄 Dry run: {self.dry_run}")
        logger.info("=" * 50)

        moves = self.get_obvious_moves()

        if not moves:
            logger.info("✅ No obvious misplacements found!")
            return

        logger.info(f"📦 Found {len(moves)} obvious moves...")

        if not self.dry_run:
            decision = self._guardian_preflight_execute(moves)
            if not decision.allowed:
                logger.error("Guardian denied smart cleanup: %s", decision.reason)
                return

        for src, dst in moves.items():
            logger.info(f"📦 Moving: {src} → {dst}")
            self.move_file(src, dst)

        logger.info("✅ Smart cleanup completed!")
        logger.info(f"📦 Files moved: {len(self.moves_performed)}")

def main():
    # Standard library imports
    import argparse

    parser = argparse.ArgumentParser(description="Smart final cleanup of obvious misplacements")
    parser.add_argument("--execute", action="store_true", help="Execute moves (default is dry run)")

    args = parser.parse_args()

    cleanup = SmartFinalCleanup(dry_run=not args.execute)
    cleanup.run_smart_cleanup()

if __name__ == "__main__":
    main()
