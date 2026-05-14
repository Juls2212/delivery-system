"""Delivery history module.

This file centralizes delivery event records so future services can expose
timelines, audits, and analytics without a database dependency.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List


@dataclass(slots=True)
class DeliveryEvent:
    """Single historical event for an order lifecycle."""

    order_id: str
    event_type: str
    description: str
    timestamp: datetime = field(default_factory=datetime.utcnow)


class DeliveryHistory:
    """Base event registry with in-memory history storage."""

    def __init__(self) -> None:
        self._events_by_order: Dict[str, List[DeliveryEvent]] = {}

    def record_event(self, event: DeliveryEvent) -> None:
        """Append an event to the corresponding order history."""
        self._events_by_order.setdefault(event.order_id, []).append(event)

    def get_order_history(self, order_id: str) -> List[DeliveryEvent]:
        """Return the current event list for an order."""
        return list(self._events_by_order.get(order_id, []))
