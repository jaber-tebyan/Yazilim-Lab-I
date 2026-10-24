from yazilim_lab_project.interface.atomic.price import atomic_get_price
from yazilim_lab_project.models.app_state import AppState
from yazilim_lab_project.models.command import (
    PriceCommand,
    ReservationCommand,
)


def get_price(cmd: PriceCommand | ReservationCommand, state: AppState) -> int:
    return atomic_get_price(cmd.resource, cmd.start, cmd.end, state)
