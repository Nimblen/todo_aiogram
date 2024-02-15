from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import Task, Word, User
import random





async def orm_create_user(session: AsyncSession, data: dict):
    obj = User(
        user_id=data['user_id'],
        name=data['name'],
        username=data['username'],
    )
    session.add(obj)
    await session.commit()


async def orm_get_user(session: AsyncSession, user_id: int):
    query = select(User).where(User.user_id == user_id)
    result = await session.execute(query)
    return result.scalar()

async def orm_update_user(session: AsyncSession, user_id: int, data):
    query = update(User).where(User.user_id == user_id).values(
        is_admin=data["is_admin"],)
    await session.execute(query)
    await session.commit()

async def orm_get_all_users(session: AsyncSession):
    query = select(User)
    result = await session.execute(query)
    return result.scalars().all()

async def orm_add_task(session: AsyncSession, data: dict):
    obj = Task(
        task=data['task_text'],
        routine=data['choosing_routine'],
        user_id=data['user_id'],
    )
    session.add(obj)
    await session.commit()



async def orm_get_all_tasks(session: AsyncSession):
    query = select(Task)
    result = await session.execute(query)
    return result.scalars().all()

async def orm_get_all_user_tasks(session: AsyncSession, user_id: int):
    query = select(Task).filter(Task.user_id == user_id)
    result = await session.execute(query)
    return result.scalars().all()




async def orm_get_task(session: AsyncSession, task_id: int):
    query = select(Task).where(Task.id == task_id)
    result = await session.execute(query)
    return result.scalar()


async def orm_update_task(session: AsyncSession, task_id: int, data):
    query = update(Task).where(Task.id == task_id).values(
        status=data["status"],)
    await session.execute(query)
    await session.commit()


async def orm_delete_task(session: AsyncSession, task_id: int):
    query = delete(Task).where(Task.id == task_id)
    await session.execute(query)
    await session.commit()



async def orm_add_words(session: AsyncSession, data: dict):
    obj = Word(
        rus_word=data['rus_word'],
        eng_word=data['eng_word'],
        description=data['description']
    )
    session.add(obj)
    await session.commit()


async def orm_get_random_word(session: AsyncSession):
    stmt = select(func.count()).select_from(Word)
    count = await session.execute(stmt)
    max_count = count.scalar()
    random_id = random.randint(1, max_count)
    query = select(Word).where(Word.id == random_id)
    result = await session.execute(query)
    return result.scalar()



async def orm_get_all_words(session: AsyncSession):
    query = select(Word)
    result = await session.execute(query)
    return result.scalars().all()
