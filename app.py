from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Any, Callable, Iterable, Optional

from dashboard import Dashboard
from dashboard_controller import DashboardController
from frontend_controller import FrontendController
from history_view import HistoryView
from map_view import MapView
from report_generator import ReportGenerator
from seed_data import create_sample_system
from ui_components import ResultTextBox, StandardButton, TitleLabel, show_message


class DashboardWindow(tk.Toplevel):
    """Ventana secundaria con las vistas de dashboard conectadas al backend real."""

    def __init__(self, parent: tk.Misc, system: dict[str, object]) -> None:
        super().__init__(parent)
        self.title("Dashboard del Sistema de Entregas")
        self.geometry("920x680")
        self.minsize(760, 540)

        self.controller = DashboardController(self, system=system)

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True)

        dashboard_tab = Dashboard(notebook, self.controller)
        history_tab = HistoryView(notebook, self.controller)
        map_tab = MapView(notebook, self.controller)
        report_tab = ReportGenerator(notebook, self.controller)

        notebook.add(dashboard_tab, text="Dashboard")
        notebook.add(history_tab, text="Historial")
        notebook.add(map_tab, text="Mapa")
        notebook.add(report_tab, text="Reportes")

        self.controller.set_views(dashboard_tab, history_tab, map_tab)


class DeliveryManagementApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Sistema de Gestión de Entregas")
        self.geometry("1180x720")
        self.minsize(980, 620)
        self.configure(background="#eef3f7")

        self.backend_system = create_sample_system()
        self.controller = FrontendController(self.backend_system)
        self.dashboard_window: Optional[DashboardWindow] = None

        self.selected_order_id = tk.StringVar()
        self.status_text = tk.StringVar(value="Panel listo")

        self._configure_styles()
        self._configure_grid()
        self._build_layout()

    def _configure_styles(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")

        style.configure("Root.TFrame", background="#eef3f7")
        style.configure("Panel.TFrame", background="#ffffff", relief="flat")
        style.configure("Sidebar.TFrame", background="#12324a")

        style.configure(
            "Title.TLabel",
            background="#eef3f7",
            foreground="#0f172a",
            font=("Segoe UI Semibold", 22),
        )
        style.configure(
            "Section.TLabel",
            background="#ffffff",
            foreground="#12324a",
            font=("Segoe UI Semibold", 13),
        )
        style.configure(
            "SidebarTitle.TLabel",
            background="#12324a",
            foreground="#f8fafc",
            font=("Segoe UI Semibold", 16),
        )
        style.configure(
            "SidebarText.TLabel",
            background="#12324a",
            foreground="#c7d6e3",
            font=("Segoe UI", 10),
        )
        style.configure(
            "Action.TButton",
            font=("Segoe UI Semibold", 10),
            padding=(14, 10),
            background="#1d6fa5",
            foreground="#ffffff",
            borderwidth=0,
        )
        style.map(
            "Action.TButton",
            background=[("active", "#175b87"), ("pressed", "#114766")],
            foreground=[("disabled", "#d1d5db")],
        )
        style.configure(
            "Ghost.TButton",
            font=("Segoe UI", 10),
            padding=(14, 10),
            background="#e2e8f0",
            foreground="#12324a",
            borderwidth=0,
        )
        style.map(
            "Ghost.TButton",
            background=[("active", "#cbd5e1"), ("pressed", "#bac7d6")],
        )
        style.configure(
            "Status.TLabel",
            background="#eef3f7",
            foreground="#475569",
            font=("Segoe UI", 10),
        )

    def _configure_grid(self) -> None:
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

    def _build_layout(self) -> None:
        self._build_sidebar()
        self._build_main_area()

    def _build_sidebar(self) -> None:
        sidebar = ttk.Frame(self, style="Sidebar.TFrame", padding=24)
        sidebar.grid(row=0, column=0, sticky="ns")
        sidebar.columnconfigure(0, weight=1)

        ttk.Label(sidebar, text="Gestión de entregas", style="SidebarTitle.TLabel").grid(
            row=0, column=0, sticky="w", pady=(0, 12)
        )
        ttk.Label(
            sidebar,
            text=(
                "Panel principal para visualizar pedidos, repartidores y acciones "
                "operativas desde una sola pantalla."
            ),
            style="SidebarText.TLabel",
            wraplength=240,
            justify="left",
        ).grid(row=1, column=0, sticky="w", pady=(0, 24))

        for index, item in enumerate(
            ["Pedidos", "Repartidores", "Entregas activas", "Dashboard y reportes"],
            start=2,
        ):
            ttk.Label(sidebar, text=f"• {item}", style="SidebarText.TLabel").grid(
                row=index, column=0, sticky="w", pady=4
            )

        ttk.Separator(sidebar).grid(row=6, column=0, sticky="ew", pady=24)
        ttk.Label(sidebar, text="Estado actual", style="SidebarTitle.TLabel").grid(
            row=7, column=0, sticky="w", pady=(0, 10)
        )
        ttk.Label(
            sidebar,
            textvariable=self.status_text,
            style="SidebarText.TLabel",
            wraplength=240,
            justify="left",
        ).grid(row=8, column=0, sticky="w")

    def _build_main_area(self) -> None:
        main_frame = ttk.Frame(self, style="Root.TFrame", padding=24)
        main_frame.grid(row=0, column=1, sticky="nsew")
        main_frame.columnconfigure(0, weight=3)
        main_frame.columnconfigure(1, weight=2)
        main_frame.rowconfigure(2, weight=1)

        header = ttk.Frame(main_frame, style="Root.TFrame")
        header.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 18))
        header.columnconfigure(0, weight=1)

        TitleLabel(header, text="Sistema de Gestión de Entregas").grid(row=0, column=0, sticky="w")
        ttk.Label(
            header,
            text="Interfaz principal para operar el sistema sin exponer lógica interna del backend.",
            style="Status.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(6, 0))

        self._build_summary_panels(main_frame)
        self._build_results_panel(main_frame)
        self._build_action_panel(main_frame)

    def _build_summary_panels(self, parent: ttk.Frame) -> None:
        summary_frame = ttk.Frame(parent, style="Root.TFrame")
        summary_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 18))
        for column in range(3):
            summary_frame.columnconfigure(column, weight=1)

        cards = [
            ("Pedidos", "Consulta pendientes, prioridades y actividad actual."),
            ("Repartidores", "Visualiza disponibilidad y carga de trabajo."),
            ("Operaciones", "Ejecuta acciones y abre el dashboard completo."),
        ]

        for column, (title, description) in enumerate(cards):
            card = ttk.Frame(summary_frame, style="Panel.TFrame", padding=18)
            card.grid(row=0, column=column, sticky="nsew", padx=(0 if column == 0 else 10, 0))
            ttk.Label(card, text=title, style="Section.TLabel").grid(row=0, column=0, sticky="w")
            ttk.Label(
                card,
                text=description,
                style="Status.TLabel",
                wraplength=220,
                justify="left",
                background="#ffffff",
            ).grid(row=1, column=0, sticky="w", pady=(8, 0))

    def _build_results_panel(self, parent: ttk.Frame) -> None:
        results_panel = ttk.Frame(parent, style="Panel.TFrame", padding=18)
        results_panel.grid(row=2, column=0, sticky="nsew", padx=(0, 12))
        results_panel.columnconfigure(0, weight=1)
        results_panel.rowconfigure(1, weight=1)

        ttk.Label(results_panel, text="Resultados y actividad", style="Section.TLabel").grid(
            row=0, column=0, sticky="w", pady=(0, 12)
        )
        self.result_box = ResultTextBox(results_panel)
        self.result_box.grid(row=1, column=0, sticky="nsew")

    def _build_action_panel(self, parent: ttk.Frame) -> None:
        actions_panel = ttk.Frame(parent, style="Panel.TFrame", padding=18)
        actions_panel.grid(row=2, column=1, sticky="nsew")
        actions_panel.columnconfigure(0, weight=1)

        ttk.Label(actions_panel, text="Panel de acciones", style="Section.TLabel").grid(
            row=0, column=0, sticky="w", pady=(0, 12)
        )

        ttk.Label(
            actions_panel,
            text="ID del pedido para marcar como entregado",
            style="Status.TLabel",
            background="#ffffff",
        ).grid(row=1, column=0, sticky="w")

        order_entry = ttk.Entry(actions_panel, textvariable=self.selected_order_id, font=("Segoe UI", 10))
        order_entry.grid(row=2, column=0, sticky="ew", pady=(8, 18))

        buttons: list[tuple[str, Callable[[], None], str]] = [
            ("Crear pedido de prueba", self._create_sample_order, "Action.TButton"),
            ("Asignar siguiente pedido", self._assign_next_order, "Action.TButton"),
            ("Marcar pedido como entregado", self._complete_selected_order, "Action.TButton"),
            ("Ver pedidos pendientes", self._show_pending_orders, "Ghost.TButton"),
            ("Ver repartidores", self._show_couriers, "Ghost.TButton"),
            ("Ver pedidos activos", self._show_active_orders, "Ghost.TButton"),
            ("Abrir dashboard", self._open_dashboard, "Ghost.TButton"),
            ("Limpiar pantalla", self._clear_screen, "Ghost.TButton"),
            ("Salir", self.destroy, "Ghost.TButton"),
        ]

        for row_index, (label, command, style_name) in enumerate(buttons, start=3):
            StandardButton(actions_panel, text=label, command=command, style_name=style_name).grid(
                row=row_index, column=0, sticky="ew", pady=5
            )

    def _open_dashboard(self) -> None:
        if self.dashboard_window is not None and self.dashboard_window.winfo_exists():
            self.dashboard_window.focus_set()
            self.dashboard_window.lift()
            self.status_text.set("Dashboard ya abierto")
            return

        self.dashboard_window = DashboardWindow(self, self.backend_system)
        self.status_text.set("Dashboard abierto")

    def _get_controller_method(self, method_name: str) -> Optional[Callable[..., Any]]:
        method = getattr(self.controller, method_name, None)
        if method is None:
            show_message(
                "Método no disponible",
                f"El controlador no expone el método `{method_name}`.",
                kind="error",
            )
            return None
        return method

    def _create_sample_order(self) -> None:
        self._execute_and_render("create_sample_order", "Pedido de prueba creado")

    def _assign_next_order(self) -> None:
        self._execute_and_render("assign_next_order", "Asignación realizada")

    def _complete_selected_order(self) -> None:
        order_id_value = self.selected_order_id.get().strip()
        if not order_id_value:
            show_message(
                "Dato inválido",
                "Ingresa un ID de pedido para marcarlo como entregado.",
                kind="warning",
            )
            return
        self._execute_and_render(
            "complete_selected_order",
            "Pedido marcado como entregado",
            args=(order_id_value,),
        )

    def _show_pending_orders(self) -> None:
        self._execute_and_render("show_pending_orders", "Pedidos pendientes")

    def _show_couriers(self) -> None:
        self._execute_and_render("show_couriers", "Repartidores")

    def _show_active_orders(self) -> None:
        self._execute_and_render("show_active_orders", "Pedidos activos")

    def _clear_screen(self) -> None:
        self.result_box.clear()
        self.status_text.set("Pantalla limpia")

    def _execute_and_render(
        self,
        method_name: str,
        heading: str,
        args: tuple[Any, ...] = (),
    ) -> None:
        method = self._get_controller_method(method_name)
        if method is None:
            return

        try:
            result = method(*args)
        except Exception as error:
            show_message(
                "Error de ejecución",
                f"Ocurrió un error al ejecutar la acción.\n\nDetalle: {error}",
                kind="error",
            )
            self.status_text.set("Se produjo un error durante la operación")
            return

        self._render_result(heading=heading, result=result)
        if self.dashboard_window is not None and self.dashboard_window.winfo_exists():
            self.dashboard_window.controller.refresh_all_data()

    def _render_result(self, heading: str, result: Any) -> None:
        self.result_box.append(f"\n{heading}")
        self.result_box.append("-" * len(heading))

        if result is None:
            self.result_box.append("No se obtuvo información para mostrar.")
            self.status_text.set(f"{heading}: sin resultados")
            return

        if isinstance(result, dict):
            self._append_mapping(result)
            self.status_text.set(f"{heading}: operación completada")
            return

        if isinstance(result, Iterable) and not isinstance(result, (str, bytes, dict)):
            items = list(result)
            if not items:
                self.result_box.append("No hay registros disponibles.")
                self.status_text.set(f"{heading}: lista vacía")
                return

            for index, item in enumerate(items, start=1):
                self.result_box.append(f"{index}.")
                if isinstance(item, dict):
                    self._append_mapping(item, indent="   ")
                else:
                    self.result_box.append(f"   {item}")
            self.status_text.set(f"{heading}: {len(items)} registro(s)")
            return

        self.result_box.append(str(result))
        self.status_text.set(f"{heading}: operación completada")

    def _append_mapping(self, values: dict[str, Any], indent: str = "") -> None:
        for key, value in values.items():
            self.result_box.append(f"{indent}{self._translate_label(key)}: {value}")

    def _translate_label(self, field_name: str) -> str:
        labels = {
            "id": "ID",
            "customer": "Cliente",
            "restaurant": "Restaurante",
            "origin": "Origen",
            "destination": "Destino",
            "items": "Artículos",
            "priority": "Prioridad",
            "address": "Dirección",
            "status": "Estado",
            "order_id": "ID pedido",
            "courier_id": "ID repartidor",
            "courier_name": "Nombre del repartidor",
            "name": "Nombre",
            "zone": "Zona",
            "available": "Disponible",
            "active_orders": "Pedidos activos",
            "delivered": "Entregas completadas",
            "availability": "Disponibilidad",
            "final_status": "Estado final",
            "timestamp": "Fecha y hora",
        }
        return labels.get(field_name, field_name.replace("_", " ").capitalize())


def run_app() -> None:
    app = DeliveryManagementApp()
    app.mainloop()


if __name__ == "__main__":
    run_app()
