import g4f
import asyncio


async def chatgpt_answer(q:str) -> str:
    response = await g4f.ChatCompletion.create_async(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": q}],
    )  # Alternative model setting
    return response