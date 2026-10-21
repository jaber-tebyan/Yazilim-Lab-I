from pathlib import Path

from yazilim_lab_project import CommandsFile, ResultsFile
from yazilim_lab_project.interface import DecreaseUserBalance, get_user
from yazilim_lab_project.interface.reservation import generate_reservation_id
from yazilim_lab_project.models import reservation
from yazilim_lab_project.models.app_state import AppState
from yazilim_lab_project.models.command import ReservationCommand
from yazilim_lab_project.models.generic import Err, Ok
from yazilim_lab_project.models.initial_data import InitialData
from yazilim_lab_project.models.reservation import Reservation
from yazilim_lab_project.models.results import ReservationResult
from yazilim_lab_project.rules.reservation_rules import all_rules_reservation

DATA = Path(__file__).parent / "data" / "reservation"


def test_rules_on_reservation_command():
    config = InitialData.model_validate_json((DATA / "initial_data.json").read_text())
    state = AppState(config=config)
    commands: list[ReservationCommand] = [
        cmd
        for cmd in CommandsFile().read(DATA / "commands.jsonl")
        if isinstance(cmd, ReservationCommand)
    ]
    results: list[ReservationResult.Any] = [
        res
        for res in ResultsFile().read(DATA / "results.jsonl")
        if isinstance(res, ReservationResult.Variants)
    ]
    for i, cmd in enumerate(commands):
        rule_error = all_rules_reservation(cmd, state)
        match rule_error:
            case Err(err):
                result = ReservationResult.Red(no=i + 1, error_code=err)
            case Ok((price, balance)):

                user = get_user(state, cmd.user)
                user.balance = balance

                reservation_id = generate_reservation_id(state)

                reser = Reservation(
                    id=reservation_id,
                    user=cmd.user,
                    resource=cmd.resource,
                    start=cmd.start,
                    end=cmd.end,
                    price=price,
                    state=reservation.State.APPROVED,
                    package=None,
                )

                state.reservations.append(reser)

                result = ReservationResult.Ok(
                    no=i + 1,
                    reservation_id=reservation_id,
                    price=price,
                    balance=balance,
                )
        assert result == results[i], f"rule {i} failed"
