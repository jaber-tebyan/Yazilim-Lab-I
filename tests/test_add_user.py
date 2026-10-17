from yazilim_lab_project import CommandsFile, assets_folder
from yazilim_lab_project.models.command import AnyCommand

# TODO: test rules on kullanici_ekle command


def test_rules_on_kullanici_ekle_command():
    commands = CommandsFile().read(assets_folder / "komutlar_1.jsonl")
    l: list[AnyCommand] = []
    for i in commands:
        if i.command == "kullanici_ekle":
            l.append(i)
