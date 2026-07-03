import json
from typing import TYPE_CHECKING

from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.device import Device, DeviceStatus
from app.mqtt.schemas import HeartbeatPayload, InfoPayload, RegisterPayload, StatusPayload
from app.repositories.device_repository import DeviceRepository
from app.repositories.log_repository import LogRepository
from app.schemas.device import DeviceRead
from app.utils.datetime import utcnow
from app.utils.logging import get_logger

if TYPE_CHECKING:
    from app.websocket.manager import ConnectionManager

logger = get_logger(__name__)


async def _broadcast_device_update(ws_manager: "ConnectionManager | None", device: Device) -> None:
    if ws_manager is None:
        return
    await ws_manager.broadcast(
        {"type": "device_update", "data": DeviceRead.model_validate(device).model_dump(mode="json")}
    )


async def handle_status(
    session: AsyncSession, ws_manager: "ConnectionManager | None", device_id: str, raw_payload: bytes
) -> None:
    payload = StatusPayload.model_validate_json(raw_payload)
    device = await DeviceRepository(session).get_by_device_id(device_id)
    if device is None:
        logger.warning("status_for_unknown_device", device_id=device_id)
        return

    new_status = DeviceStatus(payload.status)
    if device.status != new_status:
        device.status = new_status
        await LogRepository(session).create_log(
            action=f"RELAY_{new_status.value}",
            device_id=device.id,
            message=f"{device_id} reported status {new_status.value}",
        )
    await session.commit()
    await _broadcast_device_update(ws_manager, device)


async def handle_heartbeat(
    session: AsyncSession, ws_manager: "ConnectionManager | None", device_id: str, raw_payload: bytes
) -> None:
    payload = HeartbeatPayload.model_validate_json(raw_payload)
    repo = DeviceRepository(session)
    device = await repo.get_by_device_id(device_id)
    if device is None:
        logger.warning("heartbeat_for_unknown_device", device_id=device_id)
        return

    was_online = device.online
    device.online = payload.online
    device.rssi = payload.rssi
    device.last_seen = utcnow()

    if payload.online and not was_online:
        await LogRepository(session).create_log(
            action="DEVICE_CONNECTED", device_id=device.id, message=f"{device_id} came online"
        )
    await session.commit()
    await _broadcast_device_update(ws_manager, device)


async def handle_register(
    session: AsyncSession, ws_manager: "ConnectionManager | None", device_id: str, raw_payload: bytes
) -> None:
    payload = RegisterPayload.model_validate_json(raw_payload)
    device = await DeviceRepository(session).get_by_device_id(device_id)
    if device is None:
        logger.warning("register_for_unknown_device", device_id=device_id)
        return

    if payload.mac_address is not None:
        device.mac_address = payload.mac_address
    if payload.ip_address is not None:
        device.ip_address = payload.ip_address
    if payload.firmware is not None:
        device.firmware = payload.firmware
    device.online = True
    device.last_seen = utcnow()
    await session.commit()
    await _broadcast_device_update(ws_manager, device)


async def handle_info(
    session: AsyncSession, ws_manager: "ConnectionManager | None", device_id: str, raw_payload: bytes
) -> None:
    payload = InfoPayload.model_validate_json(raw_payload)
    device = await DeviceRepository(session).get_by_device_id(device_id)
    if device is None:
        logger.warning("info_for_unknown_device", device_id=device_id)
        return

    if payload.firmware is not None:
        device.firmware = payload.firmware
    if payload.ip_address is not None:
        device.ip_address = payload.ip_address
    if payload.mac_address is not None:
        device.mac_address = payload.mac_address
    await session.commit()
    await _broadcast_device_update(ws_manager, device)


HANDLERS = {
    "status": handle_status,
    "heartbeat": handle_heartbeat,
    "register": handle_register,
    "info": handle_info,
}


async def dispatch(
    session: AsyncSession,
    ws_manager: "ConnectionManager | None",
    device_id: str,
    suffix: str,
    raw_payload: bytes,
) -> None:
    handler = HANDLERS.get(suffix)
    if handler is None:
        logger.warning("no_handler_for_suffix", suffix=suffix)
        return
    try:
        await handler(session, ws_manager, device_id, raw_payload)
    except (ValidationError, json.JSONDecodeError) as exc:
        logger.warning("mqtt_payload_parse_error", device_id=device_id, suffix=suffix, error=str(exc))
