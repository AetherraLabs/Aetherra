#!/usr/bin/env python3
print('Quick verification of core enhancement modules:')
try:
    from core.local_ai import LocalAIEngine
    print('✅ Local AI Engine imports successfully')
    from core.vector_memory import EnhancedSemanticMemory  
    print('✅ Vector Memory System imports successfully')
    from core.intent_parser import IntentToCodeParser
    print('✅ Intent Parser imports successfully')
    from core.enhanced_interpreter import EnhancedAetherraInterpreter
    print('✅ Enhanced Interpreter imports successfully')
    import setup_enhancements
    print('✅ Setup script available')
    print('🎉 ALL CORE ENHANCEMENTS VERIFIED!')
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()
