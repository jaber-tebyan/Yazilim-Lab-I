from datetime import timedelta

from yazilim_lab_project.models import reservation
from yazilim_lab_project.models.app_state import AppState
from yazilim_lab_project.models.command import PriceCommand
from yazilim_lab_project.models.results import PriceResult

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
"""


# User or resource not found
def rule_price_not_found(cmd: PriceCommand, state: AppState):
    user_exists = any(user.id == cmd.user for user in state.config.users)
    resource_exists = any(res.id == cmd.resource for res in state.config.resources)
    return not (user_exists and resource_exists)


# Start or end date doesn't sit on 15 minutes or end date is not after start date
def rule_price_time_step_error(cmd: PriceCommand):
    start_not_on_15_minutes = cmd.start.minute % 15 != 0
    end_not_on_15_minutes = cmd.end.minute % 15 != 0
    end_not_after_start = cmd.end <= cmd.start
    return start_not_on_15_minutes or end_not_on_15_minutes or end_not_after_start


# Start date is before simulated time
def rule_price_past_time(cmd: PriceCommand, state: AppState):
    return cmd.start < state.config.time


# start and end not on same day or on opening and closing hours which are between 08:00 and 22:00
def rule_price_out_of_working_hours(cmd: PriceCommand):
    that_day = cmd.start.replace(hour=0, minute=0)
    opening_time, closeing_time = that_day.replace(hour=8, minute=0), that_day.replace(
        hour=22, minute=0
    )
    return not (cmd.start >= opening_time and cmd.end <= closeing_time)


# Duration is less than 30 minutes or higher than role's allowed duration
def rule_price_duration_limit(cmd: PriceCommand, state: AppState):
    user = next(user for user in state.config.users if user.id == cmd.user)
    role_duration_mins = state.config.roles[user.role].max_duration_min
    current_duration_mins = (cmd.end - cmd.start).total_seconds() / 60
    return current_duration_mins < 30 or current_duration_mins > role_duration_mins


# End date is more than 1 day after role's allowed end date
def rule_price_future_date_limit(cmd: PriceCommand, state: AppState):
    user = next(user for user in state.config.users if user.id == cmd.user)
    normal_end_date = state.config.time + timedelta(
        days=state.config.roles[user.role].future_day
    )
    low_reliability_end_date = state.config.time + timedelta(days=1)
    end_date = low_reliability_end_date if user.reliability < 50 else normal_end_date
    return cmd.start > end_date


# Role has no permission to use this resource
def rule_price_no_role_permission(cmd: PriceCommand, state: AppState):
    user = next(user for user in state.config.users if user.id == cmd.user)
    res = next(res for res in state.config.resources if res.id == cmd.resource)
    return user.role not in res.allowed_roles


# Required certificate is not present
def rule_price_no_certificate(cmd: PriceCommand, state: AppState):
    user = next(user for user in state.config.users if user.id == cmd.user)
    resource = next(res for res in state.config.resources if res.id == cmd.resource)
    res_type = state.config.resource_types[resource.type]
    return res_type.certificate != None and all(
        cert != res_type.certificate for cert in user.certificates
    )


# Reservation collision with maintenance window
def rule_price_maintenance(cmd: PriceCommand, state: AppState):
    return any(
        maint
        for maint in state.config.maintenance_windows
        if maint.resource == cmd.resource
        and maint.start < cmd.end
        and cmd.start < maint.end
    )


# Reservation collision with other reservations
def rule_price_intersection(cmd: PriceCommand, state: AppState):
    return any(
        resv
        for resv in state.reservations
        if resv.resource == cmd.resource
        and resv.state in [reservation.State.IN_USE, reservation.State.APPROVED]
        and resv.start < cmd.end
        and cmd.start < resv.end
    )


# Preparation time violation
def rule_price_preparation_violation(cmd: PriceCommand, state: AppState):
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
def rule_price_consecutive_use(cmd: PriceCommand, state: AppState):
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


def all_rules_price(cmd: PriceCommand, state: AppState) -> PriceResult.Error | None:
    if rule_price_not_found(cmd, state):
        return PriceResult.Error.NOT_FOUND
    if rule_price_time_step_error(cmd):
        return PriceResult.Error.TIME_STEP_ERROR
    if rule_price_past_time(cmd, state):
        return PriceResult.Error.PAST_TIME
    if rule_price_out_of_working_hours(cmd):
        return PriceResult.Error.OUT_OF_WORKING_HOURS
    if rule_price_duration_limit(cmd, state):
        return PriceResult.Error.DURATION_LIMIT
    if rule_price_future_date_limit(cmd, state):
        return PriceResult.Error.FUTURE_DATE_LIMIT
    if rule_price_no_role_permission(cmd, state):
        return PriceResult.Error.NO_ROLE_PERMISSION
    if rule_price_no_certificate(cmd, state):
        return PriceResult.Error.NO_CERTIFICATE
    if rule_price_maintenance(cmd, state):
        return PriceResult.Error.MAINTENANCE
    if rule_price_intersection(cmd, state):
        return PriceResult.Error.INTERSECTION
    if rule_price_preparation_violation(cmd, state):
        return PriceResult.Error.PREPARATION_VIOLATION
    if rule_price_consecutive_use(cmd, state):
        return PriceResult.Error.CONSECUTIVE_USE
    return None
