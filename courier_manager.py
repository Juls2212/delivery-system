"""Courier management module.

This file implements courier assignment using a doubly circular linked list for
fair rotation, plus in-memory registries for frontend-friendly access.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass(slots=True, init=False)
class Courier:
    """Core courier entity used by the assignment system."""

    courier_id: str
    name: str
    current_zone: str
    is_available: bool
    active_orders: List[str]
    delivered_orders_count: int

    def __init__(
        self,
        courier_id: str,
        name: str,
        current_zone: Optional[str] = None,
        is_available: bool = True,
        active_orders: Optional[List[str]] = None,
        delivered_orders_count: int = 0,
        current_zone_id: Optional[str] = None,
    ) -> None:
        resolved_zone = current_zone if current_zone is not None else current_zone_id
        if not resolved_zone:
            raise ValueError("A current zone is required for every courier.")

        self.courier_id = courier_id
        self.name = name
        self.current_zone = resolved_zone
        self.is_available = is_available
        self.active_orders = list(active_orders or [])
        self.delivered_orders_count = delivered_orders_count

    @property
    def current_zone_id(self) -> str:
        """Compatibility alias for older seed/bootstrap code."""
        return self.current_zone


@dataclass(slots=True)
class CourierNode:
    """Node used by the doubly circular linked list."""

    courier: Courier
    next: Optional[CourierNode] = None
    previous: Optional[CourierNode] = None


class CircularCourierList:
    """Real doubly circular linked list for round-robin courier rotation."""

    def __init__(self) -> None:
        self.head: Optional[CourierNode] = None
        self.current: Optional[CourierNode] = None
        self.size: int = 0

    def add_courier(self, courier: Courier) -> CourierNode:
        """Insert a courier node into the circular structure."""
        new_node = CourierNode(courier=courier)

        if self.head is None:
            new_node.next = new_node
            new_node.previous = new_node
            self.head = new_node
            self.current = new_node
            self.size = 1
            return new_node

        assert self.head.previous is not None
        tail = self.head.previous

        new_node.next = self.head
        new_node.previous = tail
        tail.next = new_node
        self.head.previous = new_node
        self.size += 1
        return new_node

    def remove_courier(self, courier_id: str) -> Optional[Courier]:
        """Remove a courier node by identifier."""
        target_node = self._find_node(courier_id)
        if target_node is None:
            return None

        removed_courier = target_node.courier

        if self.size == 1:
            self.head = None
            self.current = None
            self.size = 0
            return removed_courier

        assert target_node.next is not None
        assert target_node.previous is not None

        target_node.previous.next = target_node.next
        target_node.next.previous = target_node.previous

        if self.head == target_node:
            self.head = target_node.next

        if self.current == target_node:
            self.current = target_node.next

        self.size -= 1
        return removed_courier

    def get_next_available_courier(self) -> Optional[Courier]:
        """Return the next available courier using circular rotation."""
        if self.current is None or self.size == 0:
            return None

        start_node = self.current
        node = start_node

        while True:
            if node.courier.is_available:
                return node.courier

            assert node.next is not None
            node = node.next
            if node == start_node:
                break

        return None

    def move_to_next(self) -> Optional[Courier]:
        """Rotate the current pointer forward in the circle."""
        if self.current is None:
            return None

        assert self.current.next is not None
        self.current = self.current.next
        return self.current.courier

    def move_to_previous(self) -> Optional[Courier]:
        """Rotate the current pointer backward in the circle."""
        if self.current is None:
            return None

        assert self.current.previous is not None
        self.current = self.current.previous
        return self.current.courier

    def mark_courier_busy(self, courier_id: str) -> bool:
        """Set a courier node as busy inside the list."""
        node = self._find_node(courier_id)
        if node is None:
            return False

        node.courier.is_available = False
        return True

    def mark_courier_available(self, courier_id: str) -> bool:
        """Set a courier node as available inside the list."""
        node = self._find_node(courier_id)
        if node is None:
            return False

        node.courier.is_available = True
        return True

    def list_couriers(self) -> List[Courier]:
        """Return all couriers in circular order starting from the head."""
        couriers: List[Courier] = []
        if self.head is None:
            return couriers

        node = self.head
        while True:
            couriers.append(node.courier)
            assert node.next is not None
            node = node.next
            if node == self.head:
                break

        return couriers

    def _find_node(self, courier_id: str) -> Optional[CourierNode]:
        """Find a node by courier identifier."""
        if self.head is None:
            return None

        node = self.head
        while True:
            if node.courier.courier_id == courier_id:
                return node

            assert node.next is not None
            node = node.next
            if node == self.head:
                break

        return None


class CourierManager:
    """Coordinator for courier storage, assignment, and round-robin rotation."""

    def __init__(self) -> None:
        # Dictionary lookup supports fast access by courier identifier.
        self._couriers_by_id: Dict[str, Courier] = {}

        # Array-style registry keeps a simple full snapshot for reporting layers.
        self._all_couriers: List[Courier] = []

        # The doubly circular linked list provides fair rotation across couriers.
        self._courier_rotation = CircularCourierList()

    def add_courier(self, courier: Courier) -> None:
        """Store a courier and insert it into the rotation structure."""
        if courier.courier_id in self._couriers_by_id:
            raise ValueError(f"Courier '{courier.courier_id}' already exists.")

        self._couriers_by_id[courier.courier_id] = courier
        self._all_couriers.append(courier)
        self._courier_rotation.add_courier(courier)

    def register_courier(self, courier: Courier) -> None:
        """Compatibility alias for existing bootstrap code."""
        self.add_courier(courier)

    def remove_courier(self, courier_id: str) -> Optional[Courier]:
        """Remove a courier from every in-memory structure."""
        courier = self._couriers_by_id.pop(courier_id, None)
        if courier is None:
            return None

        self._all_couriers = [
            stored_courier
            for stored_courier in self._all_couriers
            if stored_courier.courier_id != courier_id
        ]
        self._courier_rotation.remove_courier(courier_id)
        return courier

    def assign_order_to_courier(self, order: object) -> Optional[Courier]:
        """Assign an order to the next available courier and rotate the pointer."""
        courier = self._courier_rotation.get_next_available_courier()
        if courier is None:
            return None

        order_id = getattr(order, "order_id", None)
        if order_id is None:
            raise ValueError("The provided order must expose an 'order_id' attribute.")

        courier.active_orders.append(order_id)
        self._courier_rotation.mark_courier_busy(courier.courier_id)
        self._courier_rotation.move_to_next()
        return courier

    def complete_order(self, courier_id: str, order_id: str) -> Courier:
        """Complete an assigned order and release the courier when possible."""
        courier = self._get_required_courier(courier_id)
        if order_id not in courier.active_orders:
            raise ValueError(
                f"Order '{order_id}' is not assigned to courier '{courier_id}'."
            )

        courier.active_orders.remove(order_id)
        courier.delivered_orders_count += 1

        if not courier.active_orders:
            self._courier_rotation.mark_courier_available(courier_id)

        return courier

    def get_available_couriers(self) -> List[Courier]:
        """Return all couriers currently available for assignment."""
        return [courier for courier in self._all_couriers if courier.is_available]

    def get_busy_couriers(self) -> List[Courier]:
        """Return all couriers currently handling orders."""
        return [courier for courier in self._all_couriers if not courier.is_available]

    def list_couriers(self) -> List[Courier]:
        """Return all registered couriers."""
        return list(self._all_couriers)

    def get_courier(self, courier_id: str) -> Optional[Courier]:
        """Return one courier by identifier."""
        return self._couriers_by_id.get(courier_id)

    def find_available_couriers(self, zone_id: str) -> List[Courier]:
        """Return available couriers filtered by zone."""
        return [
            courier
            for courier in self._all_couriers
            if courier.is_available and courier.current_zone == zone_id
        ]

    def _get_required_courier(self, courier_id: str) -> Courier:
        """Return a courier or raise an explicit error when missing."""
        courier = self._couriers_by_id.get(courier_id)
        if courier is None:
            raise KeyError(f"Courier '{courier_id}' was not found.")
        return courier


if __name__ == "__main__":
    class DemoOrder:
        """Simple local order object for manual courier tests."""

        def __init__(self, order_id: str) -> None:
            self.order_id = order_id

    manager = CourierManager()

    for courier in [
        Courier("COU-001", "Andres Ruiz", current_zone="Centro"),
        Courier("COU-002", "Sofia Castro", current_zone="Norte"),
        Courier("COU-003", "Miguel Torres", current_zone="Sur"),
        Courier("COU-004", "Laura Medina", current_zone="Occidente"),
        Courier("COU-005", "Camila Rojas", current_zone="Oriente"),
    ]:
        manager.add_courier(courier)

    print("Repartidores registrados en la lista circular:")
    for courier in manager.list_couriers():
        print(f"- {courier.courier_id}: {courier.name} en zona {courier.current_zone}.")

    demo_orders = [
        DemoOrder("ORD-101"),
        DemoOrder("ORD-102"),
        DemoOrder("ORD-103"),
    ]

    print("\nAsignaciones iniciales con rotacion circular:")
    for order in demo_orders:
        assigned_courier = manager.assign_order_to_courier(order)
        if assigned_courier is None:
            print(f"No hay repartidores disponibles para el pedido {order.order_id}.")
        else:
            print(
                f"Pedido {order.order_id} asignado a {assigned_courier.name} "
                f"({assigned_courier.courier_id})."
            )

    print("\nEstado actual de los repartidores:")
    for courier in manager.list_couriers():
        availability = "disponible" if courier.is_available else "ocupado"
        print(
            f"- {courier.courier_id}: {courier.name}, {availability}, "
            f"pedidos activos {courier.active_orders}."
        )

    print("\nLiberando un repartidor y demostrando la siguiente rotacion:")
    manager.complete_order("COU-002", "ORD-102")
    print("Pedido ORD-102 completado por el repartidor COU-002.")

    extra_order = DemoOrder("ORD-104")
    reassigned_courier = manager.assign_order_to_courier(extra_order)
    if reassigned_courier is not None:
        print(
            f"Pedido {extra_order.order_id} asignado despues de rotar a "
            f"{reassigned_courier.name} ({reassigned_courier.courier_id})."
        )

    print("\nRepartidores disponibles:")
    for courier in manager.get_available_couriers():
        print(f"- {courier.courier_id}: {courier.name}.")

    print("\nRepartidores ocupados:")
    for courier in manager.get_busy_couriers():
        print(f"- {courier.courier_id}: {courier.name}.")
