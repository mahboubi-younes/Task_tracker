"""
Task list page with filtering, sorting, and task management.
"""
from qt import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QScrollArea, QPushButton, QLineEdit, QComboBox,
    QGridLayout, QProgressBar, QMenu, QSizePolicy,
    Qt, Signal
)

from styles import (
    COLORS, IMPORTANCE_LABELS, URGENCY_LABELS, STATUS_LABELS,
    IMPORTANCE_COLORS, URGENCY_COLORS, STATUS_COLORS
)
import database as db
from dialogs import TaskDialog, TaskDetailDialog, ConfirmDialog


class TaskCard(QFrame):
    """Individual task card widget."""
    clicked = Signal(int)
    action = Signal(str, int)  # action_name, task_id

    def __init__(self, task, parent=None):
        super().__init__(parent)
        self.task = task
        self.task_id = task['id']
        self.setProperty("class", "card")
        self.setCursor(Qt.PointingHandCursor)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_menu)

        imp = task.get('importance', 2)
        urg = task.get('urgency', 2)
        border_color = IMPORTANCE_COLORS.get(imp, COLORS['primary'])
        if imp >= 3 and urg >= 3:
            border_color = COLORS['danger']

        self.setStyleSheet(f"""
            TaskCard {{
                background: {COLORS['bg_card']};
                border: 1px solid {COLORS['border']};
                border-left: 4px solid {border_color};
                border-radius: 10px;
            }}
            TaskCard:hover {{
                border-color: {COLORS['primary']};
                background: {COLORS['bg_hover']};
            }}
        """)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(14, 12, 14, 12)
        lay.setSpacing(8)

        # Top row: title + status
        top = QHBoxLayout()
        title = QLabel(task['title'])
        title.setStyleSheet(f"font-size:14px;font-weight:600;color:{COLORS['text_primary']};background:transparent;")
        title.setWordWrap(True)
        top.addWidget(title, 1)

        status = task.get('status', 'todo')
        s_color = STATUS_COLORS.get(status, COLORS['text_secondary'])
        badge = QLabel(STATUS_LABELS.get(status, ''))
        badge.setStyleSheet(f"""
            background:{s_color}; color:white; border-radius:8px;
            padding:2px 8px; font-size:10px; font-weight:600;
        """)
        badge.setFixedHeight(20)
        top.addWidget(badge, alignment=Qt.AlignTop)
        lay.addLayout(top)

        # Description preview
        desc = task.get('description', '')
        if desc:
            d_lbl = QLabel(desc[:80] + ('...' if len(desc) > 80 else ''))
            d_lbl.setStyleSheet(f"color:{COLORS['text_muted']};font-size:12px;background:transparent;")
            d_lbl.setWordWrap(True)
            lay.addWidget(d_lbl)

        # Meta row
        meta = QHBoxLayout()
        meta.setSpacing(12)

        # Importance
        imp_color = IMPORTANCE_COLORS.get(imp, COLORS['text_secondary'])
        imp_lbl = QLabel(f"{'●' * imp} {IMPORTANCE_LABELS.get(imp, '')}")
        imp_lbl.setStyleSheet(f"color:{imp_color};font-size:11px;font-weight:500;background:transparent;")
        imp_lbl.setToolTip("Importance")
        meta.addWidget(imp_lbl)

        # Urgency
        urg_color = URGENCY_COLORS.get(urg, COLORS['text_secondary'])
        urg_lbl = QLabel(f"{'▲' * urg} {URGENCY_LABELS.get(urg, '')}")
        urg_lbl.setStyleSheet(f"color:{urg_color};font-size:11px;font-weight:500;background:transparent;")
        urg_lbl.setToolTip("Urgence")
        meta.addWidget(urg_lbl)

        meta.addStretch()

        # Due date
        if task.get('due_date'):
            due = QLabel(f"📅 {task['due_date']}")
            due.setStyleSheet(f"color:{COLORS['text_secondary']};font-size:11px;background:transparent;")
            meta.addWidget(due)

        # Category
        if task.get('category'):
            cat = QLabel(f"🏷️ {task['category']}")
            cat.setStyleSheet(f"color:{COLORS['text_muted']};font-size:11px;background:transparent;")
            meta.addWidget(cat)

        # Recurring indicator
        if task.get('is_recurring'):
            rec = QLabel("🔄")
            rec.setToolTip("Tâche récurrente")
            rec.setStyleSheet("background:transparent;")
            meta.addWidget(rec)

        lay.addLayout(meta)

        # Progress bar (if in progress)
        progress = task.get('progress', 0)
        if status == 'in_progress' or progress > 0:
            prog_bar = QProgressBar()
            prog_bar.setValue(progress)
            prog_bar.setFixedHeight(8)
            prog_bar.setTextVisible(False)
            lay.addWidget(prog_bar)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.task_id)
        super().mousePressEvent(event)

    def _show_menu(self, pos):
        menu = QMenu(self)
        status = self.task.get('status', 'todo')

        if status == 'todo':
            menu.addAction("▶️  Démarrer", lambda: self.action.emit('start', self.task_id))
        elif status == 'in_progress':
            menu.addAction("⏸️  Mettre en pause", lambda: self.action.emit('pause', self.task_id))
            menu.addAction("✅  Terminer", lambda: self.action.emit('complete', self.task_id))

        if status != 'completed':
            menu.addAction("✅  Marquer terminée", lambda: self.action.emit('complete', self.task_id))

        menu.addSeparator()
        menu.addAction("✏️  Modifier", lambda: self.action.emit('edit', self.task_id))
        menu.addAction("📋  Détails", lambda: self.action.emit('detail', self.task_id))
        menu.addSeparator()

        if status not in ('completed', 'abandoned'):
            menu.addAction("🚫  Abandonner", lambda: self.action.emit('abandon', self.task_id))

        menu.addAction("🗑️  Supprimer", lambda: self.action.emit('delete', self.task_id))

        menu.exec(self.mapToGlobal(pos))


class TasksPage(QWidget):
    """Task list with filtering and management."""
    task_created = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        main = QVBoxLayout(self)
        main.setContentsMargins(24, 24, 24, 24)
        main.setSpacing(16)

        # Header
        header = QHBoxLayout()
        title = QLabel("📋  Mes Tâches")
        title.setProperty("class", "section_title")
        header.addWidget(title)
        header.addStretch()

        self.task_count_lbl = QLabel("")
        self.task_count_lbl.setStyleSheet(f"color:{COLORS['text_secondary']};font-size:13px;")
        header.addWidget(self.task_count_lbl)

        add_btn = QPushButton("➕  Nouvelle tâche")
        add_btn.setProperty("class", "primary_btn")
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.setMinimumHeight(38)
        add_btn.clicked.connect(self._create_task)
        header.addWidget(add_btn)
        main.addLayout(header)

        # Filters
        filters = QHBoxLayout()
        filters.setSpacing(10)

        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("🔍  Rechercher une tâche...")
        self.search_edit.setMinimumWidth(200)
        self.search_edit.textChanged.connect(self._apply_filters)
        filters.addWidget(self.search_edit, 1)

        self.status_filter = QComboBox()
        self.status_filter.addItem("Tous les statuts", None)
        self.status_filter.addItem("📝 À faire", "todo")
        self.status_filter.addItem("🔄 En cours", "in_progress")
        self.status_filter.addItem("✅ Terminées", "completed")
        self.status_filter.addItem("❌ Abandonnées", "abandoned")
        self.status_filter.currentIndexChanged.connect(self._apply_filters)
        filters.addWidget(self.status_filter)

        self.imp_filter = QComboBox()
        self.imp_filter.addItem("Toute importance", None)
        for val, label in IMPORTANCE_LABELS.items():
            self.imp_filter.addItem(f"{'●' * val} {label}", val)
        self.imp_filter.currentIndexChanged.connect(self._apply_filters)
        filters.addWidget(self.imp_filter)

        self.urg_filter = QComboBox()
        self.urg_filter.addItem("Toute urgence", None)
        for val, label in URGENCY_LABELS.items():
            self.urg_filter.addItem(f"{'▲' * val} {label}", val)
        self.urg_filter.currentIndexChanged.connect(self._apply_filters)
        filters.addWidget(self.urg_filter)

        self.cat_filter = QComboBox()
        self.cat_filter.addItem("Toute catégorie", None)
        self.cat_filter.currentIndexChanged.connect(self._apply_filters)
        filters.addWidget(self.cat_filter)

        main.addLayout(filters)

        # Task list (scroll area)
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
        # Refresh categories
        self.cat_filter.blockSignals(True)
        current_cat = self.cat_filter.currentData()
        self.cat_filter.clear()
        self.cat_filter.addItem("Toute catégorie", None)
        for cat in db.get_categories():
            self.cat_filter.addItem(f"🏷️ {cat}", cat)
        if current_cat:
            for i in range(self.cat_filter.count()):
                if self.cat_filter.itemData(i) == current_cat:
                    self.cat_filter.setCurrentIndex(i)
                    break
        self.cat_filter.blockSignals(False)

        self._apply_filters()

    def _apply_filters(self):
        status = self.status_filter.currentData()
        importance = self.imp_filter.currentData()
        urgency = self.urg_filter.currentData()
        category = self.cat_filter.currentData()
        search = self.search_edit.text().strip()

        tasks = db.get_all_tasks(
            status_filter=status,
            importance_filter=importance,
            urgency_filter=urgency,
            category_filter=category,
            search_text=search if search else None,
        )

        self._populate_list(tasks)

    def _populate_list(self, tasks):
        # Clear existing
        while self.list_layout.count():
            item = self.list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self.task_count_lbl.setText(f"{len(tasks)} tâche(s)")

        if not tasks:
            empty = QLabel("🎯  Aucune tâche trouvée. Créez-en une !")
            empty.setStyleSheet(f"color:{COLORS['text_muted']};font-size:14px;padding:40px;")
            empty.setAlignment(Qt.AlignCenter)
            self.list_layout.addWidget(empty)
        else:
            for task in tasks:
                card = TaskCard(task)
                card.clicked.connect(self._on_card_clicked)
                card.action.connect(self._on_card_action)
                self.list_layout.addWidget(card)

        self.list_layout.addStretch()

    def _on_card_clicked(self, task_id):
        dlg = TaskDetailDialog(self, task_id)
        dlg.exec()

    def _on_card_action(self, action, task_id):
        if action == 'start':
            db.start_task(task_id)
        elif action == 'pause':
            db.pause_task(task_id)
        elif action == 'complete':
            db.complete_task(task_id)
        elif action == 'abandon':
            dlg = ConfirmDialog(self, "Abandonner", "Voulez-vous vraiment abandonner cette tâche ?",
                                "Abandonner", danger=True)
            if dlg.exec() != ConfirmDialog.Accepted:
                return
            db.abandon_task(task_id)
        elif action == 'edit':
            task = db.get_task(task_id)
            if task:
                dlg = TaskDialog(self, task)
                if dlg.exec() == TaskDialog.Accepted:
                    data = dlg.get_data()
                    db.update_task(task_id, data)
        elif action == 'detail':
            dlg = TaskDetailDialog(self, task_id)
            dlg.exec()
        elif action == 'delete':
            dlg = ConfirmDialog(self, "Supprimer", "Voulez-vous vraiment supprimer cette tâche ?",
                                "Supprimer", danger=True)
            if dlg.exec() != ConfirmDialog.Accepted:
                return
            db.delete_task(task_id)

        self.refresh_data()

    def _create_task(self):
        dlg = TaskDialog(self)
        if dlg.exec() == TaskDialog.Accepted:
            data = dlg.get_data()
            db.create_task(data)
            self.refresh_data()
            self.task_created.emit()

    def create_task_for_date(self, date_str):
        """Called from calendar to create a task on a specific date."""
        dlg = TaskDialog(self)
        dlg.due_date_check.setChecked(True)
        y, m, d = date_str.split('-')
        from PySide6.QtCore import QDate
        dlg.due_date_edit.setDate(QDate(int(y), int(m), int(d)))
        if dlg.exec() == TaskDialog.Accepted:
            data = dlg.get_data()
            db.create_task(data)
            self.refresh_data()
            self.task_created.emit()
