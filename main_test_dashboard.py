import tkinter as tk
from tkinter import ttk
from dashboard import Dashboard
from history_view import HistoryView
from map_view import MapView
from report_generator import ReportGenerator
from dashboard_controller import DashboardController

class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Gestión de Entregas - Frontend")
        self.geometry("800x600")
        
        # Main Controller
        self.controller = DashboardController(self)
        
        # Setup Notebook (Tabs)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)
        
        # Create Views
        self.dashboard_tab = Dashboard(self.notebook, self.controller)
        self.history_tab = HistoryView(self.notebook, self.controller)
        self.map_tab = MapView(self.notebook, self.controller)
        self.report_tab = ReportGenerator(self.notebook, self.controller)
        
        # Add tabs to notebook
        self.notebook.add(self.dashboard_tab, text="Dashboard")
        self.notebook.add(self.history_tab, text="Historial")
        self.notebook.add(self.map_tab, text="Mapa")
        self.notebook.add(self.report_tab, text="Reportes")
        
        # Inject views into controller to allow updates
        self.controller.set_views(self.dashboard_tab, self.history_tab, self.map_tab)

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
