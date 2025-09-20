# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

# Standard library imports
import asyncio

# Aetherra imports
from Aetherra.lyrixa.lyrixa_basic import LyrixaBasicAssistant


async def main():
    lyrixa = LyrixaBasicAssistant()
    ok = await lyrixa.initialize()
    if not ok:
        print("INIT_FAIL")
        return
    msg = "Who owns Aetherra Labs?"
    resp = await lyrixa.ai_chat_system.send_message(msg)
    print(resp)


if __name__ == "__main__":
    asyncio.run(main())
