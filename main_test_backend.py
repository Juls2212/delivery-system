"""Backend integration test module.

This file demonstrates how the in-memory managers interact in a complete
assignment and delivery workflow.
"""

from __future__ import annotations

from courier_manager import CourierManager
from delivery_history import DeliveryHistoryStack, DeliveryRecord
from order_manager import OrderManager, OrderStatus
from seed_data import create_sample_system
from zone_map import ZoneMap


def show_pending_orders(order_manager: OrderManager) -> None:
    """Print the current pending order list."""
    print("Pedidos pendientes en el sistema:")
    pending_orders = order_manager.list_pending_orders()
    if not pending_orders:
        print("- No hay pedidos pendientes.")
        return

    for order in pending_orders:
        print(
            f"- {order.order_id}: {order.customer_name}, {order.restaurant_name}, "
            f"prioridad {order.priority}, ruta {order.origin_zone} -> "
            f"{order.destination_zone}, estado {order.status.value}."
        )


def show_available_couriers(courier_manager: CourierManager) -> None:
    """Print the current available courier list."""
    print("\nRepartidores disponibles:")
    available_couriers = courier_manager.get_available_couriers()
    if not available_couriers:
        print("- No hay repartidores disponibles.")
        return

    for courier in available_couriers:
        print(
            f"- {courier.courier_id}: {courier.name}, zona actual "
            f"{courier.current_zone}."
        )


def show_delivery_history(delivery_history: DeliveryHistoryStack) -> None:
    """Print the stack-based delivery history."""
    print("\nHistorial de entregas:")
    history_records = delivery_history.list_history()
    if not history_records:
        print("- No hay entregas registradas en la pila.")
        return

    for record in history_records:
        print(
            f"- {record.order_id}: {record.customer_name}, estado final "
            f"{record.final_status}."
        )


def show_distance_matrix(zone_map: ZoneMap) -> None:
    """Print the configured zone distance matrix."""
    print("\nMatriz de distancias entre zonas:")
    zones = zone_map.list_zones()
    header = "            " + "  ".join(f"{zone:>10}" for zone in zones)
    print(header)

    for zone_name, row in zip(zones, zone_map.show_distance_matrix()):
        formatted_row = "  ".join(f"{distance:>10}" for distance in row)
        print(f"{zone_name:>10}  {formatted_row}")


def main() -> None:
    """Run the full backend integration workflow."""
    services = create_sample_system()
    order_manager = services["order_manager"]
    courier_manager = services["courier_manager"]
    delivery_history = services["delivery_history"]
    zone_map = services["zone_map"]

    print("Sistema backend inicializado correctamente con datos de prueba.\n")

    show_pending_orders(order_manager)
    show_available_couriers(courier_manager)

    print("\nObteniendo el siguiente pedido a procesar:")
    next_order = order_manager.get_next_order()
    if next_order is None:
        print("No hay pedidos listos para asignacion.")
        return

    print(
        f"Pedido seleccionado: {next_order.order_id}, prioridad "
        f"{next_order.priority}, destino {next_order.destination_zone}."
    )

    nearest_zone = zone_map.get_nearest_courier_zone(
        destination_zone=next_order.destination_zone,
        courier_zones=[
            courier.current_zone for courier in courier_manager.get_available_couriers()
        ],
    )
    if nearest_zone is not None:
        print(
            f"La zona de repartidor mas cercana para este pedido es {nearest_zone}."
        )

    assigned_courier = courier_manager.assign_order_to_courier(next_order)
    if assigned_courier is None:
        print("No hay repartidores disponibles para asignar el pedido.")
        return

    order_manager.mark_order_as_assigned(next_order.order_id)
    order_manager.update_order_status(next_order.order_id, OrderStatus.IN_TRANSIT)
    print(
        f"Pedido {next_order.order_id} asignado a {assigned_courier.name} "
        f"({assigned_courier.courier_id}) y marcado en transito."
    )

    courier_manager.complete_order(assigned_courier.courier_id, next_order.order_id)
    order_manager.mark_order_as_delivered(next_order.order_id)
    delivery_history.push_delivery(
        DeliveryRecord(
            order_id=next_order.order_id,
            customer_name=next_order.customer_name,
            final_status=OrderStatus.DELIVERED.value,
        )
    )
    print(
        f"Pedido {next_order.order_id} entregado y almacenado en el historial."
    )

    show_delivery_history(delivery_history)
    show_distance_matrix(zone_map)

    queried_distance = zone_map.get_distance("Centro", "Oriente")
    print(f"\nConsulta de distancia entre Centro y Oriente: {queried_distance} km.")


if __name__ == "__main__":
    main()


# Frontend integration examples:
# from order_manager import OrderManager
# from courier_manager import CourierManager
# from delivery_history import DeliveryHistoryStack
# from zone_map import ZoneMap
# from seed_data import create_sample_system
