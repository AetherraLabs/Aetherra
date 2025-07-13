import unittest
from unittest.mock import MagicMock, patch

from Aetherra.core.webhook_manager import WebhookManager


class TestWebhookManager(unittest.TestCase):
    def setUp(self):
        self.manager = WebhookManager()

    @patch("requests.post")
    def test_register_and_trigger_webhook(self, mock_post):
        # Mock the POST request
        mock_post.return_value = MagicMock(status_code=200)

        # Register a webhook
        self.manager.register_webhook("memory_update", "http://example.com/webhook")

        # Trigger the webhook
        self.manager.trigger_webhook("memory_update", {"data": "test"})

        # Assert the POST request was made
        mock_post.assert_called_once_with(
            "http://example.com/webhook", json={"data": "test"}
        )

    def test_remove_webhook(self):
        # Register and then remove a webhook
        self.manager.register_webhook("memory_update", "http://example.com/webhook")
        self.manager.remove_webhook("memory_update", "http://example.com/webhook")

        # Trigger the webhook (should not call anything)
        with patch("requests.post") as mock_post:
            self.manager.trigger_webhook("memory_update", {"data": "test"})
            mock_post.assert_not_called()


if __name__ == "__main__":
    unittest.main()
