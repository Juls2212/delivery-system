from order_manager import OrderManager, OrderStatus
from courier_manager import CourierManager, Courier
from delivery_history import DeliveryHistoryStack, DeliveryRecord
from zone_map import ZoneMap


def create_sample_system():
    """Bootstrap the backend with sample data for testing and demos."""
    order_manager = OrderManager()
    courier_manager = CourierManager()
    history = DeliveryHistoryStack()
    zone_map = ZoneMap()

    for courier in [
        Courier("COU-001", "Andres Ruiz", current_zone="Centro"),
        Courier("COU-002", "Sofia Castro", current_zone="Norte"),
        Courier("COU-003", "Miguel Torres", current_zone="Sur"),
        Courier("COU-004", "Laura Medina", current_zone="Occidente"),
        Courier("COU-005", "Camila Rojas", current_zone="Oriente"),
    ]:
        courier_manager.add_courier(courier)

    order_manager.create_order(
        "ORD-001", "Laura Gomez", "Burger House",
        "Centro", "Norte", ["Hamburguesa", "Papas"], 3,
    )
    order_manager.create_order(
        "ORD-002", "Carlos Perez", "Sushi Point",
        "Sur", "Centro", ["Combo sushi", "Bebida"], 1,
    )
    order_manager.create_order(
        "ORD-003", "Ana Torres", "Pizza Lab",
        "Norte", "Occidente", ["Pizza familiar"], 2,
    )
    order_manager.create_order(
        "ORD-004", "Mario Ruiz", "Taco Express",
        "Oriente", "Sur", ["Tacos", "Bebida"], 3,
    )
    order_manager.create_order(
        "ORD-005", "Elena Vega", "Pasta House",
        "Occidente", "Oriente", ["Pasta carbonara"], 1,
    )

    # Assign first two priority orders to available couriers
    for _ in range(2):
        order = order_manager.get_next_order()
        if order:
            courier = courier_manager.assign_order_to_courier(order)
            if courier:
                order_manager.mark_order_as_assigned(order.order_id)

    # Deliver one order and record it in the history stack
    order = order_manager.get_next_order()
    if order:
        order_manager.mark_order_as_delivered(order.order_id)
        history.push_delivery(DeliveryRecord(
            order_id=order.order_id,
            customer_name=order.customer_name,
            final_status="Delivered",
        ))

    # Additional history records for demonstration
    history.push_delivery(DeliveryRecord("ORD-101", "Pedro Mora", "Delivered"))
    history.push_delivery(DeliveryRecord("ORD-102", "Rosa Silva", "Cancelled"))
    history.push_delivery(DeliveryRecord("ORD-103", "Juan Lopez", "Delivered"))

    return order_manager, courier_manager, history, zone_map


# Controlador principal que integra las vistas con los módulos del backend
class DashboardController:
    """
    Controlador que conecta las vistas de la interfaz con los módulos backend:
    - OrderManager   (order_manager.py)
    - CourierManager (courier_manager.py)
    - DeliveryHistoryStack (delivery_history.py)
    - ZoneMap        (zone_map.py)
    """

    def __init__(self, root):
        self.root = root

        # Inicializar el backend con datos de muestra
        (
            self.order_manager,
            self.courier_manager,
            self.history,
            self.zone_map,
        ) = create_sample_system()

        # Referencias a las vistas registradas
        self.dashboard_view = None
        self.history_view = None
        self.map_view = None

    # Inyecta las dependencias de las vistas en el controlador
    def set_views(self, dashboard, history, map_view):
        self.dashboard_view = dashboard
        self.history_view = history
        self.map_view = map_view
        self.refresh_all_data()

    # Función principal para refrescar todas las vistas a la vez
    def refresh_all_data(self):
        if self.dashboard_view:
            self.dashboard_view.update_data(self._get_dashboard_data())
        if self.history_view:
            self.history_view.update_history(self._format_history_list())
        if self.map_view:
            self.refresh_map_data()

    def _get_dashboard_data(self):
        all_orders = self.order_manager.get_all_orders()
        pending = sum(
            1 for o in all_orders
            if o.status in {OrderStatus.CREATED, OrderStatus.WAITING}
        )
        assigned = sum(
            1 for o in all_orders
            if o.status in {OrderStatus.ASSIGNED, OrderStatus.IN_TRANSIT}
        )
        delivered = sum(1 for o in all_orders if o.status == OrderStatus.DELIVERED)

        available = len(self.courier_manager.get_available_couriers())
        busy = len(self.courier_manager.get_busy_couriers())

        last = self.history.peek_last_delivery()
        last_text = (
            f"Pedido {last.order_id} - {last.customer_name} - {last.final_status}"
            if last else "Ninguno"
        )

        return {
            "total_orders": len(all_orders),
            "pending_orders": pending,
            "assigned_orders": assigned,
            "delivered_orders": delivered,
            "available_couriers": available,
            "busy_couriers": busy,
            "last_delivery": last_text,
        }

    def _format_history_list(self):
        # list_history() returns newest-first; reverse to oldest-first so the
        # history view's reversed() call will display newest at the top.
        records = list(reversed(self.history.list_history()))
        return [
            f"Pedido {r.order_id} | {r.customer_name} | {r.final_status}"
            for r in records
        ]

    def _get_map_data(self):
        zones = self.zone_map.list_zones()
        matrix = self.zone_map.show_distance_matrix()
        distance = self.zone_map.get_distance("Centro", "Norte")
        nearest = self.zone_map.get_nearest_courier_zone("Norte") or "N/A"
        return {
            "zones": zones,
            "matrix": matrix,
            "distance_to_dest": distance,
            "closest_zone": nearest,
        }

    # --- Operaciones de Mapa ---

    def refresh_map_data(self):
        if self.map_view:
            self.map_view.update_map_data(self._get_map_data())

    # --- Operaciones de Historial (Pila LIFO) ---

    def get_last_delivery_from_history(self):
        record = self.history.peek_last_delivery()
        if record:
            return (
                f"Pedido {record.order_id} - {record.customer_name}"
                f" - {record.final_status}"
            )
        return None

    def remove_last_delivery(self):
        record = self.history.pop_last_delivery()
        if record:
            if self.history_view:
                self.history_view.update_history(self._format_history_list())
            return True
        return False

    def clear_delivery_history(self):
        self.history.clear_history()
        if self.history_view:
            self.history_view.update_history([])

    # --- Operaciones de Reportes ---

    def get_general_summary_report(self):
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

    def get_orders_status_report(self):
        all_orders = self.order_manager.get_all_orders()
        lines = ["--- Estado de Pedidos ---"]
        for order in all_orders:
            lines.append(
                f"{order.order_id} | {order.customer_name} | "
                f"{order.restaurant_name} | {order.status.value}"
            )
        lines.append("-------------------------")
        lines.append(
            f"Historial reciente ({len(self.history.list_history())} registros):"
        )
        for entry in self.history.list_history():
            lines.append(
                f"  {entry.order_id} | {entry.customer_name} | {entry.final_status}"
            )
        return "\n".join(lines) + "\n"
