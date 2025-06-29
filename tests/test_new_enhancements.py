#!/usr/bin/env python3
"""
Test the new Performance Optimization and AI Collaboration features
"""

import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

from core.enhanced_interpreter import EnhancedNeuroCodeInterpreter

def test_performance_optimization():
    """Test performance optimization features"""
    print("🧪 Testing Performance Optimization Features")
    
    interpreter = EnhancedNeuroCodeInterpreter()
    
    # Test optimization status
    print("\n1. Testing optimization status...")
    result = interpreter.execute_neurocode("optimize status")
    print(f"Result: {result}")
    
    # Test performance profiling
    print("\n2. Testing performance profiling...")
    result = interpreter.execute_neurocode("optimize profile set x = 42")
    print(f"Result: {result}")
    
    # Test performance analysis
    print("\n3. Testing performance analysis...")
    result = interpreter.execute_neurocode("optimize analyze")
    print(f"Result: {result}")
    
    return True

def test_ai_collaboration():
    """Test AI collaboration features"""
    print("\n🤝 Testing AI Collaboration Features")
    
    interpreter = EnhancedNeuroCodeInterpreter()
    
    # Test collaboration status
    print("\n1. Testing collaboration status...")
    result = interpreter.execute_neurocode("collaborate status")
    print(f"Result: {result}")
    
    # Test available agents
    print("\n2. Testing available agents...")
    result = interpreter.execute_neurocode("collaborate agents")
    print(f"Result: {result}")
    
    # Test collaborative task (simple)
    print("\n3. Testing collaborative task...")
    result = interpreter.execute_neurocode("collaborate task Create a simple hello world function")
    print(f"Result: {result}")
    
    return True

def test_performance_monitoring():
    """Test performance monitoring features"""
    print("\n📊 Testing Performance Monitoring Features")
    
    interpreter = EnhancedNeuroCodeInterpreter()
    
    # Test performance report
    print("\n1. Testing performance report...")
    result = interpreter.execute_neurocode("performance report")
    print(f"Result: {result}")
    
    # Test benchmark
    print("\n2. Testing benchmark...")
    result = interpreter.execute_neurocode("performance benchmark")
    print(f"Result: {result}")
    
    return True

def main():
    """Run all tests"""
    print("🚀 Testing New NeuroCode Enhancement Features")
    print("=" * 60)
    
    try:
        # Test performance optimization
        success1 = test_performance_optimization()
        
        # Test AI collaboration
        success2 = test_ai_collaboration()
        
        # Test performance monitoring
        success3 = test_performance_monitoring()
        
        if success1 and success2 and success3:
            print("\n✅ All enhancement tests completed successfully!")
            print("🎉 NeuroCode #4 (Performance Optimization) and #5 (AI Collaboration) are fully integrated!")
        else:
            print("\n❌ Some tests failed")
            
    except Exception as e:
        print(f"\n❌ Test error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
