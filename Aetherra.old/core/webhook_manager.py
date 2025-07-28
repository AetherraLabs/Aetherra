import requests


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

        for url in self.webhooks[event]:
            try:
                response = requests.post(url, json=payload)
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
