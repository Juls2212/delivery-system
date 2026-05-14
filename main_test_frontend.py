from __future__ import annotations

from app import DeliveryManagementApp
from ui_components import ResultTextBox, validate_numeric_id


def test_startup() -> bool:
    app = DeliveryManagementApp()
    app.update_idletasks()
    app.update()
    titulo = app.title()
    app.destroy()
    assert titulo == "Sistema de Gestión de Entregas", f"Título incorrecto: {titulo}"
    return True


def test_widgets_exist() -> bool:
    app = DeliveryManagementApp()
    app.update_idletasks()
    assert hasattr(app, "result_box"), "Falta el widget result_box"
    assert hasattr(app, "status_text"), "Falta la variable status_text"
    assert hasattr(app, "selected_order_id"), "Falta la variable selected_order_id"
    assert isinstance(app.result_box, ResultTextBox), "result_box no es ResultTextBox"
    assert app.result_box.is_empty(), "El área de resultados debe iniciar vacía"
    app.destroy()
    return True


def test_validate_numeric_id() -> bool:
    ok, _ = validate_numeric_id("5")
    assert ok, "El ID '5' debería ser válido"

    ok, msg = validate_numeric_id("")
    assert not ok and "vacío" in msg, "Campo vacío debería fallar"

    ok, msg = validate_numeric_id("abc")
    assert not ok and "número" in msg, "Texto no numérico debería fallar"

    ok, msg = validate_numeric_id("0")
    assert not ok and "mayor" in msg, "Cero debería fallar"
    return True


def test_status_initial_value() -> bool:
    app = DeliveryManagementApp()
    app.update_idletasks()
    valor = app.status_text.get()
    app.destroy()
    assert valor == "Panel listo", f"Estado inicial incorrecto: '{valor}'"
    return True


PRUEBAS = [
    ("Inicio de la aplicación", test_startup),
    ("Existencia de widgets", test_widgets_exist),
    ("Validación de ID numérico", test_validate_numeric_id),
    ("Valor inicial del estado", test_status_initial_value),
]

if __name__ == "__main__":
    errores = 0
    for nombre, prueba in PRUEBAS:
        try:
            prueba()
            print(f"  PASS  {nombre}")
        except Exception as exc:
            print(f"  FAIL  {nombre}: {exc}")
            errores += 1

    print()
    if errores == 0:
        print("Todas las pruebas pasaron correctamente.")
    else:
        print(f"{errores} prueba(s) fallaron.")
