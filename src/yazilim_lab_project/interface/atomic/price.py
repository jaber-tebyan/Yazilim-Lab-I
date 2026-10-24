from datetime import datetime, timedelta
from decimal import ROUND_HALF_UP, Decimal
import math

from yazilim_lab_project.models import reservation
from yazilim_lab_project.models.app_state import AppState


def atomic_get_price(
    resource_id: str,
    start: datetime,
    end: datetime,
    state: AppState,
) -> int:
    cmd_resource = next(res for res in state.config.resources if res.id == resource_id)
    cmd_resource_type = state.config.resource_types[cmd_resource.type]
    base_fee = cmd_resource_type.base_fee

    total = 0
    curr = start
    while curr < end:
        band_start = curr - timedelta(
            hours=curr.hour % 2, minutes=curr.minute, seconds=curr.second
        )
        band_end = band_start + timedelta(hours=2, minutes=0, seconds=0)
        total_occupied_minutes: int = 0
        for res in state.reservations:
            if not (res.start < band_end and band_start < res.end):
                continue
            if not (
                res.state in [reservation.State.IN_USE, reservation.State.APPROVED]
            ):
                continue
            resource = next(r for r in state.config.resources if r.id == res.resource)
            if resource.type != cmd_resource.type:
                continue

            # total occupied minutes for 2 hour band
            overlap_start = max(res.start, band_start)
            overlap_end = min(res.end, band_end)
            overlap_minutes: int = int(
                (overlap_end - overlap_start).total_seconds() / 60
            )
            total_occupied_minutes += overlap_minutes

        # calculate occupancy for current band
        same_resources_count = (
            len(
                [res for res in state.config.resources if res.type == cmd_resource.type]
            )
            * 120
        )
        occupancy = total_occupied_minutes / same_resources_count

        band_multiplier = 1 + 0.25 * math.floor(4 * occupancy)

        # calculate peak multiplier
        peak_hours_start = curr.replace(hour=10, minute=0, second=0)
        peak_hours_end = curr.replace(hour=16, minute=0, second=0)
        if (
            curr >= peak_hours_start
            and curr < peak_hours_end
            and cmd_resource_type.energy_intensive
        ):
            peak_multiplier = 1.5
        else:
            peak_multiplier = 1

        slice_cost = base_fee * 0.25 * band_multiplier * peak_multiplier
        total += slice_cost
        curr += timedelta(minutes=15)

    return int(Decimal(str(total)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
