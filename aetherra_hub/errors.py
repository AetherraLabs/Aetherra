"""Lifecycle failures shared with the Hub's owning launcher."""


class HubRequestDrainTimeoutError(RuntimeError):
    """The stop budget expired; admitted work and its resources remain owned."""
