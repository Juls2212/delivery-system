from __future__ import annotations

import tkinter as tk

from app import DeliveryManagementApp
from frontend_controller import FrontendController
from ui_components import ResultTextBox, validate_numeric_id


class TestSkipped(Exception):
    """Raised when a UI test cannot run in the current environment."""


def create_app_or_skip() -> DeliveryManagementApp:
    try:
        app = DeliveryManagementApp()
        app.update_idletasks()
        return app
    except tk.TclError as error:
        raise TestSkipped(f"Tkinter no pudo iniciarse en este entorno: {error}") from error


def test_startup() -> bool:
    app = create_app_or_skip()
    app.update()
    title = app.title()
    app.destroy()
    assert title == "Sistema de Gestion de Entregas", f"Titulo incorrecto: {title}"
    return True


def test_widgets_exist() -> bool:
    app = create_app_or_skip()
    assert hasattr(app, "result_box"), "Falta el widget result_box"
    assert hasattr(app, "status_text"), "Falta la variable status_text"
    assert hasattr(app, "selected_order_id"), "Falta la variable selected_order_id"
    assert isinstance(app.result_box, ResultTextBox), "result_box no es ResultTextBox"
    app.destroy()
    return True


def test_validate_numeric_id() -> bool:
    ok, _ = validate_numeric_id("5")
    assert ok, "El ID '5' deberia ser valido"

    ok, msg = validate_numeric_id("")
    assert not ok and bool(msg.strip()), "Campo vacio deberia fallar"

    ok, msg = validate_numeric_id("abc")
    assert not ok and bool(msg.strip()), "Texto no numerico deberia fallar"

    ok, msg = validate_numeric_id("0")
    assert not ok and bool(msg.strip()), "Cero deberia fallar"
    return True


def test_status_initial_value() -> bool:
    app = create_app_or_skip()
    value = app.status_text.get()
    app.destroy()
    assert value == "Panel listo", f"Estado inicial incorrecto: '{value}'"
    return True


def test_controller_uses_real_backend() -> bool:
    controller = FrontendController()
    summary = controller.get_dashboard_summary()
    assert summary["pending_orders"] >= 1, "El backend real debe iniciar con pedidos de muestra"
    assert summary["available_couriers"] >= 1, "El backend real debe iniciar con repartidores"
    return True


def test_controller_order_flow() -> bool:
    controller = FrontendController()
    created_order = controller.create_order(
        "Maria Lopez",
        "Panaderia Central",
        "Centro",
        "Norte",
        "Pan, Jugo",
        "1",
    )
    assert created_order["customer"] == "Maria Lopez", "El pedido creado debe conservar el cliente"
    assert created_order["status"] == "Waiting", "El pedido creado debe quedar en espera"

    assigned = controller.assign_next_order()
    assert assigned["status"] == "In transit", "El pedido asignado debe quedar en transito"

    completed = controller.complete_selected_order(assigned["order_id"])
    assert completed["final_status"] == "Delivered", "El pedido debe registrarse como entregado"

    history = controller.show_delivery_history()
    assert history, "El historial debe contener al menos una entrega"
    return True


TESTS = [
    ("Inicio de la aplicacion", test_startup),
    ("Existencia de widgets", test_widgets_exist),
    ("Validacion de ID numerico", test_validate_numeric_id),
    ("Valor inicial del estado", test_status_initial_value),
    ("Controlador con backend real", test_controller_uses_real_backend),
    ("Flujo principal del controlador", test_controller_order_flow),
]


if __name__ == "__main__":
    failures = 0
    skipped = 0

    for name, test in TESTS:
        try:
            test()
            print(f"  PASS  {name}")
        except TestSkipped as exc:
            print(f"  SKIP  {name}: {exc}")
            skipped += 1
        except Exception as exc:
            print(f"  FAIL  {name}: {exc}")
            failures += 1

    print()
    if failures == 0:
        if skipped == 0:
            print("Todas las pruebas pasaron correctamente.")
        else:
            print(f"Todas las pruebas ejecutables pasaron correctamente. Omitidas: {skipped}.")
    else:
        print(f"{failures} prueba(s) fallaron. Omitidas: {skipped}.")
