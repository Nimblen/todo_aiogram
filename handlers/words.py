from aiogram import F, types, Router
from aiogram.filters import Command, StateFilter, or_f
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession
from database.orm_query import orm_add_words, orm_get_all_words, orm_get_random_word, orm_get_user
from handlers.admin import admins_list_id

words_router = Router()


class AddWord(StatesGroup):
    rus_word = State()
    eng_word = State()
    description = State()


class GetWord(StatesGroup):
    waiting_word = State()


@words_router.message(
    StateFilter(None), or_f(Command("addWord"), (F.text.lower() == "добавить слово."))
)
async def add_word_cmd(message: types.Message, state: FSMContext, session: AsyncSession):
    admin = await orm_get_user(session, user_id=message.from_user.id)
    if admin.is_admin:
        await message.reply("Напишите русское слово!")
        await state.set_state(AddWord.rus_word)
    else: message.answer('У вас нет доступа')


@words_router.message(AddWord.rus_word, or_f(F.text, F.text == "."))
async def add_rus_word_text(message: types.Message, state: FSMContext):
    await state.update_data(rus_word=message.text.lower())
    await message.answer(text="Теперь перевод слова")
    await state.set_state(AddWord.eng_word)


@words_router.message(AddWord.eng_word, or_f(F.text, F.text == "."))
async def add_eng_word_text(message: types.Message, state: FSMContext):
    await state.update_data(eng_word=message.text.lower())
    await message.answer(text="Можете добавить описание ")
    await state.set_state(AddWord.description)


@words_router.message(AddWord.description, or_f(F.text, F.text == "."))
async def add_description_text(
    message: types.Message, state: FSMContext, session: AsyncSession
):
    await state.update_data(description=message.text.lower())
    data = await state.get_data()
    await orm_add_words(session, data)
    await message.answer(text="Все записано")
    await state.clear()


@words_router.message(or_f(Command("allWords"), (F.text.lower() == "все слова.")))
async def all_words_cmd(message: types.Message, session: AsyncSession):
    if message.from_user.id in admins_list_id:
        for result in await orm_get_all_words(session):
            await message.answer(
                f"<strong>{result.rus_word}</strong> - <strong>{result.eng_word}</strong>\n {result.description}",
                parse_mode="HTML",
            )
        await message.answer("-"*50)
    else: await message.answer("У вас нет доступа!")


@words_router.message(
    StateFilter(None), or_f(Command("getWord"), (F.text.lower() == "рандомное слово."))
)
async def get_random_word_cmd(
    message: types.Message, state: FSMContext, session: AsyncSession
):
    result = await orm_get_random_word(session)
    await message.answer("Напишите перевод следующего слова")
    await message.answer(result.rus_word)
    await state.set_state(GetWord.waiting_word)
    await state.update_data(waiting_word=result.eng_word)


@words_router.message(GetWord.waiting_word, or_f(F.text, F.text == "."))
async def get_currently_word(
    message: types.Message, state: FSMContext, session: AsyncSession
):
    data = await state.get_data()
    if data["waiting_word"] == message.text.lower():
        await message.answer("правильно")
        await get_random_word_cmd(message, state, session)
    else:
        await message.answer("неправильно, попробуйте еще")
