import asyncio
import json
from typing import TYPE_CHECKING

import aiomqtt
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.config import Settings
from app.mqtt import handlers
from app.mqtt.topics import SUBSCRIBE_FILTERS, parse_topic
from app.utils.logging import get_logger

if TYPE_CHECKING:
    from app.websocket.manager import ConnectionManager

logger = get_logger(__name__)

RECONNECT_DELAY_SECONDS = 5


class MQTTService:
    """Dedicated MQTT service layer: maintains a single long-lived connection to the
    broker with automatic reconnect, subscribes to device topics, dispatches inbound
    messages to app.mqtt.handlers, and exposes publish() for outbound relay commands.
    """

    def __init__(
        self,
        settings: Settings,
        session_factory: async_sessionmaker,
        ws_manager: "ConnectionManager | None" = None,
    ):
        self._settings = settings
        self._session_factory = session_factory
        self._ws_manager = ws_manager
        self._client: aiomqtt.Client | None = None
        self._task: asyncio.Task | None = None

    @property
    def is_connected(self) -> bool:
        return self._client is not None

    def start(self) -> None:
        self._task = asyncio.create_task(self._run(), name="mqtt-service")

    async def stop(self) -> None:
        if self._task is None:
            return
        self._task.cancel()
        try:
            await self._task
        except asyncio.CancelledError:
            pass

    async def _run(self) -> None:
        while True:
            try:
                async with aiomqtt.Client(
                    hostname=self._settings.mqtt_host,
                    port=self._settings.mqtt_port,
                    username=self._settings.mqtt_username,
                    password=self._settings.mqtt_password,
                ) as client:
                    self._client = client
                    logger.info("mqtt_connected", host=self._settings.mqtt_host)
                    for topic_filter in SUBSCRIBE_FILTERS:
                        await client.subscribe(topic_filter)
                    async for message in client.messages:
                        await self._dispatch(message)
            except aiomqtt.MqttError as exc:
                self._client = None
                logger.warning("mqtt_connection_lost", error=str(exc), retry_in=RECONNECT_DELAY_SECONDS)
                await asyncio.sleep(RECONNECT_DELAY_SECONDS)
            except asyncio.CancelledError:
                self._client = None
                raise

    async def _dispatch(self, message: aiomqtt.Message) -> None:
        parsed = parse_topic(str(message.topic))
        if parsed is None:
            logger.warning("mqtt_unrecognized_topic", topic=str(message.topic))
            return
        device_id, suffix = parsed
        async with self._session_factory() as session:
            await handlers.dispatch(session, self._ws_manager, device_id, suffix, message.payload)

    async def publish(self, topic: str, payload: dict) -> None:
        if self._client is None:
            raise RuntimeError("MQTT client is not connected")
        await self._client.publish(topic, json.dumps(payload), qos=1)
