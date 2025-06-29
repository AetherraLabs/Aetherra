#!/usr/bin/env python3
print('Testing OpenAI client initialization fix...')
print('=' * 50)

# Import multiple modules that use ai_runtime
from core.enhanced_interpreter import EnhancedNeuroCodeInterpreter
print('Enhanced interpreter loaded')

from core.agent import NeuroAgent  
print('Agent loaded')

from core.goal_system import GoalSystem
print('Goal system loaded')

print('=' * 50)
print('Test complete - OpenAI message should appear only once above')
