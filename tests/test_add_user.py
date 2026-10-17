import unittest

from yazilim_lab_project import CommandsFile, assets_folder
from yazilim_lab_project.models.command import AnyCommand

# TODO: test rules on kullanici_ekle command


class TestAddUser(unittest.TestCase):

    def test_rules_on_kullanici_ekle_command(self):
        commands = CommandsFile().read(assets_folder / "komutlar_1.jsonl")
        l: list[AnyCommand] = []
        for i in commands:
            if i.command == "kullanici_ekle":
                l.append(i)


if __name__ == "__main__":
    unittest.main()
