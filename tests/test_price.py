from pathlib import Path

from yazilim_lab_project import CommandsFile, ResultsFile
from yazilim_lab_project.interface.price import get_price
from yazilim_lab_project.models.command import PriceCommand
from yazilim_lab_project.models.initial_data import InitialData
from yazilim_lab_project.models.results import PriceResult
from yazilim_lab_project.rules.price_rules import all_rules_price

DATA = Path(__file__).parent / "data" / "price"


def test_rules_on_kullanici_ekle_command():
    app_state = InitialData.model_validate_json(
        (DATA / "initial_data.json").read_text()
    )
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
    for i, cmd in enumerate(commands):
        rule_error = all_rules_price(cmd, app_state)
        if rule_error:
            result = PriceResult.Red(no=i + 1, error_code=rule_error)
        else:
            price = get_price(cmd, app_state)
            result = PriceResult.Ok(no=i + 1, price=price)
        assert result == results[i], f"rule {i} failed"
