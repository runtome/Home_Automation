import jwt
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, status

from app.auth.security import decode_token
from app.database.session import get_db
from app.repositories.user_repository import UserRepository
from app.utils.logging import get_logger

logger = get_logger(__name__)

router = APIRouter()


async def _authenticate(websocket: WebSocket) -> bool:
    token = websocket.query_params.get("token")
    if token is None:
        return False
    try:
        decoded = decode_token(token, expected_type="access")
    except jwt.InvalidTokenError:
        return False

    async for db in get_db():
        user = await UserRepository(db).get(decoded.sub)
        return user is not None
    return False


@router.websocket("/ws/devices")
async def ws_devices(websocket: WebSocket) -> None:
    if not await _authenticate(websocket):
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    ws_manager = websocket.app.state.ws_manager
    await ws_manager.connect(websocket)
    try:
        while True:
            # Dashboard is a listen-only client; drain any client pings/messages.
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        ws_manager.disconnect(websocket)
