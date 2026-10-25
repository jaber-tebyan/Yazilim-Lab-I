"""Dialogs for dynamically creating users and resources."""

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QSpinBox,
    QVBoxLayout,
)

from yazilim_lab_project.gui.controller import AppController
from yazilim_lab_project.gui.error_mapper import get_error_desc
from yazilim_lab_project.models.command import AddResourceCommand, AddUserCommand
from yazilim_lab_project.models.results import AddResourceResult, AddUserResult


class AddUserDialog(QDialog):
    def __init__(self, controller: AppController, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.setWindowTitle("Yeni Kullanıcı Ekle")
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.txt_id = QLineEdit()
        self.txt_name = QLineEdit()
        self.combo_role = QComboBox()
        self.spin_balance = QSpinBox()
        self.spin_balance.setRange(0, 10000)
        self.spin_reliability = QSpinBox()
        self.spin_reliability.setRange(0, 100)
        self.spin_reliability.setValue(80)

        # Populate roles from config
        if self.controller.state:
            for role_name in self.controller.state.config.roles.keys():
                self.combo_role.addItem(role_name)

        # Available certificates (collect from all types)
        self.list_certs = QListWidget()
        self.list_certs.setSelectionMode(QListWidget.MultiSelection)
        known_certs = set()
        if self.controller.state:
            for rt in self.controller.state.config.resource_types.values():
                if rt.certificate:
                    known_certs.add(rt.certificate)
        for cert in sorted(known_certs):
            self.list_certs.addItem(cert)

        form.addRow("Kullanıcı ID:", self.txt_id)
        form.addRow("Ad Soyad:", self.txt_name)
        form.addRow("Rol:", self.combo_role)
        form.addRow("Başlangıç Bakiye (KP):", self.spin_balance)
        form.addRow("Güvenilirlik Puanı:", self.spin_reliability)
        form.addRow("Sertifikalar:", self.list_certs)
        layout.addLayout(form)

        btn_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btn_box.accepted.connect(self._on_accept)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)

    def _on_accept(self):
        user_id = self.txt_id.text().strip()
        name = self.txt_name.text().strip()
        role = self.combo_role.currentText()
        balance = self.spin_balance.value()
        reliability = self.spin_reliability.value()
        certs = [item.text() for item in self.list_certs.selectedItems()]

        cmd = AddUserCommand(
            id=user_id,
            ad=name,
            rol=role,
            bakiye=balance,
            guvenilirlik=reliability,
            sertifikalar=certs,
        )
        result = self.controller.execute(cmd, record=True)
        match result:
            case AddUserResult.Ok():
                self.accept()
            case AddUserResult.Red(error_code=code):
                QMessageBox.warning(self, "Hata", f"Kullanıcı Eklenemedi [{code}]: {get_error_desc(code)}")


class AddResourceDialog(QDialog):
    def __init__(self, controller: AppController, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.setWindowTitle("Yeni Kaynak Ekle")
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.txt_id = QLineEdit()
        self.txt_name = QLineEdit()
        self.combo_type = QComboBox()

        if self.controller.state:
            for t_name in self.controller.state.config.resource_types.keys():
                self.combo_type.addItem(t_name)

        self.list_roles = QListWidget()
        self.list_roles.setSelectionMode(QListWidget.MultiSelection)
        if self.controller.state:
            for r_name in self.controller.state.config.roles.keys():
                item = QListWidgetItem(r_name)
                item.setSelected(True)
                self.list_roles.addItem(item)

        form.addRow("Kaynak ID:", self.txt_id)
        form.addRow("Kaynak Adı:", self.txt_name)
        form.addRow("Kaynak Türü:", self.combo_type)
        form.addRow("İzinli Roller:", self.list_roles)
        layout.addLayout(form)

        btn_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btn_box.accepted.connect(self._on_accept)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)

    def _on_accept(self):
        res_id = self.txt_id.text().strip()
        name = self.txt_name.text().strip()
        res_type = self.combo_type.currentText()
        roles = [item.text() for item in self.list_roles.selectedItems()]

        cmd = AddResourceCommand(
            id=res_id,
            ad=name,
            tur=res_type,
            izinli_roller=roles,
        )
        result = self.controller.execute(cmd, record=True)
        match result:
            case AddResourceResult.Ok():
                self.accept()
            case AddResourceResult.Red(error_code=code):
                QMessageBox.warning(self, "Hata", f"Kaynak Eklenemedi [{code}]: {get_error_desc(code)}")
