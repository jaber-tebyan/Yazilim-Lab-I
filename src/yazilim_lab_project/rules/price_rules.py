from yazilim_lab_project.models.app_state import AppState
from yazilim_lab_project.models.command import PriceCommand
from yazilim_lab_project.models.results import PriceResult
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


def rule_price_not_found(cmd: PriceCommand, state: AppState):
    return atomic_rule_reservation_not_found(cmd.user, cmd.resource, state)


def rule_price_time_step_error(cmd: PriceCommand):
    return atomic_rule_reservation_time_step_error(cmd.start, cmd.end)


def rule_price_past_time(cmd: PriceCommand, state: AppState):
    return atomic_rule_reservation_past_time(cmd.start, state.config.time)


def rule_price_out_of_working_hours(cmd: PriceCommand):
    return atomic_rule_reservation_out_of_working_hours(cmd.start, cmd.end)


def rule_price_duration_limit(cmd: PriceCommand, state: AppState):
    return atomic_rule_reservation_duration_limit(
        cmd.user, cmd.start, cmd.end, state
    )


def rule_price_future_date_limit(cmd: PriceCommand, state: AppState):
    return atomic_rule_reservation_future_date_limit(cmd.user, cmd.start, state)


def rule_price_no_role_permission(cmd: PriceCommand, state: AppState):
    return atomic_rule_reservation_no_role_permission(
        cmd.user, cmd.resource, state
    )


def rule_price_no_certificate(cmd: PriceCommand, state: AppState):
    return atomic_rule_reservation_no_certificate(cmd.user, cmd.resource, state)


def rule_price_maintenance(cmd: PriceCommand, state: AppState):
    return atomic_rule_reservation_maintenance(
        cmd.resource, cmd.start, cmd.end, state
    )


def rule_price_intersection(cmd: PriceCommand, state: AppState):
    return atomic_rule_reservation_intersection(
        cmd.resource, cmd.start, cmd.end, state
    )


def rule_price_preparation_violation(cmd: PriceCommand, state: AppState):
    return atomic_rule_reservation_preparation_violation(
        cmd.resource, cmd.start, cmd.end, state
    )


def rule_price_consecutive_use(cmd: PriceCommand, state: AppState):
    return atomic_rule_reservation_consecutive_use(
        cmd.user, cmd.resource, cmd.start, cmd.end, state
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
