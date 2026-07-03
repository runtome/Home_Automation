from sqlalchemy import desc, func, select

from app.models.log import Log
from app.repositories.base import BaseRepository


class LogRepository(BaseRepository[Log]):
    model = Log

    async def create_log(
        self,
        action: str,
        user_id: int | None = None,
        device_id: int | None = None,
        message: str | None = None,
    ) -> Log:
        log = Log(action=action, user_id=user_id, device_id=device_id, message=message)
        return await self.add(log)

    async def list_logs(
        self,
        action: str | None = None,
        device_id: int | None = None,
        user_id: int | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[Log], int]:
        query = select(Log)
        count_query = select(func.count()).select_from(Log)
        if action is not None:
            query = query.where(Log.action == action)
            count_query = count_query.where(Log.action == action)
        if device_id is not None:
            query = query.where(Log.device_id == device_id)
            count_query = count_query.where(Log.device_id == device_id)
        if user_id is not None:
            query = query.where(Log.user_id == user_id)
            count_query = count_query.where(Log.user_id == user_id)

        query = query.order_by(desc(Log.created_at)).limit(limit).offset(offset)

        result = await self.session.execute(query)
        total = (await self.session.execute(count_query)).scalar_one()
        return list(result.scalars().all()), total
