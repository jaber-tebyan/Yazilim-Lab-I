from yazilim_lab_project.models.app_state import AppState
from yazilim_lab_project.models.command import ReservationCommand
from yazilim_lab_project.models.generic import Err, Ok, Result
from yazilim_lab_project.models.results import ReservationResult
from yazilim_lab_project.rules.atomic.reservation import (
    atomic_rule_reservation_consecutive_use,
    atomic_rule_reservation_duration_limit,
    atomic_rule_reservation_future_date_limit,
    atomic_rule_reservation_insufficient_balance,
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


"""
    NOT_FOUND = "BULUNAMADI"
    TIME_STEP_ERROR = "ZAMAN_ADIMI_HATASI"
    PAST_TIME = "GECMIS_ZAMAN"
    OUT_OF_WORKING_HOURS = "CALISMA_SAATI_DISI"
    DURATION_LIMIT = "SURE_SINIRI"
    FUTURE_DATE_LIMIT = "ILERI_TARIH_SINIRI"
    NO_ROLE_PERMISSION = "ROL_IZNI_YOK"
    NO_CERTIFICATE = "SERTIFIKA_YOK"
    MAINTENANCE = "BAKIM"
    INTERSECTION = "KESISME"
    PREPARATION_VIOLATION = "HAZIRLIK_IHLALI"
    CONSECUTIVE_USE = "ARDISIK_KULLANIM"
    INSUFFICIENT_BALANCE = "BAKIYE_YETERSIZ"
"""


# User or resource not found
def rule_reservation_not_found(cmd: ReservationCommand, state: AppState):
    return atomic_rule_reservation_not_found(cmd.user, cmd.resource, state)


# Start or end date doesn't sit on 15 minutes or end date is before start date
def rule_reservation_time_step_error(cmd: ReservationCommand):
    return atomic_rule_reservation_time_step_error(cmd.start, cmd.end)


# Start date is before simulated time
def rule_reservation_past_time(cmd: ReservationCommand, state: AppState):
    return atomic_rule_reservation_past_time(cmd.start, state.config.time)


# start and end not on same day or on opening and closing hours which are between 08:00 and 22:00
def rule_reservation_out_of_working_hours(cmd: ReservationCommand):
    return atomic_rule_reservation_out_of_working_hours(cmd.start, cmd.end)


# Duration is less than 30 minutes or higher than role's allowed duration
def rule_reservation_duration_limit(cmd: ReservationCommand, state: AppState):
    return atomic_rule_reservation_duration_limit(
        cmd.user, cmd.start, cmd.end, state
    )


# End date is more than 1 day after role's allowed end date
def rule_reservation_future_date_limit(cmd: ReservationCommand, state: AppState):
    return atomic_rule_reservation_future_date_limit(
        cmd.user, cmd.start, state
    )


# Role has no permission to use this resource
def rule_reservation_no_role_permission(cmd: ReservationCommand, state: AppState):
    return atomic_rule_reservation_no_role_permission(
        cmd.user, cmd.resource, state
    )


# Required certificate is not present
def rule_reservation_no_certificate(cmd: ReservationCommand, state: AppState):
    return atomic_rule_reservation_no_certificate(
        cmd.user, cmd.resource, state
    )


# Reservation collision with maintenance window
def rule_reservation_maintenance(cmd: ReservationCommand, state: AppState):
    return atomic_rule_reservation_maintenance(
        cmd.resource, cmd.start, cmd.end, state
    )


# Reservation collision with other reservations
def rule_reservation_intersection(cmd: ReservationCommand, state: AppState):
    return atomic_rule_reservation_intersection(
        cmd.resource, cmd.start, cmd.end, state
    )


# Preparation time violation
def rule_reservation_preparation_violation(cmd: ReservationCommand, state: AppState):
    return atomic_rule_reservation_preparation_violation(
        cmd.resource, cmd.start, cmd.end, state
    )


# Same user cannot use same resource in a duration less than 60 minutes
def rule_reservation_consecutive_use(cmd: ReservationCommand, state: AppState):
    return atomic_rule_reservation_consecutive_use(
        cmd.user, cmd.resource, cmd.start, cmd.end, state
    )


def rule_reservation_insufficient_balance(
    cmd: ReservationCommand, state: AppState
) -> None | tuple[int, int]:
    return atomic_rule_reservation_insufficient_balance(
        cmd.user, cmd.resource, cmd.start, cmd.end, state
    )



def all_rules_reservation(
    cmd: ReservationCommand, state: AppState
) -> Result[tuple[int, int], ReservationResult.Error]:
    if rule_reservation_not_found(cmd, state):
        return Err(ReservationResult.Error.NOT_FOUND)
    if rule_reservation_time_step_error(cmd):
        return Err(ReservationResult.Error.TIME_STEP_ERROR)
    if rule_reservation_past_time(cmd, state):
        return Err(ReservationResult.Error.PAST_TIME)
    if rule_reservation_out_of_working_hours(cmd):
        return Err(ReservationResult.Error.OUT_OF_WORKING_HOURS)
    if rule_reservation_duration_limit(cmd, state):
        return Err(ReservationResult.Error.DURATION_LIMIT)
    if rule_reservation_future_date_limit(cmd, state):
        return Err(ReservationResult.Error.FUTURE_DATE_LIMIT)
    if rule_reservation_no_role_permission(cmd, state):
        return Err(ReservationResult.Error.NO_ROLE_PERMISSION)
    if rule_reservation_no_certificate(cmd, state):
        return Err(ReservationResult.Error.NO_CERTIFICATE)
    if rule_reservation_maintenance(cmd, state):
        return Err(ReservationResult.Error.MAINTENANCE)
    if rule_reservation_intersection(cmd, state):
        return Err(ReservationResult.Error.INTERSECTION)
    if rule_reservation_preparation_violation(cmd, state):
        return Err(ReservationResult.Error.PREPARATION_VIOLATION)
    if rule_reservation_consecutive_use(cmd, state):
        return Err(ReservationResult.Error.CONSECUTIVE_USE)

    insufficient_rule = rule_reservation_insufficient_balance(cmd, state)

    if insufficient_rule is None:
        return Err(ReservationResult.Error.INSUFFICIENT_BALANCE)

    return Ok(insufficient_rule)
