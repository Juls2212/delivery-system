from __future__ import annotations

from typing import Dict, List, Optional

from courier_manager import CourierManager
from delivery_history import DeliveryHistory, DeliveryRecord
from order_manager import OrderManager
from seed_data import create_sample_system
from zone_map import ZoneMap


class FrontendController:
    """Controlador que conecta la interfaz con la capa de servicios del backend real.
    
    Este controlador centraliza las operaciones que la interfaz necesita
    y evita que la vista conozca detalles internos del backend.
    """

    def __init__(self) -> None:
        # Inicializa el backend real con datos de muestra
        system = create_sample_system()
        self.order_manager: OrderManager = system["order_manager"]
        self.courier_manager: CourierManager = system["courier_manager"]
        self.delivery_history: DeliveryHistory = system["delivery_history"]
        self.zone_map: ZoneMap = system["zone_map"]

    def create_sample_order(self) -> Dict[str, str | int]:
        """Crea un pedido de prueba para poblar la interfaz.
        
        Toma el siguiente pedido pendiente del sistema de backend.
        """
        order = self.order_manager.get_next_order()
        if order is None:
            return {}
        
        return self._serialize_order(order)

    def assign_next_order(self) -> Optional[Dict[str, int | str]]:
        """Solicita la asignación del siguiente pedido pendiente a un repartidor."""
        order = self.order_manager.get_next_order()
        if order is None:
            return None

        # Asigna el pedido a un repartidor disponible
        courier = self.courier_manager.assign_order_to_courier(order)
        if courier is None:
            return None

        # Marca el pedido como asignado
        self.order_manager.mark_order_as_assigned(order.order_id)

        return {
            "order_id": order.order_id,
            "courier_id": courier.courier_id,
            "courier_name": courier.name,
            "status": order.status,
        }

    def complete_selected_order(self, order_id: str) -> Optional[Dict[str, int | str]]:
        """Completa un pedido seleccionado desde la interfaz."""
        order = self.order_manager.get_order(order_id)
        if order is None:
            return None

        # Obtén el repartidor que está entregando este pedido
        couriers = self.courier_manager.list_couriers()
        assigned_courier = None
        for courier in couriers:
            if order_id in courier.active_orders:
                assigned_courier = courier
                break

        if assigned_courier is None:
            return None

        # Marca el pedido como entregado
        self.order_manager.mark_order_as_delivered(order_id)
        
        # Completa el pedido en el repartidor
        self.courier_manager.complete_order(assigned_courier.courier_id, order_id)

        # Registra en el historial de entregas
        delivery_record = DeliveryRecord(
            order_id=order.order_id,
            customer_name=order.customer_name,
            final_status="Delivered",
        )
        self.delivery_history.push_delivery(delivery_record)

        return {
            "order_id": order.order_id,
            "courier_id": assigned_courier.courier_id,
            "courier_name": assigned_courier.name,
            "status": order.status,
        }

    def show_pending_orders(self) -> List[Dict[str, str | int]]:
        """Entrega al frontend la lista de pedidos pendientes."""
        orders = self.order_manager.list_pending_orders()
        return [self._serialize_order(order) for order in orders]

    def show_couriers(self) -> List[Dict[str, str | int | bool]]:
        """Entrega al frontend la lista de repartidores disponibles y ocupados."""
        couriers = self.courier_manager.list_couriers()
        return [self._serialize_courier(courier) for courier in couriers]

    def show_active_orders(self) -> List[Dict[str, str | int]]:
        """Entrega al frontend la lista de pedidos activos (asignados o en tránsito)."""
        all_orders = self.order_manager.get_all_orders()
        # Filtra solo los pedidos que tienen repartidor asignado
        active_orders = [
            order for order in all_orders 
            if order.status in {"Assigned", "In transit"}
        ]
        return [self._serialize_order(order) for order in active_orders]

    def show_delivery_history(self) -> List[Dict[str, str]]:
        """Entrega al frontend el historial de entregas completadas."""
        records = self.delivery_history.list_history()
        return [
            {
                "order_id": record.order_id,
                "customer_name": record.customer_name,
                "final_status": record.final_status,
                "timestamp": record.timestamp.isoformat(),
            }
            for record in records
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
            "status": order.status,
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
