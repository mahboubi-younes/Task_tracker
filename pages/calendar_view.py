"""
Calendar view page with monthly grid, task density, and day detail panel.
"""
import calendar
from datetime import date, timedelta
from qt import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QScrollArea, QPushButton, QGridLayout, QSizePolicy, QMenu,
    Qt, Signal, QDate
)

from styles import COLORS, STATUS_LABELS, IMPORTANCE_COLORS, STATUS_COLORS
import database as db
from dialogs import TaskDialog, TaskDetailDialog, ConfirmDialog

# French day and month names
JOURS = ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim']
MOIS = ['', 'Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin',
        'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']


class DayCell(QPushButton):
    """A single day cell in the calendar grid."""
    day_clicked = Signal(str)  # date string yyyy-MM-dd

    def __init__(self, day_num, date_str, is_today=False, is_outside=False, task_count=0, parent=None):
        super().__init__(parent)
        self.date_str = date_str
        self.day_num = day_num
        self.setProperty("class", "cal_day")
        self.setProperty("today", "true" if is_today else "false")
        self.setProperty("outside", "true" if is_outside else "false")
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(75)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.clicked.connect(lambda: self.day_clicked.emit(self.date_str))

        # Build cell content
        self._setup_content(day_num, is_today, task_count, is_outside)

    def _setup_content(self, day_num, is_today, task_count, is_outside):
        text = str(day_num)
        if task_count > 0:
            dots = min(task_count, 4)
            dot_str = '●' * dots
            if task_count > 4:
                dot_str += f'+{task_count - 4}'
            text += f"\n{dot_str}"

        self.setText(text)

        bg = COLORS['bg_card']
        border = COLORS['border']
        text_color = COLORS['text_primary']

        if is_outside:
            bg = COLORS['bg_dark']
            text_color = COLORS['text_muted']
        if is_today:
            border = COLORS['primary']
            bg = '#2a2b52'

        # Color dots based on task count
        dot_color = COLORS['text_muted']
        if task_count >= 4:
            dot_color = COLORS['danger']
        elif task_count >= 2:
            dot_color = COLORS['accent_gold']
        elif task_count >= 1:
            dot_color = COLORS['accent_teal']

        self.setStyleSheet(f"""
            QPushButton {{
                background: {bg};
                border: {'2px' if is_today else '1px'} solid {border};
                border-radius: 8px;
                color: {text_color};
                font-size: 12px;
                text-align: left;
                padding: 6px 8px;
            }}
            QPushButton:hover {{
                border-color: {COLORS['primary']};
                background: {COLORS['bg_hover']};
            }}
        """)


class CalendarPage(QWidget):
    """Monthly calendar view with task visualization."""
    navigate_to_tasks = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_year = date.today().year
        self.current_month = date.today().month
        self.selected_date = date.today().isoformat()
        self._build_ui()

    def _build_ui(self):
        main = QVBoxLayout(self)
        main.setContentsMargins(24, 24, 24, 24)
        main.setSpacing(16)

        # Header
        header = QHBoxLayout()
        title = QLabel("📅  Calendrier")
        title.setProperty("class", "section_title")
        header.addWidget(title)
        header.addStretch()
        main.addLayout(header)

        # Navigation bar
        nav = QHBoxLayout()
        nav.setSpacing(8)

        prev_btn = QPushButton("◀  Précédent")
        prev_btn.setCursor(Qt.PointingHandCursor)
        prev_btn.clicked.connect(self._prev_month)
        nav.addWidget(prev_btn)

        today_btn = QPushButton("Aujourd'hui")
        today_btn.setProperty("class", "primary_btn")
        today_btn.setCursor(Qt.PointingHandCursor)
        today_btn.clicked.connect(self._go_today)
        nav.addWidget(today_btn)

        next_btn = QPushButton("Suivant  ▶")
        next_btn.setCursor(Qt.PointingHandCursor)
        next_btn.clicked.connect(self._next_month)
        nav.addWidget(next_btn)

        nav.addStretch()

        self.month_label = QLabel()
        self.month_label.setStyleSheet(f"font-size:18px;font-weight:700;color:{COLORS['primary']};")
        nav.addWidget(self.month_label)

        main.addLayout(nav)

        # Calendar + detail split
        split = QHBoxLayout()
        split.setSpacing(16)

        # Calendar grid container
        cal_container = QVBoxLayout()

        # Day headers
        day_header = QGridLayout()
        day_header.setSpacing(4)
        for i, jour in enumerate(JOURS):
            lbl = QLabel(jour)
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet(f"color:{COLORS['primary']};font-weight:600;font-size:12px;padding:4px;")
            day_header.addWidget(lbl, 0, i)
        cal_container.addLayout(day_header)

        # Calendar grid
        self.cal_grid = QGridLayout()
        self.cal_grid.setSpacing(4)
        cal_container.addLayout(self.cal_grid)

        split.addLayout(cal_container, 3)

        # Day detail panel
        detail_frame = QFrame()
        detail_frame.setProperty("class", "card")
        detail_frame.setMinimumWidth(260)
        detail_frame.setMaximumWidth(320)
        self.detail_layout = QVBoxLayout(detail_frame)
        self.detail_layout.setSpacing(8)
        self.detail_layout.setContentsMargins(12, 12, 12, 12)

        self.detail_date_label = QLabel("Sélectionnez un jour")
        self.detail_date_label.setStyleSheet(f"font-size:15px;font-weight:600;color:{COLORS['primary']};")
        self.detail_layout.addWidget(self.detail_date_label)

        self.detail_scroll = QScrollArea()
        self.detail_scroll.setWidgetResizable(True)
        self.detail_scroll.setFrameShape(QFrame.NoFrame)
        self.detail_content = QWidget()
        self.detail_content_layout = QVBoxLayout(self.detail_content)
        self.detail_content_layout.setSpacing(6)
        self.detail_content_layout.setContentsMargins(0, 0, 0, 0)
        self.detail_content_layout.addStretch()
        self.detail_scroll.setWidget(self.detail_content)
        self.detail_layout.addWidget(self.detail_scroll, 1)

        # Add task button for selected day
        self.add_day_btn = QPushButton("➕  Ajouter une tâche")
        self.add_day_btn.setProperty("class", "primary_btn")
        self.add_day_btn.setCursor(Qt.PointingHandCursor)
        self.add_day_btn.clicked.connect(self._add_task_for_day)
        self.detail_layout.addWidget(self.add_day_btn)

        split.addWidget(detail_frame, 1)

        main.addLayout(split, 1)

    def refresh_data(self):
        self._render_calendar()
        self._update_detail()

    def _render_calendar(self):
        # Clear grid
        while self.cal_grid.count():
            item = self.cal_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self.month_label.setText(f"{MOIS[self.current_month]} {self.current_year}")

        cal = calendar.Calendar(firstweekday=0)
        days = cal.monthdayscalendar(self.current_year, self.current_month)

        # Get task density
        density = db.get_task_density(self.current_year, self.current_month)
        today = date.today()

        for row_idx, week in enumerate(days):
            for col_idx, day_num in enumerate(week):
                if day_num == 0:
                    # Outside month - show adjacent month's day
                    cell = QLabel("")
                    cell.setStyleSheet(f"background:{COLORS['bg_dark']};border-radius:8px;min-height:75px;")
                    self.cal_grid.addWidget(cell, row_idx, col_idx)
                else:
                    date_str = f"{self.current_year:04d}-{self.current_month:02d}-{day_num:02d}"
                    is_today = (self.current_year == today.year and
                                self.current_month == today.month and
                                day_num == today.day)
                    task_count = density.get(date_str, 0)
                    cell = DayCell(day_num, date_str, is_today=is_today,
                                   task_count=task_count)
                    cell.day_clicked.connect(self._on_day_clicked)
                    self.cal_grid.addWidget(cell, row_idx, col_idx)

    def _on_day_clicked(self, date_str):
        self.selected_date = date_str
        self._update_detail()

    def _update_detail(self):
        # Clear detail
        while self.detail_content_layout.count():
            item = self.detail_content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not self.selected_date:
            return

        # Parse date for display
        try:
            y, m, d = self.selected_date.split('-')
            display_date = f"{int(d)} {MOIS[int(m)]} {y}"
        except (ValueError, IndexError):
            display_date = self.selected_date

        self.detail_date_label.setText(f"📅  {display_date}")

        tasks = db.get_tasks_by_date(self.selected_date)

        if not tasks:
            empty = QLabel("Aucune tâche ce jour.")
            empty.setStyleSheet(f"color:{COLORS['text_muted']};font-size:13px;padding:16px 0;")
            empty.setAlignment(Qt.AlignCenter)
            self.detail_content_layout.addWidget(empty)
        else:
            for task in tasks:
                card = self._make_day_task_card(task)
                self.detail_content_layout.addWidget(card)

        self.detail_content_layout.addStretch()

    def _make_day_task_card(self, task):
        frame = QFrame()
        imp = task.get('importance', 2)
        border_color = IMPORTANCE_COLORS.get(imp, COLORS['primary'])
        status = task.get('status', 'todo')
        s_color = STATUS_COLORS.get(status, COLORS['text_secondary'])

        frame.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['bg_surface']};
                border: 1px solid {COLORS['border']};
                border-left: 3px solid {border_color};
                border-radius: 8px;
                padding: 8px;
            }}
            QFrame:hover {{ border-color: {COLORS['primary']}; }}
        """)
        frame.setCursor(Qt.PointingHandCursor)
        frame.setContextMenuPolicy(Qt.CustomContextMenu)
        frame.customContextMenuRequested.connect(
            lambda pos, t=task: self._day_task_menu(frame, pos, t)
        )

        lay = QVBoxLayout(frame)
        lay.setContentsMargins(8, 6, 8, 6)
        lay.setSpacing(4)

        top = QHBoxLayout()
        title = QLabel(task['title'])
        title.setStyleSheet(f"font-weight:500;font-size:12px;color:{COLORS['text_primary']};background:transparent;")
        title.setWordWrap(True)
        top.addWidget(title, 1)

        badge = QLabel(STATUS_LABELS.get(status, ''))
        badge.setStyleSheet(f"background:{s_color};color:white;border-radius:6px;padding:1px 6px;font-size:9px;font-weight:600;")
        badge.setFixedHeight(16)
        top.addWidget(badge, alignment=Qt.AlignTop)
        lay.addLayout(top)

        if task.get('due_time'):
            time_lbl = QLabel(f"🕐 {task['due_time']}")
            time_lbl.setStyleSheet(f"color:{COLORS['text_muted']};font-size:11px;background:transparent;")
            lay.addWidget(time_lbl)

        return frame

    def _day_task_menu(self, widget, pos, task):
        menu = QMenu(self)
        task_id = task['id']
        status = task.get('status', 'todo')

        if status == 'todo':
            menu.addAction("▶️  Démarrer", lambda: self._task_action('start', task_id))
        if status == 'in_progress':
            menu.addAction("✅  Terminer", lambda: self._task_action('complete', task_id))
        menu.addAction("✏️  Modifier", lambda: self._task_action('edit', task_id))
        menu.addAction("📋  Détails", lambda: self._task_action('detail', task_id))
        menu.addSeparator()
        menu.addAction("🗑️  Supprimer", lambda: self._task_action('delete', task_id))
        menu.exec(widget.mapToGlobal(pos))

    def _task_action(self, action, task_id):
        if action == 'start':
            db.start_task(task_id)
        elif action == 'complete':
            db.complete_task(task_id)
        elif action == 'edit':
            task = db.get_task(task_id)
            if task:
                dlg = TaskDialog(self, task)
                if dlg.exec() == TaskDialog.Accepted:
                    db.update_task(task_id, dlg.get_data())
        elif action == 'detail':
            TaskDetailDialog(self, task_id).exec()
        elif action == 'delete':
            dlg = ConfirmDialog(self, "Supprimer", "Supprimer cette tâche ?", "Supprimer", True)
            if dlg.exec() == ConfirmDialog.Accepted:
                db.delete_task(task_id)
        self.refresh_data()

    def _add_task_for_day(self):
        if not self.selected_date:
            return
        dlg = TaskDialog(self)
        dlg.due_date_check.setChecked(True)
        y, m, d = self.selected_date.split('-')
        dlg.due_date_edit.setDate(QDate(int(y), int(m), int(d)))
        if dlg.exec() == TaskDialog.Accepted:
            db.create_task(dlg.get_data())
            self.refresh_data()

    def _prev_month(self):
        if self.current_month == 1:
            self.current_month = 12
            self.current_year -= 1
        else:
            self.current_month -= 1
        self.refresh_data()

    def _next_month(self):
        if self.current_month == 12:
            self.current_month = 1
            self.current_year += 1
        else:
            self.current_month += 1
        self.refresh_data()

    def _go_today(self):
        today = date.today()
        self.current_year = today.year
        self.current_month = today.month
        self.selected_date = today.isoformat()
        self.refresh_data()
