from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_device_service
from app.auth.dependencies import get_current_user, require_role
from app.database.session import get_db
from app.models.user import Role, User
from app.schemas.common import PaginatedResponse
from app.schemas.device import DeviceCreate, DeviceRead, DeviceUpdate
from app.services.device_service import DeviceError, DeviceService

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.get("", response_model=PaginatedResponse[DeviceRead])
async def list_devices(
    room: str | None = None,
    online: bool | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=200),
    service: DeviceService = Depends(get_device_service),
) -> PaginatedResponse[DeviceRead]:
    devices, total = await service.list_devices(room=room, online=online, page=page, page_size=page_size)
    return PaginatedResponse(
        items=[DeviceRead.model_validate(d) for d in devices], total=total, page=page, page_size=page_size
    )


@router.get("/{device_pk}", response_model=DeviceRead)
async def get_device(
    device_pk: int, service: DeviceService = Depends(get_device_service)
) -> DeviceRead:
    try:
        device = await service.get_device(device_pk)
    except DeviceError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return DeviceRead.model_validate(device)


@router.post("", response_model=DeviceRead, status_code=status.HTTP_201_CREATED)
async def create_device(
    data: DeviceCreate,
    db: AsyncSession = Depends(get_db),
    service: DeviceService = Depends(get_device_service),
    _admin: User = Depends(require_role(Role.ADMIN)),
) -> DeviceRead:
    try:
        device = await service.create_device(data)
    except DeviceError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    await db.commit()
    return DeviceRead.model_validate(device)


@router.put("/{device_pk}", response_model=DeviceRead)
async def update_device(
    device_pk: int,
    data: DeviceUpdate,
    db: AsyncSession = Depends(get_db),
    service: DeviceService = Depends(get_device_service),
    _admin: User = Depends(require_role(Role.ADMIN)),
) -> DeviceRead:
    try:
        device = await service.update_device(device_pk, data)
    except DeviceError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    await db.commit()
    return DeviceRead.model_validate(device)


@router.delete("/{device_pk}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_device(
    device_pk: int,
    db: AsyncSession = Depends(get_db),
    service: DeviceService = Depends(get_device_service),
    _admin: User = Depends(require_role(Role.ADMIN)),
) -> None:
    try:
        await service.delete_device(device_pk)
    except DeviceError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    await db.commit()


async def _relay(
    device_pk: int,
    command: Literal["ON", "OFF", "TOGGLE"],
    db: AsyncSession,
    service: DeviceService,
    user: User,
) -> DeviceRead:
    try:
        device = await service.send_relay_command(device_pk, command, user)
    except DeviceError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    await db.commit()
    return DeviceRead.model_validate(device)


@router.post("/{device_pk}/on", response_model=DeviceRead)
async def turn_on(
    device_pk: int,
    db: AsyncSession = Depends(get_db),
    service: DeviceService = Depends(get_device_service),
    user: User = Depends(get_current_user),
) -> DeviceRead:
    return await _relay(device_pk, "ON", db, service, user)


@router.post("/{device_pk}/off", response_model=DeviceRead)
async def turn_off(
    device_pk: int,
    db: AsyncSession = Depends(get_db),
    service: DeviceService = Depends(get_device_service),
    user: User = Depends(get_current_user),
) -> DeviceRead:
    return await _relay(device_pk, "OFF", db, service, user)


@router.post("/{device_pk}/toggle", response_model=DeviceRead)
async def toggle(
    device_pk: int,
    db: AsyncSession = Depends(get_db),
    service: DeviceService = Depends(get_device_service),
    user: User = Depends(get_current_user),
) -> DeviceRead:
    return await _relay(device_pk, "TOGGLE", db, service, user)
