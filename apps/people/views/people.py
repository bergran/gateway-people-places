#  -*- coding: utf-8 -*-
from json import JSONDecodeError

from fastapi import HTTPException
from fastapi.routing import APIRouter
from starlette import status
from starlette.requests import Request

from core.services.proxy import proxy, make_request
from core.config import PEOPLE_MICROSERVICES, PLACES_MICROSERVICES

router = APIRouter()
router.get('/')(proxy(PEOPLE_MICROSERVICES))
router.get('/{people_id}')(proxy(PEOPLE_MICROSERVICES))
router.delete('/{people_id}')(proxy(PEOPLE_MICROSERVICES))


@router.post('/')
async def create_people(request: Request):
    await validate_place_id(request)
    return await proxy(PEOPLE_MICROSERVICES)(request)


@router.put('/{people_id}')
async def update_people(request: Request):
    await validate_place_id(request)
    return await proxy(PEOPLE_MICROSERVICES)(request)


async def validate_place_id(request):
    try:
        payload = await request.json()
    except JSONDecodeError:
        raise HTTPException(
            detail='payload can not be decode',
            status_code=status.HTTP_400_BAD_REQUEST
        )

    place_id = payload.get('place_id')
    if place_id is None:
        raise HTTPException(
            detail='place_id is required',
            status_code=status.HTTP_400_BAD_REQUEST
        )

    url_place = '{}/places/{}'.format(PLACES_MICROSERVICES, place_id)
    status_code, payload, headers = await make_request(
        'get',
        url_place,
        payload,
        dict(request.headers)
    )

    if status_code != status.HTTP_200_OK:
        raise HTTPException(
            detail='people does not exists',
            status_code=status.HTTP_400_BAD_REQUEST
        )
