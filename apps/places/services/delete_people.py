# -*- coding: utf-8 -*-
from core.config import PEOPLE_MICROSERVICES
from core.services.proxy import make_request


async def send_delete_people_by_place(place_id, request):
    delete_people_url = '{}/people/place/{}'.format(PEOPLE_MICROSERVICES, place_id)
    status_code, payload, headers = await make_request('delete', delete_people_url, {}, dict(request.headers))
    return status_code, payload, headers
