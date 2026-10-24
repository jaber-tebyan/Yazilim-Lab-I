from yazilim_lab_project.models.app_state import AppState
from yazilim_lab_project.models.initial_data import Resource, User


def AddUser(state: AppState, user: User) -> None:
    state.config.users.append(user)


def AddResource(state: AppState, resource: Resource) -> None:
    state.config.resources.append(resource)


def DecreaseUserBalance(state: AppState, user_id: str, amount: int) -> None:
    user = next(user for user in state.config.users if user.id == user_id)
    user.balance -= amount
    if user.balance < 0:
        print("This shouldn't have happend.")
        raise Exception("User balance went below zero.")


def get_user(state: AppState, user_id: str) -> User:
    user = next(user for user in state.config.users if user.id == user_id)
    return user


# This assumes the reservations will never be deleted.
def generate_reservation_id(state: AppState) -> str:
    count = len(state.reservations) + 1
    return f"r{count}"

