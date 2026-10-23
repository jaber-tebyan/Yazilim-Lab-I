from yazilim_lab_project.models.app_state import AppState
from yazilim_lab_project.models.command import QueryUserCommand
from yazilim_lab_project.models.results import QueryUserResult


# Returns true if no user with this id exists
def rule_query_user_not_found(cmd: QueryUserCommand, state: AppState) -> bool:
    return not any(user.id == cmd.id for user in state.config.users)


def all_rules_query_user(
    cmd: QueryUserCommand, state: AppState
) -> QueryUserResult.Error | None:
    if rule_query_user_not_found(cmd, state):
        return QueryUserResult.Error.NOT_FOUND
    return None
