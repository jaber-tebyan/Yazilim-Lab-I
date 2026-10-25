"""Session audit log widget."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from yazilim_lab_project.gui.controller import AppController


class AuditLogWidget(QWidget):
    def __init__(self, controller: AppController, parent=None):
        super().__init__(parent)
        self.controller = controller
        self._init_ui()

    def _init_ui(self):
        group = QGroupBox("Olay Günlüğü (Session Audit Log)")
        layout = QVBoxLayout(group)

        splitter = QSplitter(Qt.Vertical)

        # Log Table
        self.table_logs = QTableWidget()
        self.table_logs.setColumnCount(4)
        self.table_logs.setHorizontalHeaderLabels(["No", "Komut", "Durum", "Özet / Kod"])
        self.table_logs.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_logs.itemSelectionChanged.connect(self._on_selection_changed)
        splitter.addWidget(self.table_logs)

        # Detail text areas (Command JSON vs Result JSON)
        detail_widget = QWidget()
        d_layout = QHBoxLayout(detail_widget)
        d_layout.setContentsMargins(0, 0, 0, 0)

        v1 = QVBoxLayout()
        v1.addWidget(QLabel("Komut JSON:"))
        self.txt_cmd = QTextEdit()
        self.txt_cmd.setReadOnly(True)
        v1.addWidget(self.txt_cmd)
        d_layout.addLayout(v1)

        v2 = QVBoxLayout()
        v2.addWidget(QLabel("Sonuç JSON:"))
        self.txt_res = QTextEdit()
        self.txt_res.setReadOnly(True)
        v2.addWidget(self.txt_res)
        d_layout.addLayout(v2)

        splitter.addWidget(detail_widget)
        layout.addWidget(splitter)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(group)

    def refresh(self):
        if not self.controller.engine:
            self.table_logs.setRowCount(0)
            self.txt_cmd.clear()
            self.txt_res.clear()
            return

        history = self.controller.engine.history
        self.table_logs.setRowCount(len(history))
        for row, (cmd, res) in enumerate(history):
            cmd_name = getattr(cmd, "command", type(cmd).__name__)
            status = getattr(res, "status", "-")
            status_val = status.value if hasattr(status, "value") else str(status)
            code = getattr(res, "error_code", "")
            code_str = code.value if hasattr(code, "value") else str(code) if code else "OK"

            self.table_logs.setItem(row, 0, QTableWidgetItem(str(row + 1)))
            self.table_logs.setItem(row, 1, QTableWidgetItem(cmd_name))
            self.table_logs.setItem(row, 2, QTableWidgetItem(status_val))
            self.table_logs.setItem(row, 3, QTableWidgetItem(code_str))

    def _on_selection_changed(self):
        rows = self.table_logs.selectedItems()
        if not rows:
            return
        row = rows[0].row()
        history = self.controller.engine.history if self.controller.engine else []
        if 0 <= row < len(history):
            cmd, res = history[row]
            self.txt_cmd.setText(cmd.model_dump_json(by_alias=True, indent=2))
            self.txt_res.setText(res.model_dump_json(by_alias=True, exclude_none=True, indent=2))
