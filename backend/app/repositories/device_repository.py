from datetime import datetime

from sqlalchemy import func, select

from app.models.device import Device
from app.repositories.base import BaseRepository


class DeviceRepository(BaseRepository[Device]):
    model = Device

    async def get_by_device_id(self, device_id: str) -> Device | None:
        result = await self.session.execute(select(Device).where(Device.device_id == device_id))
        return result.scalar_one_or_none()

    async def list_devices(
        self,
        room: str | None = None,
        online: bool | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[list[Device], int]:
        query = select(Device)
        count_query = select(func.count()).select_from(Device)
        if room is not None:
            query = query.where(Device.room == room)
            count_query = count_query.where(Device.room == room)
        if online is not None:
            query = query.where(Device.online == online)
            count_query = count_query.where(Device.online == online)

        query = query.order_by(Device.id).limit(limit).offset(offset)

        result = await self.session.execute(query)
        total = (await self.session.execute(count_query)).scalar_one()
        return list(result.scalars().all()), total

    async def list_stale(self, cutoff: datetime) -> list[Device]:
        result = await self.session.execute(
            select(Device).where(Device.online.is_(True), Device.last_seen < cutoff)
        )
        return list(result.scalars().all())
