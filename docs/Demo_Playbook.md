# Aetherra Demo Playbook

This playbook lists runnable demos that align with real, passing endpoints and OS capabilities. Use these for quick walkthroughs, screenshots, and smoke checks.

- Prereqs
  - Optional: Start the Hub server (often started by the OS). Default host/port: localhost:3001.
  - Env overrides: AETHERRA_WEB_HOST, AETHERRA_WEB_PORT.
  - Python env should have requests installed (tests already use it).

- Demos (Unified Runner: `demos/run_demo.py`)
  - chat_lyrixa_bridge
    - Description: Sends a message via the Hub Lyrixa bridge: POST /api/lyrixa/chat.
    - Contract: returns JSON with at least `text` string; may include `suggestions[]`, `applied_changes[]`.
    - Example: run_demo.py chat_lyrixa_bridge --message "Who are you?"
  - kernel_boot_status
    - Description: Shows Hub stats and best‑effort Lyrixa chat registration status: GET /api/stats.
    - Fields: requests_served, plugins_registered, uptime, lyrixa_chat.registered/status.
  - site_status_dashboard
    - Description: Compact dashboard from GET /api/site_status.
    - Fields: kernel.running, kernel.uptime_seconds, queue sizes, plugin count, hub request counter.

- Notes
  - If the Lyrixa chat service isn’t registered, the Hub returns a deterministic fallback for /api/lyrixa/chat.
  - These demos are read-only (except chat POST), safe in test profile.
  - For Windows users, the Python scripts work in PowerShell and CMD.

- Troubleshooting
  - Connection refused: ensure the Hub is running or OS launcher started it.
  - 501 disabled: some optional APIs are gated by env; these demos use public endpoints that are enabled by default.
