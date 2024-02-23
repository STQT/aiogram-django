from aiogram import BaseMiddleware
from aiogram.types import Update
from typing import Callable, Dict, Awaitable, Any
from app.users.models import TelegramUser


class AuthenticationMiddleware(BaseMiddleware):
    async def __call__(self, handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
                       event: Update,
                       data: Dict[str, Any]
                       ) -> Any:
        bot_user = data['event_from_user']
        if bot_user is None:
            return await handler(event, data)

        user, _ = await TelegramUser.objects.aupdate_or_create(id=bot_user.id,
                                                               defaults={"is_active": True})
        data['user'] = user

        return await handler(event, data)
