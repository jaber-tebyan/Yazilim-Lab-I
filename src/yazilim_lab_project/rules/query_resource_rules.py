from datetime import datetime, time, timedelta

from yazilim_lab_project.models import reservation
from yazilim_lab_project.models.app_state import AppState
from yazilim_lab_project.models.command import QueryResourceCommand
from yazilim_lab_project.models.generic import Err, Ok, Result
from yazilim_lab_project.models.initial_data import Resource
from yazilim_lab_project.models.results import QueryResult


def _overlaps_day(
    start: datetime, end: datetime, day_start: datetime, day_end: datetime
) -> bool:
    return start < day_end and day_start < end


def rule_query_resource_not_found(
    cmd: QueryResourceCommand, state: AppState
) -> list[QueryResult.OccupancyRow] | None:
    # 1. Check if resource exists
    resource = next((res for res in state.config.resources if res.id == cmd.id), None)
    if resource is None:
        return None

    day_start = datetime.combine(cmd.day, time.min)
    day_end = day_start + timedelta(days=1)
    occupancy_rows: list[QueryResult.OccupancyRow] = []

    # 2. Collect maintenance windows that overlap the given day
    for maint in state.config.maintenance_windows:
        if maint.resource == cmd.id and _overlaps_day(
            maint.start, maint.end, day_start, day_end
        ):
            occupancy_rows.append(
                QueryResult.OccupancyRow(
                    start=max(maint.start, day_start),
                    end=min(maint.end, day_end),
                    type=QueryResult.OccupancyType.MAINTENANCE,
                    reservation=None,
                )
            )

    # 3. Collect active (APPROVED / IN_USE) reservations that overlap the day
    for res in state.reservations:
        if (
            res.resource == cmd.id
            and res.state
            in [
                reservation.State.APPROVED,
                reservation.State.IN_USE,
            ]
            and _overlaps_day(res.start, res.end, day_start, day_end)
        ):
            occupancy_rows.append(
                QueryResult.OccupancyRow(
                    start=max(res.start, day_start),
                    end=min(res.end, day_end),
                    type=QueryResult.OccupancyType.RESERVATION,
                    reservation=res.id,
                )
            )

    # 4. Sort occupancy chronologically by start time
    occupancy_rows.sort(key=lambda row: row.start)

    return occupancy_rows


def all_rules_query_resource(
    cmd: QueryResourceCommand, state: AppState
) -> Result[list[QueryResult.OccupancyRow], QueryResult.Error]:
    occupancy_rows = rule_query_resource_not_found(cmd, state)
    if occupancy_rows is None:
        return Err(QueryResult.Error.NOT_FOUND)
    return Ok(occupancy_rows)
