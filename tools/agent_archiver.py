#!/usr/bin/env python3
"""
🧠 aetherra Agent Archive System
Core state extraction and archival functionality for preserving agent consciousness.

This module implements the Neural State Exchange (NSE) format for serializing
and preserving complete agent cognitive states, including memories, goals,
learned patterns, and decision trees.
"""

import gzip
import hashlib
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NSEFormat:
    """Neural State Exchange format handler"""

    VERSION = "1.0"
    MAGIC_BYTES = b"NSE\x01"  # File format identifier

    @classmethod
    def create_metadata(
        cls,
        agent_name: str,
        version: str,
        created_by: str,
        description: str,
        tags: List[str],
        privacy_level: str = "private",
    ) -> Dict[str, Any]:
        """Create standardized metadata for agent archive"""
        return {
            "nse_version": cls.VERSION,
            "agent_metadata": {
                "name": agent_name,
                "version": version,
                "created_by": created_by,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "description": description,
                "tags": tags,
                "privacy_level": privacy_level,
                "aetherra_version": "3.0",  # Current aetherra version
                "archive_id": hashlib.sha256(
                    f"{agent_name}_{version}_{datetime.now(timezone.utc).isoformat()}".encode()
                ).hexdigest()[:16],
            },
        }


class CognitiveStateExtractor:
    """Extracts and serializes agent cognitive state"""

    def __init__(self, agent_instance):
        """Initialize with agent instance to extract from"""
        self.agent = agent_instance
        self.extraction_timestamp = datetime.now(timezone.utc)

    def extract_memory_store(self) -> Dict[str, Any]:
        """Extract and compress agent memory store"""
        try:
            if hasattr(self.agent, "memory_store"):
                memory_data = self.agent.memory_store
                if hasattr(memory_data, "to_dict"):
                    return memory_data.to_dict()
                elif isinstance(memory_data, dict):
                    return memory_data
                else:
                    logger.warning(
                        "Memory store format not recognized, attempting generic extraction"
                    )
                    return {"raw_memory": str(memory_data)}
            else:
                logger.warning("Agent has no memory_store attribute")
                return {
                    "extracted_at": self.extraction_timestamp.isoformat(),
                    "memories": [],
                }
        except Exception as e:
            logger.error(f"Failed to extract memory store: {e}")
            return {
                "error": str(e),
                "extracted_at": self.extraction_timestamp.isoformat(),
            }

    def extract_goal_hierarchies(self) -> Dict[str, Any]:
        """Extract agent goal structures and priorities"""
        try:
            goals_data = {}

            # Try different possible goal storage patterns
            goal_attributes = ["goals", "goal_store", "objectives", "targets"]
            for attr in goal_attributes:
                if hasattr(self.agent, attr):
                    goal_data = getattr(self.agent, attr)
                    if hasattr(goal_data, "to_dict"):
                        goals_data[attr] = goal_data.to_dict()
                    else:
                        goals_data[attr] = goal_data

            if not goals_data:
                logger.warning("No goal structures found in agent")
                goals_data = {
                    "default_goals": [],
                    "extracted_at": self.extraction_timestamp.isoformat(),
                }

            return goals_data
        except Exception as e:
            logger.error(f"Failed to extract goal hierarchies: {e}")
            return {
                "error": str(e),
                "extracted_at": self.extraction_timestamp.isoformat(),
            }

    def extract_learned_patterns(self) -> Dict[str, Any]:
        """Extract learned behavioral patterns and decision weights"""
        try:
            patterns_data = {}

            # Look for pattern storage
            pattern_attributes = [
                "patterns",
                "learned_behaviors",
                "decision_weights",
                "experience_data",
            ]
            for attr in pattern_attributes:
                if hasattr(self.agent, attr):
                    pattern_data = getattr(self.agent, attr)
                    if hasattr(pattern_data, "to_dict"):
                        patterns_data[attr] = pattern_data.to_dict()
                    elif hasattr(pattern_data, "__dict__"):
                        patterns_data[attr] = vars(pattern_data)
                    else:
                        patterns_data[attr] = pattern_data

            # Try to extract runtime learning data
            if hasattr(self.agent, "llm_integration"):
                llm_data = self.agent.llm_integration
                if hasattr(llm_data, "conversation_history"):
                    patterns_data["conversation_patterns"] = (
                        llm_data.conversation_history[-100:]
                    )  # Last 100 interactions

            return patterns_data
        except Exception as e:
            logger.error(f"Failed to extract learned patterns: {e}")
            return {
                "error": str(e),
                "extracted_at": self.extraction_timestamp.isoformat(),
            }

    def extract_decision_traces(self) -> List[Dict[str, Any]]:
        """Extract recent decision-making traces for replay"""
        try:
            traces = []

            # Look for decision logging
            if hasattr(self.agent, "decision_log"):
                decision_log = self.agent.decision_log
                if isinstance(decision_log, list):
                    traces = decision_log[-50:]  # Last 50 decisions
                elif hasattr(decision_log, "get_recent"):
                    traces = decision_log.get_recent(50)

            # Fallback: try to get from debug system
            if not traces and hasattr(self.agent, "debug_system"):
                debug_data = self.agent.debug_system
                if hasattr(debug_data, "decision_traces"):
                    traces = debug_data.decision_traces[-50:]

            return traces
        except Exception as e:
            logger.error(f"Failed to extract decision traces: {e}")
            return []

    def extract_full_state(self) -> Dict[str, Any]:
        """Extract complete cognitive state"""
        logger.info(
            f"Extracting cognitive state from agent at {self.extraction_timestamp}"
        )

        cognitive_state = {
            "memory_store": self.extract_memory_store(),
            "goal_hierarchies": self.extract_goal_hierarchies(),
            "learned_patterns": self.extract_learned_patterns(),
            "extraction_metadata": {
                "timestamp": self.extraction_timestamp.isoformat(),
                "agent_type": type(self.agent).__name__,
                "agent_id": getattr(self.agent, "agent_id", "unknown"),
                "runtime_stats": self._get_runtime_stats(),
            },
        }

        # Add replay data
        replay_data = {
            "decision_traces": self.extract_decision_traces(),
            "session_metadata": {
                "extraction_time": self.extraction_timestamp.isoformat(),
                "session_duration": self._get_session_duration(),
                "decisions_count": len(self.extract_decision_traces()),
            },
        }

        return {"cognitive_state": cognitive_state, "replay_data": replay_data}

    def _get_runtime_stats(self) -> Dict[str, Any]:
        """Get runtime statistics about the agent"""
        stats = {}
        try:
            if hasattr(self.agent, "performance_stats"):
                stats = self.agent.performance_stats
            else:
                # Calculate basic stats
                stats = {
                    "memory_items": len(
                        self.extract_memory_store().get("memories", [])
                    ),
                    "goals_count": len(
                        self.extract_goal_hierarchies().get("goals", [])
                    ),
                    "patterns_count": len(self.extract_learned_patterns()),
                    "decisions_logged": len(self.extract_decision_traces()),
                }
        except Exception as e:
            logger.error(f"Failed to get runtime stats: {e}")
            stats = {"error": str(e)}

        return stats

    def _get_session_duration(self) -> Optional[float]:
        """Calculate session duration if possible"""
        try:
            if hasattr(self.agent, "start_time"):
                start_time = self.agent.start_time
                if isinstance(start_time, datetime):
                    duration = (self.extraction_timestamp - start_time).total_seconds()
                    return duration
        except Exception:
            pass
        return None


class AgentArchiver:
    """Main agent archival system"""

    def __init__(self, archive_dir: Optional[str] = None):
        """Initialize archiver with storage directory"""
        if archive_dir is None:
            # Default to data/agent_archives
            current_dir = Path(__file__).parent.parent
            self.archive_dir = current_dir / "data" / "agent_archives"
        else:
            self.archive_dir = Path(archive_dir)
        self.archive_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Agent archiver initialized with directory: {self.archive_dir}")

    def create_archive(
        self, agent_instance, metadata: Dict[str, Any], compression: bool = True
    ) -> str:
        """Create complete agent archive"""
        try:
            # Extract cognitive state
            extractor = CognitiveStateExtractor(agent_instance)
            state_data = extractor.extract_full_state()

            # Create complete archive structure
            archive_data = {
                **metadata,
                **state_data,
                "compatibility": {
                    "aetherra_version": ">=3.0",
                    "required_plugins": self._detect_required_plugins(agent_instance),
                    "model_dependencies": self._detect_model_dependencies(
                        agent_instance
                    ),
                },
            }

            # Generate filename
            agent_name = metadata["agent_metadata"]["name"]
            version = metadata["agent_metadata"]["version"]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{agent_name}_v{version}_{timestamp}.nse"

            filepath = self.archive_dir / filename

            # Save with compression if requested
            if compression:
                self._save_compressed(archive_data, filepath)
            else:
                self._save_uncompressed(archive_data, filepath)

            logger.info(f"Agent archive created successfully: {filepath}")
            return str(filepath)

        except Exception as e:
            logger.error(f"Failed to create agent archive: {e}")
            raise

    def _save_compressed(self, data: Dict[str, Any], filepath: Path):
        """Save archive with gzip compression"""
        with gzip.open(filepath, "wb") as f:
            # Write magic bytes
            f.write(NSEFormat.MAGIC_BYTES)
            # Write JSON data
            json_data = json.dumps(data, indent=2, default=str).encode("utf-8")
            f.write(json_data)

    def _save_uncompressed(self, data: Dict[str, Any], filepath: Path):
        """Save archive without compression"""
        with open(filepath, "wb") as f:
            # Write magic bytes
            f.write(NSEFormat.MAGIC_BYTES)
            # Write JSON data
            json_data = json.dumps(data, indent=2, default=str).encode("utf-8")
            f.write(json_data)

    def _detect_required_plugins(self, agent_instance) -> List[str]:
        """Detect plugins required by the agent"""
        plugins = []
        try:
            if hasattr(agent_instance, "plugin_manager"):
                pm = agent_instance.plugin_manager
                if hasattr(pm, "loaded_plugins"):
                    plugins = list(pm.loaded_plugins.keys())
                elif hasattr(pm, "active_plugins"):
                    plugins = list(pm.active_plugins.keys())
        except Exception as e:
            logger.warning(f"Could not detect required plugins: {e}")

        return plugins

    def _detect_model_dependencies(self, agent_instance) -> List[str]:
        """Detect AI model dependencies"""
        models = []
        try:
            if hasattr(agent_instance, "llm_integration"):
                llm = agent_instance.llm_integration
                if hasattr(llm, "model_name"):
                    models.append(llm.model_name)
                elif hasattr(llm, "active_models"):
                    models.extend(llm.active_models)
        except Exception as e:
            logger.warning(f"Could not detect model dependencies: {e}")

        return models

    def list_archives(self) -> List[Dict[str, Any]]:
        """List all available archives with metadata"""
        archives = []

        for archive_file in self.archive_dir.glob("*.nse"):
            try:
                metadata = self._read_archive_metadata(archive_file)
                metadata["file_path"] = str(archive_file)
                metadata["file_size"] = archive_file.stat().st_size
                metadata["created_on_disk"] = datetime.fromtimestamp(
                    archive_file.stat().st_ctime
                )
                archives.append(metadata)
            except Exception as e:
                logger.error(f"Failed to read metadata from {archive_file}: {e}")

        return sorted(
            archives, key=lambda x: x.get("created_on_disk", datetime.min), reverse=True
        )

    def _read_archive_metadata(self, filepath: Path) -> Dict[str, Any]:
        """Read just the metadata from an archive file"""
        try:
            # Try compressed first
            try:
                with gzip.open(filepath, "rb") as f:
                    magic = f.read(4)
                    if magic == NSEFormat.MAGIC_BYTES:
                        data = json.loads(f.read().decode("utf-8"))
                        return data.get("agent_metadata", {})
            except Exception:
                # Try uncompressed
                with open(filepath, "rb") as f:
                    magic = f.read(4)
                    if magic == NSEFormat.MAGIC_BYTES:
                        data = json.loads(f.read().decode("utf-8"))
                        return data.get("agent_metadata", {})

            raise ValueError("Invalid NSE format")

        except Exception as e:
            logger.error(f"Failed to read archive metadata: {e}")
            return {"error": str(e), "name": filepath.stem}


def export_agent(
    agent_instance,
    name: str,
    version: str,
    description: str,
    tags: Optional[List[str]] = None,
    created_by: str = "user",
    privacy_level: str = "private",
    archive_dir: Optional[str] = None,
) -> str:
    """
    High-level function to export an agent to archive

    Args:
        agent_instance: The agent object to archive
        name: Agent name
        version: Agent version
        description: Description of the agent
        tags: List of tags for categorization
        created_by: Creator identifier
        privacy_level: "private", "team", or "public"
        archive_dir: Custom archive directory

    Returns:
        Path to created archive file
    """
    if tags is None:
        tags = []

    # Create metadata
    metadata = NSEFormat.create_metadata(
        agent_name=name,
        version=version,
        created_by=created_by,
        description=description,
        tags=tags,
        privacy_level=privacy_level,
    )

    # Create archiver and save
    archiver = AgentArchiver(archive_dir)
    return archiver.create_archive(agent_instance, metadata, compression=True)


if __name__ == "__main__":
    # Demo/test functionality
    class MockAgent:
        """Mock agent for testing"""

        def __init__(self):
            self.agent_id = "test_agent_001"
            self.memory_store = {
                "memories": [
                    "learned to optimize queries",
                    "user prefers detailed responses",
                ]
            }
            self.goals = {"primary": "help users", "secondary": ["learn continuously"]}
            self.start_time = datetime.now(timezone.utc)

    # Test export
    mock_agent = MockAgent()
    archive_path = export_agent(
        agent_instance=mock_agent,
        name="TestAgent",
        version="1.0",
        description="Test agent for development",
        tags=["development", "testing"],
        created_by="developer@aetherra.dev",
    )

    print(f"✅ Test archive created: {archive_path}")

    # Test listing
    archiver = AgentArchiver()
    archives = archiver.list_archives()
    print(f"📦 Found {len(archives)} archives:")
    for archive in archives:
        print(
            f"  - {archive.get('name', 'Unknown')} v{archive.get('version', '?')} ({archive.get('file_size', 0)} bytes)"
        )
