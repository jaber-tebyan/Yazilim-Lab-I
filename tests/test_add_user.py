from pydantic import TypeAdapter

from yazilim_lab_project import APP_STATE, CommandsFile, assets_folder
from yazilim_lab_project.models.command import AddUserCommand, AnyCommand
from yazilim_lab_project.models.initial_data import InitialData
from yazilim_lab_project.rules import (
    AddUserErrors,
    all_rules_user_add,
    rule_user_add_id_exist,
)

# TODO: test rules on kullanici_ekle command


def test_rules_on_kullanici_ekle_command():
    test_start = {
        "saat": "2027-03-08T08:00",
        "kaynak_turleri": {},
        "roller": {
            "OGRENCI": {"haftalik_kota": 120, "ileri_gun": 7, "azami_sure_dk": 180},
            "ARASTIRMACI": {
                "haftalik_kota": 300,
                "ileri_gun": 14,
                "azami_sure_dk": 480,
            },
            "TEKNISYEN": {"haftalik_kota": 600, "ileri_gun": 30, "azami_sure_dk": 840},
        },
        "kaynaklar": [],
        "bakim_pencereleri": [],
        "kullanicilar": [
            {
                "id": "u3",
                "ad": "Elif Sahin",
                "rol": "ARASTIRMACI",
                "sertifikalar": [],
                "bakiye": 300,
                "guvenilirlik": 80,
            }
        ],
    }

    app_state = InitialData.model_validate(test_start)  # dict -> model
    test_commands = """{"komut":"kullanici_ekle","id":"u1","ad":"Ayse","rol":"OGRENCI","sertifikalar":["LAB_GUVENLIK"],"bakiye":120,"guvenilirlik":0}
{"komut":"kullanici_ekle","id":"u2","ad":"Ali","rol":"ARASTIRMACI","sertifikalar":[],"bakiye":300,"guvenilirlik":100}
{"komut":"kullanici_ekle","id":"u4","ad":"Veli","rol":"TEKNISYEN","sertifikalar":[],"bakiye":0,"guvenilirlik":40}
{"komut":"kullanici_ekle","id":"u1","ad":"Kopya","rol":"OGRENCI","sertifikalar":[],"bakiye":120,"guvenilirlik":80}
{"komut":"kullanici_ekle","id":"u3","ad":"Kopya Start","rol":"OGRENCI","sertifikalar":[],"bakiye":120,"guvenilirlik":80}
{"komut":"kullanici_ekle","id":"u5","ad":"Hale","rol":"PROFESOR","sertifikalar":[],"bakiye":120,"guvenilirlik":80}
{"komut":"kullanici_ekle","id":"u6","ad":"Irem","rol":"ogrenci","sertifikalar":[],"bakiye":120,"guvenilirlik":80}
{"komut":"kullanici_ekle","id":"u7","ad":"Jale","rol":"OGRENCI","sertifikalar":[],"bakiye":121,"guvenilirlik":80}
{"komut":"kullanici_ekle","id":"u8","ad":"Kemal","rol":"OGRENCI","sertifikalar":[],"bakiye":-1,"guvenilirlik":80}
{"komut":"kullanici_ekle","id":"u9","ad":"Mert","rol":"OGRENCI","sertifikalar":[],"bakiye":120,"guvenilirlik":101}
{"komut":"kullanici_ekle","id":"u10","ad":"Naz","rol":"OGRENCI","sertifikalar":[],"bakiye":120,"guvenilirlik":-1}
{"komut":"kullanici_ekle","id":"u1","ad":"Kopya 2","rol":"PROFESOR","sertifikalar":[],"bakiye":120,"guvenilirlik":80}
{"komut":"kullanici_ekle","id":"u13","ad":"Rana","rol":"PROFESOR","sertifikalar":[],"bakiye":99999,"guvenilirlik":80}
{"komut":"kullanici_ekle","id":"u1","ad":"Kopya 3","rol":"OGRENCI","sertifikalar":[],"bakiye":-5,"guvenilirlik":80}
{"komut":"kullanici_ekle","id":"u7","ad":"Jale","rol":"OGRENCI","sertifikalar":[],"bakiye":120,"guvenilirlik":80} """
    results = [
        AddUserErrors.OK,
        AddUserErrors.OK,
        AddUserErrors.OK,
        AddUserErrors.OK,  # 4: u1 was not saved, so no duplicate
        AddUserErrors.ID_EXISTS,  # 5: u3 from the start state
        AddUserErrors.UNDEFINED_VALUE,
        AddUserErrors.UNDEFINED_VALUE,
        AddUserErrors.INVALID_VALUE,
        AddUserErrors.INVALID_VALUE,
        AddUserErrors.INVALID_VALUE,
        AddUserErrors.INVALID_VALUE,
        AddUserErrors.UNDEFINED_VALUE,  # 14
        AddUserErrors.UNDEFINED_VALUE,  # 15
        AddUserErrors.INVALID_VALUE,  # 16
        AddUserErrors.OK,
    ]
    app_state = InitialData.model_validate(test_start)
    commands: list[AddUserCommand] = []
    type_adapter = TypeAdapter(AnyCommand)
    for line in test_commands.split("\n"):
        command = type_adapter.validate_json(line)
        if isinstance(command, AddUserCommand):
            commands.append(command)
    for i, cmd in enumerate(commands):
        result = all_rules_user_add(cmd, app_state)
        assert result == results[i], f"rule {i} failed"
        # do three rules and get their results in true or false
