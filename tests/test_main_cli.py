import json
from pathlib import Path

from yazilim_lab_project import CommandsFile
from yazilim_lab_project.interface.engine import Engine
from yazilim_lab_project.models.app_state import AppState
from yazilim_lab_project.models.initial_data import InitialData

ASSETS = Path(__file__).parent.parent / "src" / "yazilim_lab_project" / "assets"


def test_main_execution_against_sonuclar_1():
    # 1. Load initial data and state
    config = InitialData.model_validate_json(
        (ASSETS / "baslangic_1.json").read_text(encoding="utf-8")
    )
    state = AppState(config=config)
    engine = Engine(state)

    # 2. Read commands using CommandsFile
    commands = CommandsFile().read(ASSETS / "komutlar_1.jsonl")

    # 3. Execute each command through engine and serialize like main() does
    actual_lines = [
        engine.execute(cmd).model_dump_json(by_alias=True, exclude_none=True)
        for cmd in commands
    ]

    # 4. Read expected sonuclar_1.jsonl without overwriting
    expected_raw_lines = [
        line.strip()
        for line in (ASSETS / "sonuclar_1.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("//")
    ]

    assert len(actual_lines) == len(expected_raw_lines)

    # 5. Assert line by line (comparing parsed json dicts so key ordering doesn't falsely fail)
    for i, (actual, expected) in enumerate(zip(actual_lines, expected_raw_lines)):
        actual_dict = json.loads(actual)
        expected_dict = json.loads(expected)
        assert actual_dict == expected_dict, f"Line {i + 1} mismatch: {actual_dict} != {expected_dict}"
