from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from sqlalchemy.ext.asyncio import async_sessionmaker


class DataBaseSession(BaseMiddleware):
    """
    This class is a middleware that is used to handle all the database operations.
    Args:
        session_pool (async_sessionmaker): an async sessionmaker object that is used to create a new session for the database
    """
    def __init__(self, session_pool: async_sessionmaker):
        self.session_pool = session_pool

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        """
        This method is a middleware that is used to handle all the database operations.
        Args:
            handler (Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]]): a handler that is used to handle the incoming update
            event (TelegramObject): an incoming update
            data (Dict[str, Any]): a data dictionary that is used to pass data between different stages of the update's processing
        Returns:
            Any: the result of the handler's execution
        """

        async with self.session_pool() as session:
            data['session'] = session
            return await handler(event, data)
