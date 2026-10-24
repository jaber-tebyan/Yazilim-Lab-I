from datetime import timedelta

from yazilim_lab_project.models import reservation
from yazilim_lab_project.models.app_state import AppState
from yazilim_lab_project.models.command import EntryCommand
from yazilim_lab_project.models.generic import Err, Ok, Result
from yazilim_lab_project.models.reservation import Reservation
from yazilim_lab_project.models.results import EntryResult


# Reservation not found
def rule_entry_not_found(cmd: EntryCommand, state: AppState) -> bool:
    return not any(r.id == cmd.reservation for r in state.reservations)


# Reservation is not in APPROVED state
def rule_entry_state_error(res: Reservation) -> bool:
    return res.state != reservation.State.APPROVED


# Entry time is outside the allowed window [start - 10 minutes, start + 15 minutes]
def rule_entry_outside_window(res: Reservation, state: AppState) -> bool:
    window_start = res.start - timedelta(minutes=10)
    window_end = res.start + timedelta(minutes=15)
    return state.config.time < window_start or state.config.time > window_end


def all_rules_entry(
    cmd: EntryCommand, state: AppState
) -> Result[Reservation, EntryResult.Error]:
    if rule_entry_not_found(cmd, state):
        return Err(EntryResult.Error.NOT_FOUND)

    res = next(r for r in state.reservations if r.id == cmd.reservation)

    if rule_entry_state_error(res):
        return Err(EntryResult.Error.STATE_ERROR)

    if rule_entry_outside_window(res, state):
        return Err(EntryResult.Error.OUTSIDE_USE_WINDOW)

    return Ok(res)
