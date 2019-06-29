#  -*- coding: utf-8 -*-
from fastapi import HTTPException
from starlette import status

from core.services.proxy import make_request


async def send_list_people_filter_by_places(people_url, place, request):
    people_url_filtered = '{}/people/?places_id={}'.format(people_url, place.get('id'))

    status_code, payload, headers = await make_request('get', people_url_filtered, {}, dict(request.headers))

    if status_code != status.HTTP_200_OK:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    place['people'] = payload

    return status_code, payload, headers
