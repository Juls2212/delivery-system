"""Order management module.

This file defines order entities and the base manager contract for future
assignment, tracking, and frontend integration workflows.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional


class OrderStatus(str, Enum):
    """Base lifecycle states for an order."""

    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


@dataclass(slots=True)
class Order:
    """Core order entity used by backend services."""

    order_id: str
    customer_name: str
    delivery_address: str
    zone_id: str
    status: OrderStatus = OrderStatus.PENDING
    assigned_courier_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)


class OrderManager:
    """Base order coordinator with in-memory storage."""

    def __init__(self) -> None:
        self._orders: Dict[str, Order] = {}

    def register_order(self, order: Order) -> None:
        """Store a new order in memory."""
        self._orders[order.order_id] = order

    def get_order(self, order_id: str) -> Optional[Order]:
        """Return a single order by its identifier."""
        return self._orders.get(order_id)

    def list_orders(self) -> List[Order]:
        """Return the current in-memory order collection."""
        return list(self._orders.values())

    def assign_order(self, order_id: str, courier_id: str) -> None:
        """Reserve this method for future assignment logic."""
        raise NotImplementedError("Assignment logic will be implemented later.")

    def update_order_status(self, order_id: str, new_status: OrderStatus) -> None:
        """Reserve this method for future status transition rules."""
        raise NotImplementedError("Status update logic will be implemented later.")
