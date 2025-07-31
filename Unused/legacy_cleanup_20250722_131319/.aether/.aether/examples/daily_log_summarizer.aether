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
