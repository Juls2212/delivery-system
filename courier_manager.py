"""Courier management module.

This file defines courier entities and the base manager contract for future
availability, assignment, and routing coordination.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional


class CourierStatus(str, Enum):
    """Base availability states for a courier."""

    AVAILABLE = "available"
    BUSY = "busy"
    OFFLINE = "offline"


@dataclass(slots=True)
class Courier:
    """Core courier entity used by backend services."""

    courier_id: str
    name: str
    current_zone_id: str
    status: CourierStatus = CourierStatus.AVAILABLE
    active_order_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)


class CourierManager:
    """Base courier coordinator with in-memory storage."""

    def __init__(self) -> None:
        self._couriers: Dict[str, Courier] = {}

    def register_courier(self, courier: Courier) -> None:
        """Store a new courier in memory."""
        self._couriers[courier.courier_id] = courier

    def get_courier(self, courier_id: str) -> Optional[Courier]:
        """Return a single courier by its identifier."""
        return self._couriers.get(courier_id)

    def list_couriers(self) -> List[Courier]:
        """Return the current in-memory courier collection."""
        return list(self._couriers.values())

    def set_courier_status(self, courier_id: str, new_status: CourierStatus) -> None:
        """Reserve this method for future availability rules."""
        raise NotImplementedError("Courier status logic will be implemented later.")

    def find_available_couriers(self, zone_id: str) -> List[Courier]:
        """Reserve this method for future filtering and matching logic."""
        raise NotImplementedError("Courier filtering logic will be implemented later.")
