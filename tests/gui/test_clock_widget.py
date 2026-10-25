import pytest
from datetime import datetime
from pathlib import Path
from PySide6.QtCore import QDateTime
from PySide6.QtWidgets import QApplication
from yazilim_lab_project.gui.controller import AppController
from yazilim_lab_project.gui.clock_widget import ClockControlWidget

@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app

def test_clock_widget_advancement(qapp):
    controller = AppController(Path("tests/data/price/initial_data.json"))
    widget = ClockControlWidget(controller)
    widget.refresh()

    assert "2027-03-08 08:00" in widget.lbl_clock.text()

    # Advance clock to 11:20
    target_dt = datetime(2027, 3, 8, 11, 20)
    widget.dt_target.setDateTime(QDateTime(target_dt))
    widget._advance_time()

    assert "2027-03-08 11:20" in widget.lbl_clock.text()
