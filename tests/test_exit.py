from datetime import datetime
from pathlib import Path

from yazilim_lab_project import CommandsFile, ResultsFile
from yazilim_lab_project.interface.reservation import exit_reservation
from yazilim_lab_project.models import reservation
from yazilim_lab_project.models.app_state import AppState
from yazilim_lab_project.models.command import ExitCommand
from yazilim_lab_project.models.generic import Err, Ok
from yazilim_lab_project.models.initial_data import InitialData
from yazilim_lab_project.models.reservation import Reservation
from yazilim_lab_project.models.results import ExitResult
from yazilim_lab_project.rules.exit_rules import all_rules_exit

DATA = Path(__file__).parent / "data" / "exit"


def seed(id: str, start: str, end: str, st: reservation.State):
    return Reservation(
        id=id,
        user="u1",
        resource="ODA-1",
        start=datetime.fromisoformat(start),
        end=datetime.fromisoformat(end),
        price=16,
        state=st,
        package=None,
    )


def test_rules_on_exit_command():
    config = InitialData.model_validate_json((DATA / "initial_data.json").read_text())
    state = AppState(config=config)
    commands: list[ExitCommand] = [
        cmd
        for cmd in CommandsFile().read(DATA / "commands.jsonl")
        if isinstance(cmd, ExitCommand)
    ]
    results: list[ExitResult.Any] = [
        res
        for res in ResultsFile().read(DATA / "results.jsonl")
        if isinstance(res, ExitResult.Variants)
    ]

    S = reservation.State
    # Current time in initial_data is 2027-03-08T12:00
    seeds: list[Reservation] = [
        seed("r1", "2027-03-08T10:00", "2027-03-08T12:00", S.APPROVED),
        seed("r2", "2027-03-08T10:00", "2027-03-08T12:00", S.IN_USE),
        seed("r3", "2027-03-08T11:00", "2027-03-08T13:00", S.IN_USE),
    ]
    state.reservations.extend(seeds)

    for i, cmd in enumerate(commands):
        rule_error = all_rules_exit(cmd, state)
        match rule_error:
            case Err(err):
                result = ExitResult.Red(no=i + 1, error_code=err)
            case Ok((res, new_reliability)):
                exit_reservation(res, state, new_reliability)
                result = ExitResult.Ok(
                    no=i + 1,
                    new_status=res.state,
                    reliability=new_reliability,
                    events=[],
                )
        assert result == results[i], f"rule {i} failed"
