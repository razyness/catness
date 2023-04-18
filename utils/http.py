import aiohttp

class HTTP():

    async def get(self, url, params=None, headers=None):
        """Get a url with parameters and headers

        Args:
            url (str): URL to fetch
            params (dict, optional): aiohttp session paramters. Defaults to None.
            headers (dict, optional): aiohttp session headers. Defaults to None.

        Returns:
            json: A json dict with the response
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, headers=headers) as response:
                response.raise_for_status()
                return await response.json()

    async def post(self, url, data=None, headers=None):
        """Post to a url with data and headers

        Args:
            url (_type_): URL to post to
            data (dict, optional): aiohttp session data. Defaults to None.
            headers (dict, optional): aiohttp session headers. Defaults to None.

        Returns:
            json: A json dict with the response
        """
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=data, headers=headers) as response:
                response.raise_for_status()
                return await response.json()
