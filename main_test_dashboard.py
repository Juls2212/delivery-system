from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from dashboard import Dashboard
from dashboard_controller import DashboardController
from history_view import HistoryView
from map_view import MapView
from report_generator import ReportGenerator
from seed_data import create_sample_system


def _can_start_tk() -> tuple[bool, str]:
    try:
        root = tk.Tk()
        root.withdraw()
        root.destroy()
        return True, ""
    except tk.TclError as error:
        return False, str(error)


class DashboardTestApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.withdraw()
        self.title("Sistema de Gestión de Entregas - Dashboard")
        self.geometry("800x600")

        self.controller = DashboardController(self, system=create_sample_system())
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        self.dashboard_tab = Dashboard(self.notebook, self.controller)
        self.history_tab = HistoryView(self.notebook, self.controller)
        self.map_tab = MapView(self.notebook, self.controller)
        self.report_tab = ReportGenerator(self.notebook, self.controller)

        self.notebook.add(self.dashboard_tab, text="Dashboard")
        self.notebook.add(self.history_tab, text="Historial")
        self.notebook.add(self.map_tab, text="Mapa")
        self.notebook.add(self.report_tab, text="Reportes")

        self.controller.set_views(self.dashboard_tab, self.history_tab, self.map_tab)


def test_dashboard_startup() -> bool:
    app = DashboardTestApp()
    app.update_idletasks()
    app.update()
    assert app.notebook.index("end") == 4, "El notebook debe tener 4 pestañas"
    app.destroy()
    return True


def test_dashboard_refresh() -> bool:
    app = DashboardTestApp()
    app.controller.refresh_all_data()
    app.update_idletasks()
    assert app.dashboard_tab.total_orders_var.get() != "", "Falta total de pedidos"
    assert app.map_tab.distance_var.get().endswith("km"), "Falta distancia del mapa"
    app.destroy()
    return True


def test_report_generation() -> bool:
    controller = DashboardController(system=create_sample_system())
    summary = controller.get_general_summary_report()
    orders_report = controller.get_orders_status_report()
    assert "Resumen General" in summary, "No se generó el resumen general"
    assert "Estado de Pedidos" in orders_report, "No se generó el reporte de pedidos"
    return True


PRUEBAS = [
    ("Inicio del dashboard", test_dashboard_startup),
    ("Actualización de vistas", test_dashboard_refresh),
    ("Generación de reportes", test_report_generation),
]


if __name__ == "__main__":
    can_start_tk, error_message = _can_start_tk()
    if not can_start_tk:
        print("  SKIP  Pruebas gráficas del dashboard omitidas: Tcl/Tk no está disponible.")
        print(f"         Detalle técnico: {error_message}")
        test_report_generation()
        print("  PASS  Generación de reportes")
        print()
        print("Las pruebas no gráficas del dashboard pasaron correctamente.")
    else:
        errors = 0
        for nombre, prueba in PRUEBAS:
            try:
                prueba()
                print(f"  PASS  {nombre}")
            except Exception as exc:
                print(f"  FAIL  {nombre}: {exc}")
                errors += 1

        print()
        if errors == 0:
            print("Todas las pruebas del dashboard pasaron correctamente.")
        else:
            print(f"{errors} prueba(s) del dashboard fallaron.")
