from fastapi import FastAPI

from app.controller.auth_controller import router as auth_router
from app.controller.comman_controller import router as comman_router
from app.controller.user_controller import router as users_router


def register_routes(app: FastAPI) -> None:
    app.include_router(auth_router)
    app.include_router(comman_router)
    app.include_router(users_router)
