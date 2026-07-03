from fastapi import WebSocket

from app.utils.logging import get_logger

logger = get_logger(__name__)


class ConnectionManager:
    """Tracks active dashboard WebSocket connections and broadcasts JSON messages
    to all of them. A single instance is shared by the /ws router, the MQTT
    handlers, and the offline-watchdog background task."""

    def __init__(self) -> None:
        self._active: set[WebSocket] = set()

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self._active.add(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        self._active.discard(websocket)

    async def broadcast(self, message: dict) -> None:
        dead: list[WebSocket] = []
        for websocket in self._active:
            try:
                await websocket.send_json(message)
            except Exception:
                dead.append(websocket)
        for websocket in dead:
            self.disconnect(websocket)
