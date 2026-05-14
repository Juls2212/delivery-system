import tkinter as tk
from tkinter import ttk

# Clase que representa la vista principal del Dashboard (Tablero)
class Dashboard(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # Variables reactivas para actualizar la interfaz automáticamente
        self.total_orders_var = tk.StringVar(value="0")
        self.pending_orders_var = tk.StringVar(value="0")
        self.assigned_orders_var = tk.StringVar(value="0")
        self.delivered_orders_var = tk.StringVar(value="0")
        
        self.available_couriers_var = tk.StringVar(value="0")
        self.busy_couriers_var = tk.StringVar(value="0")
        
        self.last_delivery_var = tk.StringVar(value="Ninguno")
        
        # Inicializa la estructura de la interfaz
        self._setup_ui()
        
    def _setup_ui(self):
        # Sección de resumen de pedidos
        summary_frame = ttk.LabelFrame(self, text="Resumen de Pedidos")
        summary_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(summary_frame, text="Pedidos Totales:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        ttk.Label(summary_frame, textvariable=self.total_orders_var).grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        ttk.Label(summary_frame, text="Pedidos Pendientes:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        ttk.Label(summary_frame, textvariable=self.pending_orders_var).grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        ttk.Label(summary_frame, text="Pedidos Asignados:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        ttk.Label(summary_frame, textvariable=self.assigned_orders_var).grid(row=2, column=1, padx=5, pady=5, sticky="w")
        
        ttk.Label(summary_frame, text="Pedidos Entregados:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        ttk.Label(summary_frame, textvariable=self.delivered_orders_var).grid(row=3, column=1, padx=5, pady=5, sticky="w")
        
        # Sección del estado de los repartidores
        couriers_frame = ttk.LabelFrame(self, text="Estado de Repartidores")
        couriers_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(couriers_frame, text="Repartidores Disponibles:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        ttk.Label(couriers_frame, textvariable=self.available_couriers_var).grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        ttk.Label(couriers_frame, text="Repartidores Ocupados:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        ttk.Label(couriers_frame, textvariable=self.busy_couriers_var).grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        # Sección de la última entrega realizada
        last_delivery_frame = ttk.LabelFrame(self, text="Última Entrega")
        last_delivery_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(last_delivery_frame, textvariable=self.last_delivery_var).pack(padx=5, pady=5)

    # Actualiza los valores visibles en pantalla usando un diccionario de datos
    def update_data(self, data):
        self.total_orders_var.set(str(data.get("total_orders", 0)))
        self.pending_orders_var.set(str(data.get("pending_orders", 0)))
        self.assigned_orders_var.set(str(data.get("assigned_orders", 0)))
        self.delivered_orders_var.set(str(data.get("delivered_orders", 0)))
        
        self.available_couriers_var.set(str(data.get("available_couriers", 0)))
        self.busy_couriers_var.set(str(data.get("busy_couriers", 0)))
        
        self.last_delivery_var.set(data.get("last_delivery", "Ninguno"))
