from pathlib import Path

from pydantic import TypeAdapter

from yazilim_lab_project import APP_STATE, CommandsFile, ResultsFile, assets_folder
from yazilim_lab_project.interface import AddUser
from yazilim_lab_project.models.command import AddUserCommand, AnyCommand
from yazilim_lab_project.models.initial_data import InitialData, User
from yazilim_lab_project.models.results import AddUserResult
from yazilim_lab_project.rules import (
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

    results: list[AddUserResult.Any] = [
        res
        for res in ResultsFile().read(DATA / "results.jsonl")
        if isinstance(res, AddUserResult.Variants)
    ]
    for i, cmd in enumerate(commands):
        result = all_rules_user_add(cmd, app_state)
        if result is None:
            result = AddUserResult.Ok(
                no=i + 1, komut="kullanici_ekle", durum=AddUserResult.Status.OK
            )
        else:
            result = AddUserResult.Red(
                no=i + 1,
                komut="kullanici_ekle",
                durum=AddUserResult.Status.RED,
                kod=result,
            )
        AddUser(
            app_state,
            User(
                id=cmd.id,
                ad=cmd.name,
                rol=cmd.role,
                sertifikalar=cmd.certificates,
                bakiye=cmd.balance,
                guvenilirlik=cmd.reliability,
            ),
        )
        print(result.model_dump_json(by_alias=True))
        assert result == results[i], f"rule {i} failed"
