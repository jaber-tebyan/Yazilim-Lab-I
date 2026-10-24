from datetime import datetime
from pathlib import Path

from yazilim_lab_project import CommandsFile, ResultsFile
from yazilim_lab_project.interface.price import get_price
from yazilim_lab_project.models import reservation
from yazilim_lab_project.models.app_state import AppState
from yazilim_lab_project.models.command import PriceCommand
from yazilim_lab_project.models.initial_data import InitialData
from yazilim_lab_project.models.results import PriceResult
from yazilim_lab_project.rules.price_rules import all_rules_price

DATA = Path(__file__).parent / "data" / "price"


def seed(id: str, resource: str, start: str, end: str, st: reservation.State):
    return reservation.Reservation(
        id=id,
        user="u3",
        resource=resource,
        start=datetime.fromisoformat(start),
        end=datetime.fromisoformat(end),
        price=0,
        state=st,
        package=None,
    )


def test_rules_on_price_command():
    config = InitialData.model_validate_json((DATA / "initial_data.json").read_text())
    state = AppState(config=config)
    commands: list[PriceCommand] = [
        cmd
        for cmd in CommandsFile().read(DATA / "commands.jsonl")
        if isinstance(cmd, PriceCommand)
    ]
    results: list[PriceResult.Any] = [
        res
        for res in ResultsFile().read(DATA / "results.jsonl")
        if isinstance(res, PriceResult.Variants)
    ]

    S = reservation.State
    seeds: list[reservation.Reservation] = [
        seed("r1", "ODA-1", "2027-03-09T10:00", "2027-03-09T12:00", S.IN_USE),
        seed("r2", "YAZ-1", "2027-03-10T10:00", "2027-03-10T11:00", S.COMPLETED),
        seed("r3", "ODA-1", "2027-03-10T10:00", "2027-03-10T12:00", S.CANCELLED),
        seed("r4", "ODA-1", "2027-03-10T12:00", "2027-03-10T14:00", S.DID_NOT_ARRIVE),
        seed("r5", "CIH-1", "2027-03-11T08:00", "2027-03-11T10:00", S.APPROVED),
        seed("r6", "ODA-2", "2027-03-12T08:00", "2027-03-12T09:00", S.APPROVED),
        seed("r7", "ODA-2", "2027-03-12T10:00", "2027-03-12T12:00", S.APPROVED),
        seed("r8", "ODA-2", "2027-03-12T12:00", "2027-03-12T14:00", S.APPROVED),
        seed("r9", "ODA-1", "2027-03-12T13:00", "2027-03-12T14:00", S.APPROVED),
        seed("r10", "ODA-2", "2027-03-13T09:00", "2027-03-13T10:30", S.APPROVED),
    ]

    state.reservations.extend(seeds)
    for i, cmd in enumerate(commands):
        rule_error = all_rules_price(cmd, state)
        if rule_error:
            result = PriceResult.Red(no=i + 1, error_code=rule_error)
        else:
            price = get_price(cmd, state)
            result = PriceResult.Ok(no=i + 1, price=price)
        assert result == results[i], f"rule {i} failed"
