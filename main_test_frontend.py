from __future__ import annotations

from app import DeliveryManagementApp


def validate_startup() -> bool:
    # Esta prueba básica confirma que la ventana puede construirse sin iniciar el bucle principal.
    app = DeliveryManagementApp()
    app.update_idletasks()
    app.update()
    app.destroy()
    return True


if __name__ == "__main__":
    if validate_startup():
        print("La interfaz inició correctamente.")
