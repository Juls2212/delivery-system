"""Zone mapping module.

This file models delivery distances using a matrix so zone-to-zone lookups are
constant-time and easy to expose to future routing or frontend layers.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import inf
from typing import Dict, List, Optional


@dataclass(slots=True)
class Zone:
    """Delivery zone entity used by the map service."""

    zone_id: str
    name: str


class ZoneMap:
    """Distance matrix for known delivery zones."""

    def __init__(self) -> None:
        # The ordered list defines the matrix index for each zone.
        self._zones: List[str] = ["Norte", "Sur", "Centro", "Occidente", "Oriente"]

        # This dictionary maps each zone name to its row and column index.
        self._zone_indexes: Dict[str, int] = {
            zone_name: index for index, zone_name in enumerate(self._zones)
        }

        # The 2D list acts as an adjacency matrix where each position stores the
        # simulated distance between an origin zone row and a destination zone column.
        self._distance_matrix: List[List[int]] = [
            [0, 14, 6, 9, 8],
            [14, 0, 7, 10, 11],
            [6, 7, 0, 5, 4],
            [9, 10, 5, 0, 8],
            [8, 11, 4, 8, 0],
        ]

        self._registered_zones: Dict[str, Zone] = {}

    def register_zone(self, zone: Zone) -> None:
        """Store an external zone entity for compatibility with bootstrap code."""
        normalized_name = self._normalize_zone_name(zone.name)
        if normalized_name not in self._zone_indexes:
            raise ValueError(f"Zone '{zone.name}' is not part of the configured matrix.")
        self._registered_zones[zone.zone_id] = zone

    def get_zone(self, zone_id: str) -> Optional[Zone]:
        """Return one registered zone by identifier."""
        return self._registered_zones.get(zone_id)

    def get_distance(self, origin_zone: str, destination_zone: str) -> int:
        """Return the simulated distance between two zones."""
        origin_index = self._get_zone_index(origin_zone)
        destination_index = self._get_zone_index(destination_zone)
        return self._distance_matrix[origin_index][destination_index]

    def list_zones(self) -> List[str]:
        """Return the zone names represented in the matrix."""
        return list(self._zones)

    def show_distance_matrix(self) -> List[List[int]]:
        """Return a copy of the current distance matrix."""
        return [row[:] for row in self._distance_matrix]

    def get_nearest_courier_zone(
        self, destination_zone: str, courier_zones: Optional[List[str]] = None
    ) -> Optional[str]:
        """Return the nearest courier zone to the requested destination zone."""
        destination_index = self._get_zone_index(destination_zone)
        candidate_zones = courier_zones if courier_zones is not None else self._zones

        nearest_zone: Optional[str] = None
        nearest_distance = inf

        # Iterating through the candidate array allows comparison of all courier
        # origin zones against the destination using direct matrix lookups.
        for courier_zone in candidate_zones:
            normalized_zone = self._normalize_zone_name(courier_zone)
            zone_index = self._get_zone_index(normalized_zone)
            current_distance = self._distance_matrix[zone_index][destination_index]

            if current_distance < nearest_distance:
                nearest_distance = current_distance
                nearest_zone = normalized_zone

        return nearest_zone

    def _get_zone_index(self, zone_name: str) -> int:
        """Return the matrix index for a zone name."""
        normalized_name = self._normalize_zone_name(zone_name)
        if normalized_name not in self._zone_indexes:
            raise KeyError(f"Zone '{zone_name}' is not defined in the matrix.")
        return self._zone_indexes[normalized_name]

    @staticmethod
    def _normalize_zone_name(zone_name: str) -> str:
        """Normalize zone labels to match the configured matrix values."""
        cleaned_name = zone_name.strip()
        alias_map = {
            "ZONE-NORTE": "Norte",
            "ZONE-SUR": "Sur",
            "ZONE-CENTRO": "Centro",
            "ZONE-OCCIDENTE": "Occidente",
            "ZONE-ORIENTE": "Oriente",
            "norte": "Norte",
            "sur": "Sur",
            "centro": "Centro",
            "occidente": "Occidente",
            "oriente": "Oriente",
        }
        return alias_map.get(cleaned_name, cleaned_name)


if __name__ == "__main__":
    zone_map = ZoneMap()

    print("Zonas disponibles en la matriz:")
    for zone_name in zone_map.list_zones():
        print(f"- {zone_name}")

    print("\nMatriz de distancias simuladas:")
    zones = zone_map.list_zones()
    header = "            " + "  ".join(f"{zone:>10}" for zone in zones)
    print(header)
    for zone_name, row in zip(zones, zone_map.show_distance_matrix()):
        formatted_row = "  ".join(f"{distance:>10}" for distance in row)
        print(f"{zone_name:>10}  {formatted_row}")

    distance = zone_map.get_distance("Centro", "Oriente")
    print(f"\nDistancia entre Centro y Oriente: {distance} km.")

    nearest_zone = zone_map.get_nearest_courier_zone(
        destination_zone="Sur",
        courier_zones=["Norte", "Centro", "Occidente"],
    )
    if nearest_zone is not None:
        print(
            f"La zona de repartidor mas cercana para entregar en Sur es {nearest_zone}."
        )
