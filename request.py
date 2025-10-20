from aiohttp import ClientSession, ClientResponse
from logging import basicConfig, DEBUG, info

class Request:

    basicConfig(
        level=DEBUG,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    def __init__(self, name: str, url: str, method: str = 'post', content_type: str = 'application/json', headers: dict[str, str] = {}, body: dict[str, str] = {}):
        self.name         = name
        self.url          = url
        self.method       = method.upper()
        self.content_type = content_type
        self.headers      = headers
        self.body         = body

    async def perform(self):
        async with ClientSession() as session:
            info(f'Request {self.name}: started')
            match self.content_type:
                case 'application/json':
                    async with session.request(url=self.url, method=self.method, headers=self.headers, json=self.body) as response:
                        return await self.__get_dict_response(response)
                case 'application/x-www-form-urlencoded':
                    async with session.request(url=self.url, method=self.method, headers=self.headers, data=self.body) as response:
                        return await self.__get_dict_response(response)

    async def __get_dict_response(self, response: ClientResponse):
        info(f'Request {self.name}: finished')
        content_type = 'json'
        try:
            body = await response.json()
        except:
            body = await response.text()
            content_type = 'text'
        return {
            'status':  response.status,
            'headers': self.__flatten_dict(dict(response.headers)),
            'body':    self.__flatten_dict(body) if content_type == 'form' else body,
        }

    def __flatten_dict(self, data: dict, parent_key: str = '', seperator: str = '.'):
        items = {}
        for key, value in data.items():
            new_key = f"{parent_key}{seperator}{key}" if parent_key else key
            if isinstance(value, dict):
                items.update(self.__flatten_dict(value, new_key, seperator))
            else:
                items[new_key] = value
        return items
