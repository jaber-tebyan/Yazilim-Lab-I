from pathlib import Path

from yazilim_lab_project import CommandsFile, ResultsFile
from yazilim_lab_project.models.app_state import AppState
from yazilim_lab_project.models.command import QueryResourceCommand
from yazilim_lab_project.models.generic import Err, Ok
from yazilim_lab_project.models.initial_data import InitialData
from yazilim_lab_project.models.results import QueryResult
from yazilim_lab_project.rules.query_resource_rules import all_rules_query_resource

DATA = Path(__file__).parent / "data" / "query_resource"


def test_rules_on_query_resource_command():
    config = InitialData.model_validate_json((DATA / "initial_data.json").read_text())
    state = AppState(config=config)
    commands: list[QueryResourceCommand] = [
        cmd
        for cmd in CommandsFile().read(DATA / "commands.jsonl")
        if isinstance(cmd, QueryResourceCommand)
    ]
    results: list[QueryResult.Any] = [
        res
        for res in ResultsFile().read(DATA / "results.jsonl")
        if isinstance(res, QueryResult.Variants)
    ]
    for i, cmd in enumerate(commands):
        rule_result = all_rules_query_resource(cmd, state)
        match rule_result:
            case Err(err):
                result = QueryResult.Red(no=i + 1, error_code=err)
            case Ok(occupancy_rows):
                result = QueryResult.OkResource(
                    no=i + 1,
                    occupancy=occupancy_rows,
                )

        assert result == results[i], f"rule {i} failed"
