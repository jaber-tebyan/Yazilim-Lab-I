from enum import Enum

from yazilim_lab_project.models.command import AddUserCommand
from yazilim_lab_project.models.initial_data import InitialData


class AddUserErrors(Enum):
    OK = 0
    ID_EXISTS = 1
    UNDEFINED_VALUE = 2
    INVALID_VALUE = 3


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


def all_rules_user_add(cmd: AddUserCommand, app_state: InitialData) -> AddUserErrors:
    if rule_user_add_id_exist(cmd, app_state):
        return AddUserErrors.ID_EXISTS
    if rule_user_undefined_value(cmd, app_state):
        return AddUserErrors.UNDEFINED_VALUE
    if rule_user_invalid_value(cmd, app_state):
        return AddUserErrors.INVALID_VALUE
    return AddUserErrors.OK
