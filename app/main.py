from fastapi import FastAPI
from slowapi.middleware import SlowAPIMiddleware
from app.core.database import engine, Base

from .core.api import register_routes
from .core.logging import LogLevels, configure_logging
from .core.rate_limiter import limiter

configure_logging(LogLevels.info)

app = FastAPI()
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

Base.metadata.create_all(bind=engine)
register_routes(app)
