"""Order management module.

This file defines the complete in-memory order workflow, including a normal
queue, a priority queue, and a global order registry for future integrations.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import heapq
from itertools import count
from typing import Deque, Dict, List, Optional


class OrderStatus(str, Enum):
    """Available lifecycle states for an order."""

    CREATED = "Created"
    WAITING = "Waiting"
    ASSIGNED = "Assigned"
    IN_TRANSIT = "In transit"
    DELIVERED = "Delivered"
    CANCELLED = "Cancelled"


@dataclass(slots=True)
class Order:
    """Core order entity used by the assignment system."""

    order_id: str
    customer_name: str
    restaurant_name: str
    origin_zone: str
    destination_zone: str
    items: List[str]
    priority: int
    status: OrderStatus = OrderStatus.CREATED
    created_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self) -> None:
        if self.priority not in {1, 2, 3}:
            raise ValueError("Priority must be 1, 2, or 3.")


class OrderManager:
    """Coordinator for in-memory order creation, queueing, and status updates."""

    def __init__(self) -> None:
        # Fast identifier lookup for all created orders.
        self._orders_by_id: Dict[str, Order] = {}

        # Array-style registry that preserves insertion order for reporting.
        self._all_orders: List[Order] = []

        # FIFO queue for standard orders that should be processed by arrival time.
        self._normal_orders_queue: Deque[Order] = deque()

        # Min-heap priority queue where lower numeric priority is processed first.
        self._priority_orders_heap: List[tuple[int, int, Order]] = []
        self._sequence = count()

    def create_order(
        self,
        order_id: str,
        customer_name: str,
        restaurant_name: str,
        origin_zone: str,
        destination_zone: str,
        items: List[str],
        priority: int,
    ) -> Order:
        """Create an order, store it, and enqueue it in the correct structure."""
        if order_id in self._orders_by_id:
            raise ValueError(f"Order '{order_id}' already exists.")

        order = Order(
            order_id=order_id,
            customer_name=customer_name,
            restaurant_name=restaurant_name,
            origin_zone=origin_zone,
            destination_zone=destination_zone,
            items=list(items),
            priority=priority,
            status=OrderStatus.CREATED,
        )

        self._store_order(order)

        if priority == 3:
            self.enqueue_normal_order(order)
        else:
            self.enqueue_priority_order(order)

        return order

    def register_order(self, order: Order) -> None:
        """Register an externally created order and enqueue it."""
        if order.order_id in self._orders_by_id:
            raise ValueError(f"Order '{order.order_id}' already exists.")

        self._store_order(order)

        if order.priority == 3:
            self.enqueue_normal_order(order)
        else:
            self.enqueue_priority_order(order)

    def enqueue_normal_order(self, order: Order) -> None:
        """Add a standard order to the FIFO queue."""
        order.status = OrderStatus.WAITING
        self._normal_orders_queue.append(order)

    def enqueue_priority_order(self, order: Order) -> None:
        """Add an urgent or medium order to the priority queue."""
        order.status = OrderStatus.WAITING
        heapq.heappush(
            self._priority_orders_heap,
            (order.priority, next(self._sequence), order),
        )

    def get_next_order(self) -> Optional[Order]:
        """Return the next pending order, prioritizing the heap before the FIFO queue."""
        priority_order = self._pop_next_priority_order()
        if priority_order is not None:
            return priority_order

        while self._normal_orders_queue:
            order = self._normal_orders_queue.popleft()
            if order.status == OrderStatus.WAITING:
                return order

        return None

    def update_order_status(self, order_id: str, new_status: OrderStatus) -> Order:
        """Update the status of a stored order."""
        order = self._get_required_order(order_id)
        order.status = new_status
        return order

    def cancel_order(self, order_id: str) -> Order:
        """Cancel an order without removing it from historical storage."""
        order = self._get_required_order(order_id)
        order.status = OrderStatus.CANCELLED
        return order

    def list_pending_orders(self) -> List[Order]:
        """Return all orders that are still waiting to be processed."""
        return [
            order
            for order in self._all_orders
            if order.status in {OrderStatus.CREATED, OrderStatus.WAITING}
        ]

    def get_all_orders(self) -> List[Order]:
        """Return all stored orders."""
        return list(self._all_orders)

    def list_orders(self) -> List[Order]:
        """Backward-compatible alias for listing every stored order."""
        return self.get_all_orders()

    def get_order(self, order_id: str) -> Optional[Order]:
        """Return one stored order by identifier."""
        return self._orders_by_id.get(order_id)

    def mark_order_as_assigned(self, order_id: str) -> Order:
        """Mark an order as assigned to a courier."""
        return self.update_order_status(order_id, OrderStatus.ASSIGNED)

    def mark_order_as_delivered(self, order_id: str) -> Order:
        """Mark an order as delivered."""
        return self.update_order_status(order_id, OrderStatus.DELIVERED)

    def _store_order(self, order: Order) -> None:
        """Persist an order in the in-memory registry structures."""
        self._orders_by_id[order.order_id] = order
        self._all_orders.append(order)

    def _get_required_order(self, order_id: str) -> Order:
        """Return an order or raise an explicit error when missing."""
        order = self._orders_by_id.get(order_id)
        if order is None:
            raise KeyError(f"Order '{order_id}' was not found.")
        return order

    def _pop_next_priority_order(self) -> Optional[Order]:
        """Return the next active order from the priority heap."""
        while self._priority_orders_heap:
            _, _, order = heapq.heappop(self._priority_orders_heap)
            if order.status == OrderStatus.WAITING:
                return order
        return None


if __name__ == "__main__":
    manager = OrderManager()

    manager.create_order(
        order_id="ORD-001",
        customer_name="Laura Gomez",
        restaurant_name="Burger House",
        origin_zone="Centro",
        destination_zone="Norte",
        items=["Hamburguesa", "Papas"],
        priority=3,
    )
    manager.create_order(
        order_id="ORD-002",
        customer_name="Carlos Perez",
        restaurant_name="Sushi Point",
        origin_zone="Chapinero",
        destination_zone="Centro",
        items=["Combo sushi", "Bebida"],
        priority=1,
    )
    manager.create_order(
        order_id="ORD-003",
        customer_name="Ana Torres",
        restaurant_name="Pizza Lab",
        origin_zone="Norte",
        destination_zone="Occidente",
        items=["Pizza familiar"],
        priority=2,
    )

    print("Pedidos registrados en memoria:")
    for order in manager.get_all_orders():
        print(
            f"- {order.order_id}: {order.customer_name}, prioridad {order.priority}, "
            f"estado {order.status.value}"
        )

    print("\nProcesamiento de pedidos:")
    next_order = manager.get_next_order()
    if next_order is not None:
        print(
            f"Primer pedido procesado: {next_order.order_id} "
            f"(prioridad {next_order.priority})."
        )
        manager.mark_order_as_assigned(next_order.order_id)
        print(f"Pedido {next_order.order_id} marcado como asignado.")

    next_order = manager.get_next_order()
    if next_order is not None:
        print(
            f"Segundo pedido procesado: {next_order.order_id} "
            f"(prioridad {next_order.priority})."
        )
        manager.mark_order_as_delivered(next_order.order_id)
        print(f"Pedido {next_order.order_id} marcado como entregado.")

    next_order = manager.get_next_order()
    if next_order is not None:
        print(
            f"Tercer pedido procesado: {next_order.order_id} "
            f"(prioridad {next_order.priority})."
        )

    print("\nPedidos pendientes:")
    pending_orders = manager.list_pending_orders()
    if not pending_orders:
        print("No hay pedidos pendientes en espera.")
    else:
        for order in pending_orders:
            print(f"- {order.order_id}: estado {order.status.value}.")
