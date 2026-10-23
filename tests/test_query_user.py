from pathlib import Path

from yazilim_lab_project import CommandsFile, ResultsFile
from yazilim_lab_project.models.app_state import AppState
from yazilim_lab_project.models.command import QueryUserCommand
from yazilim_lab_project.models.generic import Err, Ok
from yazilim_lab_project.models.initial_data import InitialData
from yazilim_lab_project.models.results import QueryResult
from yazilim_lab_project.rules.query_user_rules import all_rules_query_user

DATA = Path(__file__).parent / "data" / "query_user"


def test_rules_on_query_user_command():
    config = InitialData.model_validate_json((DATA / "initial_data.json").read_text())
    state = AppState(config=config)
    commands: list[QueryUserCommand] = [
        cmd
        for cmd in CommandsFile().read(DATA / "commands.jsonl")
        if isinstance(cmd, QueryUserCommand)
    ]
    results: list[QueryResult.Any] = [
        res
        for res in ResultsFile().read(DATA / "results.jsonl")
        if isinstance(res, QueryResult.Variants)
    ]
    for i, cmd in enumerate(commands):
        rule_error = all_rules_query_user(cmd, state)
        match rule_error:
            case Err(err):
                result = QueryResult.Red(no=i + 1, error_code=err)
            case Ok(user_data):
                result = QueryResult.OkUser(
                    no=i + 1,
                    balance=user_data.balance,
                    reliability=user_data.reliability,
                    reservations=user_data.reservations,
                )

        assert result == results[i], f"rule {i} failed"
