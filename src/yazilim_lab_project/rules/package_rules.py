from datetime import timedelta

from yazilim_lab_project.interface.price import get_price
from yazilim_lab_project.models.app_state import AppState
from yazilim_lab_project.models.command import (
    PackageCommand,
    ReservationRequests,
    ReservationCommand,
)
from yazilim_lab_project.models.generic import Err, Ok, Result
from yazilim_lab_project.models.initial_data import User
from yazilim_lab_project.models.results import PackageResult
from yazilim_lab_project.rules.atomic.reservation import (
    atomic_intervals_overlap,
    atomic_rule_reservation_consecutive_use,
    atomic_rule_reservation_duration_limit,
    atomic_rule_reservation_future_date_limit,
    atomic_rule_reservation_intersection,
    atomic_rule_reservation_maintenance,
    atomic_rule_reservation_no_certificate,
    atomic_rule_reservation_no_role_permission,
    atomic_rule_reservation_out_of_working_hours,
    atomic_rule_reservation_past_time,
    atomic_rule_reservation_preparation_violation,
    atomic_rule_reservation_time_step_error,
)

# --- Package-Level Rules ---


def rule_package_not_found(cmd: PackageCommand, state: AppState) -> bool:
    """Checks if the user exists."""
    return not any(user.id == cmd.user for user in state.config.users)


def rule_package_package_size(cmd: PackageCommand) -> bool:
    """Checks if the number of package items is between 2 and 4."""
    return not (2 <= len(cmd.items) <= 4)


def rule_package_low_reliability(user: User) -> bool:
    """Checks if the user reliability is below 50."""
    return user.reliability < 50


# --- Package Item-Level Rules (for each reservation item) ---


def rule_package_item_not_found(item: ReservationRequests, state: AppState) -> bool:
    """Checks if the requested resource exists."""
    return not any(res.id == item.resource for res in state.config.resources)


def rule_package_item_time_step_error(item: ReservationRequests) -> bool:
    """Checks if start/end times sit on 15-minute intervals and end is after start."""
    return atomic_rule_reservation_time_step_error(item.start, item.end)


def rule_package_item_past_time(item: ReservationRequests, state: AppState) -> bool:
    """Checks if start time is before simulated time."""
    return atomic_rule_reservation_past_time(item.start, state.config.time)


def rule_package_item_out_of_working_hours(item: ReservationRequests) -> bool:
    """Checks if reservation falls within 08:00 and 22:00 on the same day."""
    return atomic_rule_reservation_out_of_working_hours(item.start, item.end)


def rule_package_item_duration_limit(
    item: ReservationRequests, user: User, state: AppState
) -> bool:
    """Checks if duration is between 30 minutes and the role's maximum allowed duration."""
    return atomic_rule_reservation_duration_limit(
        user.id, item.start, item.end, state
    )


def rule_package_item_future_date_limit(
    item: ReservationRequests, user: User, state: AppState
) -> bool:
    """Checks if start date exceeds the future date limit based on role and reliability."""
    return atomic_rule_reservation_future_date_limit(user.id, item.start, state)


def rule_package_item_no_role_permission(
    item: ReservationRequests, user: User, state: AppState
) -> bool:
    """Checks if user's role is permitted to use the resource."""
    return atomic_rule_reservation_no_role_permission(
        user.id, item.resource, state
    )


def rule_package_item_no_certificate(
    item: ReservationRequests, user: User, state: AppState
) -> bool:
    """Checks if required resource certificate is present."""
    return atomic_rule_reservation_no_certificate(user.id, item.resource, state)


def rule_package_item_maintenance(item: ReservationRequests, state: AppState) -> bool:
    """Checks for collision with maintenance windows."""
    return atomic_rule_reservation_maintenance(
        item.resource, item.start, item.end, state
    )


def rule_package_item_intersection(item: ReservationRequests, state: AppState) -> bool:
    """Checks for collision with existing approved or in-use reservations."""
    return atomic_rule_reservation_intersection(
        item.resource, item.start, item.end, state
    )


def rule_package_item_preparation_violation(
    item: ReservationRequests, state: AppState
) -> bool:
    """Checks for resource preparation time violations."""
    return atomic_rule_reservation_preparation_violation(
        item.resource, item.start, item.end, state
    )


def rule_package_item_consecutive_use(
    item: ReservationRequests, user: User, state: AppState
) -> bool:
    """Checks for consecutive use violations by the same user on the same resource."""
    return atomic_rule_reservation_consecutive_use(
        user.id, item.resource, item.start, item.end, state
    )


# --- Intra-Package and Balance Package-Level Rules ---


def rule_package_intra_package_intersection(
    cmd: PackageCommand, state: AppState
) -> bool:
    """Checks if any items within the package intersect or violate preparation/consecutive use rules with each other."""
    for i in range(len(cmd.items)):
        for j in range(i + 1, len(cmd.items)):
            item1 = cmd.items[i]
            item2 = cmd.items[j]
            if item1.resource == item2.resource:
                if atomic_intervals_overlap(
                    item1.start, item1.end, item2.start, item2.end
                ):
                    return True

                resource = next(
                    (r for r in state.config.resources if r.id == item1.resource), None
                )
                if resource:
                    res_type = state.config.resource_types[resource.type]
                    prep_delta = timedelta(minutes=res_type.preparation_min)
                    if atomic_intervals_overlap(
                        item1.start,
                        item1.end + prep_delta,
                        item2.start,
                        item2.end + prep_delta,
                    ):
                        return True

                cons_delta = timedelta(minutes=60)
                if atomic_intervals_overlap(
                    item1.start,
                    item1.end + cons_delta,
                    item2.start,
                    item2.end + cons_delta,
                ):
                    return True
    return False


def rule_package_insufficient_balance(
    cmd: PackageCommand, user: User, state: AppState
) -> tuple[bool, list[int], int]:
    """Calculates total price and checks if user balance is insufficient."""
    prices: list[int] = []
    for item in cmd.items:
        price_cmd = ReservationCommand(
            command="rezervasyon",
            user=cmd.user,
            resource=item.resource,
            start=item.start,
            end=item.end,
        )
        prices.append(get_price(price_cmd, state))
    total_price = sum(prices)
    return user.balance < total_price, prices, total_price


# --- Coordinator Function ---


def all_rules_package(
    cmd: PackageCommand, state: AppState
) -> Result[
    tuple[list[int], int], tuple[PackageResult.Error, list[PackageResult.Item]]
]:
    # 1. BULUNAMADI
    if rule_package_not_found(cmd, state):
        return Err((PackageResult.Error.NOT_FOUND, []))

    user = next(u for u in state.config.users if u.id == cmd.user)

    # 2. PAKET_BOYUTU
    if rule_package_package_size(cmd):
        return Err((PackageResult.Error.PACKAGE_SIZE, []))

    # 3. GUVENILIRLIK_DUSUK
    if rule_package_low_reliability(user):
        return Err((PackageResult.Error.LOW_RELIABILITY, []))

    # 4. PAKET_RED (Validate each item)
    item_results: list[PackageResult.Item] = []
    has_item_error = False

    for idx, item in enumerate(cmd.items):
        if rule_package_item_not_found(item, state):
            item_results.append(
                PackageResult.Item(
                    index=idx,
                    status=PackageResult.Status.RED,
                    error_code=PackageResult.ItemError.NOT_FOUND,
                )
            )
            has_item_error = True
            continue

        if rule_package_item_time_step_error(item):
            item_results.append(
                PackageResult.Item(
                    index=idx,
                    status=PackageResult.Status.RED,
                    error_code=PackageResult.ItemError.TIME_STEP_ERROR,
                )
            )
            has_item_error = True
            continue

        if rule_package_item_past_time(item, state):
            item_results.append(
                PackageResult.Item(
                    index=idx,
                    status=PackageResult.Status.RED,
                    error_code=PackageResult.ItemError.PAST_TIME,
                )
            )
            has_item_error = True
            continue

        if rule_package_item_out_of_working_hours(item):
            item_results.append(
                PackageResult.Item(
                    index=idx,
                    status=PackageResult.Status.RED,
                    error_code=PackageResult.ItemError.OUT_OF_WORKING_HOURS,
                )
            )
            has_item_error = True
            continue

        if rule_package_item_duration_limit(item, user, state):
            item_results.append(
                PackageResult.Item(
                    index=idx,
                    status=PackageResult.Status.RED,
                    error_code=PackageResult.ItemError.DURATION_LIMIT,
                )
            )
            has_item_error = True
            continue

        if rule_package_item_future_date_limit(item, user, state):
            item_results.append(
                PackageResult.Item(
                    index=idx,
                    status=PackageResult.Status.RED,
                    error_code=PackageResult.ItemError.FUTURE_DATE_LIMIT,
                )
            )
            has_item_error = True
            continue

        if rule_package_item_no_role_permission(item, user, state):
            item_results.append(
                PackageResult.Item(
                    index=idx,
                    status=PackageResult.Status.RED,
                    error_code=PackageResult.ItemError.NO_ROLE_PERMISSION,
                )
            )
            has_item_error = True
            continue

        if rule_package_item_no_certificate(item, user, state):
            item_results.append(
                PackageResult.Item(
                    index=idx,
                    status=PackageResult.Status.RED,
                    error_code=PackageResult.ItemError.NO_CERTIFICATE,
                )
            )
            has_item_error = True
            continue

        if rule_package_item_maintenance(item, state):
            item_results.append(
                PackageResult.Item(
                    index=idx,
                    status=PackageResult.Status.RED,
                    error_code=PackageResult.ItemError.MAINTENANCE,
                )
            )
            has_item_error = True
            continue

        if rule_package_item_intersection(item, state):
            item_results.append(
                PackageResult.Item(
                    index=idx,
                    status=PackageResult.Status.RED,
                    error_code=PackageResult.ItemError.INTERSECTION,
                )
            )
            has_item_error = True
            continue

        if rule_package_item_preparation_violation(item, state):
            item_results.append(
                PackageResult.Item(
                    index=idx,
                    status=PackageResult.Status.RED,
                    error_code=PackageResult.ItemError.PREPARATION_VIOLATION,
                )
            )
            has_item_error = True
            continue

        if rule_package_item_consecutive_use(item, user, state):
            item_results.append(
                PackageResult.Item(
                    index=idx,
                    status=PackageResult.Status.RED,
                    error_code=PackageResult.ItemError.CONSECUTIVE_USE,
                )
            )
            has_item_error = True
            continue

        item_results.append(
            PackageResult.Item(
                index=idx, status=PackageResult.Status.OK, error_code=None
            )
        )

    if has_item_error:
        return Err((PackageResult.Error.PACKAGE_REJECTED, item_results))

    ok_all_items = [
        PackageResult.Item(index=k, status=PackageResult.Status.OK)
        for k in range(len(cmd.items))
    ]

    # 5. PAKET_ICI_KESISME
    if rule_package_intra_package_intersection(cmd, state):
        return Err((PackageResult.Error.INTRA_PACKAGE_INTERSECTION, ok_all_items))

    # 6. BAKIYE_YETERSIZ
    is_insufficient, prices, total_price = rule_package_insufficient_balance(
        cmd, user, state
    )
    if is_insufficient:
        return Err((PackageResult.Error.INSUFFICIENT_BALANCE, ok_all_items))

    return Ok((prices, total_price))
