from yazilim_lab_project.interface import generate_reservation_id  # re-export for backwards compatibility
from yazilim_lab_project.interface.waiting import process_waiting_list_for_resource
from yazilim_lab_project.models import reservation
from yazilim_lab_project.models.app_state import AppState
from yazilim_lab_project.models.event import AutoAssign
from yazilim_lab_project.models.reservation import Reservation
from yazilim_lab_project.rules.cancel_rules import CancelData


def entry_reservation(res: Reservation) -> None:
    res.state = reservation.State.IN_USE


def exit_reservation(res: Reservation, state: AppState, new_reliability: int) -> None:
    res.state = reservation.State.COMPLETED
    if state.config.time < res.end:
        res.end = state.config.time
    user = next(u for u in state.config.users if u.id == res.user)
    user.reliability = new_reliability


def no_show_reservation(res: Reservation, state: AppState) -> None:
    res.state = reservation.State.DID_NOT_ARRIVE
    user = next(u for u in state.config.users if u.id == res.user)
    user.reliability = max(0, user.reliability - 15)


def cancel_reservation(
    res: Reservation, state: AppState, cancel_data: CancelData
) -> list[AutoAssign]:
    res.state = reservation.State.CANCELLED
    user = next(u for u in state.config.users if u.id == res.user)
    user.balance = cancel_data.new_balance
    user.reliability = cancel_data.new_reliability

    events = process_waiting_list_for_resource(state, res.resource)
    return events
