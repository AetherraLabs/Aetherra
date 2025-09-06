# Lyrixa Chat Endpoint

This document describes the lightweight HTTP bridge to Lyrixa's chat service exposed by the Hub server.

## Endpoint

- Method: POST
- URL: /api/lyrixa/chat

## Request Body

- message (string): User message or prompt to Lyrixa.
- allow_edits (bool, optional, default=false): If true, Lyrixa may perform safe workspace edits when suggesting and applying fixes.
- edit_root (string, optional): Absolute path scope for edits; when provided, any edit must fall under this directory.

Example:

{
  "message": "Who are you?",
  "allow_edits": false
}

## Response

On success (including fallback), status code is 200 with a JSON body:

- text (string): Lyrixa's reply or a deterministic fallback.
- suggestions (array): Optional list of suggested fixes with {title, file, action, rationale}.
- applied_changes (array): Optional list of applied changes if allow_edits=true and changes were made.
- persona (object, optional): Lyrixa persona/identity snapshot. When available includes { name, title, about }.
- awareness (object, optional): Workspace awareness summary; when online may include:
  - confidence_breakdown: { model?, grounding?, coherence?, safety? }
  - evidence: array of normalized citations derived from persistent memory
  - consciousness: optional small snapshot when available
- edit_plan (array, optional): Planned edits synthesized from suggestions; items include { title, file, action }.
- confidence (number, optional): Conservative confidence float (0.0–1.0). Defaults to 0.5 if unspecified.

Example success:

{
  "text": "I'm Lyrixa, the conversational and awareness layer of the Aetherra AI Operating System…",
  "suggestions": [],
  "applied_changes": [],
  "persona": { "name": "Lyrixa", "title": "Lyrixa AI Assistant" },
  "awareness": { "total_py_files": 123, "key_components": ["aetherra_os_launcher.py", "aetherra_hub_server.py"] },
  "edit_plan": [],
  "confidence": 0.72
}

Service-unavailable fallback (still HTTP 200):

{
  "text": "Lyrixa chat service is not online right now. I can still answer identity and Aetherra questions.",
  "suggestions": [],
  "applied_changes": [],
  "persona": { "name": "Lyrixa", "title": "Lyrixa AI Assistant" },
  "awareness": { "note": "service offline; awareness limited" },
  "edit_plan": [],
  "confidence": 0.5
}

Backward compatibility: older clients relying only on text/suggestions/applied_changes remain supported.

## Behavior Notes

- If the Lyrixa chat service is registered and healthy in the Aetherra Service Registry, the Hub forwards chat requests to it.
- If unavailable, the Hub returns a deterministic fallback so clients always get a stable response.
- Safe edits are gated:
  - Edits only occur if allow_edits=true.
  - When edit_root is provided, edits are restricted to that directory.
- Always-on path: Lyrixa attempts to initialize intelligence, memory, orchestrator, and consciousness on startup, with graceful degradation (no feature flags required).

## Errors

- 200 with fallback for unavailable service (see above).
- 500 for unexpected server errors (malformed JSON, internal exceptions).

<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->

<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->

<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->
