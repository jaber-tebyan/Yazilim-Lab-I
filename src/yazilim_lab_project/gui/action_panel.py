"""Reservation actions widget (check-in, check-out, cancel)."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from yazilim_lab_project.gui.controller import AppController
from yazilim_lab_project.gui.error_mapper import get_error_desc
from yazilim_lab_project.gui.logger import log_gui_action
from yazilim_lab_project.models.command import CancelCommand, EntryCommand, ExitCommand
from yazilim_lab_project.models.results import CancelResult, EntryResult, ExitResult


class ReservationActionPanel(QWidget):
    def __init__(self, controller: AppController, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.active_res_id: str | None = None
        self._init_ui()

    def _init_ui(self):
        group = QGroupBox("Seçili Rezervasyon Eylemleri")
        layout = QVBoxLayout(group)

        self.lbl_selected = QLabel("Seçili Rezervasyon: Yok")
        self.lbl_selected.setStyleSheet("font-weight: bold;")
        layout.addWidget(self.lbl_selected)

        btn_layout = QHBoxLayout()
        self.btn_entry = QPushButton("Giriş Yap (giris)")
        self.btn_entry.clicked.connect(self._do_entry)
        self.btn_exit = QPushButton("Çıkış Yap (cikis)")
        self.btn_exit.clicked.connect(self._do_exit)
        self.btn_cancel = QPushButton("İptal Et (iptal)")
        self.btn_cancel.clicked.connect(self._do_cancel)

        btn_layout.addWidget(self.btn_entry)
        btn_layout.addWidget(self.btn_exit)
        btn_layout.addWidget(self.btn_cancel)
        layout.addLayout(btn_layout)

        self.lbl_result = QLabel("")
        self.lbl_result.setWordWrap(True)
        layout.addWidget(self.lbl_result)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(group)
        self._set_buttons_enabled(False)

    def select_reservation(self, res_id: str):
        self.active_res_id = res_id
        state = self.controller.state
        if not state:
            return
        res = next((r for r in state.reservations if r.id == res_id), None)
        if not res:
            self.lbl_selected.setText(f"Seçili Rezervasyon: {res_id} (Bulunamadı)")
            self._set_buttons_enabled(False)
            return

        status_str = res.state.value if hasattr(res.state, "value") else str(res.state)
        self.lbl_selected.setText(
            f"Seçili: {res.id} | Kullanıcı: {res.user} | Kaynak: {res.resource} | Durum: {status_str} | Ücret: {res.price} KP"
        )
        self._set_buttons_enabled(True)
        self.lbl_result.setText("")

    def _set_buttons_enabled(self, enabled: bool):
        self.btn_entry.setEnabled(enabled)
        self.btn_exit.setEnabled(enabled)
        self.btn_cancel.setEnabled(enabled)

    def _do_entry(self):
        if not self.active_res_id:
            return
        log_gui_action("click_entry_reservation", reservation=self.active_res_id)
        cmd = EntryCommand(rezervasyon=self.active_res_id)
        result = self.controller.execute(cmd, record=True)
        match result:
            case EntryResult.Ok(new_status=st):
                self.lbl_result.setStyleSheet("color: green; font-weight: bold;")
                self.lbl_result.setText(f"Giriş Başarılı! Yeni Durum: {st}")
            case EntryResult.Red(error_code=code):
                self.lbl_result.setStyleSheet("color: red; font-weight: bold;")
                self.lbl_result.setText(f"Giriş Reddedildi [{code}]: {get_error_desc(code)}")
        self.select_reservation(self.active_res_id)

    def _do_exit(self):
        if not self.active_res_id:
            return
        log_gui_action("click_exit_reservation", reservation=self.active_res_id)
        cmd = ExitCommand(rezervasyon=self.active_res_id)
        result = self.controller.execute(cmd, record=True)
        match result:
            case ExitResult.Ok(new_status=st, reliability=rel, events=evts):
                self.lbl_result.setStyleSheet("color: green; font-weight: bold;")
                msg = f"Çıkış Yapıldı! Yeni Durum: {st}, Güncel Güvenilirlik: {rel}"
                if evts:
                    msg += f"\nOtomatik Atanan Bekleyenler: {len(evts)}"
                self.lbl_result.setText(msg)
            case ExitResult.Red(error_code=code):
                self.lbl_result.setStyleSheet("color: red; font-weight: bold;")
                self.lbl_result.setText(f"Çıkış Reddedildi [{code}]: {get_error_desc(code)}")
        self.select_reservation(self.active_res_id)

    def _do_cancel(self):
        if not self.active_res_id:
            return
        log_gui_action("click_cancel_reservation", reservation=self.active_res_id)
        cmd = CancelCommand(rezervasyon=self.active_res_id)
        result = self.controller.execute(cmd, record=True)
        match result:
            case CancelResult.Ok(refund=ref, balance=bal, reliability=rel, events=evts):
                self.lbl_result.setStyleSheet("color: green; font-weight: bold;")
                msg = f"İptal Başarılı! İade: {ref} KP, Yeni Bakiye: {bal} KP, Güvenilirlik: {rel}"
                if evts:
                    msg += f"\nOtomatik Atanan Bekleyenler: {len(evts)}"
                self.lbl_result.setText(msg)
            case CancelResult.Red(error_code=code):
                self.lbl_result.setStyleSheet("color: red; font-weight: bold;")
                self.lbl_result.setText(f"İptal Reddedildi [{code}]: {get_error_desc(code)}")
        self.select_reservation(self.active_res_id)
