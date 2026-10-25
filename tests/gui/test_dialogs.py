import pytest
from pathlib import Path
from PySide6.QtWidgets import QApplication
from yazilim_lab_project.gui.controller import AppController
from yazilim_lab_project.gui.dialogs import AddUserDialog, AddResourceDialog

@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app

def test_add_user_dialog(qapp):
    controller = AppController(Path("tests/data/price/initial_data.json"))
    dialog = AddUserDialog(controller)
    assert dialog.combo_role.count() > 0

    dialog.txt_id.setText("u_new")
    dialog.txt_name.setText("Test Student")
    dialog.combo_role.setCurrentText("OGRENCI")
    dialog.spin_balance.setValue(100)
    dialog.spin_reliability.setValue(90)
    
    dialog._on_accept()
    # Verify user was added to state
    user_ids = [u.id for u in controller.state.config.users]
    assert "u_new" in user_ids

def test_add_resource_dialog(qapp):
    controller = AppController(Path("tests/data/price/initial_data.json"))
    dialog = AddResourceDialog(controller)
    assert dialog.combo_type.count() > 0

    dialog.txt_id.setText("RES_NEW")
    dialog.txt_name.setText("New Lab Equipment")
    dialog.combo_type.setCurrentText("LAB")
    
    # Select allowed roles
    for i in range(dialog.list_roles.count()):
        dialog.list_roles.item(i).setSelected(True)
        
    dialog._on_accept()
    # Verify resource was added to state
    res_ids = [r.id for r in controller.state.config.resources]
    assert "RES_NEW" in res_ids
