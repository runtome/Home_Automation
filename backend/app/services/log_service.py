from app.models.log import Log
from app.repositories.log_repository import LogRepository


class LogService:
    def __init__(self, repo: LogRepository):
        self.repo = repo

    async def log(
        self,
        action: str,
        user_id: int | None = None,
        device_id: int | None = None,
        message: str | None = None,
    ) -> Log:
        return await self.repo.create_log(
            action=action, user_id=user_id, device_id=device_id, message=message
        )

    async def list_logs(
        self,
        action: str | None = None,
        device_id: int | None = None,
        user_id: int | None = None,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[list[Log], int]:
        offset = (page - 1) * page_size
        return await self.repo.list_logs(
            action=action,
            device_id=device_id,
            user_id=user_id,
            limit=page_size,
            offset=offset,
        )
