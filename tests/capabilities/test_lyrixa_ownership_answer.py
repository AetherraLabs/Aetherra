# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

import pytest

from Aetherra.lyrixa.chat.lyrixa_chat_service import ChatOptions, LyrixaChatService


@pytest.mark.asyncio
async def test_lyrixa_answers_ownership_from_memory():
    svc = LyrixaChatService()
    await svc.initialize()
    resp = await svc.chat("Who owns Aetherra Labs?", ChatOptions())
    assert (
        "Timothy Holdorff" in resp.text
        or "don't have a record of ownership" in resp.text
    )
