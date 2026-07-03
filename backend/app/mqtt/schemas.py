from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class SetCommandPayload(BaseModel):
    command: Literal["ON", "OFF"]


class StatusPayload(BaseModel):
    status: Literal["ON", "OFF"]
    timestamp: datetime | None = None


class HeartbeatPayload(BaseModel):
    online: bool = True
    rssi: int | None = None


class RegisterPayload(BaseModel):
    mac_address: str | None = None
    ip_address: str | None = None
    firmware: str | None = None


class InfoPayload(BaseModel):
    firmware: str | None = None
    ip_address: str | None = None
    mac_address: str | None = None
