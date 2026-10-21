from datetime import timedelta

from yazilim_lab_project.interface.price import get_price
from yazilim_lab_project.models import reservation
from yazilim_lab_project.models.app_state import AppState
from yazilim_lab_project.models.command import ReservationCommand
from yazilim_lab_project.models.generic import Err, Ok, Result
from yazilim_lab_project.models.results import ReservationResult

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
    user_exists = any(user.id == cmd.user for user in state.config.users)
    resource_exists = any(res.id == cmd.resource for res in state.config.resources)
    return not (user_exists and resource_exists)


# Start or end date doesn't sit on 15 minutes or end date is before start date
def rule_reservation_time_step_error(cmd: ReservationCommand):
    start_not_on_15_minutes = cmd.start.minute % 15 != 0
    end_not_on_15_minutes = cmd.end.minute % 15 != 0
    end_before_start = cmd.end < cmd.start
    return start_not_on_15_minutes or end_not_on_15_minutes or end_before_start


# Start date is before simulated time
def rule_reservation_past_time(cmd: ReservationCommand, state: AppState):
    return cmd.start < state.config.time


# start and end not on same day or on opening and closing hours which are between 08:00 and 22:00
def rule_reservation_out_of_working_hours(cmd: ReservationCommand):
    that_day = cmd.start.replace(hour=0, minute=0)
    opening_time, closeing_time = that_day.replace(hour=8, minute=0), that_day.replace(
        hour=22, minute=0
    )
    return not (cmd.start >= opening_time and cmd.end <= closeing_time)


# Duration is less than 30 minutes or higher than role's allowed duration
def rule_reservation_duration_limit(cmd: ReservationCommand, state: AppState):
    user = next(user for user in state.config.users if user.id == cmd.user)
    role_duration_mins = state.config.roles[user.role].max_duration_min
    current_duration_mins = (cmd.end - cmd.start).total_seconds() / 60
    return current_duration_mins < 30 or current_duration_mins > role_duration_mins


# End date is more than 1 day after role's allowed end date
def rule_reservation_future_date_limit(cmd: ReservationCommand, state: AppState):
    user = next(user for user in state.config.users if user.id == cmd.user)
    normal_end_date = state.config.time + timedelta(
        days=state.config.roles[user.role].future_day
    )
    low_reliability_end_date = state.config.time + timedelta(days=1)
    end_date = low_reliability_end_date if user.reliability < 50 else normal_end_date
    return cmd.start > end_date


# Role has no permission to use this resource
def rule_reservation_no_role_permission(cmd: ReservationCommand, state: AppState):
    user = next(user for user in state.config.users if user.id == cmd.user)
    res = next(res for res in state.config.resources if res.id == cmd.resource)
    return user.role not in res.allowed_roles


# Required certificate is not present
def rule_reservation_no_certificate(cmd: ReservationCommand, state: AppState):
    user = next(user for user in state.config.users if user.id == cmd.user)
    resource = next(res for res in state.config.resources if res.id == cmd.resource)
    res_type = state.config.resource_types[resource.type]
    return res_type.certificate != None and all(
        cert != res_type.certificate for cert in user.certificates
    )


# Reservation collision with maintenance window
def rule_reservation_maintenance(cmd: ReservationCommand, state: AppState):
    return any(
        maint
        for maint in state.config.maintenance_windows
        if maint.resource == cmd.resource
        and maint.start < cmd.end
        and cmd.start < maint.end
    )


# Reservation collision with other reservations
def rule_reservation_intersection(cmd: ReservationCommand, state: AppState):
    return any(
        resv
        for resv in state.reservations
        if resv.resource == cmd.resource
        and resv.state in [reservation.State.IN_USE, reservation.State.APPROVED]
        and resv.start < cmd.end
        and cmd.start < resv.end
    )


# Preparation time violation
def rule_reservation_preparation_violation(cmd: ReservationCommand, state: AppState):
    resource = next(res for res in state.config.resources if res.id == cmd.resource)
    res_type = state.config.resource_types[resource.type]
    preparation_delta = timedelta(minutes=res_type.preparation_min)
    return any(
        res
        for res in state.reservations
        if res.resource == cmd.resource
        and res.state
        in [
            reservation.State.COMPLETED,
            reservation.State.APPROVED,
            reservation.State.IN_USE,
        ]
        and res.start < cmd.end + preparation_delta
        and cmd.start < res.end + preparation_delta
    )


# Same user cannot use same resource in a duration less than 60 minutes
def rule_reservation_consecutive_use(cmd: ReservationCommand, state: AppState):
    delta = timedelta(minutes=60)
    return any(
        res
        for res in state.reservations
        if res.resource == cmd.resource
        and res.state
        in [
            reservation.State.COMPLETED,
            reservation.State.APPROVED,
            reservation.State.IN_USE,
        ]
        and res.start < cmd.end + delta
        and cmd.start < res.end + delta
        and res.user == cmd.user
    )


def rule_reservation_insufficient_balance(
    cmd: ReservationCommand, state: AppState
) -> None | tuple[int, int]:
    user = next(user for user in state.config.users if user.id == cmd.user)
    price = get_price(cmd, state)

    if user.balance < price:
        return None
    return (price, user.balance)


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
