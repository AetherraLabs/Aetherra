#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

# Standard library imports
import asyncio

# Aetherra imports
from Aetherra.lyrixa.chat.lyrixa_chat_service import ChatOptions, LyrixaChatService


async def main():
    svc = LyrixaChatService()
    await svc.initialize()
    resp = await svc.chat("Say hello and summarize your awareness.", ChatOptions())
    print("TEXT:", resp.text)
    print("AWARENESS_KEYS:", list(resp.awareness.keys()))
    print("CONSCIOUSNESS:", resp.awareness.get("consciousness"))
    print("CONFIDENCE_BREAKDOWN:", resp.awareness.get("confidence_breakdown"))


if __name__ == "__main__":
    asyncio.run(main())
