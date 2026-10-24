from datetime import datetime
from pathlib import Path

from yazilim_lab_project import CommandsFile, ResultsFile
from yazilim_lab_project.interface.waiting import add_waiting_entry
from yazilim_lab_project.models import reservation
from yazilim_lab_project.models.app_state import AppState
from yazilim_lab_project.models.command import WaitingCommand
from yazilim_lab_project.models.generic import Err, Ok
from yazilim_lab_project.models.initial_data import InitialData
from yazilim_lab_project.models.reservation import Reservation
from yazilim_lab_project.models.results import WaitingResult
from yazilim_lab_project.rules.waiting_rules import all_rules_waiting

DATA = Path(__file__).parent / "data" / "waiting"


def seed(id: str, resource: str, start: str, end: str, st: reservation.State):
    return Reservation(
        id=id,
        user="u1",
        resource=resource,
        start=datetime.fromisoformat(start),
        end=datetime.fromisoformat(end),
        price=16,
        state=st,
        package=None,
    )


def test_rules_on_waiting_command():
    config = InitialData.model_validate_json((DATA / "initial_data.json").read_text())
    state = AppState(config=config)
    commands: list[WaitingCommand] = [
        cmd
        for cmd in CommandsFile().read(DATA / "commands.jsonl")
        if isinstance(cmd, WaitingCommand)
    ]

    results: list[WaitingResult.Any] = [
        res
        for res in ResultsFile().read(DATA / "results.jsonl")
        if isinstance(res, WaitingResult.Variants)
    ]

    S = reservation.State
    # ODA-1 is occupied between 13:00 and 15:00
    state.reservations.append(
        seed("r1", "ODA-1", "2027-03-08T13:00", "2027-03-08T15:00", S.APPROVED)
    )

    for i, cmd in enumerate(commands):
        rule_error = all_rules_waiting(cmd, state)
        match rule_error:
            case Err(err):
                result = WaitingResult.Red(no=i + 1, error_code=err)
            case Ok(waiting_data):
                add_waiting_entry(state, waiting_data.entry)
                result = WaitingResult.Ok(
                    no=i + 1,
                    waitlist_id=waiting_data.waitlist_id,
                    position=waiting_data.position,
                )
        assert result == results[i], f"rule {i} failed"
