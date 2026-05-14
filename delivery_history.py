"""Delivery history module.

This file stores completed delivery outcomes in an in-memory stack so the most
recent delivered or cancelled order can be accessed with LIFO behavior.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass(slots=True)
class DeliveryRecord:
    """Historical record for a delivered or cancelled order."""

    order_id: str
    customer_name: str
    final_status: str
    timestamp: datetime = field(default_factory=datetime.utcnow)


class DeliveryHistoryStack:
    """In-memory stack for the most recent delivery outcomes."""

    def __init__(self) -> None:
        # A Python list is used as a stack where the last inserted element is
        # also the first one removed, which matches LIFO stack behavior.
        self._history_stack: List[DeliveryRecord] = []

    def push_delivery(self, record: DeliveryRecord) -> None:
        """Push a delivered or cancelled order record onto the stack."""
        normalized_status = record.final_status.strip().lower()
        if normalized_status not in {"delivered", "cancelled"}:
            raise ValueError("Only delivered or cancelled orders can be stored.")

        self._history_stack.append(record)

    def pop_last_delivery(self) -> Optional[DeliveryRecord]:
        """Remove and return the last delivery record from the stack."""
        if not self._history_stack:
            return None
        return self._history_stack.pop()

    def peek_last_delivery(self) -> Optional[DeliveryRecord]:
        """Return the last delivery record without removing it."""
        if not self._history_stack:
            return None
        return self._history_stack[-1]

    def list_history(self) -> List[DeliveryRecord]:
        """Return the full stack content from newest to oldest."""
        return list(reversed(self._history_stack))

    def clear_history(self) -> None:
        """Remove all stored delivery history records."""
        self._history_stack.clear()


class DeliveryHistory(DeliveryHistoryStack):
    """Compatibility alias used by the existing project bootstrap."""


if __name__ == "__main__":
    history = DeliveryHistoryStack()

    history.push_delivery(
        DeliveryRecord(
            order_id="ORD-201",
            customer_name="Laura Gomez",
            final_status="Delivered",
        )
    )
    history.push_delivery(
        DeliveryRecord(
            order_id="ORD-202",
            customer_name="Carlos Perez",
            final_status="Cancelled",
        )
    )
    history.push_delivery(
        DeliveryRecord(
            order_id="ORD-203",
            customer_name="Ana Torres",
            final_status="Delivered",
        )
    )

    print("Historial de entregas almacenado en pila:")
    for record in history.list_history():
        print(
            f"- {record.order_id}: {record.customer_name}, "
            f"estado final {record.final_status}."
        )

    last_record = history.peek_last_delivery()
    if last_record is not None:
        print(
            f"\nUltimo registro en la pila: {last_record.order_id} "
            f"con estado {last_record.final_status}."
        )

    removed_record = history.pop_last_delivery()
    if removed_record is not None:
        print(
            f"Registro retirado desde la pila: {removed_record.order_id} "
            f"con estado {removed_record.final_status}."
        )

    print("\nHistorial restante despues de hacer pop:")
    for record in history.list_history():
        print(f"- {record.order_id}: {record.final_status}.")

    history.clear_history()
    print("\nLa pila de historial fue limpiada correctamente.")
