import asyncio
from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from cachetools import TTLCache

# --- Throttling Middleware (limits request frequency) ---
class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, rate_limit: float = 0.5):
        self.cache = TTLCache(maxsize=10_000, ttl=rate_limit)

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        user_id = event.from_user.id
        if user_id in self.cache:
            return
        self.cache[user_id] = None
        return await handler(event, data)

# --- Anti-Flood Middleware ---
class AntiFloodMiddleware(BaseMiddleware):
    def __init__(self, time_window: int = 10, max_messages: int = 5):
        self.limit = TTLCache(maxsize=10_000, ttl=time_window)

    async def __call__(
        self,
        handler: Callable[[CallbackQuery, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        user_id = event.from_user.id
        
        # Increment message counter
        self.limit[user_id] = self.limit.get(user_id, 0) + 1
        
        # If the limit is exceeded, do nothing
        if self.limit[user_id] > max_messages:
            return
            
        return await handler(event, data)
