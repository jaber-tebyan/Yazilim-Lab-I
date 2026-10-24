from datetime import datetime
from pathlib import Path

from yazilim_lab_project import CommandsFile, ResultsFile
from yazilim_lab_project.interface.reservation import cancel_reservation
from yazilim_lab_project.models import reservation
from yazilim_lab_project.models.app_state import AppState
from yazilim_lab_project.models.command import CancelCommand
from yazilim_lab_project.models.generic import Err, Ok
from yazilim_lab_project.models.initial_data import InitialData
from yazilim_lab_project.models.reservation import Reservation
from yazilim_lab_project.models.results import CancelResult
from yazilim_lab_project.models.waiting import WaitingEntry
from yazilim_lab_project.rules.cancel_rules import all_rules_cancel

DATA = Path(__file__).parent / "data" / "cancel"


def seed(id: str, start: str, end: str, st: reservation.State, price: int = 16):
    return Reservation(
        id=id,
        user="u1",
        resource="ODA-1",
        start=datetime.fromisoformat(start),
        end=datetime.fromisoformat(end),
        price=price,
        state=st,
        package=None,
    )


def test_rules_on_cancel_command():
    config = InitialData.model_validate_json((DATA / "initial_data.json").read_text())
    state = AppState(config=config)
    commands: list[CancelCommand] = [
        cmd
        for cmd in CommandsFile().read(DATA / "commands.jsonl")
        if isinstance(cmd, CancelCommand)
    ]
    results: list[CancelResult.Any] = [
        res
        for res in ResultsFile().read(DATA / "results.jsonl")
        if isinstance(res, CancelResult.Variants)
    ]

    S = reservation.State
    # Current time in initial_data is 2027-03-08T10:00
    seeds: list[Reservation] = [
        # r1: starts at 14:00 (has waiting list entry b1 for ODA-1 14:00-16:00)
        seed("r1", "2027-03-08T14:00", "2027-03-08T16:00", S.APPROVED, price=16),
        # r2: already cancelled
        seed("r2", "2027-03-08T12:00", "2027-03-08T14:00", S.CANCELLED, price=16),
        # r3: starts at 11:00 (1 hour delta < 2h -> 0% refund, -5 reliability)
        seed("r3", "2027-03-08T11:00", "2027-03-08T12:00", S.APPROVED, price=8),
        # r4: starts at 14:00 (4 hour delta in [2h, 24h) -> 50% refund: floor(15 * 0.5) = 7)
        seed("r4", "2027-03-08T14:00", "2027-03-08T16:00", S.APPROVED, price=15),
        # r5: starts at 2027-03-09T12:00 (26h delta >= 24h -> 100% refund: 20, but capped at quota 120 -> 0 added)
        seed("r5", "2027-03-09T12:00", "2027-03-09T14:00", S.APPROVED, price=20),
    ]
    state.reservations.extend(seeds)

    # Waiting list entry for ODA-1 at 14:00-16:00 by user u2
    state.waiting_list.append(
        WaitingEntry(
            id="b1",
            user="u2",
            resource="ODA-1",
            start=datetime.fromisoformat("2027-03-08T14:00"),
            end=datetime.fromisoformat("2027-03-08T16:00"),
            registered_at=datetime.fromisoformat("2027-03-08T09:00"),
        )
    )

    for i, cmd in enumerate(commands):
        rule_error = all_rules_cancel(cmd, state)
        match rule_error:
            case Err(err):
                result = CancelResult.Red(no=i + 1, error_code=err)
            case Ok(cancel_data):
                events = cancel_reservation(cancel_data.reservation, state, cancel_data)
                result = CancelResult.Ok(
                    no=i + 1,
                    refund=cancel_data.actual_refund,
                    balance=cancel_data.new_balance,
                    reliability=cancel_data.new_reliability,
                    events=events,
                )
        assert result == results[i], f"rule {i} failed"
