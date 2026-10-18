from pathlib import Path

from pydantic import TypeAdapter

from yazilim_lab_project import APP_STATE, CommandsFile, assets_folder
from yazilim_lab_project.models.command import AddUserCommand, AnyCommand
from yazilim_lab_project.models.initial_data import InitialData
from yazilim_lab_project.rules import (
    AddUserErrors,
    all_rules_user_add,
    rule_user_add_id_exist,
)

DATA = Path(__file__).parent / "data" / "add_user"


def test_rules_on_kullanici_ekle_command():
    app_state = InitialData.model_validate_json(
        (DATA / "initial_data.json").read_text()
    )
    commands: list[AddUserCommand] = [
        cmd
        for cmd in CommandsFile().read(DATA / "commands.jsonl")
        if isinstance(cmd, AddUserCommand)
    ]
    results = [
        AddUserErrors.OK,
        AddUserErrors.OK,
        AddUserErrors.OK,
        AddUserErrors.OK,  # 4: u1 was not saved, so no duplicate
        AddUserErrors.ID_EXISTS,  # 5: u3 from the start state
        AddUserErrors.UNDEFINED_VALUE,
        AddUserErrors.UNDEFINED_VALUE,
        AddUserErrors.INVALID_VALUE,
        AddUserErrors.INVALID_VALUE,
        AddUserErrors.INVALID_VALUE,
        AddUserErrors.INVALID_VALUE,
        AddUserErrors.UNDEFINED_VALUE,  # 14
        AddUserErrors.UNDEFINED_VALUE,  # 15
        AddUserErrors.INVALID_VALUE,  # 16
        AddUserErrors.OK,
    ]
    for i, cmd in enumerate(commands):
        result = all_rules_user_add(cmd, app_state)
        assert result == results[i], f"rule {i} failed"
        # do three rules and get their results in true or false
