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

Example success:

{
  "text": "I'm Lyrixa, the conversational and awareness layer of the Aetherra AI Operating System…",
  "suggestions": [],
  "applied_changes": []
}

Service-unavailable fallback (still HTTP 200):

{
  "text": "Lyrixa chat service is not online right now. I can still answer identity and Aetherra questions.",
  "suggestions": [],
  "applied_changes": []
}

## Behavior Notes

- If the Lyrixa chat service is registered and healthy in the Aetherra Service Registry, the Hub forwards chat requests to it.
- If unavailable, the Hub returns a deterministic fallback so clients always get a stable response.
- Safe edits are gated:
  - Edits only occur if allow_edits=true.
  - When edit_root is provided, edits are restricted to that directory.
- Environment gating:
  - AETHERRA_OFFLINE or AETHERRA_QUIET may lead Lyrixa to use deterministic identity/awareness replies instead of external intelligence providers.

## Errors

- 200 with fallback for unavailable service (see above).
- 500 for unexpected server errors (malformed JSON, internal exceptions).
