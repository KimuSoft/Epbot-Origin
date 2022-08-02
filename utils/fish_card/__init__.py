import asyncio
from concurrent.futures import ThreadPoolExecutor

from utils.fish_card.generator import get_card

thread_pool = ThreadPoolExecutor()


async def get_card_async(loop: asyncio.AbstractEventLoop, fish=None, room=None, user=None):
    return await loop.run_in_executor(
        thread_pool, get_card, fish, room, user
    )
