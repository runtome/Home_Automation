import asyncio
from datetime import timedelta
from typing import TYPE_CHECKING

from sqlalchemy.ext.asyncio import async_sessionmaker

from app.repositories.device_repository import DeviceRepository
from app.repositories.log_repository import LogRepository
from app.schemas.device import DeviceRead
from app.utils.datetime import utcnow
from app.utils.logging import get_logger

if TYPE_CHECKING:
    from app.websocket.manager import ConnectionManager

logger = get_logger(__name__)


async def offline_watchdog(
    session_factory: async_sessionmaker,
    ws_manager: "ConnectionManager | None",
    timeout_seconds: int = 90,
    poll_interval_seconds: int = 15,
) -> None:
    """Marks devices offline once their last heartbeat exceeds timeout_seconds
    (spec: 30s heartbeat interval, 90s offline threshold)."""
    while True:
        await asyncio.sleep(poll_interval_seconds)
        try:
            await _sweep(session_factory, ws_manager, timeout_seconds)
        except Exception:
            logger.exception("offline_watchdog_sweep_failed")


async def _sweep(
    session_factory: async_sessionmaker,
    ws_manager: "ConnectionManager | None",
    timeout_seconds: int,
) -> None:
    cutoff = utcnow() - timedelta(seconds=timeout_seconds)
    async with session_factory() as session:
        device_repo = DeviceRepository(session)
        stale = await device_repo.list_stale(cutoff)
        for device in stale:
            device.online = False
            await LogRepository(session).create_log(
                action="DEVICE_DISCONNECTED",
                device_id=device.id,
                message=f"{device.device_id} heartbeat timeout",
            )
        await session.commit()

        if ws_manager is not None:
            for device in stale:
                await ws_manager.broadcast(
                    {"type": "device_update", "data": DeviceRead.model_validate(device).model_dump(mode="json")}
                )

        if stale:
            logger.info("offline_watchdog_marked_offline", count=len(stale))
