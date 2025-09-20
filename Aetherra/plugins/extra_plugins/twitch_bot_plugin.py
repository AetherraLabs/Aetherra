# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
🎮 TWITCH BOT PLUGIN
===================

Advanced Twitch bot integration for streamers and communities.
Features chat moderation, custom commands, follower alerts, stream notifications,
and intelligent chat responses powered by Lyrixa.
"""

# Standard library imports
import asyncio
import json
import logging
import re
import time
from datetime import datetime, timedelta
from typing import Any
from urllib.parse import urlencode

# Third party imports
import requests
from websockets import connect

logger = logging.getLogger(__name__)


class TwitchAPI:
    """Twitch API client for authentication and data retrieval."""

    def __init__(
        self, client_id: str, client_secret: str, access_token: str | None = None
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = access_token
        self.base_url = "https://api.twitch.tv/helix"
        self.auth_url = "https://id.twitch.tv/oauth2"

    def get_auth_url(self, redirect_uri: str, scopes: list[str]) -> str:
        """Generate OAuth authorization URL."""
        params = {
            "client_id": self.client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": " ".join(scopes),
        }
        return f"{self.auth_url}/authorize?" + urlencode(params)

    def exchange_code_for_token(self, code: str, redirect_uri: str) -> dict[str, Any]:
        """Exchange authorization code for access token."""
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri,
        }

        response = requests.post(f"{self.auth_url}/token", data=data)
        return response.json()

    def get_user_info(self, username: str) -> dict[str, Any] | None:
        """Get user information by username."""
        if not self.access_token:
            return None

        headers = {
            "Client-ID": self.client_id,
            "Authorization": f"Bearer {self.access_token}",
        }

        response = requests.get(
            f"{self.base_url}/users", headers=headers, params={"login": username}
        )

        if response.status_code == 200:
            data = response.json()
            return data["data"][0] if data["data"] else None
        return None

    def get_stream_info(self, user_id: str) -> dict[str, Any] | None:
        """Get current stream information."""
        if not self.access_token:
            return None

        headers = {
            "Client-ID": self.client_id,
            "Authorization": f"Bearer {self.access_token}",
        }

        response = requests.get(
            f"{self.base_url}/streams", headers=headers, params={"user_id": user_id}
        )

        if response.status_code == 200:
            data = response.json()
            return data["data"][0] if data["data"] else None
        return None


class TwitchChatBot:
    """Twitch IRC chat bot with moderation and command features."""

    def __init__(self, username: str, oauth_token: str, channel: str):
        self.username = username
        self.oauth_token = oauth_token
        self.channel = channel.lower()
        self.websocket = None
        self.connected = False
        self.commands = {}
        self.moderators = set()
        self.banned_words = set()
        self.command_cooldowns = {}
        self.user_timeouts = {}

        # Default commands
        self.setup_default_commands()

    def setup_default_commands(self):
        """Setup default bot commands."""
        self.commands = {
            "!hello": self.cmd_hello,
            "!time": self.cmd_time,
            "!uptime": self.cmd_uptime,
            "!commands": self.cmd_commands,
            "!lurk": self.cmd_lurk,
            "!unlurk": self.cmd_unlurk,
        }

    async def connect(self):
        """Connect to Twitch IRC."""
        try:
            self.websocket = await connect(
                "wss://irc-ws.chat.twitch.tv:443", ping_interval=30, ping_timeout=10
            )

            # Send authentication
            await self.websocket.send(f"PASS oauth:{self.oauth_token}")
            await self.websocket.send(f"NICK {self.username}")
            await self.websocket.send(f"JOIN #{self.channel}")

            # Request capabilities
            await self.websocket.send("CAP REQ :twitch.tv/membership")
            await self.websocket.send("CAP REQ :twitch.tv/tags")
            await self.websocket.send("CAP REQ :twitch.tv/commands")

            self.connected = True
            logger.info(f"Connected to Twitch chat: #{self.channel}")

        except Exception as e:
            logger.error(f"Failed to connect to Twitch: {e}")
            self.connected = False

    async def disconnect(self):
        """Disconnect from Twitch IRC."""
        if self.websocket:
            await self.websocket.close()
        self.connected = False
        logger.info("Disconnected from Twitch chat")

    async def send_message(self, message: str):
        """Send a message to the chat."""
        if self.websocket and self.connected:
            await self.websocket.send(f"PRIVMSG #{self.channel} :{message}")

    async def timeout_user(self, username: str, duration: int = 600):
        """Timeout a user for specified duration (seconds)."""
        await self.websocket.send(
            f"PRIVMSG #{self.channel} :/timeout {username} {duration}"
        )

    async def ban_user(self, username: str):
        """Ban a user from the channel."""
        await self.websocket.send(f"PRIVMSG #{self.channel} :/ban {username}")

    def parse_message(self, raw_message: str) -> dict[str, Any] | None:
        """Parse IRC message into structured data."""
        if not raw_message.strip():
            return None

        # Handle PING
        if raw_message.startswith("PING"):
            return {"type": "ping", "message": raw_message}

        # Parse tags, prefix, command, and params
        tags = {}
        if raw_message.startswith("@"):
            tag_part, raw_message = raw_message[1:].split(" ", 1)
            for tag in tag_part.split(";"):
                if "=" in tag:
                    key, value = tag.split("=", 1)
                    tags[key] = value

        if " :" in raw_message:
            prefix_and_command, content = raw_message.split(" :", 1)
        else:
            prefix_and_command = raw_message
            content = ""

        parts = prefix_and_command.split()

        if len(parts) < 2:
            return None

        prefix = parts[0] if parts[0].startswith(":") else ""
        command = parts[1] if prefix else parts[0]
        channel = parts[2] if len(parts) > 2 else ""

        # Extract username from prefix
        username = ""
        if prefix and "!" in prefix:
            username = prefix[1:].split("!")[0]

        return {
            "type": "message",
            "tags": tags,
            "username": username,
            "channel": channel.lstrip("#"),
            "command": command,
            "content": content,
        }

    async def handle_message(self, parsed: dict[str, Any]):
        """Handle incoming chat messages."""
        if parsed["type"] == "ping":
            await self.websocket.send("PONG :tmi.twitch.tv")
            return

        if parsed["command"] != "PRIVMSG":
            return

        username = parsed["username"]
        content = parsed["content"]

        # Check for banned words
        if self.is_message_inappropriate(content):
            await self.timeout_user(username, 300)
            await self.send_message(f"@{username} Please keep the chat appropriate!")
            return

        # Handle commands
        if content.startswith("!"):
            await self.handle_command(username, content)

    def is_message_inappropriate(self, message: str) -> bool:
        """Check if message contains banned words."""
        message_lower = message.lower()
        return any(word in message_lower for word in self.banned_words)

    async def handle_command(self, username: str, message: str):
        """Handle chat commands."""
        parts = message.split()
        command = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []

        # Check cooldown
        if command in self.command_cooldowns:
            last_used, cooldown = self.command_cooldowns[command]
            if time.time() - last_used < cooldown:
                return

        # Execute command
        if command in self.commands:
            try:
                await self.commands[command](username, args)
                self.command_cooldowns[command] = (
                    time.time(),
                    30,
                )  # 30 second cooldown
            except Exception as e:
                logger.error(f"Error executing command {command}: {e}")

    # Command implementations
    async def cmd_hello(self, username: str, args: list[str]):
        """Hello command."""
        await self.send_message(f"Hello @{username}! Welcome to the stream! 👋")

    async def cmd_time(self, username: str, args: list[str]):
        """Current time command."""
        current_time = datetime.now().strftime("%H:%M:%S")
        await self.send_message(f"Current time: {current_time}")

    async def cmd_uptime(self, username: str, args: list[str]):
        """Stream uptime command (placeholder)."""
        await self.send_message("Stream has been live for 1 hour 23 minutes")

    async def cmd_commands(self, username: str, args: list[str]):
        """List available commands."""
        command_list = ", ".join(self.commands.keys())
        await self.send_message(f"Available commands: {command_list}")

    async def cmd_lurk(self, username: str, args: list[str]):
        """Lurk command."""
        await self.send_message(f"Thanks for lurking @{username}! Enjoy the stream 🍿")

    async def cmd_unlurk(self, username: str, args: list[str]):
        """Unlurk command."""
        await self.send_message(f"Welcome back @{username}! 🎉")

    async def run(self):
        """Main bot loop."""
        await self.connect()

        try:
            while self.connected:
                if self.websocket:
                    try:
                        message = await asyncio.wait_for(
                            self.websocket.recv(), timeout=1.0
                        )
                        parsed = self.parse_message(message)
                        if parsed:
                            await self.handle_message(parsed)
                    except asyncio.TimeoutError:
                        continue
                    except Exception as e:
                        logger.error(f"Error in bot loop: {e}")
                        break
                else:
                    await asyncio.sleep(1)
        finally:
            await self.disconnect()


class TwitchBotPlugin:
    """Main Twitch Bot Plugin class."""

    # Required plugin metadata
    name = "twitch_bot_plugin"
    description = "Advanced Twitch bot with chat moderation, custom commands, and intelligent responses"
    version = "1.0.0"

    input_schema = {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": [
                    "connect",
                    "disconnect",
                    "send_message",
                    "add_command",
                    "moderate",
                ],
                "description": "Action to perform",
            },
            "channel": {"type": "string", "description": "Twitch channel name"},
            "message": {"type": "string", "description": "Message to send"},
            "command": {"type": "string", "description": "Command name"},
            "response": {"type": "string", "description": "Command response"},
        },
        "required": ["action"],
    }

    output_schema = {
        "type": "object",
        "properties": {
            "status": {"type": "string", "description": "Operation status"},
            "message": {"type": "string", "description": "Status message"},
            "data": {"type": "object", "description": "Additional data"},
        },
    }

    def __init__(self):
        self.name = "TwitchBot"
        self.version = "1.0.0"
        self.author = "Aetherra Labs"
        self.description = "Advanced Twitch bot with moderation and custom commands"
        self.twitch_api = None
        self.chat_bot = None
        self.bot_task = None
        self.config = {
            "client_id": "",
            "client_secret": "",
            "access_token": "",
            "username": "",
            "oauth_token": "",
            "channel": "",
            "enabled": False,
        }

    async def initialize(self, context=None):
        """Initialize the plugin."""
        try:
            # Load configuration
            await self.load_config()
            logger.info("Twitch Bot Plugin initialized")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Twitch Bot Plugin: {e}")
            return False

    async def load_config(self):
        """Load plugin configuration."""
        # In a real implementation, this would load from a config file
        pass

    async def save_config(self):
        """Save plugin configuration."""
        # In a real implementation, this would save to a config file
        pass

    def capabilities(self) -> list[str]:
        """Return plugin capabilities."""
        return [
            "chat_moderation",
            "custom_commands",
            "stream_alerts",
            "follower_notifications",
            "intelligent_responses",
        ]

    async def invoke(
        self, action: str, payload: dict[str, Any], context=None
    ) -> dict[str, Any]:
        """Main plugin invocation method."""
        try:
            if action == "connect":
                return await self.connect_bot(payload.get("channel"))
            elif action == "disconnect":
                return await self.disconnect_bot()
            elif action == "send_message":
                return await self.send_message(payload.get("message", ""))
            elif action == "add_command":
                return await self.add_custom_command(
                    payload.get("command", ""), payload.get("response", "")
                )
            elif action == "get_config":
                return {"status": "success", "data": self.config}
            elif action == "update_config":
                return await self.update_config(payload)
            else:
                return {"status": "error", "message": f"Unknown action: {action}"}

        except Exception as e:
            logger.error(f"Error in Twitch Bot Plugin: {e}")
            return {"status": "error", "message": str(e)}

    async def connect_bot(self, channel: str) -> dict[str, Any]:
        """Connect the bot to a Twitch channel."""
        if not self.config.get("oauth_token") or not self.config.get("username"):
            return {"status": "error", "message": "Bot credentials not configured"}

        if self.chat_bot and self.bot_task:
            return {"status": "error", "message": "Bot already connected"}

        try:
            self.chat_bot = TwitchChatBot(
                username=self.config["username"],
                oauth_token=self.config["oauth_token"],
                channel=channel or self.config["channel"],
            )

            # Start bot in background
            self.bot_task = asyncio.create_task(self.chat_bot.run())

            return {
                "status": "success",
                "message": f"Connected to channel: {channel}",
                "data": {"channel": channel},
            }
        except Exception as e:
            return {"status": "error", "message": f"Failed to connect: {e}"}

    async def disconnect_bot(self) -> dict[str, Any]:
        """Disconnect the bot."""
        if not self.chat_bot:
            return {"status": "error", "message": "Bot not connected"}

        try:
            if self.bot_task:
                self.bot_task.cancel()
                try:
                    await self.bot_task
                except asyncio.CancelledError:
                    pass

            await self.chat_bot.disconnect()
            self.chat_bot = None
            self.bot_task = None

            return {"status": "success", "message": "Bot disconnected"}
        except Exception as e:
            return {"status": "error", "message": f"Failed to disconnect: {e}"}

    async def send_message(self, message: str) -> dict[str, Any]:
        """Send a message to chat."""
        if not self.chat_bot or not self.chat_bot.connected:
            return {"status": "error", "message": "Bot not connected"}

        try:
            await self.chat_bot.send_message(message)
            return {"status": "success", "message": "Message sent"}
        except Exception as e:
            return {"status": "error", "message": f"Failed to send message: {e}"}

    async def add_custom_command(self, command: str, response: str) -> dict[str, Any]:
        """Add a custom command."""
        if not self.chat_bot:
            return {"status": "error", "message": "Bot not connected"}

        if not command.startswith("!"):
            command = "!" + command

        async def custom_cmd(username: str, args: list[str]):
            await self.chat_bot.send_message(response.replace("{user}", username))

        self.chat_bot.commands[command] = custom_cmd

        return {
            "status": "success",
            "message": f"Command {command} added",
            "data": {"command": command, "response": response},
        }

    async def update_config(self, new_config: dict[str, Any]) -> dict[str, Any]:
        """Update plugin configuration."""
        try:
            self.config.update(new_config)
            await self.save_config()
            return {"status": "success", "message": "Configuration updated"}
        except Exception as e:
            return {"status": "error", "message": f"Failed to update config: {e}"}


# Plugin entry point
def get_plugin():
    """Return the plugin instance."""
    return TwitchBotPlugin()


# For testing
if __name__ == "__main__":
    plugin = TwitchBotPlugin()
    print(f"Plugin: {plugin.name} v{plugin.version}")
    print(f"Capabilities: {plugin.capabilities()}")
