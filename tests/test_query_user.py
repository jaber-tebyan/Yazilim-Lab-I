from datetime import datetime
from pathlib import Path

from yazilim_lab_project import CommandsFile, ResultsFile
from yazilim_lab_project.models import reservation
from yazilim_lab_project.models.app_state import AppState
from yazilim_lab_project.models.command import QueryUserCommand
from yazilim_lab_project.models.generic import Err, Ok
from yazilim_lab_project.models.initial_data import InitialData
from yazilim_lab_project.models.reservation import Reservation
from yazilim_lab_project.models.results import QueryResult
from yazilim_lab_project.rules.query_user_rules import all_rules_query_user

DATA = Path(__file__).parent / "data" / "query_user"


def test_rules_on_query_user_command():
    config = InitialData.model_validate_json((DATA / "initial_data.json").read_text())
    state = AppState(config=config)
    state.reservations.extend(
        [
            Reservation(
                id="r2",
                user="u1",
                resource="ODA-1",
                start=datetime.fromisoformat("2027-03-08T09:00"),
                end=datetime.fromisoformat("2027-03-08T10:00"),
                price=4,
                state=reservation.State.APPROVED,
                package=None,
            ),
            Reservation(
                id="r10",
                user="u1",
                resource="ODA-1",
                start=datetime.fromisoformat("2027-03-08T09:00"),
                end=datetime.fromisoformat("2027-03-08T10:00"),
                price=4,
                state=reservation.State.APPROVED,
                package=None,
            ),
        ]
    )
    commands: list[QueryUserCommand] = [
        cmd
        for cmd in CommandsFile().read(DATA / "commands.jsonl")
        if isinstance(cmd, QueryUserCommand)
    ]
    results: list[QueryResult.Any] = [
        res
        for res in ResultsFile().read(DATA / "results.jsonl")
        if isinstance(res, QueryResult.Variants)
    ]
    for i, cmd in enumerate(commands):
        rule_error = all_rules_query_user(cmd, state)
        match rule_error:
            case Err(err):
                result = QueryResult.Red(no=i + 1, error_code=err)
            case Ok(user_data):
                result = QueryResult.OkUser(
                    no=i + 1,
                    balance=user_data.balance,
                    reliability=user_data.reliability,
                    reservations=user_data.reservations,
                )

        assert result == results[i], f"rule {i} failed"
