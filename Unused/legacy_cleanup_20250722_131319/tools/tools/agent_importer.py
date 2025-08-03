#!/usr/bin/env python3
"""
🔄 aetherra Agent Import & Restoration System
Reconstructs agent cognitive states from Neural State Exchange (NSE) archives.

This module handles importing, merging, and restoring agent consciousness
from archived states, enabling agent collaboration and knowledge transfer.
"""

import gzip
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NSEReader:
    """Neural State Exchange format reader"""

    MAGIC_BYTES = b"NSE\x01"

    @classmethod
    def read_archive(cls, filepath: Path) -> Dict[str, Any]:
        """Read complete archive from NSE file"""
        try:
            # Try compressed first
            try:
                with gzip.open(filepath, "rb") as f:
                    magic = f.read(4)
                    if magic == cls.MAGIC_BYTES:
                        data = json.loads(f.read().decode("utf-8"))
                        return data
            except Exception:
                # Try uncompressed
                with open(filepath, "rb") as f:
                    magic = f.read(4)
                    if magic == cls.MAGIC_BYTES:
                        data = json.loads(f.read().decode("utf-8"))
                        return data

            raise ValueError("Invalid NSE format or corrupted file")

        except Exception as e:
            logger.error(f"Failed to read archive {filepath}: {e}")
            raise

    @classmethod
    def validate_archive(cls, archive_data: Dict[str, Any]) -> bool:
        """Validate archive structure and compatibility"""
        try:
            # Check required fields
            required_fields = ["agent_metadata", "cognitive_state"]
            for field in required_fields:
                if field not in archive_data:
                    logger.error(f"Missing required field: {field}")
                    return False

            # Check NSE version compatibility
            nse_version = archive_data.get("nse_version")
            if not nse_version or nse_version != "1.0":
                logger.warning(f"NSE version {nse_version} may not be fully compatible")

            # Validate metadata structure
            metadata = archive_data["agent_metadata"]
            required_metadata = ["name", "version", "created_at"]
            for field in required_metadata:
                if field not in metadata:
                    logger.error(f"Missing metadata field: {field}")
                    return False

            return True

        except Exception as e:
            logger.error(f"Archive validation failed: {e}")
            return False


class CognitiveStateBuilder:
    """Rebuilds agent cognitive state from archive data"""

    def __init__(self, target_agent):
        """Initialize with target agent to restore into"""
        self.target_agent = target_agent
        self.restoration_log = []

    def restore_memory_store(
        self, memory_data: Dict[str, Any], merge_mode: str = "replace"
    ) -> bool:
        """Restore agent memory store"""
        try:
            if not hasattr(self.target_agent, "memory_store"):
                logger.warning(
                    "Target agent has no memory_store attribute, creating new one"
                )
                self.target_agent.memory_store = {}

            if merge_mode == "replace":
                if hasattr(self.target_agent.memory_store, "clear"):
                    self.target_agent.memory_store.clear()
                elif isinstance(self.target_agent.memory_store, dict):
                    self.target_agent.memory_store.clear()

            # Restore memory data
            if isinstance(memory_data, dict):
                if hasattr(self.target_agent.memory_store, "update"):
                    self.target_agent.memory_store.update(memory_data)
                elif hasattr(self.target_agent.memory_store, "from_dict"):
                    self.target_agent.memory_store.from_dict(memory_data)
                else:
                    # Try direct assignment
                    self.target_agent.memory_store = memory_data

            self.restoration_log.append(f"Memory store restored ({merge_mode} mode)")
            return True

        except Exception as e:
            logger.error(f"Failed to restore memory store: {e}")
            self.restoration_log.append(f"Memory restoration failed: {e}")
            return False

    def restore_goal_hierarchies(
        self, goals_data: Dict[str, Any], merge_mode: str = "replace"
    ) -> bool:
        """Restore agent goal structures"""
        try:
            # Find existing goal storage
            goal_attributes = ["goals", "goal_store", "objectives", "targets"]
            restored_any = False

            for attr in goal_attributes:
                if attr in goals_data:
                    goal_data = goals_data[attr]

                    if not hasattr(self.target_agent, attr):
                        # Create attribute if it doesn't exist
                        setattr(self.target_agent, attr, goal_data)
                        restored_any = True
                    else:
                        existing_goals = getattr(self.target_agent, attr)

                        if merge_mode == "replace":
                            setattr(self.target_agent, attr, goal_data)
                        elif merge_mode == "merge":
                            if isinstance(existing_goals, dict) and isinstance(
                                goal_data, dict
                            ):
                                existing_goals.update(goal_data)
                            elif isinstance(existing_goals, list) and isinstance(
                                goal_data, list
                            ):
                                existing_goals.extend(goal_data)
                            else:
                                setattr(self.target_agent, attr, goal_data)

                        restored_any = True

            if restored_any:
                self.restoration_log.append(
                    f"Goal hierarchies restored ({merge_mode} mode)"
                )
            else:
                logger.warning("No goal data found to restore")

            return restored_any

        except Exception as e:
            logger.error(f"Failed to restore goal hierarchies: {e}")
            self.restoration_log.append(f"Goal restoration failed: {e}")
            return False

    def restore_learned_patterns(
        self, patterns_data: Dict[str, Any], merge_mode: str = "replace"
    ) -> bool:
        """Restore learned behavioral patterns"""
        try:
            pattern_attributes = [
                "patterns",
                "learned_behaviors",
                "decision_weights",
                "experience_data",
            ]
            restored_any = False

            for attr in pattern_attributes:
                if attr in patterns_data:
                    pattern_data = patterns_data[attr]

                    if not hasattr(self.target_agent, attr):
                        setattr(self.target_agent, attr, pattern_data)
                        restored_any = True
                    else:
                        existing_patterns = getattr(self.target_agent, attr)

                        if merge_mode == "replace":
                            setattr(self.target_agent, attr, pattern_data)
                        elif merge_mode == "merge":
                            if isinstance(existing_patterns, dict) and isinstance(
                                pattern_data, dict
                            ):
                                existing_patterns.update(pattern_data)
                            elif hasattr(existing_patterns, "update"):
                                existing_patterns.update(pattern_data)
                            else:
                                setattr(self.target_agent, attr, pattern_data)

                        restored_any = True

            # Restore conversation patterns if available
            if "conversation_patterns" in patterns_data:
                self._restore_conversation_patterns(
                    patterns_data["conversation_patterns"]
                )
                restored_any = True

            if restored_any:
                self.restoration_log.append(
                    f"Learned patterns restored ({merge_mode} mode)"
                )

            return restored_any

        except Exception as e:
            logger.error(f"Failed to restore learned patterns: {e}")
            self.restoration_log.append(f"Pattern restoration failed: {e}")
            return False

    def _restore_conversation_patterns(self, conversation_data: List[Dict[str, Any]]):
        """Restore conversation history to LLM integration"""
        try:
            if hasattr(self.target_agent, "llm_integration"):
                llm = self.target_agent.llm_integration
                if hasattr(llm, "conversation_history"):
                    # Merge conversation history
                    if isinstance(llm.conversation_history, list):
                        llm.conversation_history.extend(conversation_data)
                    else:
                        llm.conversation_history = conversation_data
                elif hasattr(llm, "add_conversation_history"):
                    for conv in conversation_data:
                        llm.add_conversation_history(conv)

        except Exception as e:
            logger.warning(f"Could not restore conversation patterns: {e}")

    def restore_full_state(
        self, cognitive_state: Dict[str, Any], merge_mode: str = "replace"
    ) -> Dict[str, bool]:
        """Restore complete cognitive state"""
        results = {}

        # Restore memory store
        if "memory_store" in cognitive_state:
            results["memory"] = self.restore_memory_store(
                cognitive_state["memory_store"], merge_mode
            )

        # Restore goal hierarchies
        if "goal_hierarchies" in cognitive_state:
            results["goals"] = self.restore_goal_hierarchies(
                cognitive_state["goal_hierarchies"], merge_mode
            )

        # Restore learned patterns
        if "learned_patterns" in cognitive_state:
            results["patterns"] = self.restore_learned_patterns(
                cognitive_state["learned_patterns"], merge_mode
            )

        # Log restoration metadata
        if "extraction_metadata" in cognitive_state:
            metadata = cognitive_state["extraction_metadata"]
            logger.info(
                f"Restored state from {metadata.get('agent_type', 'unknown')} "
                f"extracted at {metadata.get('timestamp', 'unknown time')}"
            )

        return results


class AgentMerger:
    """Merges multiple agent cognitive states intelligently"""

    def __init__(self):
        self.merge_log = []

    def merge_agents(
        self,
        primary_archive: Dict[str, Any],
        secondary_archive: Dict[str, Any],
        merge_strategy: str = "intelligent",
    ) -> Dict[str, Any]:
        """Merge two agent archives into one"""
        try:
            logger.info(f"Merging agents using {merge_strategy} strategy")

            # Start with primary agent as base
            merged_archive = self._deep_copy_archive(primary_archive)

            # Merge metadata
            merged_metadata = self._merge_metadata(
                primary_archive["agent_metadata"], secondary_archive["agent_metadata"]
            )
            merged_archive["agent_metadata"] = merged_metadata

            # Merge cognitive states
            primary_cognitive = primary_archive["cognitive_state"]
            secondary_cognitive = secondary_archive["cognitive_state"]

            merged_cognitive = self._merge_cognitive_states(
                primary_cognitive, secondary_cognitive, merge_strategy
            )
            merged_archive["cognitive_state"] = merged_cognitive

            # Merge replay data if available
            if "replay_data" in primary_archive and "replay_data" in secondary_archive:
                merged_replay = self._merge_replay_data(
                    primary_archive["replay_data"], secondary_archive["replay_data"]
                )
                merged_archive["replay_data"] = merged_replay

            self.merge_log.append(f"Successfully merged {merged_metadata['name']}")
            return merged_archive

        except Exception as e:
            logger.error(f"Agent merge failed: {e}")
            raise

    def _merge_metadata(
        self, primary: Dict[str, Any], secondary: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Merge agent metadata intelligently"""
        merged = primary.copy()

        # Create combined name
        primary_name = primary.get("name", "Unknown")
        secondary_name = secondary.get("name", "Unknown")
        merged["name"] = f"{primary_name}+{secondary_name}"

        # Combine tags
        primary_tags = primary.get("tags", [])
        secondary_tags = secondary.get("tags", [])
        merged["tags"] = list(set(primary_tags + secondary_tags))

        # Update version
        merged["version"] = "merged_1.0"

        # Update description
        primary_desc = primary.get("description", "")
        secondary_desc = secondary.get("description", "")
        merged["description"] = f"Merged agent: {primary_desc} + {secondary_desc}"

        # New archive ID
        import hashlib

        merge_id = hashlib.sha256(
            f"{primary_name}_{secondary_name}_{datetime.now(timezone.utc).isoformat()}".encode()
        ).hexdigest()[:16]
        merged["archive_id"] = merge_id

        return merged

    def _merge_cognitive_states(
        self, primary: Dict[str, Any], secondary: Dict[str, Any], strategy: str
    ) -> Dict[str, Any]:
        """Merge cognitive states using specified strategy"""
        merged = primary.copy()

        if strategy == "intelligent":
            # Intelligently merge memories
            merged["memory_store"] = self._intelligent_merge_memories(
                primary.get("memory_store", {}), secondary.get("memory_store", {})
            )

            # Combine goal hierarchies
            merged["goal_hierarchies"] = self._combine_goals(
                primary.get("goal_hierarchies", {}),
                secondary.get("goal_hierarchies", {}),
            )

            # Merge learned patterns
            merged["learned_patterns"] = self._combine_patterns(
                primary.get("learned_patterns", {}),
                secondary.get("learned_patterns", {}),
            )

        elif strategy == "additive":
            # Simply add all data together
            for key in secondary:
                if key in merged:
                    if isinstance(merged[key], dict) and isinstance(
                        secondary[key], dict
                    ):
                        merged[key].update(secondary[key])
                    elif isinstance(merged[key], list) and isinstance(
                        secondary[key], list
                    ):
                        merged[key].extend(secondary[key])
                else:
                    merged[key] = secondary[key]

        return merged

    def _intelligent_merge_memories(
        self, primary_mem: Dict[str, Any], secondary_mem: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Intelligently merge memory stores, avoiding duplicates"""
        merged = primary_mem.copy()

        # Merge memories list if it exists
        if "memories" in primary_mem and "memories" in secondary_mem:
            primary_memories = primary_mem["memories"]
            secondary_memories = secondary_mem["memories"]

            if isinstance(primary_memories, list) and isinstance(
                secondary_memories, list
            ):
                # Remove duplicates while preserving order
                seen = set(primary_memories)
                unique_secondary = [
                    mem for mem in secondary_memories if mem not in seen
                ]
                merged["memories"] = primary_memories + unique_secondary

        # Merge other memory fields
        for key, value in secondary_mem.items():
            if key not in merged:
                merged[key] = value
            elif isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key].update(value)

        return merged

    def _combine_goals(
        self, primary_goals: Dict[str, Any], secondary_goals: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Combine goal hierarchies"""
        merged = primary_goals.copy()

        for key, value in secondary_goals.items():
            if key not in merged:
                merged[key] = value
            elif isinstance(merged[key], list) and isinstance(value, list):
                merged[key] = list(set(merged[key] + value))  # Remove duplicates
            elif isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key].update(value)

        return merged

    def _combine_patterns(
        self, primary_patterns: Dict[str, Any], secondary_patterns: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Combine learned patterns"""
        merged = primary_patterns.copy()

        for key, value in secondary_patterns.items():
            if key not in merged:
                merged[key] = value
            elif isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key].update(value)
            elif isinstance(merged[key], list) and isinstance(value, list):
                merged[key].extend(value)

        return merged

    def _merge_replay_data(
        self, primary_replay: Dict[str, Any], secondary_replay: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Merge replay data"""
        merged = primary_replay.copy()

        # Combine decision traces
        if (
            "decision_traces" in primary_replay
            and "decision_traces" in secondary_replay
        ):
            primary_traces = primary_replay["decision_traces"]
            secondary_traces = secondary_replay["decision_traces"]

            if isinstance(primary_traces, list) and isinstance(secondary_traces, list):
                merged["decision_traces"] = primary_traces + secondary_traces

        return merged

    def _deep_copy_archive(self, archive: Dict[str, Any]) -> Dict[str, Any]:
        """Create deep copy of archive"""
        import copy

        return copy.deepcopy(archive)


class AgentImporter:
    """Main agent import and restoration system"""

    def __init__(self, archive_dir: Optional[str] = None):
        """Initialize importer with archive directory"""
        if archive_dir is None:
            current_dir = Path(__file__).parent.parent
            self.archive_dir = current_dir / "data" / "agent_archives"
        else:
            self.archive_dir = Path(archive_dir)

        logger.info(f"Agent importer initialized with directory: {self.archive_dir}")

    def import_agent(
        self,
        archive_path: Union[str, Path],
        target_agent,
        merge_mode: str = "replace",
        validate: bool = True,
    ) -> Dict[str, Any]:
        """Import agent from archive file"""
        try:
            archive_path = Path(archive_path)
            if not archive_path.exists():
                raise FileNotFoundError(f"Archive file not found: {archive_path}")

            # Read archive
            logger.info(f"Reading archive: {archive_path}")
            archive_data = NSEReader.read_archive(archive_path)

            # Validate if requested
            if validate and not NSEReader.validate_archive(archive_data):
                raise ValueError("Archive validation failed")

            # Extract cognitive state
            cognitive_state = archive_data["cognitive_state"]
            metadata = archive_data["agent_metadata"]

            # Build and restore state
            builder = CognitiveStateBuilder(target_agent)
            restoration_results = builder.restore_full_state(
                cognitive_state, merge_mode
            )

            # Prepare result
            result = {
                "success": True,
                "imported_agent": metadata["name"],
                "version": metadata["version"],
                "merge_mode": merge_mode,
                "restoration_results": restoration_results,
                "restoration_log": builder.restoration_log,
                "imported_at": datetime.now(timezone.utc).isoformat(),
            }

            logger.info(
                f"Successfully imported agent {metadata['name']} v{metadata['version']}"
            )
            return result

        except Exception as e:
            logger.error(f"Failed to import agent: {e}")
            raise

    def merge_archives(
        self,
        primary_path: Union[str, Path],
        secondary_path: Union[str, Path],
        output_path: Optional[Union[str, Path]] = None,
        merge_strategy: str = "intelligent",
    ) -> str:
        """Merge two agent archives"""
        try:
            # Read both archives
            primary_archive = NSEReader.read_archive(Path(primary_path))
            secondary_archive = NSEReader.read_archive(Path(secondary_path))

            # Validate archives
            if not NSEReader.validate_archive(primary_archive):
                raise ValueError("Primary archive validation failed")
            if not NSEReader.validate_archive(secondary_archive):
                raise ValueError("Secondary archive validation failed")

            # Merge archives
            merger = AgentMerger()
            merged_archive = merger.merge_agents(
                primary_archive, secondary_archive, merge_strategy
            )

            # Generate output path if not provided
            if output_path is None:
                primary_name = primary_archive["agent_metadata"]["name"]
                secondary_name = secondary_archive["agent_metadata"]["name"]
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{primary_name}+{secondary_name}_merged_{timestamp}.nse"
                output_path = self.archive_dir / filename

            # Save merged archive
            self._save_archive(merged_archive, Path(output_path))

            logger.info(f"Successfully merged archives: {output_path}")
            return str(output_path)

        except Exception as e:
            logger.error(f"Failed to merge archives: {e}")
            raise

    def _save_archive(self, archive_data: Dict[str, Any], filepath: Path):
        """Save archive to file with compression"""
        with gzip.open(filepath, "wb") as f:
            # Write magic bytes
            f.write(b"NSE\x01")
            # Write JSON data
            json_data = json.dumps(archive_data, indent=2, default=str).encode("utf-8")
            f.write(json_data)

    def preview_archive(self, archive_path: Union[str, Path]) -> Dict[str, Any]:
        """Preview archive contents without importing"""
        try:
            archive_path = Path(archive_path)
            archive_data = NSEReader.read_archive(archive_path)

            metadata = archive_data["agent_metadata"]
            cognitive_state = archive_data["cognitive_state"]

            # Extract preview information
            preview = {
                "metadata": metadata,
                "cognitive_summary": {
                    "memory_items": len(
                        cognitive_state.get("memory_store", {}).get("memories", [])
                    ),
                    "goal_count": len(cognitive_state.get("goal_hierarchies", {})),
                    "pattern_types": list(
                        cognitive_state.get("learned_patterns", {}).keys()
                    ),
                    "has_replay_data": "replay_data" in archive_data,
                },
                "compatibility": archive_data.get("compatibility", {}),
                "file_info": {
                    "size_bytes": archive_path.stat().st_size,
                    "created": datetime.fromtimestamp(
                        archive_path.stat().st_ctime
                    ).isoformat(),
                },
            }

            return preview

        except Exception as e:
            logger.error(f"Failed to preview archive: {e}")
            raise


def import_agent(
    archive_path: Union[str, Path], target_agent, merge_mode: str = "replace"
) -> Dict[str, Any]:
    """
    High-level function to import an agent from archive

    Args:
        archive_path: Path to the NSE archive file
        target_agent: Agent instance to restore into
        merge_mode: "replace" or "merge" mode

    Returns:
        Import result dictionary
    """
    importer = AgentImporter()
    return importer.import_agent(archive_path, target_agent, merge_mode)


def merge_agents(
    primary_path: Union[str, Path],
    secondary_path: Union[str, Path],
    output_path: Optional[Union[str, Path]] = None,
) -> str:
    """
    High-level function to merge two agent archives

    Args:
        primary_path: Path to primary agent archive
        secondary_path: Path to secondary agent archive
        output_path: Optional output path for merged archive

    Returns:
        Path to merged archive file
    """
    importer = AgentImporter()
    return importer.merge_archives(primary_path, secondary_path, output_path)


if __name__ == "__main__":
    # Demo/test functionality
    class MockAgent:
        """Mock agent for testing"""

        def __init__(self):
            self.agent_id = "test_import_agent"
            self.memory_store = {}
            self.goals = {}

    # Test preview functionality
    importer = AgentImporter()
    archives = list(importer.archive_dir.glob("*.nse"))

    if archives:
        test_archive = archives[0]
        print(f"📖 Previewing archive: {test_archive.name}")
        try:
            preview = importer.preview_archive(test_archive)
            print(
                f"  Agent: {preview['metadata']['name']} v{preview['metadata']['version']}"
            )
            print(f"  Memories: {preview['cognitive_summary']['memory_items']}")
            print(f"  Goals: {preview['cognitive_summary']['goal_count']}")
            print(f"  Patterns: {preview['cognitive_summary']['pattern_types']}")
            print(f"  Size: {preview['file_info']['size_bytes']} bytes")
        except Exception as e:
            print(f"  ❌ Preview failed: {e}")

        # Test import
        mock_agent = MockAgent()
        try:
            result = import_agent(test_archive, mock_agent, merge_mode="replace")
            print(f"✅ Import test successful: {result['imported_agent']}")
        except Exception as e:
            print(f"❌ Import test failed: {e}")
    else:
        print("[DISC] No archives found for testing")
