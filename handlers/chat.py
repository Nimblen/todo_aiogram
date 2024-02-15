from aiogram import types, Router
from common.chatgpt import chatgpt_answer


chat_router = Router()




@chat_router.message()
async def chat_gpt(message: types.Message):
    await message.answer('да-ка подумать...')
    result = await chatgpt_answer(message.text)
    await message.answer(result)