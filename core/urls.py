# -*- coding: utf-8 -*-

from fastapi.routing import APIRouter

from apps.health_check.urls import router as router_health_check
from apps.people.urls import router as router_people
from apps.places.urls import router as router_places

router = APIRouter()
router.include_router(router_health_check, prefix='/api/v1', tags=['health_check'])
router.include_router(router_people, prefix='/api/v1', tags=['people'])
router.include_router(router_places, prefix='/api/v1', tags=['places'])
