from pathlib import Path

from yazilim_lab_project import CommandsFile, ResultsFile
from yazilim_lab_project.interface import get_user
from yazilim_lab_project.interface.reservation import generate_reservation_id
from yazilim_lab_project.models import reservation
from yazilim_lab_project.models.app_state import AppState
from yazilim_lab_project.models.command import PackageCommand
from yazilim_lab_project.models.generic import Err, Ok
from yazilim_lab_project.models.initial_data import InitialData
from yazilim_lab_project.models.reservation import Reservation
from yazilim_lab_project.models.results import PackageResult
from yazilim_lab_project.rules.package_rules import all_rules_package

DATA = Path(__file__).parent / "data" / "package"


def test_rules_on_package_command():
    config = InitialData.model_validate_json((DATA / "initial_data.json").read_text())
    state = AppState(config=config)

    commands: list[PackageCommand] = [
        cmd
        for cmd in CommandsFile().read(DATA / "commands.jsonl")
        if isinstance(cmd, PackageCommand)
    ]

    results: list[PackageResult.Any] = [
        res
        for res in ResultsFile().read(DATA / "results.jsonl")
        if isinstance(res, PackageResult.Variants)
    ]

    package_count = 0

    for i, cmd in enumerate(commands):
        rule_result = all_rules_package(cmd, state)

        match rule_result:
            case Err((err_code, items)):
                result = PackageResult.Red(
                    no=i + 1,
                    error_code=err_code,
                    items=items,
                )
            case Ok((prices, total_price)):
                user = get_user(state, cmd.user)
                user.balance -= total_price

                package_count += 1
                package_id = f"p{package_count}"
                created_reservations: list[str] = []

                for item_idx, item in enumerate(cmd.items):
                    res_id = generate_reservation_id(state)
                    reser = Reservation(
                        id=res_id,
                        user=cmd.user,
                        resource=item.resource,
                        start=item.start,
                        end=item.end,
                        price=prices[item_idx],
                        state=reservation.State.APPROVED,
                        package=package_id,
                    )
                    state.reservations.append(reser)
                    created_reservations.append(res_id)

                result = PackageResult.Ok(
                    no=i + 1,
                    package_id=package_id,
                    reservations=created_reservations,
                    prices=prices,
                    total=total_price,
                    balance=user.balance,
                )

        assert result == results[i], f"rule {i} failed"
