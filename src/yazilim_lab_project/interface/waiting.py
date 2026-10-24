from yazilim_lab_project.interface import generate_reservation_id, get_user
from yazilim_lab_project.models import reservation
from yazilim_lab_project.models.app_state import AppState
from yazilim_lab_project.models.command import ReservationCommand
from yazilim_lab_project.models.event import AutoAssign
from yazilim_lab_project.models.generic import Ok
from yazilim_lab_project.models.reservation import Reservation
from yazilim_lab_project.models.waiting import WaitingEntry
from yazilim_lab_project.rules.reservation_rules import all_rules_reservation


def add_waiting_entry(state: AppState, entry: WaitingEntry) -> None:
    state.waiting_list.append(entry)


def parse_waitlist_id(w_id: str) -> int:

    return int(w_id.lstrip("b")) if w_id.startswith("b") else int(w_id)


def validate_waitlist_entry_k10(
    entry: WaitingEntry, state: AppState
) -> tuple[int, int] | None:
    res_cmd = ReservationCommand(
        command="rezervasyon",
        user=entry.user,
        resource=entry.resource,
        start=entry.start,
        end=entry.end,
    )
    rule_result = all_rules_reservation(res_cmd, state)
    if isinstance(rule_result, Ok):
        return rule_result.value
    return None


def process_waiting_list_for_resource(
    state: AppState, resource_id: str
) -> list[AutoAssign]:
    events: list[AutoAssign] = []

    # 1. Clean up expired waiting entries (start < simulated time)
    state.waiting_list = [
        entry for entry in state.waiting_list if entry.start >= state.config.time
    ]

    # 2. Filter for the freed resource
    resource_entries: list[WaitingEntry] = [
        entry for entry in state.waiting_list if entry.resource == resource_id
    ]

    # 3. Sort candidates:
    #    - Higher user reliability first (-reliability)
    #    - Earlier registration time (registered_at)
    #    - Smaller id (b2 before b10)
    def sort_key(entry: WaitingEntry):
        user = get_user(state, entry.user)
        return (-user.reliability, entry.registered_at, parse_waitlist_id(entry.id))

    resource_entries.sort(key=sort_key)

    # 4. Process each entry against K10 validation
    for entry in resource_entries:
        k10_result = validate_waitlist_entry_k10(entry, state)
        if k10_result is not None:
            price, new_balance = k10_result

            user = get_user(state, entry.user)
            user.balance = new_balance

            res_id = generate_reservation_id(state)
            new_res = Reservation(
                id=res_id,
                user=entry.user,
                resource=entry.resource,
                start=entry.start,
                end=entry.end,
                price=price,
                state=reservation.State.APPROVED,
                package=None,
            )
            state.reservations.append(new_res)

            # Remove from waiting list
            state.waiting_list = [w for w in state.waiting_list if w.id != entry.id]

            events.append(
                AutoAssign(
                    time=state.config.time,
                    waitlist=entry.id,
                    reservation=res_id,
                    user=user.id,
                    price=price,
                    balance=user.balance,
                )
            )

    return events
