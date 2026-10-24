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


def waiting(id: str, user: str, resource: str, start: str, end: str, registered: str):
    return WaitingEntry(
        id=id,
        user=user,
        resource=resource,
        start=datetime.fromisoformat(start),
        end=datetime.fromisoformat(end),
        registered_at=datetime.fromisoformat(registered),
    )


def run(state: AppState, commands_path: Path, results_path: Path) -> None:
    commands: list[ClockCommand] = [
        cmd
        for cmd in CommandsFile().read(commands_path)
        if isinstance(cmd, ClockCommand)
    ]
    results: list[ClockResult.Any] = [
        res
        for res in ResultsFile().read(results_path)
        if isinstance(res, ClockResult.Variants)
    ]

    for i, cmd in enumerate(commands):
        rule_result = all_rules_clock(cmd, state)
        match rule_result:
            case Err(err):
                result = ClockResult.Red(no=i + 1, error_code=err)
            case Ok(new_time):
                events = advance_clock(state, new_time)
                result = ClockResult.Ok(no=i + 1, events=events)

        assert result == results[i], f"rule {i} failed"


def test_clock():
    config = InitialData.model_validate_json((DATA / "initial_data.json").read_text())
    state = AppState(config=config)

    S = reservation.State
    # initial time is Monday 2027-03-08T08:00
    state.reservations.extend(
        [
            # r1 completes at 09:00 (reliability +2)
            seed("r1", "u1", "YAZ-1", "2027-03-08T08:00", "2027-03-08T09:00", S.IN_USE),
            # r2 no-shows exactly at 09:15 (reliability floor at 0)
            seed("r2", "u4", "ODA-1", "2027-03-08T09:00", "2027-03-08T10:00", S.APPROVED),
            # r3 completes at 10:30 (reliability cap at 100)
            seed("r3", "u3", "YAZ-1", "2027-03-08T09:30", "2027-03-08T10:30", S.IN_USE),
            # r4 no-shows at 10:15, freeing YAZ-2 for the waitlist
            seed("r4", "u2", "YAZ-2", "2027-03-08T10:00", "2027-03-08T12:00", S.APPROVED),
            # r5/r6 no-show at 12:15 (same instant, must order by id)
            seed("r5", "u3", "ODA-2", "2027-03-08T12:00", "2027-03-08T13:00", S.APPROVED),
            seed("r6", "u2", "ODA-1", "2027-03-08T12:00", "2027-03-08T13:00", S.APPROVED),
            # r7 completes at 11:00, exactly when r8 no-shows: completed must
            # run before no-show at the same instant
            seed("r7", "u6", "ODA-2", "2027-03-08T08:00", "2027-03-08T11:00", S.IN_USE),
            seed("r8", "u5", "ODA-1", "2027-03-08T10:45", "2027-03-08T11:45", S.APPROVED),
            # r9 no-shows exactly at Monday 00:00: weekly reset must run first
            seed("r9", "u6", "YAZ-1", "2027-03-14T23:45", "2027-03-15T00:45", S.APPROVED),
        ]
    )
    # b1 is promoted by r4's no-show -> r10 (created during the advance, and its
    # own no-show at 12:15 must be processed within the same window)
    add_waiting_entry(
        state, waiting("b1", "u2", "YAZ-2", "2027-03-08T12:00", "2027-03-08T13:00", "2027-03-08T08:00")
    )
    # b2 waits for YAZ-1. r3 completes at 10:30, but completion must NOT trigger
    # a scan, so b2 is never promoted and later expires.
    add_waiting_entry(
        state, waiting("b2", "u5", "YAZ-1", "2027-03-08T10:30", "2027-03-08T11:30", "2027-03-08T08:00")
    )

    run(state, DATA / "commands.jsonl", DATA / "results.jsonl")


def test_auto_assign():
    config = InitialData.model_validate_json((DATA / "initial_data.json").read_text())
    state = AppState(config=config)

    S = reservation.State
    # initial time is Monday 2027-03-08T08:00
    # r1 no-shows at 10:15, freeing YAZ-1
    state.reservations.append(
        seed("r1", "u1", "YAZ-1", "2027-03-08T10:00", "2027-03-08T12:00", S.APPROVED)
    )
    # three waiters for YAZ-1; order is reliability desc, registered_at, id
    add_waiting_entry(
        state, waiting("b1", "u2", "YAZ-1", "2027-03-08T10:30", "2027-03-08T11:00", "2027-03-08T08:00")
    )
    add_waiting_entry(
        state, waiting("b2", "u5", "YAZ-1", "2027-03-08T11:00", "2027-03-08T11:30", "2027-03-08T09:00")
    )
    add_waiting_entry(
        state, waiting("b3", "u3", "YAZ-1", "2027-03-08T11:30", "2027-03-08T12:00", "2027-03-08T10:00")
    )
    # b4 ties b1 on reliability and registration time; the smaller id (b1) must
    # win. b4 itself is invalid (end not on a 15-minute step) and must be skipped.
    add_waiting_entry(
        state, waiting("b4", "u6", "YAZ-1", "2027-03-08T10:30", "2027-03-08T10:50", "2027-03-08T08:00")
    )

    run(state, DATA / "commands_auto_assign.jsonl", DATA / "results_auto_assign.jsonl")
