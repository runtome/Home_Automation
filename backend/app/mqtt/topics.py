"""MQTT topic builders/parsers per specification.md section 7.

home/{device_id}/set         backend -> device (relay commands)
home/{device_id}/status      device -> backend (relay confirmation)
home/{device_id}/heartbeat   device -> backend (liveness + rssi)
home/{device_id}/register    device -> backend (first contact: mac/ip/firmware)
home/{device_id}/info        device -> backend (info updates: firmware/ip/mac)
"""

SUBSCRIBE_FILTERS = ("home/+/status", "home/+/heartbeat", "home/+/register", "home/+/info")

_SUFFIXES = ("set", "status", "heartbeat", "register", "info")


def set_topic(device_id: str) -> str:
    return f"home/{device_id}/set"


def status_topic(device_id: str) -> str:
    return f"home/{device_id}/status"


def heartbeat_topic(device_id: str) -> str:
    return f"home/{device_id}/heartbeat"


def register_topic(device_id: str) -> str:
    return f"home/{device_id}/register"


def info_topic(device_id: str) -> str:
    return f"home/{device_id}/info"


def parse_topic(topic: str) -> tuple[str, str] | None:
    """Parses 'home/{device_id}/{suffix}' -> (device_id, suffix), or None if malformed."""
    parts = topic.split("/")
    if len(parts) != 3 or parts[0] != "home" or parts[2] not in _SUFFIXES:
        return None
    return parts[1], parts[2]
