import unittest
from unittest.mock import MagicMock

from Aetherra.core.idle_reflection import IdleReflectionSystem
from Aetherra.core.memory.base import AetherraMemory


class TestIdleReflectionSystem(unittest.TestCase):
    def setUp(self):
        self.mock_memory = MagicMock(spec=AetherraMemory)
        self.reflection_system = IdleReflectionSystem(memory_instance=self.mock_memory)

    def test_start_and_stop(self):
        self.reflection_system.start()
        self.assertTrue(self.reflection_system.is_running)
        self.reflection_system.stop()
        self.assertFalse(self.reflection_system.is_running)

    def test_perform_reflection(self):
        # Mock recent memories and insights
        self.mock_memory.get_recent_memories.return_value = [
            {"text": "Test memory", "tags": ["test"], "category": "general"}
        ]
        self.reflection_system.reflector.analyze_behavior = MagicMock(
            return_value={
                "recommendations": [
                    {
                        "text": "Test insight",
                        "tags": ["insight"],
                        "category": "insights",
                    }
                ]
            }
        )

        self.reflection_system._perform_reflection()

        # Verify insights were stored
        self.mock_memory.store_insights.assert_called_once()


if __name__ == "__main__":
    unittest.main()
