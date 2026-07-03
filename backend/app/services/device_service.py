from typing import Literal, Protocol

from app.models.device import Device, DeviceStatus
from app.models.user import User
from app.mqtt.topics import set_topic
from app.repositories.device_repository import DeviceRepository
from app.schemas.device import DeviceCreate, DeviceUpdate
from app.services.log_service import LogService
from app.utils.logging import get_logger

logger = get_logger(__name__)


class MQTTPublisher(Protocol):
    async def publish(self, topic: str, payload: dict) -> None: ...


class DeviceError(Exception):
    """Raised for device lookups/conflicts that should surface as 404/409."""


class DeviceService:
    def __init__(
        self,
        repo: DeviceRepository,
        log_service: LogService,
        mqtt: MQTTPublisher | None = None,
    ):
        self.repo = repo
        self.log_service = log_service
        self.mqtt = mqtt

    async def list_devices(
        self, room: str | None = None, online: bool | None = None, page: int = 1, page_size: int = 50
    ) -> tuple[list[Device], int]:
        offset = (page - 1) * page_size
        return await self.repo.list_devices(room=room, online=online, limit=page_size, offset=offset)

    async def get_device(self, device_pk: int) -> Device:
        device = await self.repo.get(device_pk)
        if device is None:
            raise DeviceError("device not found")
        return device

    async def create_device(self, data: DeviceCreate) -> Device:
        if await self.repo.get_by_device_id(data.device_id) is not None:
            raise DeviceError("device_id already registered")
        device = Device(
            device_id=data.device_id,
            device_name=data.device_name,
            room=data.room,
            status=DeviceStatus.UNKNOWN,
            online=False,
        )
        return await self.repo.add(device)

    async def update_device(self, device_pk: int, data: DeviceUpdate) -> Device:
        device = await self.get_device(device_pk)
        if data.device_name is not None:
            device.device_name = data.device_name
        if data.room is not None:
            device.room = data.room
        await self.repo.session.flush()
        return device

    async def delete_device(self, device_pk: int) -> None:
        device = await self.get_device(device_pk)
        await self.repo.delete(device)

    async def send_relay_command(
        self, device_pk: int, command: Literal["ON", "OFF", "TOGGLE"], actor: User
    ) -> Device:
        device = await self.get_device(device_pk)

        if command == "TOGGLE":
            target = DeviceStatus.OFF if device.status == DeviceStatus.ON else DeviceStatus.ON
        else:
            target = DeviceStatus(command)

        if self.mqtt is not None:
            try:
                await self.mqtt.publish(set_topic(device.device_id), {"command": target.value})
            except RuntimeError:
                # Broker briefly unreachable (mid-reconnect). We still apply the
                # optimistic update below so the dashboard/API stay usable during
                # a reconnect window (spec's "reconnect automatically" / 24-7
                # availability requirement); the status echo once MQTT recovers
                # reconciles the device's real state.
                logger.warning("mqtt_publish_failed_broker_disconnected", device_id=device.device_id)

        # Optimistic update: the dashboard reflects intent immediately (spec's <1s
        # target); the MQTT status echo (mqtt/handlers.py) reconciles with the
        # device's actual reported state moments later.
        device.status = target
        await self.repo.session.flush()

        await self.log_service.log(
            action=f"RELAY_{target.value}",
            user_id=actor.id,
            device_id=device.id,
            message=f"{actor.username} set {device.device_id} to {target.value}",
        )
        return device
