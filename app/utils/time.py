# app/utils/time.py
from datetime import datetime, timezone


def to_dt_from_ms(ts_ms: int | None) -> datetime:
    if ts_ms is None:
        return datetime.now(timezone.utc)
    return datetime.fromtimestamp(ts_ms / 1000.0, tz=timezone.utc)


def now_utc() -> datetime:
    return datetime.now(timezone.utc)
