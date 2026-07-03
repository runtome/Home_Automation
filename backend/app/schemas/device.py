from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.device import DeviceStatus


class DeviceCreate(BaseModel):
    device_id: str = Field(min_length=1, max_length=64)
    device_name: str = Field(min_length=1, max_length=128)
    room: str = Field(min_length=1, max_length=64)


class DeviceUpdate(BaseModel):
    device_name: str | None = Field(default=None, min_length=1, max_length=128)
    room: str | None = Field(default=None, min_length=1, max_length=64)


class DeviceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    device_id: str
    device_name: str
    room: str
    status: DeviceStatus
    online: bool
    ip_address: str | None
    mac_address: str | None
    firmware: str | None
    rssi: int | None
    last_seen: datetime | None
    created_at: datetime


class RelayCommandResponse(BaseModel):
    device_id: str
    status: DeviceStatus
    message: str
