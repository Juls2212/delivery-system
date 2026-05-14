"""Seed data module.

This file prepares sample in-memory entities so future tests, demos, and
frontend adapters can bootstrap the backend quickly.
"""

from __future__ import annotations

from typing import Dict, List

from courier_manager import Courier
from order_manager import Order
from zone_map import Zone


def build_seed_orders() -> List[Order]:
    """Return a small sample order collection."""
    return [
        Order(
            order_id="ORD-001",
            customer_name="Laura Gomez",
            delivery_address="Calle 72 #10-15",
            zone_id="ZONE-CENTRO",
        ),
        Order(
            order_id="ORD-002",
            customer_name="Carlos Perez",
            delivery_address="Carrera 15 #93-40",
            zone_id="ZONE-NORTE",
        ),
    ]


def build_seed_couriers() -> List[Courier]:
    """Return a small sample courier collection."""
    return [
        Courier(courier_id="COU-001", name="Andres Ruiz", current_zone_id="ZONE-CENTRO"),
        Courier(courier_id="COU-002", name="Sofia Castro", current_zone_id="ZONE-NORTE"),
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
