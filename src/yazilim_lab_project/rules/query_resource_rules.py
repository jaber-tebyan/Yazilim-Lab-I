from yazilim_lab_project.models.app_state import AppState
from yazilim_lab_project.models.command import QueryResourceCommand
from yazilim_lab_project.models.results import QueryResourceResult


# Returns true if no resource with this id exists
def rule_query_resource_not_found(cmd: QueryResourceCommand, state: AppState) -> bool:
    return not any(res.id == cmd.id for res in state.config.resources)


def all_rules_query_resource(
    cmd: QueryResourceCommand, state: AppState
) -> QueryResourceResult.Error | None:
    if rule_query_resource_not_found(cmd, state):
        return QueryResourceResult.Error.NOT_FOUND
    return None
