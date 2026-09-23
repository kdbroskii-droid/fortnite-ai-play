"""Simple structured event log for testing and diagnostics."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
import json

@dataclass
class EventLog:
    events: list[dict] = field(default_factory=list)

    def add(self, event: str, **data) -> None:
        self.events.append({
            "time": datetime.now(timezone.utc).isoformat(),
            "event": event,
            **data,
        })

    def to_json(self) -> str:
        return json.dumps(self.events, indent=2)
