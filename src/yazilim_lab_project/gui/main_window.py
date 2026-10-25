"""Main application window uniting all GUI modules."""

from datetime import date
from pathlib import Path
from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import (
    QDateEdit,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSplitter,
    QTabWidget,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from yazilim_lab_project.gui.action_panel import ReservationActionPanel
from yazilim_lab_project.gui.audit_log import AuditLogWidget
from yazilim_lab_project.gui.booking_form import BookingForm
from yazilim_lab_project.gui.calendar_view import CalendarCanvas
from yazilim_lab_project.gui.clock_widget import ClockControlWidget
from yazilim_lab_project.gui.controller import AppController
from yazilim_lab_project.gui.dialogs import AddResourceDialog, AddUserDialog
from yazilim_lab_project.gui.error_mapper import get_error_desc
from yazilim_lab_project.gui.user_panel import UserPanel
from yazilim_lab_project.models.command import WaitingCommand
from yazilim_lab_project.models.results import WaitingResult


class MainWindow(QMainWindow):
    def __init__(self, initial_data_path: Path | None = None):
        super().__init__()
        self.setWindowTitle("Kampüs Kaynak Rezervasyon Sistemi")
        self.resize(1300, 850)

        self.controller = AppController(initial_data_path)
        self.controller.subscribe(self._on_state_updated)

        self._init_ui()
        if initial_data_path:
            self._on_state_updated()

    def _init_ui(self):
        # Toolbar
        toolbar = QToolBar("Ana Araç Çubuğu")
        self.addToolBar(toolbar)

        btn_load = QPushButton("Başlangıç Dosyası Seç")
        btn_load.clicked.connect(self._choose_initial_data)
        toolbar.addWidget(btn_load)
        toolbar.addSeparator()

        btn_add_user = QPushButton("Yeni Üye Ekle")
        btn_add_user.clicked.connect(self._open_add_user)
        toolbar.addWidget(btn_add_user)

        btn_add_res = QPushButton("Yeni Kaynak Ekle")
        btn_add_res.clicked.connect(self._open_add_resource)
        toolbar.addWidget(btn_add_res)
        toolbar.addSeparator()

        # Date switcher for calendar
        toolbar.addWidget(QLabel("Takvim Günü:"))
        self.date_picker = QDateEdit(QDate.currentDate())
        self.date_picker.setDisplayFormat("yyyy-MM-dd")
        self.date_picker.dateChanged.connect(self._on_date_changed)
        toolbar.addWidget(self.date_picker)

        # Central Layout with Splitters
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        main_splitter = QSplitter(Qt.Horizontal)

        # Left / Center Area: Calendar & Clock
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        # Calendar inside ScrollArea
        self.calendar_scroll = QScrollArea()
        self.calendar_scroll.setWidgetResizable(True)
        self.calendar_canvas = CalendarCanvas(self.controller)
        self.calendar_canvas.reservation_selected.connect(self._on_reservation_selected)
        self.calendar_scroll.setWidget(self.calendar_canvas)
        left_layout.addWidget(self.calendar_scroll, stretch=3)

        # Clock Controls
        self.clock_widget = ClockControlWidget(self.controller)
        left_layout.addWidget(self.clock_widget, stretch=1)

        main_splitter.addWidget(left_widget)

        # Right Area: Tabs (Booking/Actions, User Panel, Audit Log)
        self.tabs = QTabWidget()

        # Tab 1: Bookings & Actions
        tab_booking = QWidget()
        b_layout = QVBoxLayout(tab_booking)
        self.booking_form = BookingForm(self.controller)
        self.booking_form.request_rejected_with_conflict.connect(self._prompt_auto_waitlist)
        b_layout.addWidget(self.booking_form)

        self.action_panel = ReservationActionPanel(self.controller)
        b_layout.addWidget(self.action_panel)
        self.tabs.addTab(tab_booking, "Talep & Eylemler")

        # Tab 2: User Panel
        self.user_panel = UserPanel(self.controller)
        self.user_panel.user_changed.connect(self.booking_form.set_active_user)
        self.user_panel.reservation_selected.connect(self._on_reservation_selected)
        self.tabs.addTab(self.user_panel, "Kullanıcı Paneli")

        # Tab 3: Session Audit Log
        self.audit_log = AuditLogWidget(self.controller)
        self.tabs.addTab(self.audit_log, "Olay Günlüğü")

        main_splitter.addWidget(self.tabs)
        main_splitter.setSizes([750, 550])
        main_layout.addWidget(main_splitter)

    def _choose_initial_data(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Başlangıç Dosyası Seç", "", "JSON Files (*.json)"
        )
        if file_path:
            try:
                self.controller.load_initial_data(Path(file_path))
                QMessageBox.information(self, "Başarılı", "Başlangıç verisi başarıyla yüklendi!")
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Dosya yüklenemedi:\n{e}")

    def _open_add_user(self):
        if not self.controller.state:
            QMessageBox.warning(self, "Uyarı", "Önce bir başlangıç dosyası yükleyiniz.")
            return
        dialog = AddUserDialog(self.controller, self)
        dialog.exec()

    def _open_add_resource(self):
        if not self.controller.state:
            QMessageBox.warning(self, "Uyarı", "Önce bir başlangıç dosyası yükleyiniz.")
            return
        dialog = AddResourceDialog(self.controller, self)
        dialog.exec()

    def _on_date_changed(self, qdate: QDate):
        d = date(qdate.year(), qdate.month(), qdate.day())
        self.calendar_canvas.set_date(d)

    def _on_reservation_selected(self, res_id: str):
        self.action_panel.select_reservation(res_id)
        self.tabs.setCurrentIndex(0)

    def _prompt_auto_waitlist(self, data: dict):
        user = data["user"]
        res = data["resource"]
        start = data["start"]
        end = data["end"]
        code = data["code"]

        reply = QMessageBox.question(
            self,
            "Bekleme Listesine Katıl",
            f"Talep {code} nedeniyle reddedildi.\n\n"
            f"Kullanıcı: {user}\nKaynak: {res}\n"
            f"Aralık: {start.strftime('%Y-%m-%d %H:%M')} - {end.strftime('%H:%M')}\n\n"
            f"Aynı aralık için bekleme listesine girmek ister misiniz?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes,
        )
        if reply == QMessageBox.Yes:
            cmd = WaitingCommand(
                kullanici=user,
                kaynak=res,
                baslangic=start,
                bitis=end,
            )
            res_wait = self.controller.execute(cmd, record=True)
            match res_wait:
                case WaitingResult.Ok(waiting_id=w_id, position=pos):
                    QMessageBox.information(
                        self, "Bekleme Kaydı Başarılı", f"Kaydınız alındı!\nBekleme ID: {w_id}\nSıra: {pos}"
                    )
                case WaitingResult.Red(error_code=err):
                    QMessageBox.warning(
                        self, "Bekleme Kaydı Başarısız", f"Hata [{err}]: {get_error_desc(err)}"
                    )

    def _on_state_updated(self):
        state = self.controller.state
        if state:
            # Sync calendar picker with current simulated date
            self.date_picker.blockSignals(True)
            self.date_picker.setDate(QDate(state.clock.year, state.clock.month, state.clock.day))
            self.calendar_canvas.set_date(state.clock.date())
            self.date_picker.blockSignals(False)

        self.calendar_canvas.update()
        self.user_panel.refresh()
        self.booking_form.refresh()
        self.clock_widget.refresh()
        self.audit_log.refresh()
