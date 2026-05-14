class DashboardController:
    """
    Controller that connects the UI views with the backend modules:
    - order_manager.py
    - courier_manager.py
    - delivery_history.py
    - zone_map.py
    
    Since the backend might not exist yet, this controller uses simulated data 
    if the actual modules are not found.
    """
    def __init__(self, root):
        self.root = root
        
        # Simulated Backend Data Structure
        self.simulated_data = {
            "total_orders": 120,
            "pending_orders": 15,
            "assigned_orders": 25,
            "delivered_orders": 80,
            "available_couriers": 10,
            "busy_couriers": 25,
            "last_delivery": "Pedido #120 - Entregado a Zona Centro",
            "history_stack": [
                "Pedido #118 - Entregado a Zona Norte",
                "Pedido #119 - Entregado a Zona Sur",
                "Pedido #120 - Entregado a Zona Centro"
            ],
            "zones": ["Centro", "Norte", "Sur", "Este", "Oeste"],
            "distance_matrix": [
                [0, 5, 8, 4, 6],
                [5, 0, 12, 7, 9],
                [8, 12, 0, 10, 14],
                [4, 7, 10, 0, 8],
                [6, 9, 14, 8, 0]
            ],
            "distance_to_dest": 8,
            "closest_zone": "Este"
        }
        
        # References to views
        self.dashboard_view = None
        self.history_view = None
        self.map_view = None

    def set_views(self, dashboard, history, map_view):
        self.dashboard_view = dashboard
        self.history_view = history
        self.map_view = map_view
        self.refresh_all_data()

    def refresh_all_data(self):
        if self.dashboard_view:
            self.dashboard_view.update_data(self.simulated_data)
        if self.history_view:
            self.history_view.update_history(self.simulated_data["history_stack"])
        if self.map_view:
            self.refresh_map_data()

    # --- History Operations ---
    def get_last_delivery_from_history(self):
        stack = self.simulated_data["history_stack"]
        return stack[-1] if stack else None

    def remove_last_delivery(self):
        stack = self.simulated_data["history_stack"]
        if stack:
            stack.pop()
            self.history_view.update_history(stack)
            return True
        return False

    def clear_delivery_history(self):
        self.simulated_data["history_stack"] = []
        self.history_view.update_history(self.simulated_data["history_stack"])

    # --- Map Operations ---
    def refresh_map_data(self):
        if self.map_view:
            data = {
                "zones": self.simulated_data["zones"],
                "matrix": self.simulated_data["distance_matrix"],
                "distance_to_dest": self.simulated_data["distance_to_dest"],
                "closest_zone": self.simulated_data["closest_zone"]
            }
            self.map_view.update_map_data(data)

    # --- Report Operations ---
    def get_general_summary_report(self):
        data = self.simulated_data
        return (
            "--- Resumen General ---\n"
            f"Pedidos Totales: {data['total_orders']}\n"
            f"Pedidos Pendientes: {data['pending_orders']}\n"
            f"Pedidos Asignados: {data['assigned_orders']}\n"
            f"Pedidos Entregados: {data['delivered_orders']}\n"
            "------------------------\n"
            f"Repartidores Disponibles: {data['available_couriers']}\n"
            f"Repartidores Ocupados: {data['busy_couriers']}\n"
            "------------------------\n"
            f"Última Entrega: {data['last_delivery']}\n"
        )

    def get_orders_status_report(self):
        data = self.simulated_data
        report = "--- Historial de Entregas Recientes ---\n"
        for i, item in enumerate(reversed(data["history_stack"]), 1):
            report += f"{i}. {item}\n"
        report += "---------------------------------------\n"
        return report
