from yazilim_lab_project.models.app_state import AppState
from yazilim_lab_project.models.command import AddResourceCommand
from yazilim_lab_project.models.results import AddResourceResult


def rule_resource_add_id_exist(cmd: AddResourceCommand, state: AppState) -> bool:
    return any(resource.id == cmd.id for resource in state.config.resources)


def rule_resource_undefined_value(cmd: AddResourceCommand, state: AppState) -> bool:
    return cmd.type not in state.config.resource_types or any(
        (r not in state.config.roles) for r in cmd.allowed_roles
    )


def all_rules_resource_add(
    cmd: AddResourceCommand, state: AppState
) -> AddResourceResult.Error | None:
    if rule_resource_add_id_exist(cmd, state):
        return AddResourceResult.Error.ID_EXISTS
    if rule_resource_undefined_value(cmd, state):
        return AddResourceResult.Error.UNDEFINED_VALUE
    return None
