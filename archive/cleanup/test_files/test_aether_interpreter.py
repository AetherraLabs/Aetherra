#!/usr/bin/env python3
"""
Test script for the enhanced .aether interpreter.
"""

import asyncio

from lyrixa.core.aether_interpreter import AetherInterpreter


async def test_daily_log_summarizer():
    """
    Test the `daily_log_summarizer` example.
    """
    aether_code = """
    plugin "daily_log_summarizer":
      description: "Summarizes daily system logs and stores the digest in memory"

      trigger:
        schedule: daily at "22:00"
        if memory.has("new_logs")

      memory:
        retrieve:
          from: "system.logs.daily"
          limit: 1d
        store:
          into: "summaries.logs.daily"

      ai:
        goal: "Summarize the key events from today’s logs"
        model: gpt-4o
        constraints:
          - no duplicate entries
          - include timestamps and severity levels
        output: summary_text

      actions:
        - memory.save("summaries.logs.daily", summary_text)
        - notify(user: "summary_ready", content: summary_text)

      feedback:
        expect: confirmation from user within 2h
        if no_response:
          escalate_to("admin_review_queue")
    """

    interpreter = AetherInterpreter()

    try:
        # Parse the .aether code
        workflow = await interpreter.parse_aether_code(aether_code)
        print("✅ Parsing successful")

        # Execute the workflow
        result = await interpreter.execute_workflow(workflow)
        print("✅ Execution successful")
        print(result)

    except Exception as e:
        print(f"❌ Test failed: {e}")


if __name__ == "__main__":
    asyncio.run(test_daily_log_summarizer())
