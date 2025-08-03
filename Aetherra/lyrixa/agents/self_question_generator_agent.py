#!/usr/bin/env python3
"""
❓ SELF QUESTION GENERATOR AGENT
===============================

Agent that generates self-reflective questions to drive introspection,
self-improvement, and deeper understanding of system behavior.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import random

logger = logging.getLogger(__name__)


class SelfQuestionGeneratorAgent:
    """Agent that generates self-reflective questions for system introspection"""

    def __init__(self):
        self.agent_id = "self_question_generator"
        self.name = "Self Question Generator Agent"
        self.status = "questioning"
        self.questions_generated = 0
        self.reflections_triggered = 0
        self.is_available = True

        # Question templates for different domains
        self.question_templates = {
            "performance": [
                "How efficiently am I processing requests?",
                "What bottlenecks are affecting my performance?",
                "Where can I optimize my resource usage?"
            ],
            "learning": [
                "What have I learned from recent interactions?",
                "How has my understanding evolved?",
                "What knowledge gaps should I address?"
            ],
            "behavior": [
                "Am I responding appropriately to different contexts?",
                "How consistent is my behavior across similar situations?",
                "What patterns emerge in my decision-making?"
            ],
            "goals": [
                "Are my current goals aligned with user needs?",
                "How effectively am I pursuing my objectives?",
                "What new goals should I consider?"
            ]
        }

        logger.info("❓ Self Question Generator Agent initialized")

    def generate_self_questions(self, domain: Optional[str] = None, count: int = 3) -> List[str]:
        """Generate self-reflective questions"""
        if domain and domain in self.question_templates:
            questions = random.sample(self.question_templates[domain],
                                    min(count, len(self.question_templates[domain])))
        else:
            # Mix questions from all domains
            all_questions = []
            for templates in self.question_templates.values():
                all_questions.extend(templates)
            questions = random.sample(all_questions, min(count, len(all_questions)))

        self.questions_generated += len(questions)
        return questions

    def trigger_reflection(self, question: str) -> Dict[str, Any]:
        """Trigger a reflection process based on a question"""
        self.reflections_triggered += 1
        return {
            "question": question,
            "reflection_id": f"refl_{self.reflections_triggered}",
            "timestamp": datetime.now().isoformat(),
            "status": "reflecting"
        }

    def get_reflection_metrics(self) -> Dict[str, Any]:
        """Get metrics about reflection activity"""
        return {
            "total_questions": self.questions_generated,
            "total_reflections": self.reflections_triggered,
            "reflection_rate": self.reflections_triggered / max(1, self.questions_generated)
        }

    def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "status": self.status,
            "questions_generated": self.questions_generated,
            "reflections_triggered": self.reflections_triggered,
            "is_available": self.is_available
        }


__all__ = ["SelfQuestionGeneratorAgent"]
