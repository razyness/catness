import aiohttp

class HTTP():

    async def get(self, url, params=None, headers=None):
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, headers=headers) as response:
                response.raise_for_status()
                return await response.json()

    async def post(self, url, data=None, headers=None):
        async with aiohttp.ClientSession() as session:
            async with self.session.post(url, data=data, headers=headers) as response:
                response.raise_for_status()
                return await response.json()
