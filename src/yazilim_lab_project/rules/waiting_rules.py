from typing import ClassVar

from pydantic import BaseModel, ConfigDict, Field

from yazilim_lab_project.interface.waiting import parse_waitlist_id
from yazilim_lab_project.models.app_state import AppState
from yazilim_lab_project.models.command import WaitingCommand
from yazilim_lab_project.models.generic import Err, Ok, Result
from yazilim_lab_project.models.results import WaitingResult
from yazilim_lab_project.models.waiting import WaitingEntry

from yazilim_lab_project.rules.atomic.reservation import (
    atomic_rule_reservation_consecutive_use,
    atomic_rule_reservation_duration_limit,
    atomic_rule_reservation_future_date_limit,
    atomic_rule_reservation_intersection,
    atomic_rule_reservation_maintenance,
    atomic_rule_reservation_no_certificate,
    atomic_rule_reservation_no_role_permission,
    atomic_rule_reservation_not_found,
    atomic_rule_reservation_out_of_working_hours,
    atomic_rule_reservation_past_time,
    atomic_rule_reservation_preparation_violation,
    atomic_rule_reservation_time_step_error,
)


class WaitingData(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(populate_by_name=True)
    waitlist_id: str = Field(
        validation_alias="bekleme_id", serialization_alias="bekleme_id"
    )
    position: int = Field(validation_alias="sira", serialization_alias="sira")
    entry: WaitingEntry


def calculate_waitlist_position(
    entry: WaitingEntry, state: AppState
) -> int:
    # All active entries for this resource plus the candidate entry
    resource_entries = [
        w for w in state.waiting_list if w.resource == entry.resource and w.id != entry.id
    ]
    resource_entries.append(entry)

    def sort_key(w: WaitingEntry):
        u = next(user for user in state.config.users if user.id == w.user)
        return (-u.reliability, w.registered_at, parse_waitlist_id(w.id))

    resource_entries.sort(key=sort_key)
    return resource_entries.index(entry) + 1


def all_rules_waiting(
    cmd: WaitingCommand, state: AppState
) -> Result[WaitingData, WaitingResult.Error]:

    if atomic_rule_reservation_not_found(cmd.user, cmd.resource, state):
        return Err(WaitingResult.Error.NOT_FOUND)

    if atomic_rule_reservation_time_step_error(cmd.start, cmd.end):
        return Err(WaitingResult.Error.TIME_STEP_ERROR)

    if atomic_rule_reservation_past_time(cmd.start, state.config.time):
        return Err(WaitingResult.Error.PAST_TIME)

    if atomic_rule_reservation_out_of_working_hours(cmd.start, cmd.end):
        return Err(WaitingResult.Error.OUT_OF_WORKING_HOURS)

    if atomic_rule_reservation_duration_limit(cmd.user, cmd.start, cmd.end, state):
        return Err(WaitingResult.Error.TIME_LIMIT)

    if atomic_rule_reservation_future_date_limit(cmd.user, cmd.start, state):
        return Err(WaitingResult.Error.FUTURE_DATE_LIMIT)

    if atomic_rule_reservation_no_role_permission(cmd.user, cmd.resource, state):
        return Err(WaitingResult.Error.NO_ROLE_PERMISSION)

    if atomic_rule_reservation_no_certificate(cmd.user, cmd.resource, state):
        return Err(WaitingResult.Error.NO_CERTIFICATE)

    if atomic_rule_reservation_maintenance(cmd.resource, cmd.start, cmd.end, state):
        return Err(WaitingResult.Error.MAINTENANCE)

    # Must fail due to intersection or preparation violation to be eligible for waitlist.
    # These checks come before consecutive use in K10, so the first failure decides.
    has_intersection = atomic_rule_reservation_intersection(
        cmd.resource, cmd.start, cmd.end, state
    )
    has_prep_violation = atomic_rule_reservation_preparation_violation(
        cmd.resource, cmd.start, cmd.end, state
    )

    if not (has_intersection or has_prep_violation):
        if atomic_rule_reservation_consecutive_use(
            cmd.user, cmd.resource, cmd.start, cmd.end, state
        ):
            return Err(WaitingResult.Error.CONSECUTIVE_USE)
        return Err(WaitingResult.Error.WAITING_UNNECESSARY)

    highest_active_waitlist_id = max(
        (parse_waitlist_id(entry.id) for entry in state.waiting_list), default=0
    )
    last_waitlist_id = max(state.next_waiting_id, highest_active_waitlist_id)
    waitlist_id = f"b{last_waitlist_id + 1}"
    entry = WaitingEntry(
        id=waitlist_id,
        user=cmd.user,
        resource=cmd.resource,
        start=cmd.start,
        end=cmd.end,
        registered_at=state.config.time,
    )
    position = calculate_waitlist_position(entry, state)

    return Ok(
        WaitingData(
            waitlist_id=waitlist_id,
            position=position,
            entry=entry,
        )
    )
