#!/usr/bin/env python3
"""
Test script for the real agent manager
"""

try:
    from Aetherra.lyrixa.gui.real_agent_manager import RealAgentManager

    print("✅ Import worked")

    mgr = RealAgentManager()
    print("✅ Manager created")

    print(
        f"Status: {'✅ Connected to real agents' if mgr.is_connected else '❌ Not connected to real agents - using fallback data'}"
    )

    agents = mgr.get_agent_status()
    print(f"Found {len(agents)} agents")

    if agents:
        print("\nAgent Summary:")
        for agent_data in agents:
            agent_name = agent_data.get("name", "Unknown")
            status = agent_data.get("status", "Unknown")
            load = agent_data.get("load", 0)
            print(f"  - {agent_name}: {status} (Load: {load}%)")

        # Test detailed view
        first_agent = agents[0].get("name", "Unknown")
        print(f"\nDetailed info for {first_agent}:")
        details = mgr.get_agent_details(first_agent)
        print(f"  Description: {details.get('description', 'N/A')}")
        print(f"  Capabilities: {len(details.get('capabilities', []))} listed")
        print(
            f"  Recent activities: {len(details.get('recent_activities', []))} activities"
        )

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback

    traceback.print_exc()
