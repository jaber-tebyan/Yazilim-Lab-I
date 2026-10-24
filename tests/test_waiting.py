from datetime import datetime
from pathlib import Path

from pydantic import TypeAdapter

from yazilim_lab_project import CommandsFile, ResultsFile
from yazilim_lab_project.interface.waiting import add_waiting_entry
from yazilim_lab_project.models import reservation
from yazilim_lab_project.models.app_state import AppState
from yazilim_lab_project.models.command import WaitingCommand
from yazilim_lab_project.models.generic import Err, Ok
from yazilim_lab_project.models.initial_data import InitialData
from yazilim_lab_project.models.reservation import Reservation
from yazilim_lab_project.models.results import WaitingResult
from yazilim_lab_project.models.waiting import WaitingEntry
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


def run(state: AppState, commands_path: Path, results_path: Path) -> None:
    commands: list[WaitingCommand] = [
        cmd
        for cmd in CommandsFile().read(commands_path)
        if isinstance(cmd, WaitingCommand)
    ]

    results: list[WaitingResult.Any] = [
        res
        for res in ResultsFile().read(results_path)
        if isinstance(res, WaitingResult.Variants)
    ]

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


def test_rules_on_waiting_command():
    config = InitialData.model_validate_json((DATA / "initial_data.json").read_text())
    state = AppState(config=config)

    S = reservation.State
    # ODA-1 is occupied between 13:00 and 15:00
    state.reservations.append(
        seed("r1", "ODA-1", "2027-03-08T13:00", "2027-03-08T15:00", S.APPROVED)
    )
    # u1 also used ODA-1 until 12:30, so the 13:00 request violates both
    # intersection and consecutive use. Intersection comes first in K10.
    state.reservations.append(
        seed("r2", "ODA-1", "2027-03-08T11:30", "2027-03-08T12:30", S.APPROVED)
    )

    run(state, DATA / "commands.jsonl", DATA / "results.jsonl")


def test_waiting_ids_do_not_collide_after_removal():
    config = InitialData.model_validate_json((DATA / "initial_data.json").read_text())
    state = AppState(config=config)

    S = reservation.State
    state.reservations.append(
        seed("r1", "ODA-1", "2027-03-08T13:00", "2027-03-08T15:00", S.APPROVED)
    )
    # b1 was promoted/expired earlier; b2 and b3 remain. The next id must be b4,
    # not b3 (the old len + 1 formula would collide with b3).
    state.waiting_list.extend(
        TypeAdapter(list[WaitingEntry]).validate_json(
            (DATA / "waiting_ids.json").read_text()
        )
    )

    run(state, DATA / "commands_ids.jsonl", DATA / "results_ids.jsonl")
