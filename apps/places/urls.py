#  -*- coding: utf-8 -*-

from fastapi.routing import APIRouter

from apps.places.views.places import router as router_places

router = APIRouter()
router.include_router(router_places, prefix='/places')
