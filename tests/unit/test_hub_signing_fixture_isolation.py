"""Signing tests must never consume inherited production key overrides."""

# Standard library imports
import os

# Third party imports
import pytest


@pytest.fixture(autouse=True)
def inherited_key_overrides(monkeypatch):
    monkeypatch.setenv("AETHERRA_PLUGIN_SIGNING_SECRET", "synthetic-inherited-secret")
    monkeypatch.setenv("AETHERRA_KEYS_MASTER", "synthetic-inherited-master")


def test_signing_fixture_removes_inherited_keys(signing_hub):
    assert os.getenv("AETHERRA_PLUGIN_SIGNING_SECRET") is None
    assert os.getenv("AETHERRA_KEYS_MASTER") is None
