"""Resource calendar timeline widget."""

from datetime import date, datetime, time, timedelta
from PySide6.QtCore import QPointF, QRectF, Qt, Signal
from PySide6.QtGui import QBrush, QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import QToolTip, QWidget

from yazilim_lab_project.gui.controller import AppController
from yazilim_lab_project.models.reservation import Reservation, State

# Colors for reservation statuses
STATUS_COLORS = {
    State.APPROVED: QColor(52, 152, 219, 210),          # Blue
    State.IN_USE: QColor(46, 204, 113, 220),            # Green
    State.COMPLETED: QColor(149, 165, 166, 180),        # Gray
    State.CANCELLED: QColor(231, 76, 60, 160),          # Red (semi-transparent)
    State.DID_NOT_ARRIVE: QColor(230, 126, 34, 170),   # Orange
}

MAINTENANCE_COLOR = QColor(155, 89, 182, 190)      # Purple
PREPARATION_COLOR = QColor(241, 196, 15, 120)      # Yellow hatch


class CalendarCanvas(QWidget):
    reservation_selected = Signal(str)  # Emits reservation ID

    def __init__(self, controller: AppController, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.selected_date: date = date.today()
        self.header_width = 140
        self.time_header_height = 40
        self.row_height = 60
        self.start_hour = 8
        self.end_hour = 22
        self.total_minutes = (self.end_hour - self.start_hour) * 60
        self.setMouseTracking(True)
        self._rendered_boxes: list[tuple[QRectF, object]] = []

    def set_date(self, d: date):
        self.selected_date = d
        self.update()

    def minimumSizeHint(self):
        resources_count = len(self.controller.state.config.resources) if self.controller.state else 5
        return self.sizeHint()

    def sizeHint(self):
        resources_count = len(self.controller.state.config.resources) if self.controller.state else 5
        h = self.time_header_height + max(1, resources_count) * self.row_height + 20
        return self.minimumSize().expandedTo(self.size().expandedTo(self.rect().size()))

    def _time_to_x(self, dt: datetime, width: float) -> float:
        timeline_width = width - self.header_width
        day_start = datetime.combine(self.selected_date, time(self.start_hour, 0))
        diff_minutes = (dt - day_start).total_seconds() / 60.0
        return self.header_width + (diff_minutes / self.total_minutes) * timeline_width

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()
        state = self.controller.state

        # Background
        painter.fillRect(0, 0, w, h, QColor(250, 250, 250))
        timeline_width = max(100.0, float(w - self.header_width))

        # Time header
        painter.fillRect(0, 0, w, self.time_header_height, QColor(236, 240, 241))
        painter.setPen(QPen(QColor(189, 195, 199), 1))
        painter.drawLine(0, self.time_header_height, w, self.time_header_height)
        painter.drawLine(self.header_width, 0, self.header_width, h)

        # Draw 15-minute / 1-hour grid ticks
        painter.setFont(QFont("Arial", 8))
        for minute in range(0, self.total_minutes + 1, 15):
            x = self.header_width + (minute / self.total_minutes) * timeline_width
            is_hour = (minute % 60 == 0)
            if is_hour:
                hour = self.start_hour + minute // 60
                painter.setPen(QPen(QColor(189, 195, 199), 1))
                painter.drawLine(x, 0, x, h)
                painter.setPen(QPen(QColor(52, 73, 94), 1))
                painter.drawText(QRectF(x - 20, 10, 40, 20), Qt.AlignCenter, f"{hour:02d}:00")
            else:
                painter.setPen(QPen(QColor(230, 230, 230), 1, Qt.DashLine))
                painter.drawLine(x, self.time_header_height, x, h)

        if not state:
            painter.setPen(QColor(127, 140, 141))
            painter.setFont(QFont("Arial", 12))
            painter.drawText(QRectF(0, self.time_header_height, w, h - self.time_header_height), Qt.AlignCenter, "Başlangıç dosyası yükleyiniz")
            return

        self._rendered_boxes.clear()
        resources = state.config.resources
        y = float(self.time_header_height)

        for res_idx, resource in enumerate(resources):
            # Resource label
            painter.setPen(QPen(QColor(189, 195, 199), 1))
            painter.drawLine(0, y + self.row_height, w, y + self.row_height)
            painter.setPen(QColor(44, 62, 80))
            painter.setFont(QFont("Arial", 9, QFont.Bold))
            painter.drawText(QRectF(10, y + 10, self.header_width - 15, 20), Qt.AlignLeft | Qt.AlignVCenter, resource.id)
            painter.setFont(QFont("Arial", 7))
            painter.setPen(QColor(127, 140, 141))
            painter.drawText(QRectF(10, y + 30, self.header_width - 15, 18), Qt.AlignLeft | Qt.AlignVCenter, f"{resource.type} ({resource.name})")

            # Find maintenance windows for this resource overlapping selected date
            day_start = datetime.combine(self.selected_date, time(self.start_hour, 0))
            day_end = datetime.combine(self.selected_date, time(self.end_hour, 0))

            for maint in state.config.maintenance_windows:
                if maint.resource == resource.id:
                    if maint.start < day_end and maint.end > day_start:
                        m_start = max(maint.start, day_start)
                        m_end = min(maint.end, day_end)
                        x1 = self._time_to_x(m_start, w)
                        x2 = self._time_to_x(m_end, w)
                        box_rect = QRectF(x1, y + 4, max(2.0, x2 - x1), self.row_height - 8)
                        painter.fillRect(box_rect, MAINTENANCE_COLOR)
                        painter.setPen(Qt.white)
                        painter.setFont(QFont("Arial", 8, QFont.Bold))
                        painter.drawText(box_rect, Qt.AlignCenter, "BAKIM")
                        self._rendered_boxes.append((box_rect, maint))

            # Reservations for this resource
            res_list = [
                r for r in state.reservations
                if r.resource == resource.id and r.start < day_end and r.end > day_start
            ]

            # Separate into active vs cancelled/no-show for sub-row rendering
            active_res = [r for r in res_list if r.state in (State.APPROVED, State.IN_USE, State.COMPLETED)]
            inactive_res = [r for r in res_list if r.state in (State.CANCELLED, State.DID_NOT_ARRIVE)]

            # Check overlap between active and inactive to divide row if needed
            has_overlap = False
            for act in active_res:
                for inact in inactive_res:
                    if act.start < inact.end and act.end > inact.start:
                        has_overlap = True
                        break
                if has_overlap:
                    break

            # Draw reservations
            for r in res_list:
                r_start = max(r.start, day_start)
                r_end = min(r.end, day_end)
                x1 = self._time_to_x(r_start, w)
                x2 = self._time_to_x(r_end, w)

                if has_overlap:
                    if r.state in (State.CANCELLED, State.DID_NOT_ARRIVE):
                        box_y = y + 2
                        box_h = (self.row_height / 2.0) - 3
                    else:
                        box_y = y + (self.row_height / 2.0) + 1
                        box_h = (self.row_height / 2.0) - 3
                else:
                    box_y = y + 6
                    box_h = self.row_height - 12

                box_rect = QRectF(x1, box_y, max(4.0, x2 - x1), box_h)
                color = STATUS_COLORS.get(r.state, QColor(100, 100, 100))
                painter.fillRect(box_rect, color)
                painter.setPen(QPen(color.darker(130), 1))
                painter.drawRect(box_rect)

                # Text inside block
                painter.setPen(Qt.white)
                painter.setFont(QFont("Arial", 8, QFont.Bold))
                display_text = f"{r.id} ({r.user})"
                if box_rect.width() > 40:
                    painter.drawText(box_rect, Qt.AlignCenter, display_text)

                self._rendered_boxes.append((box_rect, r))

                # Preparation time visualization after completed/in-use/approved reservations
                prep_minutes = state.config.resource_types[resource.type].preparation_min
                if prep_minutes > 0 and r.state in (State.APPROVED, State.IN_USE, State.COMPLETED):
                    prep_end = min(r.end + timedelta(minutes=prep_minutes), day_end)
                    if prep_end > r.end:
                        px1 = self._time_to_x(r.end, w)
                        px2 = self._time_to_x(prep_end, w)
                        pbox = QRectF(px1, box_y, max(2.0, px2 - px1), box_h)
                        painter.fillRect(pbox, PREPARATION_COLOR)
                        painter.setPen(QPen(QColor(211, 84, 0), 1, Qt.DotLine))
                        painter.drawRect(pbox)

            y += self.row_height

        # Simulated Clock Line
        sim_time = state.config.time
        if sim_time.date() == self.selected_date and (day_start <= sim_time <= day_end):
            cx = self._time_to_x(sim_time, w)
            painter.setPen(QPen(QColor(231, 76, 60), 2, Qt.SolidLine))
            painter.drawLine(cx, 0, cx, y)
            painter.setBrush(QColor(231, 76, 60))
            painter.drawPolygon([QPointF(cx - 5, self.time_header_height), QPointF(cx + 5, self.time_header_height), QPointF(cx, self.time_header_height + 8)])

    def mouseMoveEvent(self, event):
        pos = event.position()
        for rect, obj in self._rendered_boxes:
            if rect.contains(pos):
                if isinstance(obj, Reservation):
                    st = obj.state.value if hasattr(obj.state, "value") else str(obj.state)
                    pkg = f"\nPaket: {obj.package}" if obj.package else ""
                    tip = (
                        f"<b>Rezervasyon No:</b> {obj.id}<br>"
                        f"<b>Kullanıcı:</b> {obj.user}<br>"
                        f"<b>Kaynak:</b> {obj.resource}<br>"
                        f"<b>Aralık:</b> {obj.start.strftime('%H:%M')} – {obj.end.strftime('%H:%M')}<br>"
                        f"<b>Ücret:</b> {obj.price} KP<br>"
                        f"<b>Durum:</b> {st}"
                        f"{pkg}"
                    )
                    QToolTip.showText(event.globalPosition().toPoint(), tip, self)
                    return
                elif hasattr(obj, "resource") and hasattr(obj, "start") and hasattr(obj, "end"):
                    tip = (
                        f"<b>Bakım Penceresi</b><br>"
                        f"<b>Kaynak:</b> {obj.resource}<br>"
                        f"<b>Aralık:</b> {obj.start.strftime('%H:%M')} – {obj.end.strftime('%H:%M')}"
                    )
                    QToolTip.showText(event.globalPosition().toPoint(), tip, self)
                    return
        QToolTip.hideText()
        super().mouseMoveEvent(event)

    def mousePressEvent(self, event):
        pos = event.position()
        for rect, obj in self._rendered_boxes:
            if rect.contains(pos):
                if isinstance(obj, Reservation):
                    self.reservation_selected.emit(obj.id)
                    return
        super().mousePressEvent(event)
