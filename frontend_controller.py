from __future__ import annotations

from typing import Dict, List, Optional

from courier_manager import CourierManager
from delivery_history import DeliveryHistoryStack, DeliveryRecord
from order_manager import OrderManager, OrderStatus
from seed_data import create_sample_system
from zone_map import ZoneMap


class FrontendController:
    """Controlador que conecta la interfaz principal con el backend real."""

    def __init__(self, system: Optional[dict[str, object]] = None) -> None:
        backend_system = system or create_sample_system()
        self.order_manager: OrderManager = backend_system["order_manager"]
        self.courier_manager: CourierManager = backend_system["courier_manager"]
        self.delivery_history: DeliveryHistoryStack = backend_system["delivery_history"]
        self.zone_map: ZoneMap = backend_system["zone_map"]

    def create_sample_order(self) -> Dict[str, str | int]:
        """Crea un nuevo pedido de prueba y lo deja pendiente en el sistema."""
        new_order_number = len(self.order_manager.get_all_orders()) + 1
        order = self.order_manager.create_order(
            order_id=f"ORD-{new_order_number:03d}",
            customer_name="Cliente Demo",
            restaurant_name="Restaurante Demo",
            origin_zone="Centro",
            destination_zone="Sur",
            items=["Combo demo", "Bebida"],
            priority=3,
        )
        return self._serialize_order(order)

    def assign_next_order(self) -> Optional[Dict[str, int | str]]:
        """Asigna el siguiente pedido pendiente al próximo repartidor disponible."""
        order = self.order_manager.get_next_order()
        if order is None:
            return None

        courier = self.courier_manager.assign_order_to_courier(order)
        if courier is None:
            return None

        self.order_manager.mark_order_as_assigned(order.order_id)

        return {
            "order_id": order.order_id,
            "courier_id": courier.courier_id,
            "courier_name": courier.name,
            "status": order.status.value,
        }

    def complete_selected_order(self, order_id: str) -> Optional[Dict[str, int | str]]:
        """Completa un pedido asignado desde la interfaz."""
        order = self.order_manager.get_order(order_id)
        if order is None:
            return None

        assigned_courier = None
        for courier in self.courier_manager.list_couriers():
            if order_id in courier.active_orders:
                assigned_courier = courier
                break

        if assigned_courier is None:
            return None

        self.order_manager.mark_order_as_delivered(order_id)
        self.courier_manager.complete_order(assigned_courier.courier_id, order_id)
        self.delivery_history.push_delivery(
            DeliveryRecord(
                order_id=order.order_id,
                customer_name=order.customer_name,
                final_status=OrderStatus.DELIVERED.value,
            )
        )

        return {
            "order_id": order.order_id,
            "courier_id": assigned_courier.courier_id,
            "courier_name": assigned_courier.name,
            "status": order.status.value,
        }

    def show_pending_orders(self) -> List[Dict[str, str | int]]:
        """Entrega al frontend la lista de pedidos pendientes."""
        return [self._serialize_order(order) for order in self.order_manager.list_pending_orders()]

    def show_couriers(self) -> List[Dict[str, str | int | bool]]:
        """Entrega al frontend la lista completa de repartidores."""
        return [self._serialize_courier(courier) for courier in self.courier_manager.list_couriers()]

    def show_active_orders(self) -> List[Dict[str, str | int]]:
        """Entrega al frontend la lista de pedidos asignados o en tránsito."""
        active_orders = [
            order
            for order in self.order_manager.get_all_orders()
            if order.status in {OrderStatus.ASSIGNED, OrderStatus.IN_TRANSIT}
        ]
        return [self._serialize_order(order) for order in active_orders]

    def show_delivery_history(self) -> List[Dict[str, str]]:
        """Entrega al frontend el historial de entregas completadas."""
        return [
            {
                "order_id": record.order_id,
                "customer_name": record.customer_name,
                "final_status": record.final_status,
                "timestamp": record.timestamp.isoformat(),
            }
            for record in self.delivery_history.list_history()
        ]

    def _serialize_order(self, order: object) -> Dict[str, str | int]:
        """Transforma un pedido en un formato simple para la vista."""
        return {
            "id": order.order_id,
            "customer": order.customer_name,
            "restaurant": order.restaurant_name,
            "origin": order.origin_zone,
            "destination": order.destination_zone,
            "items": ", ".join(order.items) if order.items else "Sin items",
            "priority": order.priority,
            "status": order.status.value,
        }

    def _serialize_courier(self, courier: object) -> Dict[str, str | int | bool]:
        """Transforma un repartidor en un formato simple para la vista."""
        return {
            "id": courier.courier_id,
            "name": courier.name,
            "zone": courier.current_zone,
            "available": courier.is_available,
            "active_orders": len(courier.active_orders),
            "delivered": courier.delivered_orders_count,
        }
