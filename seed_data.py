"""Seed data module.

This file prepares sample in-memory entities so future tests, demos, and
frontend adapters can bootstrap the backend quickly.
"""

from __future__ import annotations

from typing import Dict, List

from courier_manager import Courier, CourierManager
from delivery_history import DeliveryHistory
from order_manager import Order, OrderManager
from zone_map import Zone, ZoneMap


def build_seed_orders() -> List[Order]:
    """Return a small sample order collection."""
    return [
        Order(
            order_id="ORD-001",
            customer_name="Laura Gomez",
            restaurant_name="Restaurante Central",
            origin_zone="Centro",
            destination_zone="Norte",
            items=["Pizza", "Refresco"],
            priority=3,
        ),
        Order(
            order_id="ORD-002",
            customer_name="Carlos Perez",
            restaurant_name="Comidas Rápidas",
            origin_zone="Centro",
            destination_zone="Sur",
            items=["Hamburguesa", "Papas"],
            priority=2,
        ),
        Order(
            order_id="ORD-003",
            customer_name="Ana Torres",
            restaurant_name="Sushi Express",
            origin_zone="Norte",
            destination_zone="Centro",
            items=["Sushi Mix"],
            priority=1,
        ),
    ]


def build_seed_couriers() -> List[Courier]:
    """Return a small sample courier collection."""
    return [
        Courier(courier_id="COU-001", name="Andres Ruiz", current_zone="Centro"),
        Courier(courier_id="COU-002", name="Sofia Castro", current_zone="Norte"),
        Courier(courier_id="COU-003", name="Diego Lopez", current_zone="Sur"),
    ]


def build_seed_zones() -> List[Zone]:
    """Return a small sample zone collection."""
    return [
        Zone(zone_id="ZONE-CENTRO", name="Centro"),
        Zone(zone_id="ZONE-NORTE", name="Norte"),
        Zone(zone_id="ZONE-SUR", name="Sur"),
    ]


def build_seed_bundle() -> Dict[str, List[object]]:
    """Return grouped seed data for quick bootstrap flows."""
    return {
        "orders": build_seed_orders(),
        "couriers": build_seed_couriers(),
        "zones": build_seed_zones(),
    }


def create_sample_system() -> Dict[str, object]:
    """Create and initialize a complete backend system with sample data.
    
    This function is used by the frontend to bootstrap the delivery management
    system with all required services and seed data.
    
    Returns a dictionary containing:
        - order_manager: OrderManager instance with seed orders
        - courier_manager: CourierManager instance with seed couriers
        - delivery_history: DeliveryHistory instance for tracking completions
        - zone_map: ZoneMap instance with zone data
    """
    order_manager = OrderManager()
    courier_manager = CourierManager()
    delivery_history = DeliveryHistory()
    zone_map = ZoneMap()

    seed_bundle = build_seed_bundle()

    # Register all seed orders with the manager
    for order in seed_bundle["orders"]:
        order_manager.register_order(order)

    # Register all seed couriers with the manager
    for courier in seed_bundle["couriers"]:
        courier_manager.register_courier(courier)

    # Register all zones with the map
    for zone in seed_bundle["zones"]:
        zone_map.register_zone(zone)

    return {
        "order_manager": order_manager,
        "courier_manager": courier_manager,
        "delivery_history": delivery_history,
        "zone_map": zone_map,
    }
