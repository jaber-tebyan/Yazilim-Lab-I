from datetime import datetime
from pathlib import Path

from yazilim_lab_project import CommandsFile, ResultsFile
from yazilim_lab_project.interface.reservation import entry_reservation
from yazilim_lab_project.models import reservation
from yazilim_lab_project.models.app_state import AppState
from yazilim_lab_project.models.command import EntryCommand
from yazilim_lab_project.models.generic import Err, Ok
from yazilim_lab_project.models.initial_data import InitialData
from yazilim_lab_project.models.reservation import Reservation
from yazilim_lab_project.models.results import EntryResult
from yazilim_lab_project.rules.entry_rules import all_rules_entry

DATA = Path(__file__).parent / "data" / "entry"


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


def test_rules_on_entry_command():
    config = InitialData.model_validate_json((DATA / "initial_data.json").read_text())
    state = AppState(config=config)
    commands: list[EntryCommand] = [
        cmd
        for cmd in CommandsFile().read(DATA / "commands.jsonl")
        if isinstance(cmd, EntryCommand)
    ]
    results: list[EntryResult.Any] = [
        res
        for res in ResultsFile().read(DATA / "results.jsonl")
        if isinstance(res, EntryResult.Variants)
    ]

    S = reservation.State
    # Current time in initial_data is 2027-03-08T10:00
    seeds: list[Reservation] = [
        seed("r1", "2027-03-08T10:00", "2027-03-08T12:00", S.APPROVED),
        seed("r2", "2027-03-08T10:00", "2027-03-08T12:00", S.CANCELLED),
        seed("r3", "2027-03-08T10:30", "2027-03-08T12:00", S.APPROVED),
        seed("r4", "2027-03-08T09:00", "2027-03-08T10:00", S.APPROVED),
    ]
    state.reservations.extend(seeds)

    for i, cmd in enumerate(commands):
        rule_error = all_rules_entry(cmd, state)
        match rule_error:
            case Err(err):
                result = EntryResult.Red(no=i + 1, error_code=err)
            case Ok(res):
                entry_reservation(res)
                result = EntryResult.Ok(
                    no=i + 1,
                    new_status=res.state,
                )
        assert result == results[i], f"rule {i} failed"
