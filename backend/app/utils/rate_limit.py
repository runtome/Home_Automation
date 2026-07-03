"""Lightweight placeholder rate limiting via slowapi, applied to /auth/login.

Full API-wide rate limiting, per-user quotas, and distributed (Redis-backed) limits
are deferred to a future pass per specification.md section 11.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address, default_limits=[])
