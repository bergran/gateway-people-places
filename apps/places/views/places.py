#  -*- coding: utf-8 -*-
import re
from asyncio import gather
from json import JSONDecodeError

from fastapi import HTTPException, Depends
from fastapi.routing import APIRouter
from starlette import status
from starlette.requests import Request
from starlette.responses import UJSONResponse

from apps.places.services.delete_people import send_delete_people_by_place
from apps.places.services.get_people_list import send_list_people_filter_by_places
from core import config
from core.config import PEOPLE_MICROSERVICES, PLACES_MICROSERVICES
from core.services.proxy import proxy, make_request

router = APIRouter()
router.delete('/{place_id}')(proxy(PLACES_MICROSERVICES))


@router.get('/')
async def list_places(request: Request):
    url = '{}{}?{}'.format(PLACES_MICROSERVICES, re.sub('/api/v[1-9]+', '', request.url.path), request.url.query)

    status_code, response, headers = await make_request('get', url, {}, {})

    if status_code == status.HTTP_200_OK:
        # TODO - improve performance
        await gather(*[send_list_people_filter_by_places(PEOPLE_MICROSERVICES, place, request) for place in response])

    return UJSONResponse(response, status_code=status_code)


@router.post('/')
async def create_places(request: Request):
    try:
        payload = await request.json()
    except JSONDecodeError:
        payload = {}

    payload['resource_origin'] = config.RESOURCE_ORIGIN

    place_url = '{}/places/'.format(PLACES_MICROSERVICES)
    status_code, response, headers = await make_request('post', place_url, payload, dict(request.headers))

    return UJSONResponse(response, status_code=status_code)


@router.get('/{place_id}')
async def detail_places(request: Request):
    url = '{}{}?{}'.format(PLACES_MICROSERVICES, re.sub('/api/v[1-9]+', '', request.url.path), request.url.query)
    status_code, place, headers = await make_request('get', url, {}, {})

    if status_code != status.HTTP_200_OK:
        raise HTTPException(detail='place service send status code {}'.format(status_code), status_code=status_code)

    people_url_filtered = '{}/people/?places_id={}'.format(PEOPLE_MICROSERVICES, place.get('id'))

    headers = dict(request.headers)
    headers.pop('Content-Length', None)

    status_code, people, headers = await make_request('get', people_url_filtered, {}, dict(request.headers))

    if status_code != status.HTTP_200_OK:
        return UJSONResponse(people, status_code=status_code, headers=headers)

    place['people'] = people

    return UJSONResponse(place, status_code=status_code)


@router.put('/{place_id}')
async def update_place(request: Request, place_id: int):
    try:
        payload = await request.json()
    except JSONDecodeError:
        payload = {}

    payload['resource_origin'] = config.RESOURCE_ORIGIN

    place_url = '{}/places/{}'.format(PLACES_MICROSERVICES, place_id)
    status_code, response, headers = await make_request('put', place_url, payload, dict(request.headers))

    return UJSONResponse(response, status_code=status_code)


@router.delete('/{place_id}/hook-delete')
async def delete_place(place_id: int, request: Request):
    status_code, payload, headers = await send_delete_people_by_place(place_id, request)

    if status_code == status.HTTP_204_NO_CONTENT:
        return UJSONResponse(status_code=status.HTTP_200_OK)
    else:
        return UJSONResponse(payload or {}, status_code=status_code, headers=headers)
