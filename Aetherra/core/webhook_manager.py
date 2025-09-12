# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

import asyncio

import requests

from Aetherra.security.capabilities import get_capability_limits, has_capability
from Aetherra.security.net_policy import http_post

try:
    # Optional kernel helper for standardized capability-tagged invocation
    from aetherra_kernel_loop import get_kernel  # type: ignore
except Exception:  # pragma: no cover - kernel may be unavailable in some contexts
    get_kernel = None  # type: ignore


class WebhookManager:
    """Manages webhook registration, triggering, and error handling."""

    def __init__(self):
        self.webhooks = {}  # Dictionary to store event-to-URL mappings

    def register_webhook(self, event: str, url: str):
        """Registers a webhook for a specific event."""
        if event not in self.webhooks:
            self.webhooks[event] = []
        self.webhooks[event].append(url)
        print(f"Webhook registered: {event} -> {url}")

    def trigger_webhook(self, event: str, payload: dict):
        """Triggers all webhooks registered for a specific event."""
        if event not in self.webhooks:
            print(f"No webhooks registered for event: {event}")
            return

        # Capability check (deny-by-default in strict mode)
        if not has_capability("core:webhook_manager", "network:webhook"):
            print("Webhook trigger denied by capability policy")
            return

        # Effective timeout informed by capability limits (if configured)
        timeout = 10.0
        try:
            limits = get_capability_limits("network:webhook")
            if isinstance(limits, dict) and limits.get("timeout_sec"):
                timeout = float(limits["timeout_sec"]) or timeout
        except Exception:
            pass

        for url in self.webhooks[event]:
            try:
                # Prefer kernel-mediated path if available; fallback to direct http_post
                response = None
                used_kernel = False
                if get_kernel is not None:
                    try:
                        kernel = get_kernel()
                        # Route via standardized plugin_invoke helper when possible
                        # Name intentionally generic; plugin may not exist in all profiles
                        result = None
                        try:
                            # Use waiter for synchronous result, capability-tagged
                            result = kernel and (
                                kernel.submit_plugin_invoke_and_wait(
                                    "net:http_post",
                                    capability="network:webhook",
                                    kwargs={
                                        "url": url,
                                        "json": payload,
                                        "timeout": timeout,
                                        "method": "POST",
                                    },
                                    timeout_sec=timeout,
                                    requester="core:webhook_manager",
                                    wait_timeout=timeout + 0.5,
                                )
                            )
                            if result is not None:
                                # Resolve coroutine if not already in an event loop; otherwise fallback
                                if asyncio.iscoroutine(result):
                                    try:
                                        asyncio.get_running_loop()
                                        # Already in a running loop; avoid blocking – fallback to direct HTTP
                                        result = None
                                    except RuntimeError:
                                        # No running loop – safe to run synchronously
                                        result = asyncio.run(result)
                        except Exception:
                            result = None

                        if isinstance(result, dict) and result.get("ok"):
                            # Some plugin implementations may not return requests.Response
                            # Treat as success and skip direct http
                            used_kernel = True
                            response = None
                    except Exception:
                        # Kernel path not available or failed; will fallback
                        pass

                if not used_kernel:
                    response = http_post(
                        url, payload, timeout=timeout, requester="core:webhook_manager"
                    )
                if response is None:
                    print(f"Webhook blocked or failed: {url}")
                else:
                    response.raise_for_status()
                    print(f"Webhook triggered successfully: {url}")
            except requests.RequestException as e:
                print(f"Failed to trigger webhook: {url} -> {e}")

    def remove_webhook(self, event: str, url: str):
        """Removes a webhook for a specific event."""
        if event in self.webhooks and url in self.webhooks[event]:
            self.webhooks[event].remove(url)
            print(f"Webhook removed: {event} -> {url}")


# Example usage
if __name__ == "__main__":
    manager = WebhookManager()
    manager.register_webhook("memory_update", "http://example.com/webhook")
    manager.trigger_webhook("memory_update", {"data": "Memory updated successfully"})
    manager.remove_webhook("memory_update", "http://example.com/webhook")
