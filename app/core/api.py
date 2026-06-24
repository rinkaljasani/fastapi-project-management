from fastapi import FastAPI

from app.controller.auth_controller import router as auth_router
# from app.controller.todo_controller import router as todos_router
from app.controller.user_controller import router as users_router


def register_routes(app: FastAPI) -> None:
    app.include_router(auth_router)
    # app.include_router(todos_router)
    app.include_router(users_router)