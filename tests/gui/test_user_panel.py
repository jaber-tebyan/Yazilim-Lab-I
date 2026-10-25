import pytest
from pathlib import Path
from PySide6.QtWidgets import QApplication
from yazilim_lab_project.gui.controller import AppController
from yazilim_lab_project.gui.user_panel import UserPanel

@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app

def test_user_panel_display_and_selection(qapp):
    controller = AppController(Path("tests/data/price/initial_data.json"))
    panel = UserPanel(controller)
    panel.refresh()

    assert panel.user_combo.count() > 0
    # Select researcher user u3
    panel.user_combo.setCurrentText("u3")
    assert panel.selected_user_id == "u3"
    assert panel.lbl_role.text() == "Rol: ARASTIRMACI"
    assert "300" in panel.lbl_balance.text()
    assert "300" in panel.lbl_quota.text()
    assert "80 / 100" in panel.lbl_reliability.text()
