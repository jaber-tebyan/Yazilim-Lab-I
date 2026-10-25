from pydantic import TypeAdapter
import pathlib

from yazilim_lab_project.models import AnyResult
from yazilim_lab_project.models.app_state import AppState
from yazilim_lab_project.models.initial_data import InitialData
from yazilim_lab_project.models.command import AnyCommand

assets_folder = pathlib.Path(__file__).parent / "assets"
APP_STATE: AppState = AppState(
    config=InitialData.model_validate_json(
        pathlib.Path(assets_folder / "baslangic.json").read_text(encoding="utf-8")
    )
)


def main() -> None:
    # we have jsonl file inside assets folder
    commands_file = CommandsFile()
    commands = commands_file.read(assets_folder / "komutlar_1.jsonl")


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
