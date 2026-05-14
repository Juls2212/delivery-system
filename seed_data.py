"""Seed data module.

This file creates reusable in-memory sample data for integration tests, demos,
and future frontend adapters.
"""

from __future__ import annotations

from courier_manager import Courier, CourierManager
from delivery_history import DeliveryHistoryStack
from order_manager import OrderManager
from zone_map import Zone, ZoneMap


def create_sample_orders(order_manager: OrderManager) -> OrderManager:
    """Populate the order manager with sample orders."""
    sample_orders = [
        {
            "order_id": "ORD-001",
            "customer_name": "Laura Gomez",
            "restaurant_name": "Burger House",
            "origin_zone": "Centro",
            "destination_zone": "Norte",
            "items": ["Hamburguesa doble", "Papas"],
            "priority": 3,
        },
        {
            "order_id": "ORD-002",
            "customer_name": "Carlos Perez",
            "restaurant_name": "Sushi Point",
            "origin_zone": "Oriente",
            "destination_zone": "Centro",
            "items": ["Combo sushi", "Te helado"],
            "priority": 1,
        },
        {
            "order_id": "ORD-003",
            "customer_name": "Ana Torres",
            "restaurant_name": "Pizza Lab",
            "origin_zone": "Norte",
            "destination_zone": "Occidente",
            "items": ["Pizza familiar"],
            "priority": 2,
        },
        {
            "order_id": "ORD-004",
            "customer_name": "Diego Herrera",
            "restaurant_name": "Taco Street",
            "origin_zone": "Sur",
            "destination_zone": "Centro",
            "items": ["Tacos al pastor", "Gaseosa"],
            "priority": 3,
        },
        {
            "order_id": "ORD-005",
            "customer_name": "Sofia Marin",
            "restaurant_name": "Green Bowl",
            "origin_zone": "Centro",
            "destination_zone": "Oriente",
            "items": ["Ensalada", "Jugo natural"],
            "priority": 2,
        },
        {
            "order_id": "ORD-006",
            "customer_name": "Mateo Ruiz",
            "restaurant_name": "Pasta Viva",
            "origin_zone": "Occidente",
            "destination_zone": "Sur",
            "items": ["Lasagna", "Pan de ajo"],
            "priority": 3,
        },
        {
            "order_id": "ORD-007",
            "customer_name": "Valentina Cruz",
            "restaurant_name": "Wok Express",
            "origin_zone": "Oriente",
            "destination_zone": "Norte",
            "items": ["Arroz especial", "Limonada"],
            "priority": 1,
        },
        {
            "order_id": "ORD-008",
            "customer_name": "Juan Medina",
            "restaurant_name": "Arepa Corner",
            "origin_zone": "Sur",
            "destination_zone": "Occidente",
            "items": ["Arepa rellena", "Cafe"],
            "priority": 3,
        },
    ]

    for order_data in sample_orders:
        order_manager.create_order(**order_data)

    return order_manager


def create_sample_couriers(courier_manager: CourierManager) -> CourierManager:
    """Populate the courier manager with sample couriers."""
    sample_couriers = [
        Courier("COU-001", "Andres Ruiz", current_zone="Centro"),
        Courier("COU-002", "Sofia Castro", current_zone="Norte"),
        Courier("COU-003", "Miguel Torres", current_zone="Sur"),
        Courier("COU-004", "Laura Medina", current_zone="Occidente"),
        Courier("COU-005", "Camila Rojas", current_zone="Oriente"),
    ]

    for courier in sample_couriers:
        courier_manager.add_courier(courier)

    return courier_manager


def create_sample_system() -> dict[str, object]:
    """Create the full in-memory backend system with sample data."""
    order_manager = OrderManager()
    courier_manager = CourierManager()
    delivery_history = DeliveryHistoryStack()
    zone_map = ZoneMap()

    create_sample_orders(order_manager)
    create_sample_couriers(courier_manager)

    for zone_name in zone_map.list_zones():
        zone_id = f"ZONE-{zone_name.upper()}"
        zone_map.register_zone(Zone(zone_id=zone_id, name=zone_name))

    return {
        "order_manager": order_manager,
        "courier_manager": courier_manager,
        "delivery_history": delivery_history,
        "zone_map": zone_map,
    }
