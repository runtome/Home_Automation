from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.repositories.device_repository import DeviceRepository
from app.repositories.log_repository import LogRepository
from app.services.device_service import DeviceService
from app.services.log_service import LogService


def get_log_service(db: AsyncSession = Depends(get_db)) -> LogService:
    return LogService(LogRepository(db))


def get_device_service(
    request: Request,
    db: AsyncSession = Depends(get_db),
    log_service: LogService = Depends(get_log_service),
) -> DeviceService:
    mqtt = getattr(request.app.state, "mqtt_service", None)
    return DeviceService(DeviceRepository(db), log_service, mqtt=mqtt)
