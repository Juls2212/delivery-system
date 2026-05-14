from __future__ import annotations

import tkinter as tk
from importlib import import_module
from tkinter import ttk
from typing import Any, Callable, Iterable

from ui_components import FormField, ResultTextBox, StandardButton, TitleLabel, show_message


class DeliveryManagementApp(tk.Tk):
    """Main Tkinter frontend entry point for the delivery system."""

    def __init__(self) -> None:
        super().__init__()
        self.title("Sistema de Gestion de Entregas")
        self.geometry("1220x760")
        self.minsize(1000, 640)
        self.configure(background="#eef3f7")

        self.controller = self._load_controller()
        self.available_zones = self._get_available_zones()

        self.selected_order_id = tk.StringVar()
        self.customer_name = tk.StringVar()
        self.restaurant_name = tk.StringVar()
        self.items_text = tk.StringVar()
        self.origin_zone = tk.StringVar(value=self.available_zones[0] if self.available_zones else "")
        self.destination_zone = tk.StringVar(value=self.available_zones[1] if len(self.available_zones) > 1 else self.origin_zone.get())
        self.priority_text = tk.StringVar(value="2")
        self.status_text = tk.StringVar(value="Panel listo")

        self.pending_orders_value = tk.StringVar(value="0")
        self.active_orders_value = tk.StringVar(value="0")
        self.available_couriers_value = tk.StringVar(value="0")
        self.delivered_orders_value = tk.StringVar(value="0")

        self._configure_styles()
        self._configure_grid()
        self._build_layout()
        self._refresh_summary()
        self._show_welcome_message()

    def _load_controller(self) -> object | None:
        try:
            module = import_module("frontend_controller")
            controller_class = getattr(module, "FrontendController")
            return controller_class()
        except Exception as error:
            self.after(
                150,
                lambda: show_message(
                    "Controlador no disponible",
                    f"No fue posible cargar el frontend real.\n\nDetalle: {error}",
                    kind="warning",
                ),
            )
            return None

    def _get_available_zones(self) -> list[str]:
        if self.controller is None:
            return ["Centro", "Norte", "Sur", "Occidente", "Oriente"]

        zones_method = getattr(self.controller, "get_available_zones", None)
        if callable(zones_method):
            return list(zones_method())
        return ["Centro", "Norte", "Sur", "Occidente", "Oriente"]

    def _configure_styles(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")

        style.configure("Root.TFrame", background="#eef3f7")
        style.configure("Panel.TFrame", background="#ffffff")
        style.configure("Sidebar.TFrame", background="#12324a")
        style.configure("Metric.TFrame", background="#dbe8f3")
        style.configure("MetricValue.TLabel", background="#dbe8f3", foreground="#0f172a", font=("Segoe UI Semibold", 22))
        style.configure("MetricLabel.TLabel", background="#dbe8f3", foreground="#355069", font=("Segoe UI", 10))
        style.configure("Title.TLabel", background="#eef3f7", foreground="#0f172a", font=("Segoe UI Semibold", 22))
        style.configure("Section.TLabel", background="#ffffff", foreground="#12324a", font=("Segoe UI Semibold", 13))
        style.configure("SidebarTitle.TLabel", background="#12324a", foreground="#f8fafc", font=("Segoe UI Semibold", 16))
        style.configure("SidebarText.TLabel", background="#12324a", foreground="#c7d6e3", font=("Segoe UI", 10))
        style.configure("Status.TLabel", background="#ffffff", foreground="#475569", font=("Segoe UI", 10))
        style.configure("Action.TButton", font=("Segoe UI Semibold", 10), padding=(12, 9), background="#1d6fa5", foreground="#ffffff", borderwidth=0)
        style.configure("Ghost.TButton", font=("Segoe UI", 10), padding=(12, 9), background="#e2e8f0", foreground="#12324a", borderwidth=0)
        style.map("Action.TButton", background=[("active", "#175b87"), ("pressed", "#114766")])
        style.map("Ghost.TButton", background=[("active", "#cbd5e1"), ("pressed", "#bac7d6")])

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

        ttk.Label(sidebar, text="Delivery System", style="SidebarTitle.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 12))
        ttk.Label(
            sidebar,
            text="Interfaz principal para crear pedidos, asignar entregas y consultar el estado operativo.",
            style="SidebarText.TLabel",
            wraplength=240,
            justify="left",
        ).grid(row=1, column=0, sticky="w", pady=(0, 20))

        for row_index, item in enumerate(
            [
                "Crear pedidos",
                "Asignar siguiente pedido",
                "Marcar entregas",
                "Revisar historial",
            ],
            start=2,
        ):
            ttk.Label(sidebar, text=f"- {item}", style="SidebarText.TLabel").grid(row=row_index, column=0, sticky="w", pady=4)

        ttk.Separator(sidebar).grid(row=6, column=0, sticky="ew", pady=24)
        ttk.Label(sidebar, text="Estado actual", style="SidebarTitle.TLabel").grid(row=7, column=0, sticky="w", pady=(0, 8))
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
        main_frame.columnconfigure(0, weight=5)
        main_frame.columnconfigure(1, weight=4)
        main_frame.rowconfigure(2, weight=1)

        header = ttk.Frame(main_frame, style="Root.TFrame")
        header.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 18))
        header.columnconfigure(0, weight=1)

        TitleLabel(header, text="Sistema de Gestion de Entregas").grid(row=0, column=0, sticky="w")
        ttk.Label(
            header,
            text="Frontend principal conectado al backend real de pedidos y repartidores.",
            style="MetricLabel.TLabel",
            background="#eef3f7",
        ).grid(row=1, column=0, sticky="w", pady=(6, 0))

        self._build_summary_panels(main_frame)
        self._build_results_panel(main_frame)
        self._build_action_panel(main_frame)

    def _build_summary_panels(self, parent: ttk.Frame) -> None:
        summary_frame = ttk.Frame(parent, style="Root.TFrame")
        summary_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 18))
        for column in range(4):
            summary_frame.columnconfigure(column, weight=1)

        cards = [
            ("Pedidos pendientes", self.pending_orders_value),
            ("Pedidos activos", self.active_orders_value),
            ("Repartidores disponibles", self.available_couriers_value),
            ("Entregas completadas", self.delivered_orders_value),
        ]

        for column, (label, variable) in enumerate(cards):
            card = ttk.Frame(summary_frame, style="Metric.TFrame", padding=16)
            card.grid(row=0, column=column, sticky="nsew", padx=(0 if column == 0 else 10, 0))
            ttk.Label(card, textvariable=variable, style="MetricValue.TLabel").grid(row=0, column=0, sticky="w")
            ttk.Label(card, text=label, style="MetricLabel.TLabel").grid(row=1, column=0, sticky="w", pady=(6, 0))

    def _build_results_panel(self, parent: ttk.Frame) -> None:
        results_panel = ttk.Frame(parent, style="Panel.TFrame", padding=18)
        results_panel.grid(row=2, column=0, sticky="nsew", padx=(0, 12))
        results_panel.columnconfigure(0, weight=1)
        results_panel.rowconfigure(1, weight=1)

        ttk.Label(results_panel, text="Resultados y actividad", style="Section.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 12))
        self.result_box = ResultTextBox(results_panel)
        self.result_box.grid(row=1, column=0, sticky="nsew")

    def _build_action_panel(self, parent: ttk.Frame) -> None:
        actions_panel = ttk.Frame(parent, style="Panel.TFrame", padding=18)
        actions_panel.grid(row=2, column=1, sticky="nsew")
        actions_panel.columnconfigure(0, weight=1)
        actions_panel.columnconfigure(1, weight=1)

        ttk.Label(actions_panel, text="Crear nuevo pedido", style="Section.TLabel").grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 12))

        self.customer_field = FormField(actions_panel, "Cliente", self.customer_name, style="Panel.TFrame")
        self.customer_field.grid(row=1, column=0, columnspan=2, sticky="ew", pady=4)

        self.restaurant_field = FormField(actions_panel, "Restaurante", self.restaurant_name, style="Panel.TFrame")
        self.restaurant_field.grid(row=2, column=0, columnspan=2, sticky="ew", pady=4)

        self.items_field = FormField(actions_panel, "Articulos (separados por coma)", self.items_text, style="Panel.TFrame")
        self.items_field.grid(row=3, column=0, columnspan=2, sticky="ew", pady=4)

        ttk.Label(actions_panel, text="Zona de origen", style="Status.TLabel").grid(row=4, column=0, sticky="w", pady=(10, 4))
        ttk.Label(actions_panel, text="Zona de destino", style="Status.TLabel").grid(row=4, column=1, sticky="w", pady=(10, 4))

        self.origin_combo = ttk.Combobox(actions_panel, textvariable=self.origin_zone, values=self.available_zones, state="readonly", font=("Segoe UI", 10))
        self.origin_combo.grid(row=5, column=0, sticky="ew", padx=(0, 8))
        self.destination_combo = ttk.Combobox(actions_panel, textvariable=self.destination_zone, values=self.available_zones, state="readonly", font=("Segoe UI", 10))
        self.destination_combo.grid(row=5, column=1, sticky="ew")

        ttk.Label(actions_panel, text="Prioridad", style="Status.TLabel").grid(row=6, column=0, sticky="w", pady=(10, 4))
        self.priority_combo = ttk.Combobox(actions_panel, textvariable=self.priority_text, values=["1", "2", "3"], state="readonly", font=("Segoe UI", 10))
        self.priority_combo.grid(row=7, column=0, sticky="ew", padx=(0, 8))

        StandardButton(actions_panel, text="Crear pedido", command=self._create_order_from_form).grid(row=7, column=1, sticky="ew")

        ttk.Separator(actions_panel).grid(row=8, column=0, columnspan=2, sticky="ew", pady=18)
        ttk.Label(actions_panel, text="Operaciones del sistema", style="Section.TLabel").grid(row=9, column=0, columnspan=2, sticky="w", pady=(0, 12))

        ttk.Label(actions_panel, text="ID del pedido a completar", style="Status.TLabel").grid(row=10, column=0, columnspan=2, sticky="w")
        ttk.Entry(actions_panel, textvariable=self.selected_order_id, font=("Segoe UI", 10)).grid(row=11, column=0, columnspan=2, sticky="ew", pady=(6, 12))

        buttons: list[tuple[str, Callable[[], None], str]] = [
            ("Crear pedido de prueba", self._create_sample_order, "Action.TButton"),
            ("Asignar siguiente pedido", self._assign_next_order, "Action.TButton"),
            ("Marcar como entregado", self._complete_selected_order, "Action.TButton"),
            ("Ver pedidos pendientes", self._show_pending_orders, "Ghost.TButton"),
            ("Ver repartidores", self._show_couriers, "Ghost.TButton"),
            ("Ver pedidos activos", self._show_active_orders, "Ghost.TButton"),
            ("Ver historial", self._show_delivery_history, "Ghost.TButton"),
            ("Limpiar pantalla", self._clear_screen, "Ghost.TButton"),
            ("Salir", self.destroy, "Ghost.TButton"),
        ]

        for row_index, (label, command, style_name) in enumerate(buttons, start=12):
            StandardButton(actions_panel, text=label, command=command, style_name=style_name).grid(
                row=row_index,
                column=0,
                columnspan=2,
                sticky="ew",
                pady=4,
            )

    def _show_welcome_message(self) -> None:
        self.result_box.append("Sistema listo para operar.")
        self.result_box.append("Usa el formulario para crear pedidos o las acciones para consultar el backend.")

    def _get_controller_method(self, method_name: str) -> Callable[..., Any] | None:
        if self.controller is None:
            show_message("Backend no disponible", "No se pudo cargar el controlador principal.", kind="warning")
            return None

        method = getattr(self.controller, method_name, None)
        if not callable(method):
            show_message("Metodo no disponible", f"El controlador no expone `{method_name}`.", kind="error")
            return None
        return method

    def _create_order_from_form(self) -> None:
        self._execute_and_render(
            method_name="create_order",
            heading="Pedido creado",
            args=(
                self.customer_name.get(),
                self.restaurant_name.get(),
                self.origin_zone.get(),
                self.destination_zone.get(),
                self.items_text.get(),
                self.priority_text.get(),
            ),
            clear_form=True,
        )

    def _create_sample_order(self) -> None:
        self._execute_and_render(method_name="create_sample_order", heading="Pedido de prueba creado")

    def _assign_next_order(self) -> None:
        self._execute_and_render(method_name="assign_next_order", heading="Asignacion realizada")

    def _complete_selected_order(self) -> None:
        order_id = self.selected_order_id.get().strip()
        if not order_id:
            show_message("Dato invalido", "Ingresa un ID de pedido para marcarlo como entregado.", kind="warning")
            return
        self._execute_and_render(
            method_name="complete_selected_order",
            heading="Pedido entregado",
            args=(order_id,),
        )

    def _show_pending_orders(self) -> None:
        self._execute_and_render(method_name="show_pending_orders", heading="Pedidos pendientes")

    def _show_couriers(self) -> None:
        self._execute_and_render(method_name="show_couriers", heading="Repartidores")

    def _show_active_orders(self) -> None:
        self._execute_and_render(method_name="show_active_orders", heading="Pedidos activos")

    def _show_delivery_history(self) -> None:
        self._execute_and_render(method_name="show_delivery_history", heading="Historial de entregas")

    def _clear_screen(self) -> None:
        self.result_box.clear()
        self.status_text.set("Pantalla limpia")

    def _execute_and_render(
        self,
        method_name: str,
        heading: str,
        args: tuple[Any, ...] = (),
        clear_form: bool = False,
    ) -> None:
        method = self._get_controller_method(method_name)
        if method is None:
            return

        try:
            result = method(*args)
        except Exception as error:
            show_message("Error de ejecucion", f"Ocurrio un error al ejecutar la accion.\n\nDetalle: {error}", kind="error")
            self.status_text.set("Se produjo un error durante la operacion")
            return

        if clear_form:
            self._reset_order_form()

        self._refresh_summary()
        self._render_result(heading, result)

    def _reset_order_form(self) -> None:
        self.customer_name.set("")
        self.restaurant_name.set("")
        self.items_text.set("")
        if self.available_zones:
            self.origin_zone.set(self.available_zones[0])
            self.destination_zone.set(self.available_zones[1] if len(self.available_zones) > 1 else self.available_zones[0])
        self.priority_text.set("2")

    def _refresh_summary(self) -> None:
        method = self._get_controller_method("get_dashboard_summary")
        if method is None:
            return

        try:
            summary = method()
        except Exception:
            return

        self.pending_orders_value.set(str(summary.get("pending_orders", 0)))
        self.active_orders_value.set(str(summary.get("active_orders", 0)))
        self.available_couriers_value.set(str(summary.get("available_couriers", 0)))
        self.delivered_orders_value.set(str(summary.get("delivered_orders", 0)))

    def _render_result(self, heading: str, result: Any) -> None:
        self.result_box.append("")
        self.result_box.append(heading)
        self.result_box.append("-" * len(heading))

        if result is None:
            self.result_box.append("No se obtuvo informacion para mostrar.")
            self.status_text.set(f"{heading}: sin resultados")
            return

        if isinstance(result, dict):
            self._append_mapping(result)
            self.status_text.set(f"{heading}: operacion completada")
            return

        if isinstance(result, Iterable) and not isinstance(result, (str, bytes, dict)):
            items = list(result)
            if not items:
                self.result_box.append("No hay registros disponibles.")
                self.status_text.set(f"{heading}: lista vacia")
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
        self.status_text.set(f"{heading}: operacion completada")

    def _append_mapping(self, values: dict[str, Any], indent: str = "") -> None:
        for key, value in values.items():
            label = self._translate_label(key)
            self.result_box.append(f"{indent}{label}: {value}")

    def _translate_label(self, field_name: str) -> str:
        labels = {
            "id": "ID",
            "customer": "Cliente",
            "restaurant": "Restaurante",
            "origin": "Origen",
            "destination": "Destino",
            "items": "Articulos",
            "priority": "Prioridad",
            "status": "Estado",
            "message": "Mensaje",
            "order_id": "ID pedido",
            "courier_id": "ID repartidor",
            "courier_name": "Nombre del repartidor",
            "name": "Nombre",
            "zone": "Zona",
            "available": "Disponible",
            "active_orders": "Pedidos activos",
            "delivered": "Entregas completadas",
            "pending_orders": "Pedidos pendientes",
            "available_couriers": "Repartidores disponibles",
            "delivered_orders": "Entregas completadas",
            "nearest_zone": "Zona mas cercana",
            "distance_km": "Distancia estimada (km)",
            "final_status": "Estado final",
            "timestamp": "Fecha y hora",
        }
        return labels.get(field_name, field_name.replace("_", " ").capitalize())


def run_app() -> None:
    app = DeliveryManagementApp()
    app.mainloop()


if __name__ == "__main__":
    run_app()
