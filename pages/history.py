"""
Task history page – view completed and abandoned tasks.
"""
from qt import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QScrollArea, QPushButton, QLineEdit, QComboBox, QDateEdit,
    Qt, QDate
)

from styles import COLORS, STATUS_LABELS, STATUS_COLORS, IMPORTANCE_COLORS, IMPORTANCE_LABELS
import database as db
from dialogs import TaskDetailDialog


class HistoryPage(QWidget):
    """View and search past tasks."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        main = QVBoxLayout(self)
        main.setContentsMargins(24, 24, 24, 24)
        main.setSpacing(16)

        # Header
        header = QHBoxLayout()
        title = QLabel("📜  Historique des tâches")
        title.setProperty("class", "section_title")
        header.addWidget(title)
        header.addStretch()

        self.count_lbl = QLabel("")
        self.count_lbl.setStyleSheet(f"color:{COLORS['text_secondary']};font-size:13px;")
        header.addWidget(self.count_lbl)
        main.addLayout(header)

        sub = QLabel("Retrouvez toutes vos tâches terminées ou abandonnées")
        sub.setStyleSheet(f"color:{COLORS['text_muted']};font-size:13px;margin-top:-8px;")
        main.addWidget(sub)

        # Filters
        filters = QHBoxLayout()
        filters.setSpacing(10)

        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("🔍  Rechercher dans l'historique...")
        self.search_edit.textChanged.connect(self._apply_filters)
        filters.addWidget(self.search_edit, 1)

        self.status_filter = QComboBox()
        self.status_filter.addItem("Tous", None)
        self.status_filter.addItem("✅ Terminées", "completed")
        self.status_filter.addItem("❌ Abandonnées", "abandoned")
        self.status_filter.currentIndexChanged.connect(self._apply_filters)
        filters.addWidget(self.status_filter)

        main.addLayout(filters)

        # Task list
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)

        self.list_widget = QWidget()
        self.list_layout = QVBoxLayout(self.list_widget)
        self.list_layout.setSpacing(8)
        self.list_layout.setContentsMargins(0, 0, 8, 0)
        self.list_layout.addStretch()

        self.scroll.setWidget(self.list_widget)
        main.addWidget(self.scroll, 1)

    def refresh_data(self):
        self._apply_filters()

    def _apply_filters(self):
        search = self.search_edit.text().strip() or None
        status = self.status_filter.currentData()

        tasks = db.get_history_tasks(search_text=search, status_filter=status)
        self._populate(tasks)

    def _populate(self, tasks):
        while self.list_layout.count():
            item = self.list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self.count_lbl.setText(f"{len(tasks)} résultat(s)")

        if not tasks:
            empty = QLabel("📭  Aucune tâche dans l'historique.")
            empty.setStyleSheet(f"color:{COLORS['text_muted']};font-size:14px;padding:40px;")
            empty.setAlignment(Qt.AlignCenter)
            self.list_layout.addWidget(empty)
        else:
            for task in tasks:
                card = self._make_card(task)
                self.list_layout.addWidget(card)

        self.list_layout.addStretch()

    def _make_card(self, task):
        frame = QFrame()
        frame.setProperty("class", "card")
        frame.setCursor(Qt.PointingHandCursor)

        status = task.get('status', 'completed')
        s_color = STATUS_COLORS.get(status, COLORS['text_secondary'])
        imp = task.get('importance', 2)
        imp_color = IMPORTANCE_COLORS.get(imp, COLORS['primary'])

        frame.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['bg_card']};
                border: 1px solid {COLORS['border']};
                border-left: 4px solid {s_color};
                border-radius: 10px;
            }}
            QFrame:hover {{
                border-color: {COLORS['primary']};
                background: {COLORS['bg_hover']};
            }}
        """)

        lay = QVBoxLayout(frame)
        lay.setContentsMargins(14, 10, 14, 10)
        lay.setSpacing(6)

        # Top row
        top = QHBoxLayout()
        title_lbl = QLabel(task['title'])
        title_lbl.setStyleSheet(f"font-size:14px;font-weight:600;color:{COLORS['text_primary']};background:transparent;")
        title_lbl.setWordWrap(True)
        top.addWidget(title_lbl, 1)

        badge = QLabel(STATUS_LABELS.get(status, ''))
        badge.setStyleSheet(f"background:{s_color};color:white;border-radius:8px;padding:2px 8px;font-size:10px;font-weight:600;")
        badge.setFixedHeight(20)
        top.addWidget(badge, alignment=Qt.AlignTop)
        lay.addLayout(top)

        # Meta row
        meta = QHBoxLayout()
        meta.setSpacing(12)

        imp_lbl = QLabel(f"{'●' * imp} {IMPORTANCE_LABELS.get(imp, '')}")
        imp_lbl.setStyleSheet(f"color:{imp_color};font-size:11px;background:transparent;")
        meta.addWidget(imp_lbl)

        if task.get('category'):
            cat = QLabel(f"🏷️ {task['category']}")
            cat.setStyleSheet(f"color:{COLORS['text_muted']};font-size:11px;background:transparent;")
            meta.addWidget(cat)

        meta.addStretch()

        # Completion/abandon date
        end_date = task.get('completed_at') or task.get('abandoned_at') or ''
        if end_date:
            dt_display = end_date[:10]
            date_lbl = QLabel(f"{'✅' if status == 'completed' else '❌'} {dt_display}")
            date_lbl.setStyleSheet(f"color:{COLORS['text_secondary']};font-size:11px;background:transparent;")
            meta.addWidget(date_lbl)

        lay.addLayout(meta)

        # Click handler
        frame.mousePressEvent = lambda e, tid=task['id']: self._show_detail(tid)

        return frame

    def _show_detail(self, task_id):
        dlg = TaskDetailDialog(self, task_id)
        dlg.exec()
