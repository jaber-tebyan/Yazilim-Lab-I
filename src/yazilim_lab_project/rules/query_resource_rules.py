from yazilim_lab_project.models import reservation
from yazilim_lab_project.models.app_state import AppState
from yazilim_lab_project.models.command import QueryResourceCommand
from yazilim_lab_project.models.generic import Err, Ok, Result
from yazilim_lab_project.models.initial_data import Resource
from yazilim_lab_project.models.results import QueryResult


def rule_query_resource_not_found(
    cmd: QueryResourceCommand, state: AppState
) -> list[QueryResult.OccupancyRow] | None:
    # 1. Check if resource exists
    resource = next((res for res in state.config.resources if res.id == cmd.id), None)
    if resource is None:
        return None

    occupancy_rows: list[QueryResult.OccupancyRow] = []

    # 2. Collect maintenance windows for this resource on the given day
    for maint in state.config.maintenance_windows:
        if maint.resource == cmd.id and maint.start.date() == cmd.day:
            occupancy_rows.append(
                QueryResult.OccupancyRow(
                    start=maint.start,
                    end=maint.end,
                    type=QueryResult.OccupancyType.MAINTENANCE,
                    reservation=None,
                )
            )

    # 3. Collect active (APPROVED / IN_USE) reservations on the given day
    for res in state.reservations:
        if (
            res.resource == cmd.id
            and res.start.date() == cmd.day
            and res.state
            in [
                reservation.State.APPROVED,
                reservation.State.IN_USE,
            ]
        ):
            occupancy_rows.append(
                QueryResult.OccupancyRow(
                    start=res.start,
                    end=res.end,
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
