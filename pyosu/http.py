# MIT License

# Copyright (c) 2018-2019 Renondedju

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import asyncio

from json        import loads
from aiohttp     import ClientSession
from .exceptions import WrongApiKey, RouteNotFound, InvalidArgument, HTTPError, ReplayUnavailable

class Route:

    def __init__(self, path : str = '', api_key : str = '', base = 'https://osu.ppy.sh/api/', **parameters):

        self.base        = base
        self.path        = path
        self.api_key     = api_key
        self.parameters  = {}

        for key, value in parameters.items():
            if value != None:
                self.parameters[key] = value

    @property
    def route(self):
        """ Returns the current route """

        params = []
        if self.api_key != '':
            params.append(f'k={self.api_key}')

        for key, value in self.parameters.items():
            params.append(f'{str(key)}={str(value)}')

        if len(params) > 0:
            return f"{self.base}{self.path}?{'&'.join(params)}"

        return f"{self.base}{self.path}"
        
    def add_param(self, key, value):
        """ Adds or updates a prameter """

        if (value is None):
            return
            
        self.parameters[key] = value

        return

    def remove_param(self, key):
        """ Removes a parameter from the route """

        return self.parameters.pop(key, None) != None

    def check_params(self):
        """ Raise the InvalidArgument Exception if one of the parameters that is
        being used isn't in the following list : 
        
        [a, h, k, m, b, u, s, mp, limit, type, mods, event_days, since]
        """
        accepted_params = ['a', 'h', 'k', 'm', 'b', 'u', 's', 'mp',
            'limit', 'type', 'mods', 'event_days', 'since']

        for key in self.parameters.keys():
            if (key not in accepted_params):
                raise InvalidArgument(key)

        return

class Request():

    def __init__(self, route : Route, retry : int = 5, json_response : bool = True):

        self.json_response = json_response
        self.retry_count   = retry # Number of retrys to do before throwing any errors
        self.route         = route
        self._data         = []

    @property
    def data(self):
        return self._data

    async def get_json(self, response, *args):
        """ Returns the json version of an api response """
        text = await response.text()

        if self.json_response is False:
            return text

        if (text == None or text == ''):
            return {}

        data = loads(text)

        if len(args) == 0:
            return data

        for key in args:
            try:
                data = data[key]
            except KeyError:
                return ''

        return data

    async def fetch_with_session(self, session):
        """ Fetches some data with a session using the actual route """

        self.route.check_params()

        async with session.get(self.route.route) as response:
                
            if response.status == 401: #Unauthorized
                raise WrongApiKey(await self.get_json(response, 'error'))

            if response.status in [302, 404]: #Redirection or route not found
                raise RouteNotFound(f'{self.route.route} was not found.', response.status)

            if response.status != 200: #Unknown error
                raise HTTPError(response.status, await self.get_json(response, 'error'))

            if response.status == 200:
                data = await self.get_json(response)
                
                if (type(data) == dict) and ('error' in data):

                    if data.get('error') == 'Replay not available.':
                        raise ReplayUnavailable(data.get('error'))
                        
                    raise HTTPError(400, data.get('error'))

                self._data = data
                return data

    async def fetch(self, session = None):
        """ Fetches some data using the actual route """
        
        if session is not None:
            return await self.fetch_with_session(session)

        async with ClientSession() as session:
            return await self.fetch_with_session(session)