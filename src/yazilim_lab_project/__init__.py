from pydantic import TypeAdapter
import pathlib

from yazilim_lab_project.models.initial_data import InitialData
from yazilim_lab_project.models.command import AnyCommand

assets_folder = pathlib.Path(__file__).parent / "assets"


def main() -> None:
    initial_data = InitialData.model_validate_json(
        pathlib.Path(assets_folder / "baslangic.json").read_text()
    )
    print(initial_data)
    # we have jsonl file inside assets folder
    with open(assets_folder / "komutlar_1.jsonl") as f:
        t = TypeAdapter(AnyCommand)
        for line in f:
            o = t.validate_json(line)
            print(o)
