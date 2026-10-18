from enum import Enum

from yazilim_lab_project.models.command import AddResourceCommand
from yazilim_lab_project.models.initial_data import InitialData
from yazilim_lab_project.models.results import AddResourceResult


def rule_resource_add_id_exist(cmd: AddResourceCommand, app_state: InitialData) -> bool:
    return any(resource.id == cmd.id for resource in app_state.resources)


def rule_resource_undefined_value(
    cmd: AddResourceCommand, app_state: InitialData
) -> bool:
    return cmd.type not in app_state.resource_types or any(
        (r not in app_state.roles) for r in cmd.allowed_roles
    )


def all_rules_resource_add(
    cmd: AddResourceCommand, app_state: InitialData
) -> AddResourceResult.Error | None:
    if rule_resource_add_id_exist(cmd, app_state):
        return AddResourceResult.Error.ID_EXISTS
    if rule_resource_undefined_value(cmd, app_state):
        return AddResourceResult.Error.UNDEFINED_VALUE
    return None
