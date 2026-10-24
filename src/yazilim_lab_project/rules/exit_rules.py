from yazilim_lab_project.models import reservation
from yazilim_lab_project.models.app_state import AppState
from yazilim_lab_project.models.command import ExitCommand
from yazilim_lab_project.models.generic import Err, Ok, Result
from yazilim_lab_project.models.reservation import Reservation
from yazilim_lab_project.models.results import ExitResult


# Reservation not found
def rule_exit_not_found(cmd: ExitCommand, state: AppState) -> bool:
    return not any(r.id == cmd.reservation for r in state.reservations)


# Reservation is not in IN_USE state
def rule_exit_state_error(res: Reservation) -> bool:
    return res.state != reservation.State.IN_USE


def all_rules_exit(
    cmd: ExitCommand, state: AppState
) -> Result[tuple[Reservation, int], ExitResult.Error]:
    if rule_exit_not_found(cmd, state):
        return Err(ExitResult.Error.NOT_FOUND)

    res = next(r for r in state.reservations if r.id == cmd.reservation)

    if rule_exit_state_error(res):
        return Err(ExitResult.Error.STATE_ERROR)

    user = next(u for u in state.config.users if u.id == res.user)

    if state.config.time == res.end:
        new_reliability = min(100, user.reliability + 2)
    else:
        new_reliability = user.reliability

    return Ok((res, new_reliability))
