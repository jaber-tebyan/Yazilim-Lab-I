from yazilim_lab_project.models.app_state import AppState
from yazilim_lab_project.models.command import AddUserCommand
from yazilim_lab_project.models.results import AddUserResult


# Returns true if a user with same id exists
def rule_user_add_id_exist(cmd: AddUserCommand, state: AppState) -> bool:
    return any(user.id == cmd.id for user in state.config.users)


def rule_user_undefined_value(cmd: AddUserCommand, state: AppState) -> bool:
    return cmd.role not in state.config.roles


def _is_integer(val: object) -> bool:
    if isinstance(val, bool):
        return False
    if isinstance(val, int):
        return True
    if isinstance(val, float) and val.is_integer():
        return True
    return False


def rule_user_invalid_value(cmd: AddUserCommand, state: AppState) -> bool:
    if not _is_integer(cmd.balance) or not _is_integer(cmd.reliability):
        return True
    if cmd.role not in state.config.roles:
        return False
    return (
        cmd.balance < 0
        or cmd.balance > state.config.roles[cmd.role].weekly_quota
        or cmd.reliability < 0
        or cmd.reliability > 100
    )


def all_rules_user_add(
    cmd: AddUserCommand, state: AppState
) -> AddUserResult.Error | None:
    if rule_user_add_id_exist(cmd, state):
        return AddUserResult.Error.ID_EXISTS
    if rule_user_undefined_value(cmd, state):
        return AddUserResult.Error.UNDEFINED_VALUE
    if rule_user_invalid_value(cmd, state):
        return AddUserResult.Error.INVALID_VALUE
    return None
