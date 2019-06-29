#  -*- coding: utf-8 -*-

from fastapi.routing import APIRouter

from apps.people.views.people import router as router_people

router = APIRouter()
router.include_router(router_people, prefix='/people')
