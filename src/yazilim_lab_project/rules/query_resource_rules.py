from yazilim_lab_project.models.app_state import AppState
from yazilim_lab_project.models.command import QueryResourceCommand
from yazilim_lab_project.models.generic import Err, Ok, Result
from yazilim_lab_project.models.initial_data import Resource
from yazilim_lab_project.models.results import QueryResourceResult


def rule_query_resource_not_found(
    cmd: QueryResourceCommand, state: AppState
) -> Resource | None:
    resource = next((res for res in state.config.resources if res.id == cmd.id), None)
    return resource


def all_rules_query_resource(
    cmd: QueryResourceCommand, state: AppState
) -> Result[Resource, QueryResourceResult.Error]:
    resource = rule_query_resource_not_found(cmd, state)
    if resource is None:
        return Err(QueryResourceResult.Error.NOT_FOUND)
    return Ok(resource)
