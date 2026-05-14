from __future__ import annotations

from itertools import cycle
from typing import Dict, List, Optional

from mock_backend import MockBackendFacade


class FrontendController:
    """Controlador que conecta la interfaz con la capa de servicios."""

    def __init__(self) -> None:
        # Este controlador centraliza las operaciones que la interfaz necesita
        # y evita que la vista conozca detalles internos del backend.
        self.backend = MockBackendFacade()
        self._sample_orders = cycle(
            [
                {"customer": "Laura Castro", "address": "Calle 63 #20-11"},
                {"customer": "Jorge Medina", "address": "Carrera 50 #88-09"},
                {"customer": "Paula Rios", "address": "Diagonal 21 #14-77"},
            ]
        )

        # Cuando exista el backend real, este import puede reemplazarse por:
        # from order_manager import OrderManager
        # from courier_manager import CourierManager
        # from delivery_history import DeliveryHistory
        # o por una fachada unificada que use esos módulos.

    def create_sample_order(self) -> Dict[str, str | int]:
        """Crea un pedido de prueba para poblar la interfaz."""

        sample_order = next(self._sample_orders)
        order = self.backend.create_order(
            customer=sample_order["customer"],
            address=sample_order["address"],
        )
        return self._serialize_order(order)

    def assign_next_order(self) -> Optional[Dict[str, int | str]]:
        """Solicita la asignación del siguiente pedido pendiente."""

        assignment = self.backend.assign_next_order()
        if assignment is None:
            return None

        return {
            "order_id": assignment.order_id,
            "courier_id": assignment.courier_id,
            "status": assignment.status,
        }

    def complete_selected_order(self, order_id: int) -> Optional[Dict[str, int | str]]:
        """Completa un pedido seleccionado desde la interfaz."""

        assignment = self.backend.complete_order(order_id)
        if assignment is None:
            return None

        return {
            "order_id": assignment.order_id,
            "courier_id": assignment.courier_id,
            "status": assignment.status,
        }

    def show_pending_orders(self) -> List[Dict[str, str | int]]:
        """Entrega al frontend la lista de pedidos pendientes."""

        return [self._serialize_order(order) for order in self.backend.get_pending_orders()]

    def show_couriers(self) -> List[Dict[str, str | int | bool]]:
        """Entrega al frontend la lista de repartidores disponibles y ocupados."""

        return [self._serialize_courier(courier) for courier in self.backend.get_couriers()]

    def show_active_orders(self) -> List[Dict[str, str | int]]:
        """Entrega al frontend la lista de pedidos activos."""

        return [self._serialize_order(order) for order in self.backend.get_active_orders()]

    def _serialize_order(self, order: object) -> Dict[str, str | int]:
        """Transforma un pedido en un formato simple para la vista."""

        return {
            "id": order.id,
            "customer": order.customer,
            "address": order.address,
            "status": order.status,
        }

    def _serialize_courier(self, courier: object) -> Dict[str, str | int | bool]:
        """Transforma un repartidor en un formato simple para la vista."""

        return {
            "id": courier.id,
            "name": courier.name,
            "availability": courier.availability,
        }
