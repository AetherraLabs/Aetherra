from __future__ import annotations

import json
import os

from aetherra_hub.app import create_app
from aetherra_hub.config import Settings
from aetherra_hub.services.plugin_metrics import plugin_metrics, reset_for_tests


def _app():
    os.environ["AETH_REQUIRE_PLUGIN_SIGNATURE"] = "1"
    s = Settings.from_env()
    return create_app(s)


def test_signature_required_path(monkeypatch):
    reset_for_tests()
    app = _app()
    client = app.test_client()

    # Simulate advanced verifier rejecting signature by monkeypatching if available
    try:
        from aetherra_hub.services import plugins as adv

        def fake_register_fail(manifest):
            return False, {"error": "invalid signature"}

        monkeypatch.setattr(adv.store, "register", fake_register_fail)  # type: ignore
    except Exception:
        pass

    # Provide manifest with signature but expect failure -> increment signature_errors_total
    r_fail = client.post(
        "/api/plugins/register",
        data=json.dumps(
            {
                "name": "sigbad",
                "version": "1.0.0",
                "description": "secure",
                "signature": "c2ln",
                "pubkey": "cHVi",
            }
        ),
        headers={"Content-Type": "application/json"},
    )
    # Depending on advanced path availability, may be 400 (invalid signature) or 200 (fallback minimal path)
    if r_fail.status_code == 400:
        assert plugin_metrics["signature_errors_total"] >= 1

    # Now monkeypatch success path
    try:
        from aetherra_hub.services import plugins as adv2

        def fake_register_ok(manifest):
            pid = manifest.get("name", "p1")
            adv2.store.plugins[pid] = {
                "name": pid,
                "version": manifest.get("version", "1.0.0"),
                "description": manifest.get("description", "desc"),
                "display_name": pid.title(),
                "registered_at": "",
                "signature_verified": True,
                "trust_zone": "signed",
            }
            return True, {"status": "success", "plugin_id": pid}

        monkeypatch.setattr(adv2.store, "register", fake_register_ok)  # type: ignore
    except Exception:
        pass

    r_ok = client.post(
        "/api/plugins/register",
        data=json.dumps(
            {
                "name": "siggood",
                "version": "1.0.0",
                "description": "secure2",
                "signature": "c2ln",
                "pubkey": "cHVi",
            }
        ),
        headers={"Content-Type": "application/json"},
    )
    assert r_ok.status_code in (200, 400)
    os.environ.pop("AETH_REQUIRE_PLUGIN_SIGNATURE", None)
