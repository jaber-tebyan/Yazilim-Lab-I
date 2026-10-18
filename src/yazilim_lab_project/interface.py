from yazilim_lab_project.models.initial_data import InitialData, User


def AddUser(app_state: InitialData, user: User) -> None:
    app_state.users.append(user)
