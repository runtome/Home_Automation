from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

import asyncio

from app.api.routes.devices import router as devices_router
from app.api.routes.health import router as health_router
from app.api.routes.logs import router as logs_router
from app.auth.router import router as auth_router
from app.config import get_settings
from app.database.session import async_session_maker, engine
from app.mqtt.client import MQTTService
from app.utils.background_tasks import offline_watchdog
from app.utils.logging import get_logger, setup_logging
from app.utils.rate_limit import limiter
from app.websocket.manager import ConnectionManager
from app.websocket.router import router as websocket_router

settings = get_settings()
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("app_startup")
    ws_manager = ConnectionManager()
    mqtt_service = MQTTService(settings, async_session_maker, ws_manager=ws_manager)
    mqtt_service.start()
    watchdog_task = asyncio.create_task(
        offline_watchdog(
            async_session_maker,
            ws_manager,
            timeout_seconds=settings.heartbeat_timeout_seconds,
            poll_interval_seconds=settings.heartbeat_poll_interval_seconds,
        ),
        name="offline-watchdog",
    )
    app.state.mqtt_service = mqtt_service
    app.state.ws_manager = ws_manager
    yield
    logger.info("app_shutdown")
    watchdog_task.cancel()
    try:
        await watchdog_task
    except asyncio.CancelledError:
        pass
    await mqtt_service.stop()
    await engine.dispose()


app = FastAPI(title="Home Automation Platform API", version="0.1.0", lifespan=lifespan)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(devices_router, prefix="/devices", tags=["devices"])
app.include_router(logs_router, prefix="/logs", tags=["logs"])
app.include_router(health_router, tags=["health"])
app.include_router(websocket_router, tags=["websocket"])
