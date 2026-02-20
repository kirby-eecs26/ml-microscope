#logging_store.py

from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from collections import deque
from typing import Deque, Dict, Any, List, Optional
import traceback

MAX_EVENTS = 2000  # keep last N logs in memory (it will overload with too many)

@dataclass
class LogEvent:
    timestamp: str
    event: str
    data: Dict[str, Any] 

_store: Deque[LogEvent] = deque(maxlen=MAX_EVENTS)

#fix date
def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

#copied log structure from ofm
def add_message(
    message: str,
    levelname: str = "INFO",
    filename: str = "",
    lineno: int = 0,
    logger_name: str = "backend",
    levelno: Optional[int] = None,
) -> None:
    if levelno is None:
        levelno = {"DEBUG": 10, "INFO": 20, "WARNING": 30, "ERROR": 40, "CRITICAL": 50}.get(levelname.upper(), 20)

    ev = LogEvent(
        timestamp=now_iso(),
        event="logging",
        data={
            "message": message,
            "created": now_iso(),
            "filename": filename,
            "name": logger_name,
            "levelname": levelname.upper(),
            "lineno": lineno,
            "levelno": levelno,
        },
    )
    _store.append(ev)


def add_exception(e: Exception, context: str = "") -> None:
    msg = f"{context}: {e}" if context else str(e)
    tb = traceback.format_exc()
    add_message(f"{msg}\n{tb}", levelname="ERROR")

#for dropdown filter
def list_events(level: Optional[str] = None) -> List[Dict[str, Any]]:
    if level and level.upper() != "ALL":
        level_u = level.upper()
        return [asdict(x) for x in _store if x.data.get("levelname") == level_u]
    return [asdict(x) for x in _store]