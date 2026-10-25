import pytest
from datetime import datetime
from pathlib import Path
from PySide6.QtWidgets import QApplication
from yazilim_lab_project.gui.controller import AppController
from yazilim_lab_project.gui.audit_log import AuditLogWidget
from yazilim_lab_project.models.command import PriceCommand

@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app

def test_audit_log_widget(qapp):
    controller = AppController(Path("tests/data/price/initial_data.json"))
    audit_widget = AuditLogWidget(controller)

    # Execute a command through controller
    cmd = PriceCommand(
        kullanici="u3",
        kaynak="CIH-1",
        baslangic=datetime(2027, 3, 8, 14, 0),
        bitis=datetime(2027, 3, 8, 16, 0),
    )
    controller.execute(cmd, record=True)

    audit_widget.refresh()
    assert audit_widget.table_logs.rowCount() == 1
    assert audit_widget.table_logs.item(0, 1).text() in ["PriceCommand", "fiyat"]

    # Select the first row to view formatted JSON in detail textboxes
    audit_widget.table_logs.selectRow(0)
    assert len(audit_widget.txt_cmd.toPlainText()) > 0
    assert len(audit_widget.txt_res.toPlainText()) > 0
    assert '"komut": "fiyat"' in audit_widget.txt_cmd.toPlainText() or '"kullanici": "u3"' in audit_widget.txt_cmd.toPlainText()
