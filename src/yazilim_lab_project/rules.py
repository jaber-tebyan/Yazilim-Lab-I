from enum import Enum

from yazilim_lab_project.models.command import AddUserCommand
from yazilim_lab_project.models.initial_data import InitialData
from yazilim_lab_project.models.results import AddUserResult


# Returns true if a user with same id exists
def rule_user_add_id_exist(cmd: AddUserCommand, app_state: InitialData) -> bool:
    return any(user.id == cmd.id for user in app_state.users)


def rule_user_undefined_value(cmd: AddUserCommand, app_state: InitialData) -> bool:
    return cmd.role not in app_state.roles


def rule_user_invalid_value(cmd: AddUserCommand, app_state: InitialData) -> bool:
    return (
        cmd.balance < 0
        or cmd.balance > app_state.roles[cmd.role].weekly_quota
        or cmd.reliability < 0
        or cmd.reliability > 100
    )


def all_rules_user_add(
    cmd: AddUserCommand, app_state: InitialData
) -> AddUserResult.Error | None:
    if rule_user_add_id_exist(cmd, app_state):
        return AddUserResult.Error.ID_EXISTS
    if rule_user_undefined_value(cmd, app_state):
        return AddUserResult.Error.UNDEFINED_VALUE
    if rule_user_invalid_value(cmd, app_state):
        return AddUserResult.Error.INVALID_VALUE
    return None
