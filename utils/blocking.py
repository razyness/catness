import asyncio

async def run_blocking(func):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, func)
