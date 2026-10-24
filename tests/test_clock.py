from datetime import datetime
from pathlib import Path

from yazilim_lab_project import CommandsFile, ResultsFile
from yazilim_lab_project.interface.clock import advance_clock
from yazilim_lab_project.interface.waiting import add_waiting_entry
from yazilim_lab_project.models import reservation
from yazilim_lab_project.models.app_state import AppState
from yazilim_lab_project.models.command import ClockCommand
from yazilim_lab_project.models.generic import Err, Ok
from yazilim_lab_project.models.initial_data import InitialData
from yazilim_lab_project.models.reservation import Reservation
from yazilim_lab_project.models.results import ClockResult
from yazilim_lab_project.models.waiting import WaitingEntry
from yazilim_lab_project.rules.clock_rules import all_rules_clock

DATA = Path(__file__).parent / "data" / "clock"


def seed(id: str, user: str, resource: str, start: str, end: str, st: reservation.State):
    return Reservation(
        id=id,
        user=user,
        resource=resource,
        start=datetime.fromisoformat(start),
        end=datetime.fromisoformat(end),
        price=16,
        state=st,
        package=None,
    )


def test_rules_on_clock_command():
    config = InitialData.model_validate_json((DATA / "initial_data.json").read_text())
    state = AppState(config=config)
    commands: list[ClockCommand] = [
        cmd
        for cmd in CommandsFile().read(DATA / "commands.jsonl")
        if isinstance(cmd, ClockCommand)
    ]
    results: list[ClockResult.Any] = [
        res
        for res in ResultsFile().read(DATA / "results.jsonl")
        if isinstance(res, ClockResult.Variants)
    ]

    S = reservation.State
    # initial time is Monday 08:00

    # r1 is in use and ends at 09:00 -> TAMAMLANDI
    state.reservations.append(
        seed("r1", "u1", "YAZ-1", "2027-03-08T08:00", "2027-03-08T09:00", S.IN_USE)
    )
    # r2 is approved but never entered -> GELMEDI at 10:15
    state.reservations.append(
        seed("r2", "u2", "YAZ-2", "2027-03-08T10:00", "2027-03-08T12:00", S.APPROVED)
    )
    # b1 waits for YAZ-2 -> auto-assigned when r2 no-shows
    add_waiting_entry(
        state,
        WaitingEntry(
            id="b1",
            user="u2",
            resource="YAZ-2",
            start=datetime(2027, 3, 8, 12, 0),
            end=datetime(2027, 3, 8, 13, 0),
            registered_at=datetime(2027, 3, 8, 8, 0),
        ),
    )

    for i, cmd in enumerate(commands):
        rule_result = all_rules_clock(cmd, state)
        match rule_result:
            case Err(err):
                result = ClockResult.Red(no=i + 1, error_code=err)
            case Ok(new_time):
                events = advance_clock(state, new_time)
                result = ClockResult.Ok(no=i + 1, events=events)

        assert result == results[i], f"rule {i} failed"

    # Final state after all commands.
    assert state.config.time == datetime(2027, 3, 22, 0, 0)

    u1 = next(u for u in state.config.users if u.id == "u1")
    u2 = next(u for u in state.config.users if u.id == "u2")
    assert (u1.balance, u1.reliability) == (100, 82)
    assert (u2.balance, u2.reliability) == (100, 50)

    states = {res.id: res.state for res in state.reservations}
    assert states == {
        "r1": S.COMPLETED,
        "r2": S.DID_NOT_ARRIVE,
        "r3": S.DID_NOT_ARRIVE,
    }
    assert state.waiting_list == []
