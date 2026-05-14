"""Backend bootstrap test module.

This file wires the base managers together and offers a simple console entry
point for validating the initial in-memory architecture.
"""

from __future__ import annotations

from courier_manager import CourierManager
from delivery_history import DeliveryHistory
from order_manager import OrderManager
from seed_data import build_seed_bundle
from zone_map import ZoneMap


def bootstrap_backend() -> dict[str, object]:
    """Create the initial backend service container."""
    order_manager = OrderManager()
    courier_manager = CourierManager()
    delivery_history = DeliveryHistory()
    zone_map = ZoneMap()

    seed_bundle = build_seed_bundle()

    for order in seed_bundle["orders"]:
        order_manager.register_order(order)

    for courier in seed_bundle["couriers"]:
        courier_manager.register_courier(courier)

    for zone in seed_bundle["zones"]:
        zone_map.register_zone(zone)

    return {
        "order_manager": order_manager,
        "courier_manager": courier_manager,
        "delivery_history": delivery_history,
        "zone_map": zone_map,
    }


def main() -> None:
    """Run a basic backend bootstrap check."""
    services = bootstrap_backend()
    print("Estructura inicial del backend cargada correctamente.")
    print(f"Servicios inicializados: {', '.join(services.keys())}.")


if __name__ == "__main__":
    main()
