from __future__ import annotations

from typing import Optional

from courier_manager import CourierManager
from delivery_history import DeliveryHistoryStack
from order_manager import OrderManager, OrderStatus
from seed_data import create_sample_system
from zone_map import ZoneMap


class DashboardController:
    """Controlador que conecta las vistas del dashboard con el backend real."""

    def __init__(self, root: object | None = None, system: Optional[dict[str, object]] = None):
        self.root = root
        backend_system = system or create_sample_system()
        self.order_manager: OrderManager = backend_system["order_manager"]
        self.courier_manager: CourierManager = backend_system["courier_manager"]
        self.history: DeliveryHistoryStack = backend_system["delivery_history"]
        self.zone_map: ZoneMap = backend_system["zone_map"]

        self.dashboard_view = None
        self.history_view = None
        self.map_view = None

    def set_views(self, dashboard, history, map_view) -> None:
        self.dashboard_view = dashboard
        self.history_view = history
        self.map_view = map_view
        self.refresh_all_data()

    def refresh_all_data(self) -> None:
        if self.dashboard_view:
            self.dashboard_view.update_data(self._get_dashboard_data())
        if self.history_view:
            self.history_view.update_history(self._format_history_list())
        if self.map_view:
            self.map_view.update_map_data(self._get_map_data())

    def _get_dashboard_data(self) -> dict[str, object]:
        all_orders = self.order_manager.get_all_orders()
        pending = sum(
            1 for order in all_orders if order.status in {OrderStatus.CREATED, OrderStatus.WAITING}
        )
        assigned = sum(
            1 for order in all_orders if order.status in {OrderStatus.ASSIGNED, OrderStatus.IN_TRANSIT}
        )
        delivered = sum(1 for order in all_orders if order.status == OrderStatus.DELIVERED)

        last_record = self.history.peek_last_delivery()
        last_text = (
            f"Pedido {last_record.order_id} - {last_record.customer_name} - {last_record.final_status}"
            if last_record
            else "Ninguno"
        )

        return {
            "total_orders": len(all_orders),
            "pending_orders": pending,
            "assigned_orders": assigned,
            "delivered_orders": delivered,
            "available_couriers": len(self.courier_manager.get_available_couriers()),
            "busy_couriers": len(self.courier_manager.get_busy_couriers()),
            "last_delivery": last_text,
        }

    def _format_history_list(self) -> list[str]:
        # list_history() returns newest-first; the view reverses the iterable so
        # we feed oldest-first here to keep the newest record visible on top.
        return [
            f"Pedido {record.order_id} | {record.customer_name} | {record.final_status}"
            for record in reversed(self.history.list_history())
        ]

    def _get_map_data(self) -> dict[str, object]:
        available_zones = [
            courier.current_zone for courier in self.courier_manager.get_available_couriers()
        ]
        nearest_zone = (
            self.zone_map.get_nearest_courier_zone("Norte", available_zones)
            if available_zones
            else None
        )
        return {
            "zones": self.zone_map.list_zones(),
            "matrix": self.zone_map.show_distance_matrix(),
            "distance_to_dest": self.zone_map.get_distance("Centro", "Norte"),
            "closest_zone": nearest_zone or "N/A",
        }

    def refresh_map_data(self) -> None:
        if self.map_view:
            self.map_view.update_map_data(self._get_map_data())

    def get_last_delivery_from_history(self) -> Optional[str]:
        record = self.history.peek_last_delivery()
        if record is None:
            return None
        return f"Pedido {record.order_id} - {record.customer_name} - {record.final_status}"

    def remove_last_delivery(self) -> bool:
        record = self.history.pop_last_delivery()
        if record is None:
            return False

        if self.history_view:
            self.history_view.update_history(self._format_history_list())
        if self.dashboard_view:
            self.dashboard_view.update_data(self._get_dashboard_data())
        return True

    def clear_delivery_history(self) -> None:
        self.history.clear_history()
        if self.history_view:
            self.history_view.update_history([])
        if self.dashboard_view:
            self.dashboard_view.update_data(self._get_dashboard_data())

    def get_general_summary_report(self) -> str:
        data = self._get_dashboard_data()
        lines = [
            "--- Resumen General ---",
            f"Pedidos Totales: {data['total_orders']}",
            f"Pedidos Pendientes: {data['pending_orders']}",
            f"Pedidos Asignados: {data['assigned_orders']}",
            f"Pedidos Entregados: {data['delivered_orders']}",
            "------------------------",
            f"Repartidores Disponibles: {data['available_couriers']}",
            f"Repartidores Ocupados: {data['busy_couriers']}",
            "------------------------",
            f"Última Entrega: {data['last_delivery']}",
        ]
        return "\n".join(lines) + "\n"

    def get_orders_status_report(self) -> str:
        lines = ["--- Estado de Pedidos ---"]
        for order in self.order_manager.get_all_orders():
            lines.append(
                f"{order.order_id} | {order.customer_name} | "
                f"{order.restaurant_name} | {order.status.value}"
            )
        lines.append("-------------------------")
        lines.append(f"Historial reciente ({len(self.history.list_history())} registros):")
        for record in self.history.list_history():
            lines.append(
                f"  {record.order_id} | {record.customer_name} | {record.final_status}"
            )
        return "\n".join(lines) + "\n"
