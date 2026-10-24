from pathlib import Path

from yazilim_lab_project import CommandsFile, ResultsFile
from yazilim_lab_project.models.app_state import AppState
from yazilim_lab_project.models.command import ClockCommand
from yazilim_lab_project.models.generic import Err, Ok
from yazilim_lab_project.models.initial_data import InitialData
from yazilim_lab_project.models.results import ClockResult
from yazilim_lab_project.rules.clock_rules import all_rules_clock

DATA = Path(__file__).parent / "data" / "clock"


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
    for i, cmd in enumerate(commands):
        rule_result = all_rules_clock(cmd, state)
        match rule_result:
            case Err(err):
                result = ClockResult.Red(no=i + 1, error_code=err)
            case Ok(new_time):
                state.config.time = new_time
                result = ClockResult.Ok(
                    no=i + 1,
                    events=[],
                )

        assert result == results[i], f"rule {i} failed"
