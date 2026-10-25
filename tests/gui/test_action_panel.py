import pytest
from datetime import datetime
from pathlib import Path
from PySide6.QtWidgets import QApplication
from yazilim_lab_project.gui.controller import AppController
from yazilim_lab_project.gui.action_panel import ReservationActionPanel
from yazilim_lab_project.models.command import ReservationCommand

@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app

def test_reservation_action_panel(qapp):
    controller = AppController(Path("tests/data/price/initial_data.json"))
    action_panel = ReservationActionPanel(controller)

    # Initial state with no selection
    assert not action_panel.btn_entry.isEnabled()
    assert not action_panel.btn_exit.isEnabled()
    assert not action_panel.btn_cancel.isEnabled()

    # Create a reservation
    res_cmd = ReservationCommand(
        kullanici="u3",
        kaynak="CIH-1",
        baslangic=datetime(2027, 3, 8, 14, 0),
        bitis=datetime(2027, 3, 8, 16, 0),
    )
    res_res = controller.execute(res_cmd, record=True)
    res_id = getattr(res_res, "reservation_id", None)
    assert res_id is not None

    # Select reservation in panel
    action_panel.select_reservation(res_id)
    assert action_panel.active_res_id == res_id
    assert action_panel.btn_entry.isEnabled()
    assert action_panel.btn_exit.isEnabled()
    assert action_panel.btn_cancel.isEnabled()
    assert "CIH-1" in action_panel.lbl_selected.text()
