from dataclasses import dataclass

from pydantic import TypeAdapter
import pathlib

from yazilim_lab_project.models.initial_data import InitialData
from yazilim_lab_project.models.command import AnyCommand

assets_folder = pathlib.Path(__file__).parent / "assets"


def main() -> None:
    initial_data = InitialData.model_validate_json(
        pathlib.Path(assets_folder / "baslangic.json").read_text()
    )
    # we have jsonl file inside assets folder
    commands_file = CommandsFile()
    commands = commands_file.read(assets_folder / "komutlar_1.jsonl")


class CommandsFile:
    def read(self, path: pathlib.Path) -> list[AnyCommand]:
        commands: list[AnyCommand] = []
        t = TypeAdapter(AnyCommand)
        with open(path) as f:
            for line in f:
                commands.append(t.validate_json(line))
        return commands
