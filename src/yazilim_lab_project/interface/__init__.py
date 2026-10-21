from yazilim_lab_project.models.app_state import AppState
from yazilim_lab_project.models.initial_data import Resource, User


def AddUser(state: AppState, user: User) -> None:
    state.config.users.append(user)


def AddResource(state: AppState, resource: Resource) -> None:
    state.config.resources.append(resource)
