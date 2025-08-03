# collaborative_multi_agent_system.py
# 🤖 Collaborative Multi-Agent Code Work for Lyrixa
# Specialized agents working together on complex code tasks

import asyncio
import json
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
import threading

logger = logging.getLogger(__name__)

class AgentRole(Enum):
    """Different agent roles in the collaborative system"""
    ARCHITECT = "architect"  # Designs overall structure
    REFACTOR_SPECIALIST = "refactor_specialist"  # Improves code quality
    TEST_ENGINEER = "test_engineer"  # Creates and runs tests
    SECURITY_AUDITOR = "security_auditor"  # Reviews for security issues
    PERFORMANCE_OPTIMIZER = "performance_optimizer"  # Optimizes performance
    CODE_REVIEWER = "code_reviewer"  # Reviews code quality
    DOCUMENTATION_WRITER = "documentation_writer"  # Creates documentation

class TaskPriority(Enum):
    """Task priority levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

@dataclass
class CodeTask:
    """A task that needs to be completed by agents"""
    task_id: str
    title: str
    description: str
    required_roles: List[AgentRole]
    priority: TaskPriority
    file_paths: List[str]
    estimated_complexity: float  # 1-10 scale
    dependencies: List[str]  # Other task IDs that must complete first
    metadata: Dict[str, Any]
    created_timestamp: float
    deadline: Optional[float] = None
    assigned_agents: List[str] = None

    def __post_init__(self):
        if self.assigned_agents is None:
            self.assigned_agents = []

@dataclass
class AgentContribution:
    """A contribution made by an agent to a task"""
    agent_id: str
    task_id: str
    contribution_type: str  # "code_change", "review", "test", "documentation"
    content: str
    confidence_score: float
    rationale: str
    timestamp: float

@dataclass
class CollaborationResult:
    """Result of a collaborative effort"""
    task_id: str
    success: bool
    contributions: List[AgentContribution]
    final_code: str
    quality_score: float
    completion_time: float
    lessons_learned: List[str]

class BaseAgent(ABC):
    """Base class for all collaborative agents"""

    def __init__(self, agent_id: str, role: AgentRole, workspace_path: str):
        self.agent_id = agent_id
        self.role = role
        self.workspace_path = Path(workspace_path)
        self.current_tasks: Set[str] = set()
        self.completed_tasks: List[str] = []
        self.performance_metrics = {
            "tasks_completed": 0,
            "average_quality_score": 0.0,
            "average_completion_time": 0.0,
            "success_rate": 0.0
        }

    @abstractmethod
    async def analyze_task(self, task: CodeTask) -> Dict[str, Any]:
        """Analyze a task and determine approach"""
        pass

    @abstractmethod
    async def contribute_to_task(self, task: CodeTask,
                               previous_contributions: List[AgentContribution]) -> AgentContribution:
        """Make a contribution to a task"""
        pass

    @abstractmethod
    async def review_contribution(self, contribution: AgentContribution,
                                task: CodeTask) -> Dict[str, Any]:
        """Review another agent's contribution"""
        pass

    async def can_handle_task(self, task: CodeTask) -> bool:
        """Determine if this agent can handle the given task"""
        return self.role in task.required_roles

    def update_performance_metrics(self, quality_score: float, completion_time: float, success: bool):
        """Update agent's performance metrics"""
        self.performance_metrics["tasks_completed"] += 1

        # Update averages
        total_tasks = self.performance_metrics["tasks_completed"]
        self.performance_metrics["average_quality_score"] = (
            (self.performance_metrics["average_quality_score"] * (total_tasks - 1) + quality_score) / total_tasks
        )
        self.performance_metrics["average_completion_time"] = (
            (self.performance_metrics["average_completion_time"] * (total_tasks - 1) + completion_time) / total_tasks
        )

        # Update success rate
        if success:
            current_successes = self.performance_metrics["success_rate"] * (total_tasks - 1)
            self.performance_metrics["success_rate"] = (current_successes + 1) / total_tasks
        else:
            current_successes = self.performance_metrics["success_rate"] * (total_tasks - 1)
            self.performance_metrics["success_rate"] = current_successes / total_tasks

class ArchitectAgent(BaseAgent):
    """Agent specialized in designing overall code structure"""

    def __init__(self, workspace_path: str):
        super().__init__("architect_01", AgentRole.ARCHITECT, workspace_path)

    async def analyze_task(self, task: CodeTask) -> Dict[str, Any]:
        """Analyze task from architectural perspective"""
        return {
            "structural_complexity": self._assess_structural_complexity(task),
            "design_patterns_needed": self._identify_design_patterns(task),
            "module_dependencies": self._analyze_dependencies(task),
            "recommended_approach": self._recommend_approach(task)
        }

    async def contribute_to_task(self, task: CodeTask,
                               previous_contributions: List[AgentContribution]) -> AgentContribution:
        """Provide architectural guidance and structure"""
        analysis = await self.analyze_task(task)

        # Create architectural blueprint
        blueprint = self._create_blueprint(task, analysis)

        return AgentContribution(
            agent_id=self.agent_id,
            task_id=task.task_id,
            contribution_type="architectural_design",
            content=blueprint,
            confidence_score=0.85,
            rationale="Designed optimal structure based on task requirements and best practices",
            timestamp=time.time()
        )

    async def review_contribution(self, contribution: AgentContribution,
                                task: CodeTask) -> Dict[str, Any]:
        """Review contribution for architectural soundness"""
        return {
            "architectural_compliance": self._check_architectural_compliance(contribution, task),
            "design_consistency": self._check_design_consistency(contribution),
            "scalability_assessment": self._assess_scalability(contribution),
            "recommendations": self._provide_architectural_recommendations(contribution)
        }

    def _assess_structural_complexity(self, task: CodeTask) -> float:
        """Assess how structurally complex the task is"""
        complexity_factors = {
            "file_count": min(len(task.file_paths) / 5, 1.0),
            "description_length": min(len(task.description) / 500, 1.0),
            "estimated_complexity": task.estimated_complexity / 10
        }
        return sum(complexity_factors.values()) / len(complexity_factors)

    def _identify_design_patterns(self, task: CodeTask) -> List[str]:
        """Identify which design patterns would be beneficial"""
        patterns = []
        description_lower = task.description.lower()

        if "factory" in description_lower or "create" in description_lower:
            patterns.append("Factory Pattern")
        if "observe" in description_lower or "notify" in description_lower:
            patterns.append("Observer Pattern")
        if "single" in description_lower and "instance" in description_lower:
            patterns.append("Singleton Pattern")
        if "strategy" in description_lower or "algorithm" in description_lower:
            patterns.append("Strategy Pattern")

        return patterns

    def _analyze_dependencies(self, task: CodeTask) -> Dict[str, List[str]]:
        """Analyze module dependencies"""
        return {
            "external_dependencies": [],  # Would analyze imports
            "internal_dependencies": task.dependencies,
            "circular_dependencies": []  # Would check for circular deps
        }

    def _recommend_approach(self, task: CodeTask) -> str:
        """Recommend implementation approach"""
        if task.estimated_complexity > 7:
            return "Break into smaller modules with clear interfaces"
        elif task.estimated_complexity > 4:
            return "Use layered architecture with separation of concerns"
        else:
            return "Simple, direct implementation with good documentation"

    def _create_blueprint(self, task: CodeTask, analysis: Dict[str, Any]) -> str:
        """Create architectural blueprint"""
        blueprint = f"""
# Architectural Blueprint for: {task.title}

## Overview
{task.description}

## Structural Approach
{analysis['recommended_approach']}

## Design Patterns
{', '.join(analysis['design_patterns_needed']) if analysis['design_patterns_needed'] else 'None required'}

## Module Structure
- Main implementation: Core logic
- Utilities: Helper functions
- Tests: Comprehensive test suite
- Documentation: Usage examples

## Key Considerations
- Maintainability: Code should be easy to modify
- Testability: Clear interfaces for testing
- Performance: Efficient algorithms and data structures
- Security: Input validation and error handling
"""
        return blueprint.strip()

    def _check_architectural_compliance(self, contribution: AgentContribution, task: CodeTask) -> float:
        """Check if contribution follows architectural guidelines"""
        # Simple compliance check
        return 0.8  # Would implement actual checks

    def _check_design_consistency(self, contribution: AgentContribution) -> float:
        """Check design consistency"""
        return 0.85  # Would implement actual checks

    def _assess_scalability(self, contribution: AgentContribution) -> float:
        """Assess scalability of the contribution"""
        return 0.75  # Would implement actual checks

    def _provide_architectural_recommendations(self, contribution: AgentContribution) -> List[str]:
        """Provide architectural recommendations"""
        return ["Consider using dependency injection", "Add proper error handling"]

class RefactorSpecialistAgent(BaseAgent):
    """Agent specialized in code refactoring and quality improvement"""

    def __init__(self, workspace_path: str):
        super().__init__("refactor_01", AgentRole.REFACTOR_SPECIALIST, workspace_path)

    async def analyze_task(self, task: CodeTask) -> Dict[str, Any]:
        """Analyze task for refactoring opportunities"""
        return {
            "code_smells": self._identify_code_smells(task),
            "refactoring_opportunities": self._find_refactoring_opportunities(task),
            "quality_metrics": self._assess_code_quality(task)
        }

    async def contribute_to_task(self, task: CodeTask,
                               previous_contributions: List[AgentContribution]) -> AgentContribution:
        """Provide refactoring improvements"""

        # Find code contributions to refactor
        code_contributions = [c for c in previous_contributions if c.contribution_type == "code_change"]

        if code_contributions:
            # Refactor the latest code contribution
            latest_code = code_contributions[-1].content
            refactored_code = self._refactor_code(latest_code)

            return AgentContribution(
                agent_id=self.agent_id,
                task_id=task.task_id,
                contribution_type="code_refactor",
                content=refactored_code,
                confidence_score=0.90,
                rationale="Improved code quality through refactoring: better naming, structure, and readability",
                timestamp=time.time()
            )
        else:
            # Provide refactoring guidelines
            guidelines = self._create_refactoring_guidelines(task)

            return AgentContribution(
                agent_id=self.agent_id,
                task_id=task.task_id,
                contribution_type="refactoring_guidelines",
                content=guidelines,
                confidence_score=0.85,
                rationale="Provided refactoring guidelines for better code quality",
                timestamp=time.time()
            )

    async def review_contribution(self, contribution: AgentContribution,
                                task: CodeTask) -> Dict[str, Any]:
        """Review contribution for refactoring opportunities"""
        return {
            "code_quality_score": self._rate_code_quality(contribution.content),
            "refactoring_suggestions": self._suggest_refactoring_improvements(contribution.content),
            "maintainability_score": self._assess_maintainability(contribution.content)
        }

    def _identify_code_smells(self, task: CodeTask) -> List[str]:
        """Identify potential code smells"""
        smells = []
        if task.estimated_complexity > 8:
            smells.append("High complexity - consider breaking down")
        if len(task.file_paths) > 10:
            smells.append("Too many files - might need better organization")
        return smells

    def _find_refactoring_opportunities(self, task: CodeTask) -> List[str]:
        """Find refactoring opportunities"""
        return [
            "Extract common functionality into utilities",
            "Improve variable and function naming",
            "Add type hints for better code clarity",
            "Simplify complex conditional logic"
        ]

    def _assess_code_quality(self, task: CodeTask) -> Dict[str, float]:
        """Assess overall code quality metrics"""
        return {
            "readability": 0.7,
            "maintainability": 0.8,
            "testability": 0.6,
            "performance": 0.7
        }

    def _refactor_code(self, code: str) -> str:
        """Refactor the given code"""
        # Simple refactoring example
        lines = code.split('\n')
        refactored_lines = []

        for line in lines:
            # Improve variable naming
            if 'temp' in line and '=' in line:
                line = line.replace('temp', 'temporary_value')

            # Add type hints where missing
            if 'def ' in line and ':' not in line and '(' in line:
                if line.endswith(':'):
                    continue
                else:
                    line = line.rstrip() + ' -> None:'

            refactored_lines.append(line)

        return '\n'.join(refactored_lines)

    def _create_refactoring_guidelines(self, task: CodeTask) -> str:
        """Create refactoring guidelines for the task"""
        return f"""
# Refactoring Guidelines for: {task.title}

## Code Quality Principles
1. **Single Responsibility**: Each function should have one clear purpose
2. **DRY (Don't Repeat Yourself)**: Extract common code into reusable functions
3. **Clear Naming**: Use descriptive names for variables and functions
4. **Type Hints**: Add type annotations for better code clarity

## Specific Recommendations
- Break down complex functions (>20 lines) into smaller ones
- Use constants for magic numbers
- Add docstrings for all public functions
- Handle errors gracefully with try-catch blocks

## Quality Metrics to Aim For
- Cyclomatic complexity < 10 per function
- Function length < 20 lines
- Clear variable names (avoid single letters except for loops)
- Comprehensive error handling
"""

    def _rate_code_quality(self, code: str) -> float:
        """Rate the quality of code"""
        quality_score = 0.5  # Base score

        # Check for docstrings
        if '"""' in code or "'''" in code:
            quality_score += 0.2

        # Check for type hints
        if '->' in code:
            quality_score += 0.1

        # Check for proper error handling
        if 'try:' in code and 'except' in code:
            quality_score += 0.1

        # Check line length (prefer shorter lines)
        lines = code.split('\n')
        avg_line_length = sum(len(line) for line in lines) / max(len(lines), 1)
        if avg_line_length < 80:
            quality_score += 0.1

        return min(quality_score, 1.0)

    def _suggest_refactoring_improvements(self, code: str) -> List[str]:
        """Suggest specific refactoring improvements"""
        suggestions = []

        if 'def ' in code and '"""' not in code:
            suggestions.append("Add docstrings to functions")

        if 'print(' in code:
            suggestions.append("Replace print statements with proper logging")

        if code.count('if ') > 5:
            suggestions.append("Consider using polymorphism or strategy pattern for complex conditionals")

        return suggestions

    def _assess_maintainability(self, code: str) -> float:
        """Assess how maintainable the code is"""
        maintainability = 0.6  # Base score

        # Well-documented code is more maintainable
        if '"""' in code:
            maintainability += 0.2

        # Shorter functions are more maintainable
        function_count = code.count('def ')
        if function_count > 0:
            avg_function_length = len(code.split('\n')) / function_count
            if avg_function_length < 15:
                maintainability += 0.2

        return min(maintainability, 1.0)

class TestEngineerAgent(BaseAgent):
    """Agent specialized in creating and running tests"""

    def __init__(self, workspace_path: str):
        super().__init__("test_engineer_01", AgentRole.TEST_ENGINEER, workspace_path)

    async def analyze_task(self, task: CodeTask) -> Dict[str, Any]:
        """Analyze task for testing requirements"""
        return {
            "test_types_needed": self._identify_test_types(task),
            "test_coverage_estimate": self._estimate_test_coverage(task),
            "testing_challenges": self._identify_testing_challenges(task)
        }

    async def contribute_to_task(self, task: CodeTask,
                               previous_contributions: List[AgentContribution]) -> AgentContribution:
        """Create comprehensive tests"""

        # Find code to test
        code_contributions = [c for c in previous_contributions
                            if c.contribution_type in ["code_change", "code_refactor"]]

        if code_contributions:
            # Create tests for the code
            latest_code = code_contributions[-1].content
            test_code = self._generate_test_code(task, latest_code)
        else:
            # Create test plan
            test_code = self._create_test_plan(task)

        return AgentContribution(
            agent_id=self.agent_id,
            task_id=task.task_id,
            contribution_type="test_code",
            content=test_code,
            confidence_score=0.88,
            rationale="Created comprehensive tests covering main functionality and edge cases",
            timestamp=time.time()
        )

    async def review_contribution(self, contribution: AgentContribution,
                                task: CodeTask) -> Dict[str, Any]:
        """Review contribution for testability"""
        return {
            "testability_score": self._assess_testability(contribution.content),
            "test_suggestions": self._suggest_additional_tests(contribution.content),
            "edge_cases": self._identify_edge_cases(contribution.content)
        }

    def _identify_test_types(self, task: CodeTask) -> List[str]:
        """Identify what types of tests are needed"""
        test_types = ["unit_tests"]  # Always need unit tests

        if "api" in task.description.lower():
            test_types.append("integration_tests")
        if "performance" in task.description.lower():
            test_types.append("performance_tests")
        if "security" in task.description.lower():
            test_types.append("security_tests")

        return test_types

    def _estimate_test_coverage(self, task: CodeTask) -> float:
        """Estimate achievable test coverage"""
        base_coverage = 0.8

        # Adjust based on complexity
        if task.estimated_complexity > 8:
            base_coverage -= 0.1  # Complex code harder to test
        if task.estimated_complexity < 3:
            base_coverage += 0.1  # Simple code easier to test

        return max(0.5, min(0.95, base_coverage))

    def _identify_testing_challenges(self, task: CodeTask) -> List[str]:
        """Identify potential testing challenges"""
        challenges = []

        if "async" in task.description.lower():
            challenges.append("Asynchronous code testing")
        if "file" in task.description.lower() or "io" in task.description.lower():
            challenges.append("File I/O mocking")
        if "network" in task.description.lower() or "api" in task.description.lower():
            challenges.append("Network dependency mocking")

        return challenges

    def _generate_test_code(self, task: CodeTask, code_to_test: str) -> str:
        """Generate test code for the given code"""
        test_template = f"""
import unittest
import pytest
from unittest.mock import Mock, patch

class Test{task.title.replace(' ', '')}(unittest.TestCase):
    \"\"\"Test suite for {task.title}\"\"\"

    def setUp(self):
        \"\"\"Set up test fixtures before each test method.\"\"\"
        pass

    def test_basic_functionality(self):
        \"\"\"Test basic functionality works as expected\"\"\"
        # TODO: Implement basic functionality test
        self.assertTrue(True)  # Placeholder

    def test_edge_cases(self):
        \"\"\"Test edge cases and boundary conditions\"\"\"
        # TODO: Implement edge case tests
        pass

    def test_error_handling(self):
        \"\"\"Test proper error handling\"\"\"
        # TODO: Test error conditions
        pass

    def test_performance(self):
        \"\"\"Test performance requirements\"\"\"
        # TODO: Add performance tests if needed
        pass

if __name__ == '__main__':
    unittest.main()
"""
        return test_template.strip()

    def _create_test_plan(self, task: CodeTask) -> str:
        """Create a comprehensive test plan"""
        return f"""
# Test Plan for: {task.title}

## Test Strategy
{task.description}

## Test Types Required
{self._identify_test_types(task)}

## Test Coverage Goals
Target Coverage: {self._estimate_test_coverage(task) * 100:.0f}%

## Test Scenarios

### 1. Happy Path Tests
- Test normal operation with valid inputs
- Verify expected outputs are produced
- Check state changes are correct

### 2. Edge Case Tests
- Test boundary conditions
- Test empty/null inputs
- Test maximum/minimum values

### 3. Error Handling Tests
- Test invalid inputs
- Test network failures (if applicable)
- Test resource exhaustion

### 4. Integration Tests
- Test interaction with other components
- Test data flow between modules
- Test configuration changes

## Testing Challenges
{self._identify_testing_challenges(task)}

## Test Environment Setup
- Required test data
- Mock configurations
- Test database setup (if needed)
"""

    def _assess_testability(self, code: str) -> float:
        """Assess how testable the code is"""
        testability = 0.5  # Base score

        # Functions are more testable than complex scripts
        function_count = code.count('def ')
        if function_count > 0:
            testability += 0.3

        # Clear input/output makes testing easier
        if 'return' in code:
            testability += 0.2

        return min(testability, 1.0)

    def _suggest_additional_tests(self, code: str) -> List[str]:
        """Suggest additional tests that might be needed"""
        suggestions = []

        if 'async' in code:
            suggestions.append("Add tests for async/await functionality")
        if 'try:' in code:
            suggestions.append("Test exception handling paths")
        if 'json' in code.lower():
            suggestions.append("Test JSON parsing edge cases")

        return suggestions

    def _identify_edge_cases(self, code: str) -> List[str]:
        """Identify potential edge cases to test"""
        edge_cases = []

        if 'len(' in code:
            edge_cases.append("Empty collections")
        if '/' in code:
            edge_cases.append("Division by zero")
        if '[' in code:
            edge_cases.append("Index out of bounds")

        return edge_cases

class CollaborativeMultiAgentSystem:
    """
    🤖 Collaborative Multi-Agent System

    Coordinates multiple specialized agents working together on complex code tasks
    """

    def __init__(self, workspace_path: str):
        self.workspace_path = Path(workspace_path)
        self.agents: Dict[AgentRole, BaseAgent] = {}
        self.active_tasks: Dict[str, CodeTask] = {}
        self.task_assignments: Dict[str, List[str]] = {}  # task_id -> agent_ids
        self.collaboration_history: List[CollaborationResult] = []

        # Initialize default agents
        self._initialize_agents()

    def _initialize_agents(self):
        """Initialize the default set of agents"""
        self.agents[AgentRole.ARCHITECT] = ArchitectAgent(str(self.workspace_path))
        self.agents[AgentRole.REFACTOR_SPECIALIST] = RefactorSpecialistAgent(str(self.workspace_path))
        self.agents[AgentRole.TEST_ENGINEER] = TestEngineerAgent(str(self.workspace_path))

        logger.info(f"🤖 Initialized {len(self.agents)} collaborative agents")

    async def submit_task(self, task: CodeTask) -> str:
        """Submit a new task to the collaborative system"""
        self.active_tasks[task.task_id] = task

        # Assign appropriate agents
        assigned_agents = await self._assign_agents_to_task(task)
        self.task_assignments[task.task_id] = assigned_agents

        logger.info(f"📋 Task '{task.title}' submitted with {len(assigned_agents)} agents assigned")
        return task.task_id

    async def _assign_agents_to_task(self, task: CodeTask) -> List[str]:
        """Assign the best agents to a task"""
        assigned_agents = []

        for role in task.required_roles:
            if role in self.agents:
                agent = self.agents[role]
                if await agent.can_handle_task(task):
                    assigned_agents.append(agent.agent_id)
                    agent.current_tasks.add(task.task_id)

        return assigned_agents

    async def execute_collaborative_task(self, task_id: str) -> CollaborationResult:
        """Execute a task collaboratively"""
        if task_id not in self.active_tasks:
            raise ValueError(f"Task {task_id} not found")

        task = self.active_tasks[task_id]
        assigned_agent_ids = self.task_assignments.get(task_id, [])

        if not assigned_agent_ids:
            raise ValueError(f"No agents assigned to task {task_id}")

        start_time = time.time()
        contributions: List[AgentContribution] = []

        try:
            # Phase 1: Analysis - Each agent analyzes the task
            logger.info(f"🔍 Phase 1: Analysis for task '{task.title}'")
            analyses = {}
            for agent_id in assigned_agent_ids:
                agent = self._get_agent_by_id(agent_id)
                if agent:
                    analysis = await agent.analyze_task(task)
                    analyses[agent_id] = analysis

            # Phase 2: Contribution - Agents make their contributions in optimal order
            logger.info(f"⚡ Phase 2: Contributions for task '{task.title}'")
            contribution_order = self._determine_contribution_order(task, assigned_agent_ids)

            for agent_id in contribution_order:
                agent = self._get_agent_by_id(agent_id)
                if agent:
                    contribution = await agent.contribute_to_task(task, contributions)
                    contributions.append(contribution)
                    logger.info(f"✨ {agent.role.value} contributed: {contribution.contribution_type}")

            # Phase 3: Review - Agents review each other's contributions
            logger.info(f"🔍 Phase 3: Peer review for task '{task.title}'")
            reviews = []
            for contribution in contributions:
                for agent_id in assigned_agent_ids:
                    if agent_id != contribution.agent_id:  # Don't review your own work
                        agent = self._get_agent_by_id(agent_id)
                        if agent:
                            review = await agent.review_contribution(contribution, task)
                            reviews.append({
                                "reviewer": agent_id,
                                "contribution_id": contribution.agent_id,
                                "review": review
                            })

            # Phase 4: Integration - Combine contributions into final result
            logger.info(f"[TOOL] Phase 4: Integration for task '{task.title}'")
            final_code = self._integrate_contributions(contributions)
            quality_score = self._calculate_quality_score(contributions, reviews)

            completion_time = time.time() - start_time

            # Create result
            result = CollaborationResult(
                task_id=task_id,
                success=True,
                contributions=contributions,
                final_code=final_code,
                quality_score=quality_score,
                completion_time=completion_time,
                lessons_learned=self._extract_lessons_learned(contributions, reviews)
            )

            # Update agent performance metrics
            for agent_id in assigned_agent_ids:
                agent = self._get_agent_by_id(agent_id)
                if agent:
                    agent.update_performance_metrics(quality_score, completion_time, True)
                    agent.current_tasks.discard(task_id)
                    agent.completed_tasks.append(task_id)

            # Store result
            self.collaboration_history.append(result)

            # Clean up
            del self.active_tasks[task_id]
            del self.task_assignments[task_id]

            logger.info(f"✅ Collaborative task '{task.title}' completed successfully")
            return result

        except Exception as e:
            logger.error(f"❌ Collaborative task '{task.title}' failed: {e}")

            # Create failure result
            result = CollaborationResult(
                task_id=task_id,
                success=False,
                contributions=contributions,
                final_code="",
                quality_score=0.0,
                completion_time=time.time() - start_time,
                lessons_learned=[f"Task failed due to: {str(e)}"]
            )

            # Update agent performance metrics
            for agent_id in assigned_agent_ids:
                agent = self._get_agent_by_id(agent_id)
                if agent:
                    agent.update_performance_metrics(0.0, result.completion_time, False)
                    agent.current_tasks.discard(task_id)

            self.collaboration_history.append(result)
            return result

    def _get_agent_by_id(self, agent_id: str) -> Optional[BaseAgent]:
        """Get agent by ID"""
        for agent in self.agents.values():
            if agent.agent_id == agent_id:
                return agent
        return None

    def _determine_contribution_order(self, task: CodeTask, agent_ids: List[str]) -> List[str]:
        """Determine optimal order for agent contributions"""
        # Simple ordering: Architect first, then others, Test Engineer last
        ordered_agents = []

        # Architect always goes first
        for agent_id in agent_ids:
            agent = self._get_agent_by_id(agent_id)
            if agent and agent.role == AgentRole.ARCHITECT:
                ordered_agents.append(agent_id)
                break

        # Add others (except test engineer)
        for agent_id in agent_ids:
            agent = self._get_agent_by_id(agent_id)
            if agent and agent.role not in [AgentRole.ARCHITECT, AgentRole.TEST_ENGINEER]:
                if agent_id not in ordered_agents:
                    ordered_agents.append(agent_id)

        # Test engineer goes last
        for agent_id in agent_ids:
            agent = self._get_agent_by_id(agent_id)
            if agent and agent.role == AgentRole.TEST_ENGINEER:
                ordered_agents.append(agent_id)
                break

        return ordered_agents

    def _integrate_contributions(self, contributions: List[AgentContribution]) -> str:
        """Integrate all contributions into final code"""
        integrated_parts = []

        for contribution in contributions:
            if contribution.contribution_type in ["code_change", "code_refactor"]:
                integrated_parts.append(f"# {contribution.contribution_type.upper()} by {contribution.agent_id}")
                integrated_parts.append(contribution.content)
                integrated_parts.append("")
            elif contribution.contribution_type == "test_code":
                integrated_parts.append("# TEST CODE")
                integrated_parts.append(contribution.content)
                integrated_parts.append("")

        return '\n'.join(integrated_parts)

    def _calculate_quality_score(self, contributions: List[AgentContribution],
                               reviews: List[Dict[str, Any]]) -> float:
        """Calculate overall quality score"""
        if not contributions:
            return 0.0

        # Average contribution confidence scores
        avg_confidence = sum(c.confidence_score for c in contributions) / len(contributions)

        # Factor in review scores (simplified)
        review_bonus = 0.0
        if reviews:
            # Simple bonus for having reviews
            review_bonus = 0.1

        return min(1.0, avg_confidence + review_bonus)

    def _extract_lessons_learned(self, contributions: List[AgentContribution],
                               reviews: List[Dict[str, Any]]) -> List[str]:
        """Extract lessons learned from the collaboration"""
        lessons = []

        # Analyze contribution patterns
        if len(contributions) > 3:
            lessons.append("Complex tasks benefit from multiple specialized agents")

        # Analyze review quality
        if reviews:
            lessons.append("Peer review improves overall code quality")

        # Analyze agent types
        agent_types = set(c.agent_id.split('_')[0] for c in contributions)
        if 'architect' in agent_types:
            lessons.append("Architectural guidance improves code structure")

        return lessons

    def get_system_metrics(self) -> Dict[str, Any]:
        """Get comprehensive system metrics"""
        total_tasks = len(self.collaboration_history)
        successful_tasks = sum(1 for r in self.collaboration_history if r.success)

        if total_tasks == 0:
            return {"message": "No collaborative tasks completed yet"}

        avg_quality = sum(r.quality_score for r in self.collaboration_history) / total_tasks
        avg_completion_time = sum(r.completion_time for r in self.collaboration_history) / total_tasks

        # Agent performance
        agent_metrics = {}
        for role, agent in self.agents.items():
            agent_metrics[role.value] = agent.performance_metrics

        return {
            "total_collaborative_tasks": total_tasks,
            "success_rate": successful_tasks / total_tasks,
            "average_quality_score": avg_quality,
            "average_completion_time": avg_completion_time,
            "agent_performance": agent_metrics,
            "active_tasks": len(self.active_tasks),
            "collaboration_patterns": self._analyze_collaboration_patterns()
        }

    def _analyze_collaboration_patterns(self) -> Dict[str, Any]:
        """Analyze patterns in collaborative work"""
        if not self.collaboration_history:
            return {}

        # Analyze contribution types
        contribution_types = {}
        for result in self.collaboration_history:
            for contribution in result.contributions:
                contribution_types[contribution.contribution_type] = (
                    contribution_types.get(contribution.contribution_type, 0) + 1
                )

        # Analyze agent combinations
        agent_combinations = {}
        for result in self.collaboration_history:
            agents = sorted(set(c.agent_id for c in result.contributions))
            combo_key = '+'.join(agents)
            agent_combinations[combo_key] = agent_combinations.get(combo_key, 0) + 1

        return {
            "common_contribution_types": contribution_types,
            "effective_agent_combinations": agent_combinations,
            "average_agents_per_task": sum(len(r.contributions) for r in self.collaboration_history) / len(self.collaboration_history)
        }


# Example usage
if __name__ == "__main__":
    async def test_collaborative_system():
        """Test the collaborative multi-agent system"""
        print("🤖 Testing Collaborative Multi-Agent System")
        print("=" * 50)

        system = CollaborativeMultiAgentSystem(".")

        # Create a test task
        test_task = CodeTask(
            task_id="test_001",
            title="Optimize Data Processing Function",
            description="Improve the performance and readability of a data processing function",
            required_roles=[AgentRole.ARCHITECT, AgentRole.REFACTOR_SPECIALIST, AgentRole.TEST_ENGINEER],
            priority=TaskPriority.HIGH,
            file_paths=["data_processor.py"],
            estimated_complexity=6.0,
            dependencies=[],
            metadata={"language": "python", "domain": "data_processing"},
            created_timestamp=time.time()
        )

        # Submit and execute task
        task_id = await system.submit_task(test_task)
        print(f"📋 Task submitted: {task_id}")

        result = await system.execute_collaborative_task(task_id)
        print(f"✅ Task completed: Success={result.success}, Quality={result.quality_score:.2f}")

        # Get system metrics
        metrics = system.get_system_metrics()
        print(f"📊 System metrics: {metrics}")

        print("✅ Collaborative system test completed")

    # Run test
    asyncio.run(test_collaborative_system())
