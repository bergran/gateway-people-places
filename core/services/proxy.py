# -*- coding: utf-8 -*-
import asyncio
import re
from json.decoder import JSONDecodeError

import aiohttp
from aiohttp.hdrs import CONTENT_TYPE
from starlette import status
from starlette.requests import Request
from starlette.responses import UJSONResponse


async def make_request(method, url, payload, headers):
    headers.pop('content-length', None)

    timeout = aiohttp.ClientTimeout(total=5)
    url = '{}'.format(url)

    async with aiohttp.ClientSession(timeout=timeout) as session:
        request_method = getattr(session, method, 'get')
        try:
            async with request_method(url, json=payload) as response:
                if response.headers.get(CONTENT_TYPE) == 'application/json':
                    payload = await response.json()
                else:
                    payload = await response.text()

                return response.status, payload, response.headers
        except aiohttp.ClientConnectorError:
            return status.HTTP_500_INTERNAL_SERVER_ERROR, {
                'detail': 'error on try to connect with {} service'.format(url)
            }, {}
        except asyncio.TimeoutError:
            return status.HTTP_500_INTERNAL_SERVER_ERROR, {
                'detail': 'error on try to connect with {} service'.format(url)
            }, {}


def proxy(microservice_url: str):
    async def wrap(request: Request):
        try:
            payload = await request.json()
        except JSONDecodeError:
            payload = {}

        url = '{}{}?{}'.format(microservice_url, re.sub('/api/v[1-9]+', '', request.url.path), request.url.query)

        status_code, payload, headers = await make_request(
            request.method.lower(),
            url,
            payload,
            dict(request.headers)
        )

        return UJSONResponse(payload, status_code=status_code, headers=headers)

    return wrap
