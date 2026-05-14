import tkinter as tk
from tkinter import ttk
from dashboard import Dashboard
from history_view import HistoryView
from map_view import MapView
from report_generator import ReportGenerator
from dashboard_controller import DashboardController

# Clase principal que arranca la aplicación de interfaz gráfica
class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        # Configuración básica de la ventana
        self.title("Sistema de Gestión de Entregas - Frontend")
        self.geometry("800x600")
        
        # Instanciar el controlador central
        self.controller = DashboardController(self)
        
        # Configurar un Notebook (pestañas) para agrupar vistas
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)
        
        # Instanciar cada una de las vistas (Tabs)
        self.dashboard_tab = Dashboard(self.notebook, self.controller)
        self.history_tab = HistoryView(self.notebook, self.controller)
        self.map_tab = MapView(self.notebook, self.controller)
        self.report_tab = ReportGenerator(self.notebook, self.controller)
        
        # Agregar cada pestaña generada al Notebook
        self.notebook.add(self.dashboard_tab, text="Dashboard")
        self.notebook.add(self.history_tab, text="Historial")
        self.notebook.add(self.map_tab, text="Mapa")
        self.notebook.add(self.report_tab, text="Reportes")
        
        # Inyectar las referencias de las vistas al controlador para permitir actualizaciones
        self.controller.set_views(self.dashboard_tab, self.history_tab, self.map_tab)

# Punto de entrada principal para ejecutar el script directamente
if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
