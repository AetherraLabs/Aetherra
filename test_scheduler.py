#!/usr/bin/env python3
"""
Test the background task scheduler
"""

from core.task_scheduler import BackgroundTaskScheduler, TaskPriority
import time

print('🔄 Testing Background Task Scheduler')
scheduler = BackgroundTaskScheduler(max_workers=2)

def test_task(name):
    print(f'  Executing task: {name}')
    time.sleep(0.5)
    return f'Result from {name}'

# Schedule some tasks
task1 = scheduler.schedule_task(test_task, 'Task-1', priority=TaskPriority.HIGH)
task2 = scheduler.schedule_task(test_task, 'Task-2', priority=TaskPriority.NORMAL)

print('Tasks scheduled, waiting for completion...')
time.sleep(3)

print('Final statistics:', scheduler.get_statistics())
scheduler.shutdown()
print('✅ Task scheduler test completed')
