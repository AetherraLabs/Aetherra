#!/usr/bin/env python3
"""
🔄 NeuroCode Background Task Scheduler
=====================================

Advanced task scheduling system for NeuroCode with support for:
- Background task execution
- Priority-based scheduling
- Automatic retry logic
- Task dependencies
- Performance monitoring
"""

import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum
import json
import uuid


class TaskPriority(Enum):
    """Task priority levels"""
    LOW = 1
    NORMAL = 3
    HIGH = 5
    CRITICAL = 8
    URGENT = 10


class TaskStatus(Enum):
    """Task execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"


@dataclass
class ScheduledTask:
    """Represents a scheduled task"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    function: Optional[Callable] = None
    args: tuple = field(default_factory=tuple)
    kwargs: dict = field(default_factory=dict)
    priority: TaskPriority = TaskPriority.NORMAL
    status: TaskStatus = TaskStatus.PENDING
    scheduled_time: Optional[datetime] = None
    max_retries: int = 3
    retry_count: int = 0
    retry_delay: float = 1.0
    timeout: Optional[float] = None
    dependencies: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Any = None
    error: Optional[str] = None
    metadata: Dict = field(default_factory=dict)


class BackgroundTaskScheduler:
    """Advanced background task scheduler for NeuroCode"""
    
    def __init__(self, max_workers: int = 4, enable_logging: bool = True):
        self.max_workers = max_workers
        self.enable_logging = enable_logging
        
        # Task storage
        self.tasks: Dict[str, ScheduledTask] = {}
        self.task_queue: List[ScheduledTask] = []
        self.running_tasks: Dict[str, ScheduledTask] = {}
        self.completed_tasks: List[ScheduledTask] = []
        
        # Worker management
        self.workers: List[threading.Thread] = []
        self.worker_pool_active = False
        self.shutdown_event = threading.Event()
        
        # Performance tracking
        self.stats = {
            "tasks_submitted": 0,
            "tasks_completed": 0,
            "tasks_failed": 0,
            "average_execution_time": 0.0,
            "total_execution_time": 0.0
        }
        
        # Event callbacks
        self.event_callbacks = {
            "task_started": [],
            "task_completed": [],
            "task_failed": [],
            "task_retrying": []
        }
        
        # Initialize scheduler
        self._start_scheduler()
    
    def _start_scheduler(self):
        """Start the background scheduler"""
        self.worker_pool_active = True
        
        # Start worker threads
        for i in range(self.max_workers):
            worker = threading.Thread(
                target=self._worker_loop,
                name=f"NeuroScheduler-Worker-{i+1}",
                daemon=True
            )
            worker.start()
            self.workers.append(worker)
        
        # Start scheduler thread
        scheduler_thread = threading.Thread(
            target=self._scheduler_loop,
            name="NeuroScheduler-Main",
            daemon=True
        )
        scheduler_thread.start()
        
        if self.enable_logging:
            print(f"🔄 Background Task Scheduler started with {self.max_workers} workers")
    
    def schedule_task(
        self,
        function: Callable,
        *args,
        name: str = "",
        priority: TaskPriority = TaskPriority.NORMAL,
        delay: float = 0.0,
        scheduled_time: Optional[datetime] = None,
        max_retries: int = 3,
        timeout: Optional[float] = None,
        dependencies: Optional[List[str]] = None,
        metadata: Optional[Dict] = None,
        **kwargs
    ) -> str:
        """Schedule a task for background execution"""
        
        # Calculate scheduled time
        if scheduled_time is None:
            scheduled_time = datetime.now() + timedelta(seconds=delay)
        
        # Create task
        task = ScheduledTask(
            name=name or function.__name__,
            function=function,
            args=args,
            kwargs=kwargs,
            priority=priority,
            scheduled_time=scheduled_time,
            max_retries=max_retries,
            timeout=timeout,
            dependencies=dependencies or [],
            metadata=metadata or {}
        )
        
        # Add to task storage
        self.tasks[task.id] = task
        self._add_to_queue(task)
        
        self.stats["tasks_submitted"] += 1
        
        if self.enable_logging:
            print(f"📋 Task scheduled: {task.name} (ID: {task.id[:8]}...)")
        
        return task.id
    
    def schedule_periodic_task(
        self,
        function: Callable,
        interval: float,
        *args,
        name: str = "",
        max_executions: Optional[int] = None,
        **kwargs
    ) -> str:
        """Schedule a task to run periodically"""
        
        execution_count = 0
        
        def periodic_wrapper():
            nonlocal execution_count
            while (max_executions is None or execution_count < max_executions) and self.worker_pool_active:
                try:
                    function(*args, **kwargs)
                    execution_count += 1
                    
                    if self.enable_logging:
                        print(f"🔄 Periodic task executed: {name} (#{execution_count})")
                    
                    time.sleep(interval)
                except Exception as e:
                    if self.enable_logging:
                        print(f"❌ Periodic task error: {name} - {e}")
                    break
        
        return self.schedule_task(
            periodic_wrapper,
            name=f"Periodic: {name}",
            priority=TaskPriority.LOW,
            **kwargs
        )
    
    def schedule_delayed_task(
        self,
        function: Callable,
        delay: float,
        *args,
        **kwargs
    ) -> str:
        """Schedule a task to run after a delay"""
        return self.schedule_task(
            function,
            *args,
            delay=delay,
            **kwargs
        )
    
    def cancel_task(self, task_id: str) -> bool:
        """Cancel a pending task"""
        if task_id in self.tasks:
            task = self.tasks[task_id]
            if task.status == TaskStatus.PENDING:
                task.status = TaskStatus.CANCELLED
                self._remove_from_queue(task_id)
                if self.enable_logging:
                    print(f"🚫 Task cancelled: {task.name}")
                return True
        return False
    
    def get_task_status(self, task_id: str) -> Optional[TaskStatus]:
        """Get the status of a task"""
        if task_id in self.tasks:
            return self.tasks[task_id].status
        return None
    
    def get_task_result(self, task_id: str) -> Any:
        """Get the result of a completed task"""
        if task_id in self.tasks:
            task = self.tasks[task_id]
            if task.status == TaskStatus.COMPLETED:
                return task.result
        return None
    
    def wait_for_task(self, task_id: str, timeout: Optional[float] = None) -> bool:
        """Wait for a task to complete"""
        start_time = time.time()
        
        while task_id in self.tasks:
            task = self.tasks[task_id]
            if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
                return task.status == TaskStatus.COMPLETED
            
            if timeout and (time.time() - start_time) > timeout:
                return False
            
            time.sleep(0.1)
        
        return False
    
    def add_event_callback(self, event: str, callback: Callable):
        """Add a callback for task events"""
        if event in self.event_callbacks:
            self.event_callbacks[event].append(callback)
    
    def get_statistics(self) -> Dict:
        """Get scheduler statistics"""
        return {
            **self.stats,
            "pending_tasks": len([t for t in self.tasks.values() if t.status == TaskStatus.PENDING]),
            "running_tasks": len(self.running_tasks),
            "completed_tasks": len([t for t in self.tasks.values() if t.status == TaskStatus.COMPLETED]),
            "failed_tasks": len([t for t in self.tasks.values() if t.status == TaskStatus.FAILED]),
            "worker_count": len(self.workers),
            "active": self.worker_pool_active
        }
    
    def get_task_list(self, status_filter: Optional[TaskStatus] = None) -> List[Dict]:
        """Get list of tasks with optional status filter"""
        tasks = []
        
        for task in self.tasks.values():
            if status_filter is None or task.status == status_filter:
                tasks.append({
                    "id": task.id,
                    "name": task.name,
                    "status": task.status.value,
                    "priority": task.priority.value,
                    "created_at": task.created_at.isoformat(),
                    "scheduled_time": task.scheduled_time.isoformat() if task.scheduled_time else None,
                    "retry_count": task.retry_count,
                    "metadata": task.metadata
                })
        
        return sorted(tasks, key=lambda x: x["created_at"], reverse=True)
    
    def _add_to_queue(self, task: ScheduledTask):
        """Add task to priority queue"""
        # Insert task in priority order
        inserted = False
        for i, queued_task in enumerate(self.task_queue):
            if task.priority.value > queued_task.priority.value:
                self.task_queue.insert(i, task)
                inserted = True
                break
        
        if not inserted:
            self.task_queue.append(task)
    
    def _remove_from_queue(self, task_id: str):
        """Remove task from queue"""
        self.task_queue = [t for t in self.task_queue if t.id != task_id]
    
    def _scheduler_loop(self):
        """Main scheduler loop"""
        while self.worker_pool_active:
            try:
                current_time = datetime.now()
                
                # Check for tasks ready to run
                ready_tasks = []
                for task in self.task_queue[:]:
                    if (task.scheduled_time and task.scheduled_time <= current_time and 
                        self._dependencies_satisfied(task) and
                        len(self.running_tasks) < self.max_workers):
                        ready_tasks.append(task)
                
                # Move ready tasks to running
                for task in ready_tasks:
                    self.task_queue.remove(task)
                    self.running_tasks[task.id] = task
                    task.status = TaskStatus.RUNNING
                    task.started_at = current_time
                
                time.sleep(0.1)  # Short sleep to prevent busy waiting
                
            except Exception as e:
                if self.enable_logging:
                    print(f"❌ Scheduler loop error: {e}")
    
    def _worker_loop(self):
        """Worker thread loop"""
        while self.worker_pool_active:
            try:
                # Get next task to execute
                task = None
                for task_id, running_task in list(self.running_tasks.items()):
                    if running_task.status == TaskStatus.RUNNING:
                        task = running_task
                        break
                
                if task:
                    self._execute_task(task)
                else:
                    time.sleep(0.1)  # No tasks available, short sleep
                    
            except Exception as e:
                if self.enable_logging:
                    print(f"❌ Worker loop error: {e}")
    
    def _execute_task(self, task: ScheduledTask):
        """Execute a single task"""
        try:
            # Trigger started callbacks
            for callback in self.event_callbacks["task_started"]:
                try:
                    callback(task)
                except Exception:
                    pass
            
            start_time = time.time()
            
            # Execute the task function
            if task.function:
                if task.timeout:
                    # Execute with timeout (simplified - would need proper timeout handling)
                    result = task.function(*task.args, **task.kwargs)
                else:
                    result = task.function(*task.args, **task.kwargs)
            
            execution_time = time.time() - start_time
            
            # Mark as completed
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now()
            task.result = result
            
            # Update statistics
            self.stats["tasks_completed"] += 1
            self.stats["total_execution_time"] += execution_time
            self.stats["average_execution_time"] = (
                self.stats["total_execution_time"] / self.stats["tasks_completed"]
            )
            
            # Trigger completed callbacks
            for callback in self.event_callbacks["task_completed"]:
                try:
                    callback(task)
                except Exception:
                    pass
            
            if self.enable_logging:
                print(f"✅ Task completed: {task.name} ({execution_time:.2f}s)")
                
        except Exception as e:
            # Handle task failure
            task.error = str(e)
            
            if task.retry_count < task.max_retries:
                # Retry the task
                task.retry_count += 1
                task.status = TaskStatus.RETRYING
                task.scheduled_time = datetime.now() + timedelta(seconds=task.retry_delay)
                
                # Move back to queue for retry
                del self.running_tasks[task.id]
                self._add_to_queue(task)
                
                # Trigger retrying callbacks
                for callback in self.event_callbacks["task_retrying"]:
                    try:
                        callback(task)
                    except Exception:
                        pass
                
                if self.enable_logging:
                    print(f"🔄 Task retrying: {task.name} (attempt {task.retry_count + 1})")
            else:
                # Mark as failed
                task.status = TaskStatus.FAILED
                task.completed_at = datetime.now()
                
                self.stats["tasks_failed"] += 1
                
                # Trigger failed callbacks
                for callback in self.event_callbacks["task_failed"]:
                    try:
                        callback(task)
                    except Exception:
                        pass
                
                if self.enable_logging:
                    print(f"❌ Task failed: {task.name} - {e}")
        
        finally:
            # Remove from running tasks if still there
            if task.id in self.running_tasks:
                del self.running_tasks[task.id]
    
    def _dependencies_satisfied(self, task: ScheduledTask) -> bool:
        """Check if all task dependencies are satisfied"""
        for dep_id in task.dependencies:
            if dep_id in self.tasks:
                dep_task = self.tasks[dep_id]
                if dep_task.status != TaskStatus.COMPLETED:
                    return False
            else:
                return False  # Dependency not found
        return True
    
    def shutdown(self, timeout: float = 30.0):
        """Shutdown the scheduler gracefully"""
        if self.enable_logging:
            print("🔄 Shutting down Background Task Scheduler...")
        
        self.worker_pool_active = False
        self.shutdown_event.set()
        
        # Wait for workers to finish
        start_time = time.time()
        for worker in self.workers:
            remaining_time = timeout - (time.time() - start_time)
            if remaining_time > 0:
                worker.join(timeout=remaining_time)
        
        if self.enable_logging:
            print("✅ Background Task Scheduler shut down")
    
    def save_tasks_to_file(self, filename: str):
        """Save task history to file"""
        task_data = []
        for task in self.tasks.values():
            task_dict = {
                "id": task.id,
                "name": task.name,
                "status": task.status.value,
                "priority": task.priority.value,
                "created_at": task.created_at.isoformat(),
                "scheduled_time": task.scheduled_time.isoformat() if task.scheduled_time else None,
                "started_at": task.started_at.isoformat() if task.started_at else None,
                "completed_at": task.completed_at.isoformat() if task.completed_at else None,
                "retry_count": task.retry_count,
                "error": task.error,
                "metadata": task.metadata
            }
            task_data.append(task_dict)
        
        with open(filename, 'w') as f:
            json.dump({
                "tasks": task_data,
                "statistics": self.get_statistics(),
                "saved_at": datetime.now().isoformat()
            }, f, indent=2)


# Example usage and testing functions
def example_task(name: str, duration: float = 1.0) -> str:
    """Example task for testing"""
    time.sleep(duration)
    return f"Task {name} completed successfully"


def example_failing_task() -> str:
    """Example failing task for testing retry logic"""
    import random
    if random.random() < 0.7:  # 70% chance of failure
        raise Exception("Random task failure")
    return "Task succeeded after retries"


if __name__ == "__main__":
    # Demo the background scheduler
    print("🧬 NeuroCode Background Task Scheduler Demo")
    print("=" * 50)
    
    scheduler = BackgroundTaskScheduler(max_workers=2)
    
    # Schedule some example tasks
    task1 = scheduler.schedule_task(
        example_task,
        "Alpha",
        1.0,
        name="Alpha Task",
        priority=TaskPriority.HIGH
    )
    
    task2 = scheduler.schedule_task(
        example_task,
        "Beta",
        0.5,
        name="Beta Task",
        priority=TaskPriority.NORMAL,
        delay=2.0
    )
    
    task3 = scheduler.schedule_task(
        example_failing_task,
        name="Failing Task",
        priority=TaskPriority.LOW,
        max_retries=2
    )
    
    # Schedule a periodic task
    periodic_task = scheduler.schedule_periodic_task(
        lambda: print("🔄 Periodic heartbeat"),
        interval=3.0,
        name="Heartbeat",
        max_executions=3
    )
    
    print("\n📊 Scheduler Statistics:")
    print(scheduler.get_statistics())
    
    # Wait for tasks to complete
    print("\n⏳ Waiting for tasks to complete...")
    time.sleep(8)
    
    print("\n📊 Final Statistics:")
    print(scheduler.get_statistics())
    
    print("\n📋 Task List:")
    for task in scheduler.get_task_list():
        print(f"  {task['name']}: {task['status']}")
    
    scheduler.shutdown()
