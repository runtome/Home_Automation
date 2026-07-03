from datetime import datetime

from pydantic import BaseModel, ConfigDict


class LogRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int | None
    device_id: int | None
    action: str
    message: str | None
    created_at: datetime
