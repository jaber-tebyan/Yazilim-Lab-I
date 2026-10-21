from pathlib import Path


from yazilim_lab_project import CommandsFile, ResultsFile
from yazilim_lab_project.interface import AddResource
from yazilim_lab_project.models.app_state import AppState
from yazilim_lab_project.models.command import (
    AddResourceCommand,
)
from yazilim_lab_project.models.initial_data import InitialData, Resource
from yazilim_lab_project.models.results import AddResourceResult
from yazilim_lab_project.rules.add_resource_rules import all_rules_resource_add

DATA = Path(__file__).parent / "data" / "add_resource"


def test_rules_on_add_resource_command():
    config = InitialData.model_validate_json((DATA / "initial_data.json").read_text())
    state = AppState(config=config)
    commands: list[AddResourceCommand] = [
        cmd
        for cmd in CommandsFile().read(DATA / "commands.jsonl")
        if isinstance(cmd, AddResourceCommand)
    ]

    results: list[AddResourceResult.Any] = [
        res
        for res in ResultsFile().read(DATA / "results.jsonl")
        if isinstance(res, AddResourceResult.Variants)
    ]
    for i, cmd in enumerate(commands):
        result = all_rules_resource_add(cmd, state)
        result = AddResourceResult.new(i + 1, result)
        AddResource(
            state,
            Resource(
                id=cmd.id,
                name=cmd.name,
                type=cmd.type,
                allowed_roles=cmd.allowed_roles,
            ),
        )
        print(result.model_dump_json(by_alias=True))
        assert result == results[i], f"rule {i} failed"
