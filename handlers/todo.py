from aiogram import F, types, Router
from aiogram.filters import Command, StateFilter, or_f
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, time
from database.orm_query import (
    orm_add_task,
    orm_get_all_user_tasks,
    orm_get_task,
    orm_delete_task,
    orm_update_task,
)
from keyboard.inline import get_callback_btns


todo_router = Router()


@todo_router.message_reaction()
async def message_reaction_handler(message_reaction: types.MessageReactionUpdated):
    if message_reaction.new_reaction[0].emoji == "🔥":
        await message_reaction.bot.delete_message(
            message_reaction.chat.id, message_reaction.message_id
        )
    elif message_reaction.new_reaction[0].emoji == "❤":
        await message_reaction.bot.edit_message_text(
            "₩฿₩฿₦₱ ✔", message_reaction.chat.id, message_reaction.message_id
        )


class AddTask(StatesGroup):
    task_text = State()
    choosing_routine = State()


@todo_router.message(
    StateFilter(None), or_f(Command("addTask"), (F.text.lower() == "добавить задачу."))
)
async def add_tast_cmd(
    message: types.Message, state: FSMContext):
    await message.reply("Какое задание?")
    await state.set_state(AddTask.task_text)


@todo_router.message(StateFilter("*"), Command("отмена"))
@todo_router.message(StateFilter("*"), F.text.casefold() == "отмена")
async def cancel_handler(message: types.Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.clear()
    await message.answer("Действия отменены")


@todo_router.message(AddTask.task_text, or_f(F.text, F.text == "."))
async def add_task_text(message: types.Message, state: FSMContext):
    await state.update_data(task_text=message.text.lower())
    await message.answer(text="эта задача рутинная, да или нет?")
    await state.set_state(AddTask.choosing_routine)


@todo_router.message(
    AddTask.choosing_routine, or_f(F.text.lower() == "да", F.text.lower() == "нет")
)
async def choose_routine_task(
    message: types.Message, state: FSMContext, session: AsyncSession
):
    if message.text == "да":
        await state.update_data(choosing_routine=True)
    elif message.text == "нет":
        await state.update_data(choosing_routine=False)
    data = await state.get_data()
    data['user_id'] = message.from_user.id
    await orm_add_task(session, data)
    await message.answer(text="Задание добавлено")
    await state.clear()


@todo_router.message(AddTask.choosing_routine)
async def chosen_routine_task_incorrectly(message: types.Message, state: FSMContext):
    await message.answer(text="да или нет?")
    return await state.set_state(AddTask.choosing_routine)


@todo_router.message(or_f(Command("allTasks"), (F.text.lower() == "все задачи.")))
async def all_task_cmd(message: types.Message, session: AsyncSession):
    today = datetime.today().date()
    correct_date = datetime.combine(today, time())
    user_id = message.from_user.id
    for task in await orm_get_all_user_tasks(session, user_id):
        if task.status == True:
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
    await message.answer("-"*50)


@todo_router.callback_query(
    or_f(F.data.startswith("delete_"), F.data.startswith("complete_"))
)
async def delete_product_callback(callback: types.CallbackQuery, session: AsyncSession):
    task_id = int(callback.data.split("_")[-1])
    if callback.data.startswith("delete_"):
        await orm_delete_task(session, task_id)
        await callback.answer("Задача удалена")
        await callback.bot.delete_message(
            callback.message.chat.id, callback.message.message_id
        )
    elif callback.data.startswith("complete_"):
        task = await orm_get_task(session, task_id)
        await callback.bot.edit_message_text(
            f"<s>{task.task}</s>",
            callback.message.chat.id,
            callback.message.message_id,
            parse_mode="HTML",
        )
        if task.routine == False:
            await orm_delete_task(session, task_id)
        else:
            await orm_update_task(session, task_id, data={"status": False})
        await callback.answer("Задача завершена")
