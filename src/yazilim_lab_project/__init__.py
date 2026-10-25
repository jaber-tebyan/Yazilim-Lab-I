import argparse
import pathlib
import sys
from pydantic import TypeAdapter

from yazilim_lab_project.interface.engine import Engine
from yazilim_lab_project.models import AnyResult
from yazilim_lab_project.models.app_state import AppState
from yazilim_lab_project.models.command import AnyCommand
from yazilim_lab_project.models.initial_data import InitialData


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Campus Resource Reservation System")
    parser.add_argument(
        "initial_data", type=pathlib.Path, help="Path to initial data JSON file"
    )
    parser.add_argument(
        "commands", type=pathlib.Path, help="Path to commands JSONL file"
    )
    args = parser.parse_args(argv)

    config = InitialData.model_validate_json(
        args.initial_data.read_text(encoding="utf-8")
    )
    state = AppState(config=config)
    engine = Engine(state)

    commands = CommandsFile().read(args.commands)
    for cmd in commands:
        result = engine.execute(cmd)
        print(result.model_dump_json(by_alias=True, exclude_none=True))


class CommandsFile:
    def read(self, path: pathlib.Path) -> list[AnyCommand]:
        commands: list[AnyCommand] = []
        t = TypeAdapter(AnyCommand)
        with open(path, encoding="utf-8") as f:
            for line in f:
                stripped = line.strip()
                if not stripped or stripped.startswith("//"):
                    continue
                commands.append(t.validate_json(stripped))
        return commands


class ResultsFile:
    def read(self, path: pathlib.Path) -> list[AnyResult]:
        commands: list[AnyResult] = []
        t = TypeAdapter(AnyResult)
        with open(path, encoding="utf-8") as f:
            for line in f:
                stripped = line.strip()
                if not stripped or stripped.startswith("//"):
                    continue
                commands.append(t.validate_json(stripped))
        return commands
