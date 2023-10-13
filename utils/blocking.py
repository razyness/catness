import asyncio

async def run(func):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, func)
