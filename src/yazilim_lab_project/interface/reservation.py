from yazilim_lab_project.models.app_state import AppState


# This assumes the reservations will never be deleted.
def generate_reservation_id(state: AppState):
    count = len(state.reservations) + 1
    return f"r{count}"


def entry_reservation(res: Reservation) -> None:
    res.state = reservation.State.IN_USE
