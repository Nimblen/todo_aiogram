from os import getenv
from datetime import datetime, time
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram import F, types, Router
from aiogram.filters import CommandStart, Command, or_f
from database.orm_query import (
    orm_get_all_users,
    orm_create_user,
    orm_get_user,
    orm_update_user,
    orm_get_all_tasks,
    orm_update_task,
)
from keyboard.reply import get_keyboard
from keyboard.inline import get_callback_btns

admin_router = Router()
creator_id = int(getenv("ADMIN_USER_ID"))
admins_list_id = []

KB = get_keyboard(
    "Добавить задачу.",
    "Все задачи.",
    "Рандомное слово.",
    placeholder="Что вас интересует?",
    sizes=(2, 3),
)


ADMIN_KB = get_keyboard(
    "ALL USERS.",
    "DEACTIVATE ADMIN.",
    "Все слова.",
    "Добавить слово.",
    "GET ALL USERS TASKS.",
    placeholder="Что вас интересует?",
    sizes=(2, 3),
)


@admin_router.message(CommandStart())
async def start(message: types.Message, session: AsyncSession):
    user = await orm_get_user(session, message.from_user.id)
    if user is None:
        try:
            await message.answer(
                f"Привет, {message.chat.first_name}! Я очень рад видеть тебя здесь как виртуальный помощник. Благодаря моему создателю @Nimbl_n я получил возможность помогать таким как ты. Как я могу быть полезен для тебя сегодня?",
                reply_markup=KB,
            )
            await orm_create_user(
                session,
                data={
                    "user_id": message.from_user.id,
                    "username": message.from_user.username,
                    "name": message.from_user.first_name,
                },
            )
        except ValueError as e:
            print(e)
    else:
        await message.answer(
            f"Снова привет, {message.chat.first_name}! Я очень рад видеть тебя здесь еще раз. Уже познакомился с @Nimbl_n? Как я могу быть полезен для тебя сегодня?",
            reply_markup=KB,
        )


@admin_router.message(Command("ADpanel"))
async def activtivate_admin_panel(message: types.Message, session: AsyncSession):
    user_id = message.from_user.id
    user = await orm_get_user(session, user_id)
    if user_id == creator_id or user.is_admin:
        admins_list_id.append(user_id)
        await message.answer(
            f"Вы успешно активировали административную панель {user.name}",
            reply_markup=ADMIN_KB,
        )
    else:
        await message.answer("У вас нет прав доступа к этой команде", reply_markup=KB)


@admin_router.message(or_f(Command("allUsers"), (F.text.lower() == "all users.")))
async def all_users(message: types.Message, session: AsyncSession):
    if message.from_user.id in admins_list_id:
        users = await orm_get_all_users(session)
        await message.answer(f"Количество пользователей: {len(users)}")
        for user in users:
            if user.is_admin:
                await message.answer(
                    f"id:{user.user_id} | username:{user.username} | name:{user.name} | admin:{user.is_admin}",
                    reply_markup=get_callback_btns(
                        btns={
                            "Забрать права админа": f"DelAdmin_{user.user_id}",
                        }
                    ),
                )
            else:
                await message.answer(
                    f"id:{user.user_id} | username:{user.username} | name:{user.name} | admin:{user.is_admin}",
                    reply_markup=get_callback_btns(
                        btns={
                            "Дать права админа": f"GiveAdmin_{user.user_id}",
                        }
                    ),
                )
    else:
        await message.answer("У вас нет прав доступа!")


@admin_router.callback_query(
    or_f(F.data.startswith("GiveAdmin_"), F.data.startswith("DelAdmin_"))
)
async def user_update_callback(callback: types.CallbackQuery, session: AsyncSession):
    if callback.from_user.id == creator_id:
        user_id = callback.data.split("_")[-1]
        user = await orm_get_user(session, user_id)
        if callback.data.startswith("GiveAdmin_"):
            await orm_update_user(session, user_id, data={"is_admin": True})
            await callback.answer(f"Вы назначили {user.name} администратором!")
        elif callback.data.startswith("DelAdmin_"):
            await orm_update_user(session, user_id, data={"is_admin": False})
            await callback.answer(f"Вы забрали у {user.name} права администратора!")
    else:
        await callback.answer("У вас нет прав доступа!")


@admin_router.message(
    or_f(Command("GetAllTasks"), (F.text.lower() == "get all users tasks."))
)
async def get_all_users_tasks(message: types.Message, session: AsyncSession):
    today = datetime.today().date()
    correct_date = datetime.combine(today, time())
    for task in await orm_get_all_tasks(session):
        user = await orm_get_user(session, task.user_id)
        if task.status == True:
            await message.answer(
                f"user: {user.username} | <strong>{task.task}</strong>",
                parse_mode="HTML",
                reply_markup=get_callback_btns(
                    btns={
                        "Удалить": f"delete_{task.id}",
                        "Завершить": f"complete_{task.id}",
                    }
                ),
            )
        elif task.status == False and task.updated_at != correct_date:
            await orm_update_task(session, task.id, data={"status": True})
            await message.answer(
                f"<strong>{task.task}</strong>",
                parse_mode="HTML",
                reply_markup=get_callback_btns(
                    btns={
                        "Удалить": f"delete_{task.id}",
                        "Завершить": f"complete_{task.id}",
                    }
                ),
            )
        else:
            await message.answer(f"<s>{task.task}</s>", parse_mode="HTML")
    await message.answer("all!")


@admin_router.message(or_f(Command("exitAdm"), (F.text.lower() == "deactivate admin.")))
async def deactivate_admin_panel(message: types.Message):
    if message.from_user.id in admins_list_id:
        admins_list_id.remove(message.from_user.id)
        await message.answer("Вы успешно деактивировали админку!", reply_markup=KB)
    else:
        await message.answer("Вы не активировали админку!")
