"""Booking and demand form widget."""

from datetime import datetime, time
from PySide6.QtCore import QDateTime, QTime, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QDateTimeEdit,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from yazilim_lab_project.gui.controller import AppController
from yazilim_lab_project.gui.error_mapper import get_error_desc
from yazilim_lab_project.models.command import (
    PackageCommand,
    PriceCommand,
    ReservationCommand,
    ReservationRequests,
    WaitingCommand,
)
from yazilim_lab_project.models.results import PackageResult, PriceResult, ReservationResult, WaitingResult


class BookingForm(QWidget):
    request_rejected_with_conflict = Signal(dict)  # Emits payload to suggest waitlist

    def __init__(self, controller: AppController, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.package_items: list[dict] = []
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        # Mode Selection
        mode_group = QGroupBox("Talep Türü")
        m_layout = QHBoxLayout(mode_group)
        self.radio_single = QRadioButton("Tekli Rezervasyon")
        self.radio_package = QRadioButton("Paket Rezervasyon (2-4 Kalem)")
        self.radio_single.setChecked(True)
        self.radio_single.toggled.connect(self._on_mode_toggled)
        m_layout.addWidget(self.radio_single)
        m_layout.addWidget(self.radio_package)
        layout.addWidget(mode_group)

        # Form fields
        self.form_group = QGroupBox("Talep Bilgileri")
        f_layout = QVBoxLayout(self.form_group)

        # User and Resource selectors
        row1 = QHBoxLayout()
        self.combo_user = QComboBox()
        self.combo_resource = QComboBox()
        row1.addWidget(QLabel("Kullanıcı:"))
        row1.addWidget(self.combo_user)
        row1.addWidget(QLabel("Kaynak:"))
        row1.addWidget(self.combo_resource)
        f_layout.addLayout(row1)

        # Time selectors
        row2 = QHBoxLayout()
        self.dt_start = QDateTimeEdit(QDateTime.currentDateTime())
        self.dt_start.setDisplayFormat("yyyy-MM-dd HH:mm")
        self.dt_end = QDateTimeEdit(QDateTime.currentDateTime())
        self.dt_end.setDisplayFormat("yyyy-MM-dd HH:mm")
        row2.addWidget(QLabel("Başlangıç:"))
        row2.addWidget(self.dt_start)
        row2.addWidget(QLabel("Bitiş:"))
        row2.addWidget(self.dt_end)
        f_layout.addLayout(row2)

        # Buttons for single booking & price preview
        self.row_btns = QHBoxLayout()
        self.btn_preview_price = QPushButton("Fiyat Önizle")
        self.btn_preview_price.clicked.connect(self._preview_price)
        self.btn_submit = QPushButton("Rezervasyon Yap")
        self.btn_submit.clicked.connect(self._submit_single)
        self.row_btns.addWidget(self.btn_preview_price)
        self.row_btns.addWidget(self.btn_submit)
        f_layout.addLayout(self.row_btns)

        # Package builder section (hidden by default)
        self.package_widget = QWidget()
        p_layout = QVBoxLayout(self.package_widget)
        p_layout.setContentsMargins(0, 0, 0, 0)
        p_btns = QHBoxLayout()
        self.btn_add_item = QPushButton("Kalem Ekle")
        self.btn_add_item.clicked.connect(self._add_package_item)
        self.btn_clear_items = QPushButton("Kalemleri Temizle")
        self.btn_clear_items.clicked.connect(self._clear_package_items)
        self.btn_submit_package = QPushButton("Paketi Gönder")
        self.btn_submit_package.clicked.connect(self._submit_package)
        p_btns.addWidget(self.btn_add_item)
        p_btns.addWidget(self.btn_clear_items)
        p_btns.addWidget(self.btn_submit_package)
        p_layout.addLayout(p_btns)

        self.table_package = QTableWidget()
        self.table_package.setColumnCount(4)
        self.table_package.setHorizontalHeaderLabels(["No", "Kaynak", "Başlangıç", "Bitiş"])
        self.table_package.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        p_layout.addWidget(self.table_package)
        self.package_widget.setVisible(False)
        f_layout.addWidget(self.package_widget)

        layout.addWidget(self.form_group)

        # Result display
        self.lbl_feedback = QLabel("")
        self.lbl_feedback.setWordWrap(True)
        layout.addWidget(self.lbl_feedback)

    def refresh(self):
        state = self.controller.state
        if not state:
            return
        curr_user = self.combo_user.currentText()
        curr_res = self.combo_resource.currentText()

        self.combo_user.blockSignals(True)
        self.combo_user.clear()
        for u in state.config.users:
            self.combo_user.addItem(u.id)
        if curr_user in [u.id for u in state.config.users]:
            self.combo_user.setCurrentText(curr_user)
        self.combo_user.blockSignals(False)

        self.combo_resource.blockSignals(True)
        self.combo_resource.clear()
        for r in state.config.resources:
            self.combo_resource.addItem(r.id)
        if curr_res in [r.id for r in state.config.resources]:
            self.combo_resource.setCurrentText(curr_res)
        self.combo_resource.blockSignals(False)

        # Set default times aligned with state clock
        clock = state.clock
        start_dt = clock.replace(minute=(clock.minute // 15) * 15, second=0, microsecond=0)
        self.dt_start.setDateTime(QDateTime(start_dt))
        self.dt_end.setDateTime(QDateTime(start_dt).addSecs(3600))

    def set_active_user(self, user_id: str):
        idx = self.combo_user.findText(user_id)
        if idx >= 0:
            self.combo_user.setCurrentIndex(idx)

    def _on_mode_toggled(self):
        is_single = self.radio_single.isChecked()
        self.btn_preview_price.setVisible(is_single)
        self.btn_submit.setVisible(is_single)
        self.package_widget.setVisible(not is_single)

    def _preview_price(self):
        user = self.combo_user.currentText()
        resource = self.combo_resource.currentText()
        start = self.dt_start.dateTime().toPython()
        end = self.dt_end.dateTime().toPython()

        cmd = PriceCommand(
            kullanici=user,
            kaynak=resource,
            baslangic=start,
            bitis=end,
        )
        result = self.controller.execute(cmd, record=False)
        match result:
            case PriceResult.Ok(price=price):
                self.lbl_feedback.setStyleSheet("color: green; font-weight: bold;")
                self.lbl_feedback.setText(f"Tahmini Ücret: {price} KP")
            case PriceResult.Red(error_code=code):
                self.lbl_feedback.setStyleSheet("color: red; font-weight: bold;")
                self.lbl_feedback.setText(f"Hata [{code}]: {get_error_desc(code)}")

    def _submit_single(self):
        user = self.combo_user.currentText()
        resource = self.combo_resource.currentText()
        start = self.dt_start.dateTime().toPython()
        end = self.dt_end.dateTime().toPython()

        cmd = ReservationCommand(
            kullanici=user,
            kaynak=resource,
            baslangic=start,
            bitis=end,
        )
        result = self.controller.execute(cmd, record=True)
        match result:
            case ReservationResult.Ok(reservation_id=res_id, price=price, balance=bal):
                self.lbl_feedback.setStyleSheet("color: green; font-weight: bold;")
                self.lbl_feedback.setText(f"Rezervasyon Başarılı! No: {res_id}, Ücret: {price} KP, Yeni Bakiye: {bal} KP")
            case ReservationResult.Red(error_code=code):
                self.lbl_feedback.setStyleSheet("color: red; font-weight: bold;")
                self.lbl_feedback.setText(f"Hata [{code}]: {get_error_desc(code)}")
                if code in ("KESISME", "HAZIRLIK_IHLALI"):
                    self.request_rejected_with_conflict.emit({
                        "user": user,
                        "resource": resource,
                        "start": start,
                        "end": end,
                        "code": code,
                    })

    def _add_package_item(self):
        resource = self.combo_resource.currentText()
        start = self.dt_start.dateTime().toPython()
        end = self.dt_end.dateTime().toPython()

        item = {"resource": resource, "start": start, "end": end}
        self.package_items.append(item)
        self._refresh_package_table()

    def _clear_package_items(self):
        self.package_items.clear()
        self._refresh_package_table()

    def _refresh_package_table(self):
        self.table_package.setRowCount(len(self.package_items))
        for row, itm in enumerate(self.package_items):
            self.table_package.setItem(row, 0, QTableWidgetItem(str(row + 1)))
            self.table_package.setItem(row, 1, QTableWidgetItem(itm["resource"]))
            self.table_package.setItem(row, 2, QTableWidgetItem(itm["start"].strftime("%Y-%m-%d %H:%M")))
            self.table_package.setItem(row, 3, QTableWidgetItem(itm["end"].strftime("%Y-%m-%d %H:%M")))

    def _submit_package(self):
        user = self.combo_user.currentText()
        items = [
            ReservationRequests(kaynak=itm["resource"], baslangic=itm["start"], bitis=itm["end"])
            for itm in self.package_items
        ]
        cmd = PackageCommand(kullanici=user, kalemler=items)
        result = self.controller.execute(cmd, record=True)
        match result:
            case PackageResult.Ok(package_id=p_id, reservations=res_ids, total=tot, balance=bal):
                self.lbl_feedback.setStyleSheet("color: green; font-weight: bold;")
                self.lbl_feedback.setText(f"Paket Onaylandı! Paket: {p_id}, Rezervasyonlar: {res_ids}, Toplam: {tot} KP, Kalan Bakiye: {bal} KP")
                self._clear_package_items()
            case PackageResult.Red(error_code=code, items=sub_items):
                self.lbl_feedback.setStyleSheet("color: red; font-weight: bold;")
                details = f"Paket Reddedildi [{code}]: {get_error_desc(code)}"
                if sub_items:
                    details += "\nKalem Durumları:"
                    for si in sub_items:
                        details += f"\n- Kalem {si.index}: {si.status}" + (f" ({si.code})" if si.code else "")
                self.lbl_feedback.setText(details)
