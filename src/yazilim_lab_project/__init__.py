from pydantic import BaseModel, RootModel
from datetime import datetime
import pathlib
import json
from .models import InitialData

assets_folder = pathlib.Path(__file__).parent / "assets"


def main() -> None:
    initial_data = InitialData.model_validate_json(
        pathlib.Path(assets_folder / "baslangic.json").read_text()
    )
    print(initial_data)
