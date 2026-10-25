from datetime import datetime, timedelta

from yazilim_lab_project.interface.atomic.price import atomic_get_price
from yazilim_lab_project.models import reservation
from yazilim_lab_project.models.app_state import AppState
from yazilim_lab_project.models.reservation import Reservation




def atomic_intervals_overlap(
    start_a: datetime, end_a: datetime, start_b: datetime, end_b: datetime
) -> bool:
    return start_a < end_b and start_b < end_a


def atomic_rule_reservation_not_found(
    user_id: str, resource_id: str, state: AppState
) -> bool:
    user_exists = any(user.id == user_id for user in state.config.users)
    resource_exists = any(res.id == resource_id for res in state.config.resources)
    return not (user_exists and resource_exists)


def atomic_rule_reservation_time_step_error(start: datetime, end: datetime) -> bool:
    start_not_on_15_minutes = start.minute % 15 != 0
    end_not_on_15_minutes = end.minute % 15 != 0
    end_not_after_start = end <= start
    return start_not_on_15_minutes or end_not_on_15_minutes or end_not_after_start


def atomic_rule_reservation_past_time(start: datetime, sim_time: datetime) -> bool:
    return start < sim_time


def atomic_rule_reservation_out_of_working_hours(
    start: datetime, end: datetime
) -> bool:
    that_day = start.replace(hour=0, minute=0)
    opening_time = that_day.replace(hour=8, minute=0)
    closing_time = that_day.replace(hour=22, minute=0)
    return not (start >= opening_time and end <= closing_time)


def atomic_rule_reservation_duration_limit(
    user_id: str, start: datetime, end: datetime, state: AppState
) -> bool:
    user = next(user for user in state.config.users if user.id == user_id)
    max_duration_min = state.config.roles[user.role].max_duration_min
    current_duration_mins = (end - start).total_seconds() / 60
    return current_duration_mins < 30 or current_duration_mins > max_duration_min


def atomic_rule_reservation_future_date_limit(
    user_id: str, start: datetime, state: AppState
) -> bool:
    user = next(user for user in state.config.users if user.id == user_id)
    role = state.config.roles[user.role]
    normal_end_date = state.config.time + timedelta(days=role.future_day)
    low_reliability_end_date = state.config.time + timedelta(days=1)
    end_date = low_reliability_end_date if user.reliability < 50 else normal_end_date
    return start > end_date


def atomic_rule_reservation_no_role_permission(
    user_id: str, resource_id: str, state: AppState
) -> bool:
    user = next(user for user in state.config.users if user.id == user_id)
    resource = next(res for res in state.config.resources if res.id == resource_id)
    return user.role not in resource.allowed_roles


def atomic_rule_reservation_no_certificate(
    user_id: str, resource_id: str, state: AppState
) -> bool:
    user = next(user for user in state.config.users if user.id == user_id)
    resource = next(res for res in state.config.resources if res.id == resource_id)
    res_type = state.config.resource_types[resource.type]
    return res_type.certificate is not None and all(
        cert != res_type.certificate for cert in user.certificates
    )


def atomic_rule_reservation_maintenance(
    resource_id: str,
    start: datetime,
    end: datetime,
    state: AppState,
) -> bool:
    return any(
        maint
        for maint in state.config.maintenance_windows
        if maint.resource == resource_id
        and atomic_intervals_overlap(start, end, maint.start, maint.end)
    )


def atomic_rule_reservation_intersection(
    resource_id: str,
    start: datetime,
    end: datetime,
    state: AppState,
) -> bool:
    return any(
        resv
        for resv in state.reservations
        if resv.resource == resource_id
        and resv.state in [reservation.State.IN_USE, reservation.State.APPROVED]
        and atomic_intervals_overlap(start, end, resv.start, resv.end)
    )


def atomic_rule_reservation_preparation_violation(
    resource_id: str,
    start: datetime,
    end: datetime,
    state: AppState,
) -> bool:
    resource = next(res for res in state.config.resources if res.id == resource_id)
    res_type = state.config.resource_types[resource.type]
    preparation_delta = timedelta(minutes=res_type.preparation_min)
    return any(
        res
        for res in state.reservations
        if res.resource == resource_id
        and res.state
        in [
            reservation.State.COMPLETED,
            reservation.State.APPROVED,
            reservation.State.IN_USE,
        ]
        and atomic_intervals_overlap(
            start, end + preparation_delta, res.start, res.end + preparation_delta
        )
    )


def atomic_rule_reservation_consecutive_use(
    user_id: str,
    resource_id: str,
    start: datetime,
    end: datetime,
    state: AppState,
) -> bool:
    delta = timedelta(minutes=60)
    return any(
        res
        for res in state.reservations
        if res.resource == resource_id
        and res.state
        in [
            reservation.State.COMPLETED,
            reservation.State.APPROVED,
            reservation.State.IN_USE,
        ]
        and atomic_intervals_overlap(start, end + delta, res.start, res.end + delta)
        and res.user == user_id
    )


def atomic_rule_reservation_insufficient_balance(
    user_id: str,
    resource_id: str,
    start: datetime,
    end: datetime,
    state: AppState,
) -> None | tuple[int, int]:
    user = next(user for user in state.config.users if user.id == user_id)
    price = atomic_get_price(resource_id, start, end, state)

    if user.balance < price:
        return None
    return (price, user.balance - price)


