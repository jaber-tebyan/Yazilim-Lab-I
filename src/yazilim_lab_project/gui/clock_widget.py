"""Simulated clock controls widget."""

from datetime import datetime
from PySide6.QtCore import QDateTime, Signal
from PySide6.QtWidgets import (
    QDateTimeEdit,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from yazilim_lab_project.gui.controller import AppController
from yazilim_lab_project.gui.error_mapper import get_error_desc
from yazilim_lab_project.models.command import ClockCommand
from yazilim_lab_project.models.results import ClockResult


class ClockControlWidget(QWidget):
    time_advanced = Signal()

    def __init__(self, controller: AppController, parent=None):
        super().__init__(parent)
        self.controller = controller
        self._init_ui()

    def _init_ui(self):
        group = QGroupBox("Simüle Saat Denetimi")
        layout = QVBoxLayout(group)

        # Clock display
        top_row = QHBoxLayout()
        self.lbl_clock = QLabel("Mevcut Saat: -")
        self.lbl_clock.setStyleSheet("font-size: 14px; font-weight: bold; color: #2c3e50;")
        top_row.addWidget(self.lbl_clock)

        self.dt_target = QDateTimeEdit(QDateTime.currentDateTime())
        self.dt_target.setDisplayFormat("yyyy-MM-dd HH:mm")
        self.btn_advance = QPushButton("Saati İlerlet")
        self.btn_advance.clicked.connect(self._advance_time)

        top_row.addWidget(QLabel("Hedef Saat:"))
        top_row.addWidget(self.dt_target)
        top_row.addWidget(self.btn_advance)
        layout.addLayout(top_row)

        # Event list table
        self.table_events = QTableWidget()
        self.table_events.setColumnCount(4)
        self.table_events.setHorizontalHeaderLabels(["Zaman", "Olay Türü", "Rezervasyon / Bekleme", "Detay"])
        self.table_events.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table_events)

        self.lbl_error = QLabel("")
        self.lbl_error.setStyleSheet("color: red; font-weight: bold;")
        layout.addWidget(self.lbl_error)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(group)

    def refresh(self):
        state = self.controller.state
        if not state:
            self.lbl_clock.setText("Mevcut Saat: -")
            return
        curr = state.clock
        self.lbl_clock.setText(f"Mevcut Saat: {curr.strftime('%Y-%m-%d %H:%M')}")
        self.dt_target.setDateTime(QDateTime(curr).addSecs(3600))

    def _advance_time(self):
        target = self.dt_target.dateTime().toPython()
        cmd = ClockCommand(zaman=target)
        result = self.controller.execute(cmd, record=True)
        match result:
            case ClockResult.Ok(events=events):
                self.lbl_error.setText("")
                self.table_events.setRowCount(len(events))
                for row, evt in enumerate(events):
                    time_str = evt.time.strftime("%Y-%m-%d %H:%M") if hasattr(evt, 'time') and evt.time else "-"
                    evt_type = evt.type.value if hasattr(evt.type, 'value') else str(evt.type)
                    target_id = getattr(evt, 'reservation', None) or getattr(evt, 'waiting', None) or "-"
                    
                    details = []
                    if hasattr(evt, 'user') and evt.user:
                        details.append(f"Kullanıcı: {evt.user}")
                    if hasattr(evt, 'reliability') and evt.reliability is not None:
                        details.append(f"Güvenilirlik: {evt.reliability}")
                    if hasattr(evt, 'price') and evt.price is not None:
                        details.append(f"Ücret: {evt.price} KP")
                    if hasattr(evt, 'balance') and evt.balance is not None:
                        details.append(f"Bakiye: {evt.balance} KP")
                    detail_str = ", ".join(details)

                    self.table_events.setItem(row, 0, QTableWidgetItem(time_str))
                    self.table_events.setItem(row, 1, QTableWidgetItem(evt_type))
                    self.table_events.setItem(row, 2, QTableWidgetItem(str(target_id)))
                    self.table_events.setItem(row, 3, QTableWidgetItem(detail_str))
                self.time_advanced.emit()
            case ClockResult.Red(error_code=code):
                self.lbl_error.setText(f"Hata [{code}]: {get_error_desc(code)}")
