"""User panel widget displaying user details, balances, reservations, and waitlist."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from yazilim_lab_project.gui.controller import AppController


class UserPanel(QWidget):
    user_changed = Signal(str)  # Emits selected user ID
    reservation_selected = Signal(str)  # Emits reservation ID

    def __init__(self, controller: AppController, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.selected_user_id: str | None = None
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        # User selector header
        header_group = QGroupBox("Kullanıcı Seçimi")
        h_layout = QHBoxLayout(header_group)
        self.user_combo = QComboBox()
        self.user_combo.currentTextChanged.connect(self._on_user_combo_changed)
        h_layout.addWidget(QLabel("Aktif Üye:"))
        h_layout.addWidget(self.user_combo)
        layout.addWidget(header_group)

        # User stats
        stats_group = QGroupBox("Hesap Durumu")
        s_layout = QHBoxLayout(stats_group)
        self.lbl_role = QLabel("Rol: -")
        self.lbl_balance = QLabel("Bakiye: - KP")
        self.lbl_quota = QLabel("Haftalık Kota: - KP")
        self.lbl_reliability = QLabel("Güvenilirlik: -")
        s_layout.addWidget(self.lbl_role)
        s_layout.addWidget(self.lbl_balance)
        s_layout.addWidget(self.lbl_quota)
        s_layout.addWidget(self.lbl_reliability)
        layout.addWidget(stats_group)

        # Reservations Table
        res_group = QGroupBox("Rezervasyonlar")
        r_layout = QVBoxLayout(res_group)
        self.table_res = QTableWidget()
        self.table_res.setColumnCount(6)
        self.table_res.setHorizontalHeaderLabels(["ID", "Kaynak", "Başlangıç", "Bitiş", "Durum", "Ücret"])
        self.table_res.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_res.itemClicked.connect(self._on_res_clicked)
        r_layout.addWidget(self.table_res)
        layout.addWidget(res_group)

        # Waiting list Table
        wait_group = QGroupBox("Bekleme Kayıtları")
        w_layout = QVBoxLayout(wait_group)
        self.table_wait = QTableWidget()
        self.table_wait.setColumnCount(5)
        self.table_wait.setHorizontalHeaderLabels(["ID", "Kaynak", "Başlangıç", "Bitiş", "Kayıt Saati"])
        self.table_wait.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        w_layout.addWidget(self.table_wait)
        layout.addWidget(wait_group)

    def refresh(self):
        state = self.controller.state
        if not state:
            self.user_combo.clear()
            self._clear_stats()
            return

        current_id = self.user_combo.currentText()
        self.user_combo.blockSignals(True)
        self.user_combo.clear()
        for u in state.config.users:
            self.user_combo.addItem(u.id)

        if current_id in [u.id for u in state.config.users]:
            self.user_combo.setCurrentText(current_id)
        elif state.config.users:
            self.user_combo.setCurrentIndex(0)
        self.user_combo.blockSignals(False)

        self._update_user_details()

    def _clear_stats(self):
        self.lbl_role.setText("Rol: -")
        self.lbl_balance.setText("Bakiye: - KP")
        self.lbl_quota.setText("Haftalık Kota: - KP")
        self.lbl_reliability.setText("Güvenilirlik: -")
        self.table_res.setRowCount(0)
        self.table_wait.setRowCount(0)

    def _on_user_combo_changed(self, user_id: str):
        self.selected_user_id = user_id
        self._update_user_details()
        self.user_changed.emit(user_id)

    def _on_res_clicked(self, item):
        row = item.row()
        res_id_item = self.table_res.item(row, 0)
        if res_id_item:
            self.reservation_selected.emit(res_id_item.text())

    def _update_user_details(self):
        state = self.controller.state
        if not state:
            return
        user_id = self.user_combo.currentText()
        user = next((u for u in state.config.users if u.id == user_id), None)
        if not user:
            self._clear_stats()
            return

        role_cfg = state.config.roles.get(user.role)
        quota = role_cfg.weekly_quota if role_cfg else "-"

        self.lbl_role.setText(f"Rol: {user.role}")
        self.lbl_balance.setText(f"Bakiye: {user.balance} KP")
        self.lbl_quota.setText(f"Haftalık Kota: {quota} KP")
        self.lbl_reliability.setText(f"Güvenilirlik: {user.reliability} / 100")

        # Populate user reservations
        user_reservations = [r for r in state.reservations if r.user == user.id]
        self.table_res.setRowCount(len(user_reservations))
        for row, r in enumerate(user_reservations):
            self.table_res.setItem(row, 0, QTableWidgetItem(r.id))
            self.table_res.setItem(row, 1, QTableWidgetItem(r.resource))
            self.table_res.setItem(row, 2, QTableWidgetItem(r.start.strftime("%Y-%m-%d %H:%M")))
            self.table_res.setItem(row, 3, QTableWidgetItem(r.end.strftime("%Y-%m-%d %H:%M")))
            self.table_res.setItem(row, 4, QTableWidgetItem(str(r.state.value if hasattr(r.state, 'value') else r.state)))
            self.table_res.setItem(row, 5, QTableWidgetItem(f"{r.price} KP"))

        # Populate user waiting list entries
        user_waitings = [w for w in state.waiting_list if w.user == user.id]
        self.table_wait.setRowCount(len(user_waitings))
        for row, w in enumerate(user_waitings):
            self.table_wait.setItem(row, 0, QTableWidgetItem(w.id))
            self.table_wait.setItem(row, 1, QTableWidgetItem(w.resource))
            self.table_wait.setItem(row, 2, QTableWidgetItem(w.start.strftime("%Y-%m-%d %H:%M")))
            self.table_wait.setItem(row, 3, QTableWidgetItem(w.end.strftime("%Y-%m-%d %H:%M")))
            self.table_wait.setItem(row, 4, QTableWidgetItem(w.created_at.strftime("%Y-%m-%d %H:%M")))
