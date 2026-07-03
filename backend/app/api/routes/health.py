from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Request
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db

router = APIRouter()


@router.get("/health")
async def health(request: Request, db: AsyncSession = Depends(get_db)) -> dict:
    try:
        await db.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception:
        db_status = "error"

    mqtt_service = getattr(request.app.state, "mqtt_service", None)
    mqtt_status = "connected" if mqtt_service is not None and mqtt_service.is_connected else "disconnected"

    return {
        "status": "ok" if db_status == "ok" else "degraded",
        "db": db_status,
        "mqtt": mqtt_status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
