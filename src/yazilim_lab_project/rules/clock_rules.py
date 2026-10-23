from yazilim_lab_project.models.app_state import AppState, Timestamp
from yazilim_lab_project.models.command import ClockCommand
from yazilim_lab_project.models.generic import Err, Ok, Result
from yazilim_lab_project.models.results import ClockResult


def rule_clock_back(cmd: ClockCommand, state: AppState) -> Timestamp | None:
    if cmd.time < state.config.time:
        return None
    return cmd.time


def all_rules_clock(
    cmd: ClockCommand, state: AppState
) -> Result[Timestamp, ClockResult.Error]:
    time = rule_clock_back(cmd, state)
    if time is None:
        return Err(ClockResult.Error.CLOCK_BACK)
    return Ok(time)
