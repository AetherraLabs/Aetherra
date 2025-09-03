import asyncio

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
