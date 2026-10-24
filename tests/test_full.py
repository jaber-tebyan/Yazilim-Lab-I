from pathlib import Path

from yazilim_lab_project import CommandsFile, ResultsFile
from yazilim_lab_project.interface.engine import Engine
from yazilim_lab_project.models.app_state import AppState
from yazilim_lab_project.models.initial_data import InitialData

DATA = Path(__file__).parent / "data" / "full"


def test_full_engine_scenario():
    config = InitialData.model_validate_json((DATA / "initial_data.json").read_text())
    state = AppState(config=config)
    engine = Engine(state)

    commands = CommandsFile().read(DATA / "commands.jsonl")
    expected = ResultsFile().read(DATA / "results.jsonl")

    actual = [engine.execute(command) for command in commands]

    assert actual == expected
