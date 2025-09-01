from typing import Any, Dict


def validate_lyrixa_chat_response(data: Dict[str, Any]) -> None:
    """Lightweight shape checks for Lyrixa chat bridge responses.

    Required (lenient types where noted):
      - text or response: str
      - persona: { name: str, ... }
      - awareness: str | dict
      - edit_plan: list
      - confidence: float (0..1, inclusive)

    Optional sanity if present:
      - suggestions: list
      - applied_changes: list
      - scratchpad_policy: str in {ephemeral,persisted,redacted}
    """
    assert isinstance(data, dict), "response must be an object"

    # Text/response payload
    text = data.get("text") or data.get("response")
    assert isinstance(text, str), "text/response must be a string"

    # Persona
    persona = data.get("persona")
    assert isinstance(persona, dict), "persona must be an object"
    assert isinstance(persona.get("name"), str) and persona["name"].strip(), (
        "persona.name must be a non-empty string"
    )

    # Awareness can be a short string or object
    awareness = data.get("awareness")
    assert isinstance(awareness, (str, dict)), "awareness must be str or object"

    # Edit plan list present (may be empty)
    edit_plan = data.get("edit_plan")
    assert isinstance(edit_plan, list), "edit_plan must be a list"

    # Confidence float in [0,1]
    conf = data.get("confidence")
    assert isinstance(conf, (int, float)), "confidence must be numeric"
    assert 0.0 <= float(conf) <= 1.0, "confidence must be between 0 and 1"

    # Optional lists if present
    if "suggestions" in data:
        assert isinstance(data["suggestions"], list), "suggestions must be a list"
    if "applied_changes" in data:
        assert isinstance(data["applied_changes"], list), (
            "applied_changes must be a list"
        )

    # Optional scratchpad policy sanity
    if "scratchpad_policy" in data:
        spp = str(data["scratchpad_policy"]).strip().lower()
        assert spp in {"ephemeral", "persisted", "redacted"}
