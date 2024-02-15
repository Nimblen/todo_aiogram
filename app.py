import asyncio
import os
from aiogram import Bot, Dispatcher, types
from dotenv import find_dotenv, load_dotenv
from handlers import chat, todo, words,admin
from database.engine import create_db, session_maker
from middlewares.db import DataBaseSession
from common.bot_cmds_list import commands
load_dotenv(find_dotenv())

# ALLOWED_UPDATES = ["messages, edited_messages,"]
bot = Bot(token=os.getenv("TOKEN"))



dp = Dispatcher()
dp.include_router(admin.admin_router)
dp.include_router(todo.todo_router)
dp.include_router(words.words_router)
dp.include_router(chat.chat_router)




async def on_startup(bot):
    await create_db()

async def on_shutdown(bot):
    print("Shutting down")




async def main():
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    dp.update.middleware(DataBaseSession(session_pool=session_maker))
    await bot.delete_webhook(drop_pending_updates=True)
    #await bot.set_my_commands(commands=commands, scope=types.BotCommandScopeAllPrivateChats())
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


asyncio.run(main())
