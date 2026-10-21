from yazilim_lab_project.models.initial_data import InitialData, Resource, User


def AddUser(app_state: InitialData, user: User) -> None:
    app_state.users.append(user)


def AddResource(app_state: InitialData, resource: Resource) -> None:
    app_state.resources.append(resource)
