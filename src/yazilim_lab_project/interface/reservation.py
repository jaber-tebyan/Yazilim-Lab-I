from yazilim_lab_project.models import reservation
from yazilim_lab_project.models.app_state import AppState
from yazilim_lab_project.models.reservation import Reservation


# This assumes the reservations will never be deleted.
def generate_reservation_id(state: AppState):
    count = len(state.reservations) + 1
    return f"r{count}"


def entry_reservation(res: Reservation) -> None:
    res.state = reservation.State.IN_USE


def exit_reservation(res: Reservation, state: AppState, new_reliability: int) -> None:
    res.state = reservation.State.COMPLETED
    if state.config.time < res.end:
        res.end = state.config.time
    user = next(u for u in state.config.users if u.id == res.user)
    user.reliability = new_reliability

