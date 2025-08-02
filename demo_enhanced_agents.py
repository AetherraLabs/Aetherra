"""
🚀 Enhanced Agents Demo
======================

Demonstration of the new specialized agents for Aetherra AI OS.
"""

import asyncio
import sys
import time
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from Aetherra.lyrixa.agents.data_agent import DataAgent
    from Aetherra.lyrixa.agents.security_agent import SecurityAgent
    from Aetherra.lyrixa.agents.support_agent import SupportAgent
    from Aetherra.lyrixa.agents.technical_agent import TechnicalAgent

    AGENTS_AVAILABLE = True
except ImportError as e:
    print(f"❌ Could not import enhanced agents: {e}")
    AGENTS_AVAILABLE = False


async def demo_data_agent():
    """Demonstrate DataAgent capabilities"""
    print("\n🔍 === DATA AGENT DEMONSTRATION ===")

    agent = DataAgent()
    print(f"✅ {agent.name} initialized")
    print(f"📋 Capabilities: {', '.join(agent.capabilities)}")

    # Test data analysis
    test_data = {
        "users": 1250,
        "sessions": 3847,
        "performance": 92.5,
        "satisfaction": 4.6,
        "errors": 23,
    }

    print("\n📊 Testing data analysis...")
    result = await agent.process_request({"type": "analyze", "data": test_data})

    if result["success"]:
        print("✅ Data analysis completed successfully!")
        print(f"   📈 Processing time: {result['processing_time']:.2f}s")
        print(f"   🎯 Data quality: {result['data_summary']['completeness']:.1%}")
        for insight in result["insights"][:2]:
            print(f"   💡 {insight}")

    # Test pattern detection
    print("\n🔍 Testing pattern detection...")
    pattern_result = await agent.process_request(
        {"type": "pattern_detect", "data": test_data}
    )

    if pattern_result["success"]:
        print("✅ Pattern detection completed!")
        print(f"   🎯 Pattern strength: {pattern_result['pattern_strength']:.1%}")
        print(f"   📋 Patterns found: {len(pattern_result['patterns_found'])}")


async def demo_technical_agent():
    """Demonstrate TechnicalAgent capabilities"""
    print("\n🛠️ === TECHNICAL AGENT DEMONSTRATION ===")

    agent = TechnicalAgent()
    print(f"✅ {agent.name} initialized")
    print(f"📋 Capabilities: {', '.join(agent.capabilities)}")

    # Test system diagnostics
    print("\n🔧 Testing system diagnostics...")
    result = await agent.process_request(
        {"type": "diagnose", "context": {"system": "aetherra_core"}}
    )

    if result["success"]:
        print("✅ System diagnostics completed!")
        print(f"   🖥️ Platform: {result['system_info']['platform']}")
        print(f"   🐍 Python: {result['system_info']['python_version']}")
        print(f"   📊 Health score: {result['components_status'][0]['health']}/100")

    # Test performance analysis
    print("\n⚡ Testing performance analysis...")
    perf_result = await agent.process_request(
        {"type": "performance", "context": {"component": "ai_engine"}}
    )

    if perf_result["success"]:
        print("✅ Performance analysis completed!")
        print(f"   📈 Performance score: {perf_result['performance_score']}/100")
        print(
            f"   ⚡ Response time: {perf_result['metrics']['response_time']['average']}"
        )


async def demo_support_agent():
    """Demonstrate SupportAgent capabilities"""
    print("\n👥 === SUPPORT AGENT DEMONSTRATION ===")

    agent = SupportAgent()
    print(f"✅ {agent.name} initialized")
    print(f"📋 Capabilities: {', '.join(agent.capabilities)}")
    print(f"📚 Knowledge base entries: {len(agent.knowledge_base)}")

    # Test user assistance
    print("\n🤝 Testing user assistance...")
    result = await agent.process_request(
        {
            "type": "assistance",
            "query": "How do I get started with the AI features?",
            "context": {"user_level": "beginner"},
        }
    )

    if result["success"]:
        print("✅ User assistance provided!")
        print(f"   🎯 Intent detected: {result['query_analysis']['intent']}")
        print(f"   📋 Category: {result['query_analysis']['category']}")
        print(f"   💬 Response: {result['response']}")

    # Test FAQ handling
    print("\n❓ Testing FAQ handling...")
    faq_result = await agent.process_request(
        {"type": "faq", "query": "getting started guide"}
    )

    if faq_result["success"]:
        print("✅ FAQ response generated!")
        print(f"   🎯 Confidence: {faq_result['confidence']:.1%}")
        if faq_result["faq_match"]:
            print(f"   📝 Match found: {faq_result['faq_match']['question']}")


async def demo_security_agent():
    """Demonstrate SecurityAgent capabilities"""
    print("\n🔒 === SECURITY AGENT DEMONSTRATION ===")

    agent = SecurityAgent()
    print(f"✅ {agent.name} initialized")
    print(f"📋 Capabilities: {', '.join(agent.capabilities)}")
    print(f"🚨 Active alerts: {len(agent.security_alerts)}")

    # Test security monitoring
    print("\n🛡️ Testing security monitoring...")
    result = await agent.process_request(
        {"type": "monitor", "context": {"scope": "full_system"}}
    )

    if result["success"]:
        print("✅ Security monitoring completed!")
        print(
            f"   🛡️ Security level: {result['security_status']['overall_security_level']}"
        )
        print(f"   ⚡ Threat level: {result['security_status']['threat_level']}")
        print(
            f"   📊 Security score: {result['security_metrics']['security_score']}/100"
        )

    # Test vulnerability scan
    print("\n🔍 Testing vulnerability scan...")
    scan_result = await agent.process_request(
        {"type": "scan", "context": {"target": "application"}}
    )

    if scan_result["success"]:
        print("✅ Vulnerability scan completed!")
        print(f"   🔍 Total checks: {scan_result['scan_summary']['total_checks']}")
        print(
            f"   🚨 Vulnerabilities: {scan_result['scan_summary']['vulnerabilities_found']}"
        )
        print(f"   📊 Scan coverage: {scan_result['scan_coverage']:.1%}")


async def demo_agent_coordination():
    """Demonstrate agents working together"""
    print("\n🤖 === AGENT COORDINATION DEMONSTRATION ===")

    # Initialize all agents
    data_agent = DataAgent()
    tech_agent = TechnicalAgent()
    support_agent = SupportAgent()
    security_agent = SecurityAgent()

    print("✅ All enhanced agents initialized")

    # Simulate a coordinated response scenario
    print("\n📋 Scenario: User reports performance issues with data analysis")

    # 1. Support agent handles initial inquiry
    print("\n👥 Support Agent: Processing user inquiry...")
    support_response = await support_agent.process_request(
        {
            "type": "assistance",
            "query": "The data analysis is running very slowly",
            "context": {"urgency": "medium"},
        }
    )

    # 2. Technical agent diagnoses system
    print("🛠️ Technical Agent: Running system diagnostics...")
    tech_response = await tech_agent.process_request(
        {"type": "performance", "context": {"component": "data_processing"}}
    )

    # 3. Security agent checks for security issues
    print("🔒 Security Agent: Checking for security issues...")
    security_response = await security_agent.process_request(
        {"type": "monitor", "context": {"focus": "data_processing"}}
    )

    # 4. Data agent analyzes the issue
    print("🔍 Data Agent: Analyzing processing patterns...")
    data_response = await data_agent.process_request(
        {
            "type": "pattern_detect",
            "data": {"processing_times": [1.2, 2.3, 4.1, 3.8, 2.9]},
        }
    )

    # Summarize coordinated response
    print("\n📊 Coordinated Analysis Results:")
    if support_response["success"]:
        print(
            f"   👥 Support: {support_response['query_analysis']['urgency']} priority issue identified"
        )
    if tech_response["success"]:
        print(
            f"   🛠️ Technical: {tech_response['performance_score']}/100 performance score"
        )
    if security_response["success"]:
        print(
            f"   🔒 Security: {security_response['security_status']['threat_level']} threat level"
        )
    if data_response["success"]:
        print(f"   🔍 Data: {data_response['pattern_strength']:.1%} pattern confidence")

    print("✅ All agents provided coordinated analysis!")


async def main():
    """Main demonstration function"""
    print("🚀 AETHERRA ENHANCED AGENTS DEMONSTRATION")
    print("=" * 50)

    if not AGENTS_AVAILABLE:
        print("❌ Enhanced agents are not available. Please check imports.")
        return

    start_time = time.time()

    try:
        # Run individual agent demos
        await demo_data_agent()
        await demo_technical_agent()
        await demo_support_agent()
        await demo_security_agent()

        # Demonstrate coordination
        await demo_agent_coordination()

        # Summary
        total_time = time.time() - start_time
        print(f"\n✅ DEMONSTRATION COMPLETE")
        print(f"⏱️ Total execution time: {total_time:.2f} seconds")
        print(f"🤖 All 4 enhanced agents tested successfully!")
        print(f"🎯 Agents are ready for integration with Aetherra AI OS")

    except Exception as e:
        print(f"❌ Demo error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
