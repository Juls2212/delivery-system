import tkinter as tk
from tkinter import ttk

# Clase que maneja la vista del mapa y distancias entre zonas
class MapView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # Variables reactivas
        self.zones_var = tk.StringVar()
        self.closest_zone_var = tk.StringVar(value="N/A")
        self.distance_var = tk.StringVar(value="0 km")
        
        # Referencia al área de texto para mostrar la matriz
        self.distance_matrix_text = None
        
        self._setup_ui()
        
    def _setup_ui(self):
        title_label = ttk.Label(self, text="Mapa de Zonas y Distancias", font=("Arial", 14, "bold"))
        title_label.pack(pady=10)
        
        # Sección de Zonas Disponibles
        zones_frame = ttk.LabelFrame(self, text="Zonas Disponibles")
        zones_frame.pack(fill="x", padx=10, pady=5)
        ttk.Label(zones_frame, textvariable=self.zones_var, wraplength=400).pack(padx=5, pady=5)
        
        # Sección para mostrar la Matriz de Adyacencia / Distancias
        matrix_frame = ttk.LabelFrame(self, text="Matriz de Distancias")
        matrix_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.distance_matrix_text = tk.Text(matrix_frame, height=8, width=50, state="disabled")
        self.distance_matrix_text.pack(padx=5, pady=5, fill="both", expand=True)
        
        # Sección para consultas de distancia
        queries_frame = ttk.LabelFrame(self, text="Consultas de Distancia")
        queries_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(queries_frame, text="Distancia Restaurante - Destino:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        ttk.Label(queries_frame, textvariable=self.distance_var).grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        ttk.Label(queries_frame, text="Zona Más Cercana de Repartidor:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        ttk.Label(queries_frame, textvariable=self.closest_zone_var).grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        ttk.Button(queries_frame, text="Actualizar Mapa", command=self.controller.refresh_map_data).grid(row=2, column=0, columnspan=2, pady=10)

    # Actualiza la matriz y las variables de mapa con datos provistos por el controlador
    def update_map_data(self, data):
        self.zones_var.set(", ".join(data.get("zones", [])))
        self.distance_var.set(f"{data.get('distance_to_dest', 0)} km")
        self.closest_zone_var.set(data.get("closest_zone", "N/A"))
        
        matrix = data.get("matrix", [])
        self.distance_matrix_text.config(state="normal")
        self.distance_matrix_text.delete(1.0, tk.END)
        
        # Imprimir fila por fila separando elementos por tabulación
        for row in matrix:
            self.distance_matrix_text.insert(tk.END, "\t".join(map(str, row)) + "\n")
            
        # Deshabilitar escritura para el usuario
        self.distance_matrix_text.config(state="disabled")
