from pathlib import Path

from pydantic import TypeAdapter

from yazilim_lab_project import APP_STATE, CommandsFile, ResultsFile, assets_folder
from yazilim_lab_project.interface import AddUser
from yazilim_lab_project.models.app_state import AppState
from yazilim_lab_project.models.command import AddUserCommand, AnyCommand
from yazilim_lab_project.models.initial_data import InitialData, User
from yazilim_lab_project.models.results import AddUserResult
from yazilim_lab_project.rules.add_user_rules import all_rules_user_add

DATA = Path(__file__).parent / "data" / "add_user"


def test_rules_on_add_user_command():
    config = InitialData.model_validate_json((DATA / "initial_data.json").read_text())
    state = AppState(config=config)
    commands: list[AddUserCommand] = [
        cmd
        for cmd in CommandsFile().read(DATA / "commands.jsonl")
        if isinstance(cmd, AddUserCommand)
    ]

    results: list[AddUserResult.Any] = [
        res
        for res in ResultsFile().read(DATA / "results.jsonl")
        if isinstance(res, AddUserResult.Variants)
    ]
    for i, cmd in enumerate(commands):
        result = all_rules_user_add(cmd, state)
        result = AddUserResult.new(i + 1, result)
        AddUser(
            state,
            User(
                id=cmd.id,
                name=cmd.name,
                role=cmd.role,
                certificates=cmd.certificates,
                balance=cmd.balance,
                reliability=cmd.reliability,
            ),
        )
        print(result.model_dump_json(by_alias=True))
        assert result == results[i], f"rule {i} failed"
