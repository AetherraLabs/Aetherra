#!/usr/bin/env python3
"""
🤖 Multi-Agent Framework for NeuroCode
Orchestrates specialized AI agents for complex tasks

This system enables collaborative AI processing through specialized agents
that work together to solve complex problems and optimize workflows.
"""

import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

class AgentRole(Enum):
    """Specialized agent roles"""
    PLANNER = "planner"
    MEMORY_ANALYZER = "memory_analyzer"
    BUG_HUNTER = "bug_hunter"
    OPTIMIZER = "optimizer"
    RESEARCHER = "researcher"
    COORDINATOR = "coordinator"
    EXECUTOR = "executor"
    VALIDATOR = "validator"

@dataclass
class AgentTask:
    """Task definition for agents"""
    id: str
    role: AgentRole
    description: str
    priority: int
    dependencies: List[str]
    context: Dict[str, Any]
    status: str = "pending"
    result: Optional[Dict] = None
    created_at: str = ""
    started_at: Optional[str] = None
    completed_at: Optional[str] = None

class SpecializedAgent:
    """Base class for specialized agents"""
    
    def __init__(self, role: AgentRole, name: str, capabilities: List[str]):
        self.role = role
        self.name = name
        self.capabilities = capabilities
        self.active_tasks = []
        self.completed_tasks = []
        self.performance_metrics = {
            "tasks_completed": 0,
            "success_rate": 0.0,
            "average_completion_time": 0.0
        }
    
    async def execute_task(self, task: AgentTask) -> Dict:
        """Execute a task assigned to this agent"""
        task.status = "in_progress"
        task.started_at = datetime.now().isoformat()
        
        try:
            result = await self._process_task(task)
            task.status = "completed"
            task.result = result
            task.completed_at = datetime.now().isoformat()
            
            self._update_metrics(task, success=True)
            return result
            
        except Exception as e:
            task.status = "failed"
            task.result = {"error": str(e)}
            task.completed_at = datetime.now().isoformat()
            
            self._update_metrics(task, success=False)
            raise
    
    async def _process_task(self, task: AgentTask) -> Dict:
        """Override in specialized agents"""
        raise NotImplementedError("Agents must implement _process_task")
    
    def _update_metrics(self, task: AgentTask, success: bool):
        """Update performance metrics"""
        self.performance_metrics["tasks_completed"] += 1
        
        if success:
            # Calculate completion time
            if task.started_at and task.completed_at:
                start = datetime.fromisoformat(task.started_at)
                end = datetime.fromisoformat(task.completed_at)
                completion_time = (end - start).total_seconds()
                
                # Update average completion time
                current_avg = self.performance_metrics["average_completion_time"]
                total_tasks = self.performance_metrics["tasks_completed"]
                new_avg = ((current_avg * (total_tasks - 1)) + completion_time) / total_tasks
                self.performance_metrics["average_completion_time"] = new_avg
        
        # Update success rate
        completed_tasks = self.performance_metrics["tasks_completed"]
        successful_tasks = len([t for t in self.completed_tasks if t.status == "completed"])
        self.performance_metrics["success_rate"] = successful_tasks / completed_tasks if completed_tasks > 0 else 0.0

class PlannerAgent(SpecializedAgent):
    """Strategic planning and task decomposition"""
    
    def __init__(self):
        super().__init__(
            role=AgentRole.PLANNER,
            name="Strategic Planner",
            capabilities=["task_decomposition", "strategic_planning", "resource_allocation", "timeline_estimation"]
        )
    
    async def _process_task(self, task: AgentTask) -> Dict:
        """Plan and decompose complex tasks"""
        description = task.context.get("objective", "")
        complexity = task.context.get("complexity", "medium")
        
        # Analyze the objective
        plan_components = self._analyze_objective(description)
        
        # Create execution plan
        execution_plan = self._create_execution_plan(plan_components, complexity)
        
        # Estimate resources and timeline
        estimates = self._estimate_resources(execution_plan)
        
        return {
            "plan_components": plan_components,
            "execution_plan": execution_plan,
            "estimates": estimates,
            "recommendations": self._generate_recommendations(plan_components)
        }
    
    def _analyze_objective(self, description: str) -> Dict:
        """Analyze objective and identify key components"""
        description_lower = description.lower()
        
        components = {
            "goals": [],
            "constraints": [],
            "resources_needed": [],
            "stakeholders": [],
            "success_criteria": []
        }
        
        # Extract goals
        goal_keywords = ["achieve", "complete", "build", "create", "develop", "implement"]
        for keyword in goal_keywords:
            if keyword in description_lower:
                # Simple extraction - in a real implementation, this would use NLP
                components["goals"].append(f"Primary objective involving {keyword}")
        
        # Extract constraints
        constraint_keywords = ["within", "limit", "budget", "deadline", "must", "cannot"]
        for keyword in constraint_keywords:
            if keyword in description_lower:
                components["constraints"].append(f"Constraint related to {keyword}")
        
        return components
    
    def _create_execution_plan(self, components: Dict, complexity: str) -> List[Dict]:
        """Create detailed execution plan"""
        plan = []
        
        # Phase 1: Analysis and Setup
        plan.append({
            "phase": "analysis_setup",
            "tasks": [
                "Analyze requirements in detail",
                "Set up project structure",
                "Initialize monitoring systems"
            ],
            "estimated_duration": "1-2 hours" if complexity == "low" else "2-4 hours"
        })
        
        # Phase 2: Core Implementation
        plan.append({
            "phase": "core_implementation", 
            "tasks": [
                "Implement core functionality",
                "Integrate with existing systems",
                "Handle edge cases"
            ],
            "estimated_duration": "4-8 hours" if complexity == "low" else "8-16 hours"
        })
        
        # Phase 3: Testing and Validation
        plan.append({
            "phase": "testing_validation",
            "tasks": [
                "Comprehensive testing",
                "Performance validation",
                "Security review"
            ],
            "estimated_duration": "2-4 hours"
        })
        
        # Phase 4: Deployment and Monitoring
        plan.append({
            "phase": "deployment_monitoring",
            "tasks": [
                "Deploy to production",
                "Set up monitoring",
                "Document procedures"
            ],
            "estimated_duration": "1-2 hours"
        })
        
        return plan
    
    def _estimate_resources(self, execution_plan: List[Dict]) -> Dict:
        """Estimate required resources"""
        total_duration_min = sum([int(phase["estimated_duration"].split("-")[0]) for phase in execution_plan])
        total_duration_max = sum([int(phase["estimated_duration"].split("-")[1].split()[0]) for phase in execution_plan])
        
        return {
            "estimated_time": f"{total_duration_min}-{total_duration_max} hours",
            "agents_needed": len(execution_plan),
            "complexity_score": len(execution_plan) * 2,
            "risk_level": "medium"
        }
    
    def _generate_recommendations(self, components: Dict) -> List[str]:
        """Generate strategic recommendations"""
        recommendations = [
            "Start with thorough analysis phase",
            "Implement monitoring from the beginning",
            "Plan for iterative improvements"
        ]
        
        if len(components.get("constraints", [])) > 2:
            recommendations.append("Pay special attention to constraint management")
        
        if len(components.get("goals", [])) > 3:
            recommendations.append("Consider breaking into smaller sub-projects")
        
        return recommendations

class MemoryAnalyzerAgent(SpecializedAgent):
    """Memory pattern analysis and optimization"""
    
    def __init__(self):
        super().__init__(
            role=AgentRole.MEMORY_ANALYZER,
            name="Memory Analyzer",
            capabilities=["pattern_analysis", "memory_optimization", "data_correlation", "insight_generation"]
        )
    
    async def _process_task(self, task: AgentTask) -> Dict:
        """Analyze memory patterns and provide insights"""
        memory_data = task.context.get("memory_data", [])
        analysis_type = task.context.get("analysis_type", "comprehensive")
        
        # Perform analysis based on type
        if analysis_type == "patterns":
            result = self._analyze_patterns(memory_data)
        elif analysis_type == "optimization":
            result = self._optimize_memory(memory_data)
        else:
            result = self._comprehensive_analysis(memory_data)
        
        return result
    
    def _analyze_patterns(self, memory_data: List) -> Dict:
        """Analyze patterns in memory data"""
        if not memory_data:
            return {"patterns": [], "insights": ["No memory data available for analysis"]}
        
        patterns = []
        
        # Temporal patterns
        timestamps = [item.get("timestamp") for item in memory_data if item.get("timestamp")]
        if timestamps:
            patterns.append({
                "type": "temporal",
                "description": f"Found {len(timestamps)} timestamped memories",
                "frequency": len(timestamps) / len(memory_data)
            })
        
        # Content patterns
        content_types = {}
        for item in memory_data:
            content_type = item.get("type", "unknown")
            content_types[content_type] = content_types.get(content_type, 0) + 1
        
        for content_type, count in content_types.items():
            patterns.append({
                "type": "content",
                "description": f"{content_type} memories",
                "count": count,
                "percentage": (count / len(memory_data)) * 100
            })
        
        insights = self._generate_insights(patterns)
        
        return {
            "patterns": patterns,
            "insights": insights,
            "recommendations": self._memory_recommendations(patterns)
        }
    
    def _optimize_memory(self, memory_data: List) -> Dict:
        """Optimize memory usage and organization"""
        optimizations = []
        
        # Identify duplicate or similar memories
        duplicates = self._find_duplicates(memory_data)
        if duplicates:
            optimizations.append({
                "type": "deduplication",
                "potential_savings": f"{len(duplicates)} duplicate entries",
                "action": "Merge or remove duplicate memories"
            })
        
        # Identify outdated memories
        outdated = self._find_outdated(memory_data)
        if outdated:
            optimizations.append({
                "type": "cleanup",
                "potential_savings": f"{len(outdated)} outdated entries",
                "action": "Archive or remove outdated memories"
            })
        
        return {
            "optimizations": optimizations,
            "estimated_improvement": f"{len(optimizations * 10)}% efficiency gain",
            "priority_actions": [opt["action"] for opt in optimizations[:3]]
        }
    
    def _comprehensive_analysis(self, memory_data: List) -> Dict:
        """Perform comprehensive memory analysis"""
        patterns_result = self._analyze_patterns(memory_data)
        optimization_result = self._optimize_memory(memory_data)
        
        return {
            "summary": {
                "total_memories": len(memory_data),
                "unique_types": len(set(item.get("type", "unknown") for item in memory_data)),
                "patterns_found": len(patterns_result["patterns"]),
                "optimization_opportunities": len(optimization_result["optimizations"])
            },
            "patterns": patterns_result,
            "optimizations": optimization_result,
            "overall_health": self._assess_memory_health(memory_data)
        }
    
    def _find_duplicates(self, memory_data: List) -> List:
        """Find duplicate memory entries"""
        seen = set()
        duplicates = []
        
        for item in memory_data:
            # Simple duplicate detection based on content similarity
            content = str(item.get("content", "")) + str(item.get("user_message", ""))
            content_hash = hash(content.lower().strip())
            
            if content_hash in seen:
                duplicates.append(item)
            else:
                seen.add(content_hash)
        
        return duplicates
    
    def _find_outdated(self, memory_data: List) -> List:
        """Find outdated memory entries"""
        from datetime import datetime, timedelta
        
        cutoff_date = datetime.now() - timedelta(days=30)  # Consider 30+ days old as potentially outdated
        outdated = []
        
        for item in memory_data:
            timestamp_str = item.get("timestamp")
            if timestamp_str:
                try:
                    timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                    if timestamp < cutoff_date:
                        outdated.append(item)
                except ValueError:
                    continue
        
        return outdated
    
    def _generate_insights(self, patterns: List) -> List[str]:
        """Generate insights from patterns"""
        insights = []
        
        content_patterns = [p for p in patterns if p["type"] == "content"]
        if content_patterns:
            most_common = max(content_patterns, key=lambda x: x["count"])
            insights.append(f"Most common memory type: {most_common['description']} ({most_common['percentage']:.1f}%)")
        
        temporal_patterns = [p for p in patterns if p["type"] == "temporal"]
        if temporal_patterns:
            insights.append(f"Temporal coverage: {temporal_patterns[0]['frequency']:.1%} of memories have timestamps")
        
        return insights
    
    def _memory_recommendations(self, patterns: List) -> List[str]:
        """Generate memory optimization recommendations"""
        recommendations = [
            "Regular memory analysis helps maintain optimal performance",
            "Consider archiving old memories to improve access speed"
        ]
        
        content_patterns = [p for p in patterns if p["type"] == "content"]
        if len(content_patterns) > 5:
            recommendations.append("High content diversity - consider categorization system")
        
        return recommendations
    
    def _assess_memory_health(self, memory_data: List) -> Dict:
        """Assess overall memory system health"""
        if not memory_data:
            return {"status": "empty", "score": 0, "recommendations": ["Add initial memories to begin tracking"]}
        
        # Simple health scoring
        score = min(100, len(memory_data) * 2)  # Base score on quantity
        
        # Adjust for diversity
        types = set(item.get("type", "unknown") for item in memory_data)
        diversity_bonus = min(20, len(types) * 5)
        score += diversity_bonus
        
        # Assess status
        if score >= 80:
            status = "excellent"
        elif score >= 60:
            status = "good"
        elif score >= 40:
            status = "fair"
        else:
            status = "poor"
        
        return {
            "status": status,
            "score": score,
            "factors": {
                "quantity": len(memory_data),
                "diversity": len(types),
                "health_indicators": ["timestamps", "content_types", "organization"]
            }
        }

class BugHunterAgent(SpecializedAgent):
    """Error detection and debugging assistance"""
    
    def __init__(self):
        super().__init__(
            role=AgentRole.BUG_HUNTER,
            name="Bug Hunter",
            capabilities=["error_analysis", "pattern_recognition", "diagnostic_suggestions", "fix_recommendations"]
        )
    
    async def _process_task(self, task: AgentTask) -> Dict:
        """Hunt for bugs and provide diagnostic information"""
        error_data = task.context.get("error_data", {})
        code_context = task.context.get("code_context", "")
        analysis_depth = task.context.get("depth", "standard")
        
        # Analyze the error
        error_analysis = self._analyze_error(error_data)
        
        # Look for patterns
        patterns = self._identify_error_patterns(error_data, code_context)
        
        # Generate suggestions
        suggestions = self._generate_fix_suggestions(error_analysis, patterns)
        
        # Create debugging plan
        debug_plan = self._create_debug_plan(error_analysis, analysis_depth)
        
        return {
            "error_analysis": error_analysis,
            "patterns": patterns,
            "suggestions": suggestions,
            "debug_plan": debug_plan,
            "confidence": self._calculate_confidence(error_analysis, patterns)
        }
    
    def _analyze_error(self, error_data: Dict) -> Dict:
        """Analyze error information"""
        error_type = error_data.get("type", "unknown")
        error_message = error_data.get("message", "")
        
        analysis = {
            "category": self._categorize_error(error_type, error_message),
            "severity": self._assess_severity(error_type, error_message),
            "likely_causes": self._identify_likely_causes(error_type, error_message),
            "impact": self._assess_impact(error_type)
        }
        
        return analysis
    
    def _categorize_error(self, error_type: str, message: str) -> str:
        """Categorize the error type"""
        message_lower = message.lower()
        
        if "import" in message_lower or "module" in message_lower:
            return "import_error"
        elif "attribute" in message_lower:
            return "attribute_error"
        elif "syntax" in message_lower:
            return "syntax_error"
        elif "permission" in message_lower or "access" in message_lower:
            return "permission_error"
        elif "connection" in message_lower or "network" in message_lower:
            return "network_error"
        elif "memory" in message_lower or "allocation" in message_lower:
            return "memory_error"
        else:
            return "runtime_error"
    
    def _assess_severity(self, error_type: str, message: str) -> str:
        """Assess error severity"""
        critical_keywords = ["crash", "fatal", "critical", "segmentation", "memory"]
        high_keywords = ["exception", "error", "failed"]
        
        message_lower = message.lower()
        
        if any(keyword in message_lower for keyword in critical_keywords):
            return "critical"
        elif any(keyword in message_lower for keyword in high_keywords):
            return "high"
        else:
            return "medium"
    
    def _identify_likely_causes(self, error_type: str, message: str) -> List[str]:
        """Identify likely causes of the error"""
        causes = []
        message_lower = message.lower()
        
        if "module not found" in message_lower:
            causes.extend([
                "Missing dependency installation",
                "Incorrect import path",
                "Virtual environment not activated"
            ])
        elif "attribute" in message_lower:
            causes.extend([
                "Object type mismatch",
                "Method or property doesn't exist",
                "Incorrect object initialization"
            ])
        elif "permission denied" in message_lower:
            causes.extend([
                "Insufficient file permissions",
                "Running without admin privileges",
                "File/directory locked by another process"
            ])
        else:
            causes.extend([
                "Logic error in code",
                "Unexpected input values",
                "Resource unavailability"
            ])
        
        return causes
    
    def _assess_impact(self, error_type: str) -> Dict:
        """Assess the impact of the error"""
        impact_map = {
            "syntax_error": {"blocking": True, "scope": "local"},
            "import_error": {"blocking": True, "scope": "module"},
            "runtime_error": {"blocking": False, "scope": "function"},
            "permission_error": {"blocking": True, "scope": "system"},
            "network_error": {"blocking": False, "scope": "external"}
        }
        
        return impact_map.get(error_type, {"blocking": False, "scope": "unknown"})
    
    def _identify_error_patterns(self, error_data: Dict, code_context: str) -> List[Dict]:
        """Identify patterns in errors"""
        patterns = []
        
        # Check for common patterns
        if "import" in str(error_data).lower():
            patterns.append({
                "type": "import_pattern",
                "description": "Import-related error pattern detected",
                "frequency": "common",
                "solutions": ["Check module installation", "Verify import paths"]
            })
        
        # Add more pattern detection logic here
        return patterns
    
    def _generate_fix_suggestions(self, error_analysis: Dict, patterns: List[Dict]) -> List[Dict]:
        """Generate fix suggestions based on analysis"""
        suggestions = []
        
        category = error_analysis.get("category", "unknown")
        
        if category == "import_error":
            suggestions.extend([
                {
                    "action": "Install missing package",
                    "command": "pip install <package_name>",
                    "priority": "high"
                },
                {
                    "action": "Check import path",
                    "description": "Verify the module path is correct",
                    "priority": "medium"
                }
            ])
        elif category == "attribute_error":
            suggestions.extend([
                {
                    "action": "Check object type",
                    "description": "Verify the object has the expected attributes",
                    "priority": "high"
                },
                {
                    "action": "Review documentation",
                    "description": "Check API documentation for correct usage",
                    "priority": "medium"
                }
            ])
        
        return suggestions
    
    def _create_debug_plan(self, error_analysis: Dict, depth: str) -> List[str]:
        """Create a systematic debugging plan"""
        plan = [
            "1. Reproduce the error consistently",
            "2. Examine the error message and stack trace",
            "3. Check recent code changes"
        ]
        
        if depth in ["deep", "comprehensive"]:
            plan.extend([
                "4. Add logging to trace execution flow",
                "5. Test with minimal reproduction case",
                "6. Review related code components",
                "7. Check environment and dependencies"
            ])
        
        severity = error_analysis.get("severity", "medium")
        if severity == "critical":
            plan.insert(1, "1.5. Implement immediate workaround if possible")
        
        return plan
    
    def _calculate_confidence(self, error_analysis: Dict, patterns: List[Dict]) -> float:
        """Calculate confidence in the analysis"""
        base_confidence = 0.7
        
        # Increase confidence for known error categories
        category = error_analysis.get("category", "unknown")
        if category != "unknown":
            base_confidence += 0.1
        
        # Increase confidence for pattern matches
        if patterns:
            base_confidence += 0.1 * min(len(patterns), 2)
        
        return min(base_confidence, 1.0)

class MultiAgentManager:
    """Orchestrates multiple specialized agents"""
    
    def __init__(self):
        self.agents = {}
        self.task_queue = []
        self.active_tasks = {}
        self.completed_tasks = []
        
        # Initialize default agents
        self._initialize_agents()
    
    def _initialize_agents(self):
        """Initialize the default set of agents"""
        self.agents[AgentRole.PLANNER] = PlannerAgent()
        self.agents[AgentRole.MEMORY_ANALYZER] = MemoryAnalyzerAgent()
        self.agents[AgentRole.BUG_HUNTER] = BugHunterAgent()
    
    async def submit_task(self, role: AgentRole, description: str, context: Dict, priority: int = 5) -> str:
        """Submit a task to the appropriate agent"""
        task_id = f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.task_queue)}"
        
        task = AgentTask(
            id=task_id,
            role=role,
            description=description,
            priority=priority,
            dependencies=[],
            context=context,
            created_at=datetime.now().isoformat()
        )
        
        self.task_queue.append(task)
        return task_id
    
    async def execute_task(self, task_id: str) -> Dict:
        """Execute a specific task"""
        task = next((t for t in self.task_queue if t.id == task_id), None)
        if not task:
            raise ValueError(f"Task {task_id} not found")
        
        agent = self.agents.get(task.role)
        if not agent:
            raise ValueError(f"No agent available for role {task.role}")
        
        # Move task to active
        self.task_queue.remove(task)
        self.active_tasks[task_id] = task
        
        try:
            result = await agent.execute_task(task)
            
            # Move to completed
            del self.active_tasks[task_id]
            self.completed_tasks.append(task)
            
            return {
                "task_id": task_id,
                "status": "completed",
                "result": result,
                "agent": agent.name,
                "completion_time": task.completed_at
            }
            
        except Exception as e:
            # Move to completed with error
            del self.active_tasks[task_id]
            self.completed_tasks.append(task)
            
            return {
                "task_id": task_id,
                "status": "failed",
                "error": str(e),
                "agent": agent.name
            }
    
    async def execute_workflow(self, tasks: List[Dict]) -> List[Dict]:
        """Execute a workflow of multiple tasks"""
        results = []
        
        for task_config in tasks:
            task_id = await self.submit_task(
                role=AgentRole(task_config["role"]),
                description=task_config["description"],
                context=task_config.get("context", {}),
                priority=task_config.get("priority", 5)
            )
            
            result = await self.execute_task(task_id)
            results.append(result)
            
            # If task failed and is critical, stop workflow
            if result["status"] == "failed" and task_config.get("critical", False):
                break
        
        return results
    
    def get_agent_status(self) -> Dict:
        """Get status of all agents"""
        status = {}
        
        for role, agent in self.agents.items():
            status[role.value] = {
                "name": agent.name,
                "capabilities": agent.capabilities,
                "active_tasks": len(agent.active_tasks),
                "completed_tasks": agent.performance_metrics["tasks_completed"],
                "success_rate": agent.performance_metrics["success_rate"],
                "avg_completion_time": agent.performance_metrics["average_completion_time"]
            }
        
        return status
    
    def get_task_status(self, task_id: str) -> Dict:
        """Get status of a specific task"""
        # Check active tasks
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]
            return {
                "id": task.id,
                "status": task.status,
                "role": task.role.value,
                "description": task.description,
                "created_at": task.created_at,
                "started_at": task.started_at
            }
        
        # Check completed tasks
        for task in self.completed_tasks:
            if task.id == task_id:
                return {
                    "id": task.id,
                    "status": task.status,
                    "role": task.role.value,
                    "description": task.description,
                    "created_at": task.created_at,
                    "started_at": task.started_at,
                    "completed_at": task.completed_at,
                    "result": task.result
                }
        
        # Check queued tasks
        for task in self.task_queue:
            if task.id == task_id:
                return {
                    "id": task.id,
                    "status": task.status,
                    "role": task.role.value,
                    "description": task.description,
                    "created_at": task.created_at
                }
        
        return {"error": f"Task {task_id} not found"}

# Demo usage example
async def demo_multi_agent_system():
    """Demonstrate the multi-agent system"""
    manager = MultiAgentManager()
    
    print("🤖 Multi-Agent System Demo")
    print("=" * 40)
    
    # Submit tasks to different agents
    tasks = [
        {
            "role": "planner",
            "description": "Plan a code optimization project",
            "context": {
                "objective": "Optimize NeuroCode performance and add new features",
                "complexity": "high"
            }
        },
        {
            "role": "memory_analyzer", 
            "description": "Analyze current memory patterns",
            "context": {
                "memory_data": [
                    {"type": "conversation", "timestamp": "2025-07-02T10:00:00", "content": "User asked about goals"},
                    {"type": "execution", "timestamp": "2025-07-02T10:05:00", "content": "Executed remember command"}
                ],
                "analysis_type": "comprehensive"
            }
        },
        {
            "role": "bug_hunter",
            "description": "Debug import error",
            "context": {
                "error_data": {
                    "type": "ImportError",
                    "message": "No module named 'missing_package'",
                    "stack_trace": "..."
                },
                "depth": "standard"
            }
        }
    ]
    
    # Execute workflow
    results = await manager.execute_workflow(tasks)
    
    print("\n📋 Workflow Results:")
    for i, result in enumerate(results, 1):
        print(f"\n{i}. Task: {result['task_id']}")
        print(f"   Status: {result['status']}")
        print(f"   Agent: {result['agent']}")
        if result['status'] == 'completed':
            print(f"   Result: {str(result['result'])[:100]}...")
    
    print("\n📊 Agent Status:")
    status = manager.get_agent_status()
    for role, info in status.items():
        print(f"\n{role.title()}:")
        print(f"   Name: {info['name']}")
        print(f"   Capabilities: {', '.join(info['capabilities'])}")
        print(f"   Tasks Completed: {info['completed_tasks']}")
        print(f"   Success Rate: {info['success_rate']:.1%}")

if __name__ == "__main__":
    asyncio.run(demo_multi_agent_system())
