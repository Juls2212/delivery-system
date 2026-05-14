"""Zone mapping module.

This file defines delivery zones and the base in-memory map abstraction for
future routing, coverage, and assignment decisions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Set


@dataclass(slots=True)
class Zone:
    """Delivery coverage unit used for assignment decisions."""

    zone_id: str
    name: str
    connected_zone_ids: Set[str] = field(default_factory=set)


class ZoneMap:
    """Base zone graph with in-memory adjacency storage."""

    def __init__(self) -> None:
        self._zones: Dict[str, Zone] = {}

    def register_zone(self, zone: Zone) -> None:
        """Store a new delivery zone in memory."""
        self._zones[zone.zone_id] = zone

    def get_zone(self, zone_id: str) -> Zone | None:
        """Return a single zone by its identifier."""
        return self._zones.get(zone_id)

    def list_zones(self) -> List[Zone]:
        """Return the current in-memory zone collection."""
        return list(self._zones.values())

    def connect_zones(self, source_zone_id: str, target_zone_id: str) -> None:
        """Reserve this method for future graph connection rules."""
        raise NotImplementedError("Zone connection logic will be implemented later.")
