from fastapi import APIRouter, Depends, Query

from app.api.deps import get_log_service
from app.auth.dependencies import get_current_user
from app.schemas.common import PaginatedResponse
from app.schemas.log import LogRead
from app.services.log_service import LogService

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.get("", response_model=PaginatedResponse[LogRead])
async def list_logs(
    action: str | None = None,
    device_id: int | None = None,
    user_id: int | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=200),
    service: LogService = Depends(get_log_service),
) -> PaginatedResponse[LogRead]:
    logs, total = await service.list_logs(
        action=action, device_id=device_id, user_id=user_id, page=page, page_size=page_size
    )
    return PaginatedResponse(
        items=[LogRead.model_validate(log) for log in logs], total=total, page=page, page_size=page_size
    )
