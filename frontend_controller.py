from __future__ import annotations

from typing import Any

from courier_manager import CourierManager
from delivery_history import DeliveryHistoryStack, DeliveryRecord
from order_manager import Order, OrderManager, OrderStatus
from seed_data import create_sample_system
from zone_map import ZoneMap


class FrontendController:
    """Bridge between the Tkinter UI and the backend services from main."""

    def __init__(self) -> None:
        system = create_sample_system()
        self.order_manager: OrderManager = system["order_manager"]
        self.courier_manager: CourierManager = system["courier_manager"]
        self.delivery_history: DeliveryHistoryStack = system["delivery_history"]
        self.zone_map: ZoneMap = system["zone_map"]

    def create_sample_order(self) -> dict[str, Any]:
        """Create a new sample order using the real order manager."""
        next_number = len(self.order_manager.get_all_orders()) + 1
        order = self.order_manager.create_order(
            order_id=f"ORD-{next_number:03d}",
            customer_name="Cliente de prueba",
            restaurant_name="Cocina Demo",
            origin_zone="Centro",
            destination_zone="Norte",
            items=["Pedido demo", "Bebida"],
            priority=2,
        )
        return self._serialize_order(order)

    def create_order(
        self,
        customer_name: str,
        restaurant_name: str,
        origin_zone: str,
        destination_zone: str,
        items_text: str,
        priority_text: str,
    ) -> dict[str, Any]:
        """Create an order from UI form values."""
        customer = customer_name.strip()
        restaurant = restaurant_name.strip()
        origin = origin_zone.strip()
        destination = destination_zone.strip()
        items = [item.strip() for item in items_text.split(",") if item.strip()]
        priority = int(priority_text)

        if not customer:
            raise ValueError("El nombre del cliente es obligatorio.")
        if not restaurant:
            raise ValueError("El restaurante es obligatorio.")
        if origin not in self.zone_map.list_zones():
            raise ValueError("La zona de origen no es válida.")
        if destination not in self.zone_map.list_zones():
            raise ValueError("La zona de destino no es válida.")
        if not items:
            raise ValueError("Debes ingresar al menos un artículo.")

        next_number = len(self.order_manager.get_all_orders()) + 1
        order = self.order_manager.create_order(
            order_id=f"ORD-{next_number:03d}",
            customer_name=customer,
            restaurant_name=restaurant,
            origin_zone=origin,
            destination_zone=destination,
            items=items,
            priority=priority,
        )
        return self._serialize_order(order)

    def assign_next_order(self) -> dict[str, Any]:
        """Assign the next pending order using the real courier rotation."""
        order = self.order_manager.get_next_order()
        if order is None:
            return {"message": "No hay pedidos pendientes para asignar."}

        available_couriers = self.courier_manager.get_available_couriers()
        if not available_couriers:
            return {"message": "No hay repartidores disponibles en este momento."}

        nearest_zone = self.zone_map.get_nearest_courier_zone(
            destination_zone=order.destination_zone,
            courier_zones=[courier.current_zone for courier in available_couriers],
        )
        courier = self.courier_manager.assign_order_to_courier(order)
        if courier is None:
            return {"message": "No fue posible asignar el pedido."}

        self.order_manager.mark_order_as_assigned(order.order_id)
        self.order_manager.update_order_status(order.order_id, OrderStatus.IN_TRANSIT)
        distance = self.zone_map.get_distance(order.origin_zone, order.destination_zone)

        return {
            "order_id": order.order_id,
            "customer": order.customer_name,
            "courier_id": courier.courier_id,
            "courier_name": courier.name,
            "origin": order.origin_zone,
            "destination": order.destination_zone,
            "nearest_zone": nearest_zone,
            "distance_km": distance,
            "status": order.status.value,
        }

    def complete_selected_order(self, order_id: str) -> dict[str, Any]:
        """Complete an active order and store it in delivery history."""
        normalized_order_id = order_id.strip().upper()
        order = self.order_manager.get_order(normalized_order_id)
        if order is None:
            return {"message": "El pedido indicado no existe."}
        if order.status == OrderStatus.DELIVERED:
            return {"message": "Ese pedido ya fue marcado como entregado."}

        assigned_courier = self._find_assigned_courier(normalized_order_id)
        if assigned_courier is None:
            return {"message": "El pedido no tiene un repartidor activo asignado."}

        self.courier_manager.complete_order(assigned_courier.courier_id, normalized_order_id)
        self.order_manager.mark_order_as_delivered(normalized_order_id)
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
            "final_status": OrderStatus.DELIVERED.value,
        }

    def show_pending_orders(self) -> list[dict[str, Any]]:
        return [self._serialize_order(order) for order in self.order_manager.list_pending_orders()]

    def show_couriers(self) -> list[dict[str, Any]]:
        return [self._serialize_courier(courier) for courier in self.courier_manager.list_couriers()]

    def show_active_orders(self) -> list[dict[str, Any]]:
        active_orders = [
            order
            for order in self.order_manager.get_all_orders()
            if order.status in {OrderStatus.ASSIGNED, OrderStatus.IN_TRANSIT}
        ]
        return [self._serialize_order(order) for order in active_orders]

    def show_delivery_history(self) -> list[dict[str, str]]:
        return [
            {
                "order_id": record.order_id,
                "customer": record.customer_name,
                "final_status": record.final_status,
                "timestamp": record.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            }
            for record in self.delivery_history.list_history()
        ]

    def get_dashboard_summary(self) -> dict[str, int]:
        pending_orders = len(self.order_manager.list_pending_orders())
        active_orders = len(self.show_active_orders())
        available_couriers = len(self.courier_manager.get_available_couriers())
        delivered_orders = len(self.delivery_history.list_history())
        return {
            "pending_orders": pending_orders,
            "active_orders": active_orders,
            "available_couriers": available_couriers,
            "delivered_orders": delivered_orders,
        }

    def get_available_zones(self) -> list[str]:
        return self.zone_map.list_zones()

    def _find_assigned_courier(self, order_id: str) -> Any | None:
        for courier in self.courier_manager.list_couriers():
            if order_id in courier.active_orders:
                return courier
        return None

    def _serialize_order(self, order: Order) -> dict[str, Any]:
        return {
            "id": order.order_id,
            "customer": order.customer_name,
            "restaurant": order.restaurant_name,
            "origin": order.origin_zone,
            "destination": order.destination_zone,
            "items": ", ".join(order.items) if order.items else "Sin articulos",
            "priority": order.priority,
            "status": order.status.value,
        }

    def _serialize_courier(self, courier: Any) -> dict[str, Any]:
        return {
            "id": courier.courier_id,
            "name": courier.name,
            "zone": courier.current_zone,
            "available": "Si" if courier.is_available else "No",
            "active_orders": len(courier.active_orders),
            "delivered": courier.delivered_orders_count,
        }
