"""
Dialogs for creating and editing tasks.
All UI text in French.
"""
import json
from datetime import datetime, date
from qt import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel,
    QLineEdit, QTextEdit, QComboBox, QDateEdit, QTimeEdit,
    QPushButton, QCheckBox, QSpinBox, QSlider, QGroupBox,
    QFrame, QMessageBox, QScrollArea, QWidget, QSizePolicy,
    Qt, QDate, QTime, Signal, QFont
)

from styles import (
    COLORS, IMPORTANCE_LABELS, URGENCY_LABELS, STATUS_LABELS,
    IMPORTANCE_COLORS, URGENCY_COLORS
)
import database as db


class TaskDialog(QDialog):
    """Dialog for creating or editing a task."""

    def __init__(self, parent=None, task=None):
        super().__init__(parent)
        self.task = task
        self.setWindowTitle("Modifier la tâche" if task else "Nouvelle tâche")
        self.setMinimumSize(520, 450)
        self.setMaximumWidth(600)
        self._build_ui()
        if task:
            self._populate(task)

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(24, 24, 24, 24)

        # ── Title ──
        title_lbl = QLabel("✏️  Modifier la tâche" if self.task else "➕  Nouvelle tâche")
        title_lbl.setStyleSheet(f"font-size:18px;font-weight:700;color:{COLORS['primary']};")
        layout.addWidget(title_lbl)

        # Scroll area for the form
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        form_widget = QWidget()
        form = QFormLayout(form_widget)
        form.setSpacing(10)
        form.setContentsMargins(0, 8, 0, 8)
        form.setLabelAlignment(Qt.AlignRight)

        # Title
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("Titre de la tâche...")
        form.addRow("Titre *", self.title_edit)

        # Description
        self.desc_edit = QTextEdit()
        self.desc_edit.setPlaceholderText("Description détaillée (optionnel)...")
        self.desc_edit.setMaximumHeight(80)
        form.addRow("Description", self.desc_edit)

        # Category
        self.category_edit = QComboBox()
        self.category_edit.setEditable(True)
        self.category_edit.addItem("")
        cats = db.get_categories()
        for c in cats:
            self.category_edit.addItem(c)
        self.category_edit.lineEdit().setPlaceholderText("Ex: Travail, Personnel...")
        form.addRow("Catégorie", self.category_edit)

        # Importance
        self.importance_combo = QComboBox()
        for val, label in IMPORTANCE_LABELS.items():
            self.importance_combo.addItem(f"{'●' * val}  {label}", val)
        self.importance_combo.setCurrentIndex(1)
        form.addRow("Importance", self.importance_combo)

        # Urgency
        self.urgency_combo = QComboBox()
        for val, label in URGENCY_LABELS.items():
            self.urgency_combo.addItem(f"{'▲' * val}  {label}", val)
        self.urgency_combo.setCurrentIndex(1)
        form.addRow("Urgence", self.urgency_combo)

        # Due date
        date_row = QHBoxLayout()
        self.due_date_check = QCheckBox("Échéance")
        self.due_date_edit = QDateEdit()
        self.due_date_edit.setCalendarPopup(True)
        self.due_date_edit.setDate(QDate.currentDate().addDays(1))
        self.due_date_edit.setDisplayFormat("dd/MM/yyyy")
        self.due_date_edit.setEnabled(False)
        self.due_date_check.toggled.connect(self.due_date_edit.setEnabled)
        date_row.addWidget(self.due_date_check)
        date_row.addWidget(self.due_date_edit)
        form.addRow("Date", date_row)

        # Due time
        self.due_time_edit = QTimeEdit()
        self.due_time_edit.setDisplayFormat("HH:mm")
        self.due_time_edit.setTime(QTime(9, 0))
        form.addRow("Heure", self.due_time_edit)

        # ── Reminder Override ──
        reminder_group = QGroupBox("Rappel personnalisé")
        reminder_lay = QHBoxLayout(reminder_group)
        self.reminder_check = QCheckBox("Personnaliser")
        self.reminder_spin = QSpinBox()
        self.reminder_spin.setRange(5, 1440)
        self.reminder_spin.setValue(30)
        self.reminder_spin.setSuffix(" min avant")
        self.reminder_spin.setEnabled(False)
        self.reminder_check.toggled.connect(self.reminder_spin.setEnabled)
        reminder_lay.addWidget(self.reminder_check)
        reminder_lay.addWidget(self.reminder_spin)
        form.addRow(reminder_group)

        # ── Recurrence ──
        recur_group = QGroupBox("Récurrence")
        recur_lay = QVBoxLayout(recur_group)

        self.recur_check = QCheckBox("Tâche récurrente")
        recur_lay.addWidget(self.recur_check)

        recur_detail = QWidget()
        recur_detail_lay = QFormLayout(recur_detail)
        recur_detail_lay.setContentsMargins(0, 4, 0, 0)

        self.recur_type = QComboBox()
        self.recur_type.addItems(["Quotidien", "Hebdomadaire", "Mensuel", "Personnalisé"])
        recur_detail_lay.addRow("Type", self.recur_type)

        self.recur_interval = QSpinBox()
        self.recur_interval.setRange(1, 365)
        self.recur_interval.setValue(1)
        self.recur_interval.setSuffix(" jour(s)")
        recur_detail_lay.addRow("Intervalle", self.recur_interval)

        self.recur_end_check = QCheckBox("Date de fin")
        self.recur_end_date = QDateEdit()
        self.recur_end_date.setCalendarPopup(True)
        self.recur_end_date.setDate(QDate.currentDate().addMonths(3))
        self.recur_end_date.setDisplayFormat("dd/MM/yyyy")
        self.recur_end_date.setEnabled(False)
        self.recur_end_check.toggled.connect(self.recur_end_date.setEnabled)
        end_row = QHBoxLayout()
        end_row.addWidget(self.recur_end_check)
        end_row.addWidget(self.recur_end_date)
        recur_detail_lay.addRow("Fin", end_row)

        recur_detail.setVisible(False)
        self.recur_check.toggled.connect(recur_detail.setVisible)
        recur_lay.addWidget(recur_detail)
        form.addRow(recur_group)

        self.recur_type.currentIndexChanged.connect(self._on_recur_type_change)

        # Progress (only for editing)
        if self.task:
            progress_group = QGroupBox("Progression")
            progress_lay = QVBoxLayout(progress_group)
            self.progress_slider = QSlider(Qt.Horizontal)
            self.progress_slider.setRange(0, 100)
            self.progress_slider.setValue(self.task.get('progress', 0))
            self.progress_label = QLabel(f"{self.task.get('progress', 0)}%")
            self.progress_label.setStyleSheet(f"font-weight:700;color:{COLORS['primary']};")
            self.progress_slider.valueChanged.connect(
                lambda v: self.progress_label.setText(f"{v}%")
            )
            p_row = QHBoxLayout()
            p_row.addWidget(self.progress_slider)
            p_row.addWidget(self.progress_label)
            progress_lay.addLayout(p_row)
            form.addRow(progress_group)

        scroll.setWidget(form_widget)
        layout.addWidget(scroll, 1)

        # ── Buttons ──
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        cancel_btn = QPushButton("Annuler")
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)

        save_btn = QPushButton("💾  Enregistrer")
        save_btn.setProperty("class", "primary_btn")
        save_btn.clicked.connect(self._save)
        btn_row.addWidget(save_btn)
        layout.addLayout(btn_row)

    def _on_recur_type_change(self, idx):
        suffixes = [" jour(s)", " semaine(s)", " mois", " jour(s)"]
        self.recur_interval.setSuffix(suffixes[idx])

    def _populate(self, task):
        self.title_edit.setText(task.get('title', ''))
        self.desc_edit.setPlainText(task.get('description', ''))
        cat = task.get('category', '')
        idx = self.category_edit.findText(cat)
        if idx >= 0:
            self.category_edit.setCurrentIndex(idx)
        else:
            self.category_edit.setCurrentText(cat)

        imp = task.get('importance', 2)
        for i in range(self.importance_combo.count()):
            if self.importance_combo.itemData(i) == imp:
                self.importance_combo.setCurrentIndex(i)
                break
        urg = task.get('urgency', 2)
        for i in range(self.urgency_combo.count()):
            if self.urgency_combo.itemData(i) == urg:
                self.urgency_combo.setCurrentIndex(i)
                break

        if task.get('due_date'):
            self.due_date_check.setChecked(True)
            y, m, d = task['due_date'].split('-')
            self.due_date_edit.setDate(QDate(int(y), int(m), int(d)))
        if task.get('due_time'):
            parts = task['due_time'].split(':')
            self.due_time_edit.setTime(QTime(int(parts[0]), int(parts[1])))

        if task.get('reminder_minutes') is not None:
            self.reminder_check.setChecked(True)
            self.reminder_spin.setValue(task['reminder_minutes'])

        if task.get('is_recurring'):
            self.recur_check.setChecked(True)
            pat = task.get('recurrence_pattern')
            if pat:
                try:
                    p = json.loads(pat) if isinstance(pat, str) else pat
                    type_map = {'daily': 0, 'weekly': 1, 'monthly': 2, 'custom': 3}
                    self.recur_type.setCurrentIndex(type_map.get(p.get('type', 'daily'), 0))
                    self.recur_interval.setValue(p.get('interval', 1))
                except (json.JSONDecodeError, AttributeError):
                    pass
            if task.get('recurrence_end_date'):
                self.recur_end_check.setChecked(True)
                y, m, d = task['recurrence_end_date'].split('-')
                self.recur_end_date.setDate(QDate(int(y), int(m), int(d)))

    def _save(self):
        title = self.title_edit.text().strip()
        if not title:
            QMessageBox.warning(self, "Erreur", "Le titre est obligatoire.")
            return
        self.accept()

    def get_data(self):
        data = {
            'title': self.title_edit.text().strip(),
            'description': self.desc_edit.toPlainText().strip(),
            'category': self.category_edit.currentText().strip(),
            'importance': self.importance_combo.currentData(),
            'urgency': self.urgency_combo.currentData(),
            'due_date': None,
            'due_time': self.due_time_edit.time().toString("HH:mm"),
            'reminder_minutes': None,
            'is_recurring': 0,
            'recurrence_pattern': None,
            'recurrence_end_date': None,
        }
        if self.due_date_check.isChecked():
            data['due_date'] = self.due_date_edit.date().toString("yyyy-MM-dd")
        if self.reminder_check.isChecked():
            data['reminder_minutes'] = self.reminder_spin.value()
        if self.recur_check.isChecked():
            data['is_recurring'] = 1
            type_map = {0: 'daily', 1: 'weekly', 2: 'monthly', 3: 'custom'}
            data['recurrence_pattern'] = {
                'type': type_map[self.recur_type.currentIndex()],
                'interval': self.recur_interval.value(),
            }
            if self.recur_end_check.isChecked():
                data['recurrence_end_date'] = self.recur_end_date.date().toString("yyyy-MM-dd")
        if self.task and hasattr(self, 'progress_slider'):
            data['progress'] = self.progress_slider.value()
        return data


class TaskDetailDialog(QDialog):
    """Read-only detail view with event history."""
    task_changed = Signal()

    def __init__(self, parent=None, task_id=None):
        super().__init__(parent)
        self.task_id = task_id
        self.setWindowTitle("Détails de la tâche")
        self.setMinimumSize(500, 450)
        self._build_ui()

    def _build_ui(self):
        task = db.get_task(self.task_id)
        if not task:
            return
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(24, 24, 24, 24)

        # Title
        title = QLabel(f"📋  {task['title']}")
        title.setStyleSheet(f"font-size:18px;font-weight:700;color:{COLORS['text_primary']};")
        title.setWordWrap(True)
        layout.addWidget(title)

        # Status badge
        status = task.get('status', 'todo')
        s_label = STATUS_LABELS.get(status, status)
        s_color = {'todo': COLORS['text_secondary'], 'in_progress': COLORS['info'],
                   'completed': COLORS['success'], 'abandoned': COLORS['danger']}.get(status, COLORS['text_secondary'])
        badge = QLabel(f"  {s_label}  ")
        badge.setStyleSheet(f"background:{s_color};color:white;border-radius:10px;padding:3px 12px;font-size:11px;font-weight:600;")
        badge.setFixedHeight(24)
        layout.addWidget(badge, alignment=Qt.AlignLeft)

        # Info grid
        info_frame = QFrame()
        info_frame.setProperty("class", "card")
        info_lay = QFormLayout(info_frame)
        info_lay.setSpacing(8)

        imp = task.get('importance', 2)
        imp_color = IMPORTANCE_COLORS.get(imp, COLORS['text_secondary'])
        info_lay.addRow("Importance:", QLabel(f"<span style='color:{imp_color};font-weight:600;'>{'●' * imp} {IMPORTANCE_LABELS.get(imp, '')}</span>"))

        urg = task.get('urgency', 2)
        urg_color = URGENCY_COLORS.get(urg, COLORS['text_secondary'])
        info_lay.addRow("Urgence:", QLabel(f"<span style='color:{urg_color};font-weight:600;'>{'▲' * urg} {URGENCY_LABELS.get(urg, '')}</span>"))

        if task.get('due_date'):
            dd = task['due_date']
            dt = task.get('due_time', '')
            info_lay.addRow("Échéance:", QLabel(f"{dd}  {dt}"))

        if task.get('category'):
            info_lay.addRow("Catégorie:", QLabel(task['category']))

        if task.get('description'):
            desc_lbl = QLabel(task['description'])
            desc_lbl.setWordWrap(True)
            desc_lbl.setStyleSheet(f"color:{COLORS['text_secondary']};")
            info_lay.addRow("Description:", desc_lbl)

        info_lay.addRow("Progression:", QLabel(f"{task.get('progress', 0)}%"))
        layout.addWidget(info_frame)

        # Event history
        events = db.get_task_events(self.task_id)
        if events:
            hist_label = QLabel("📜  Historique")
            hist_label.setStyleSheet(f"font-size:14px;font-weight:600;color:{COLORS['primary']};margin-top:8px;")
            layout.addWidget(hist_label)

            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setFrameShape(QFrame.NoFrame)
            scroll.setMaximumHeight(200)
            event_w = QWidget()
            event_lay = QVBoxLayout(event_w)
            event_lay.setSpacing(4)
            event_lay.setContentsMargins(0, 0, 0, 0)

            event_icons = {
                'created': '🆕', 'started': '▶️', 'paused': '⏸️',
                'completed': '✅', 'abandoned': '❌', 'edited': '✏️',
                'progress': '📊', 'rescheduled': '📅',
            }
            for ev in events:
                icon = event_icons.get(ev['event_type'], '•')
                dt_str = ev['event_date'][:16].replace('T', ' ')
                detail = ev.get('details', '')
                ev_lbl = QLabel(f"{icon}  {dt_str}  —  {detail}")
                ev_lbl.setStyleSheet(f"color:{COLORS['text_secondary']};font-size:12px;padding:2px 0;")
                event_lay.addWidget(ev_lbl)

            event_lay.addStretch()
            scroll.setWidget(event_w)
            layout.addWidget(scroll)

        layout.addStretch()

        # Close button
        close_btn = QPushButton("Fermer")
        close_btn.setProperty("class", "primary_btn")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn, alignment=Qt.AlignRight)


class ConfirmDialog(QDialog):
    """Simple confirmation dialog in French."""

    def __init__(self, parent, title, message, confirm_text="Confirmer", danger=False):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumWidth(350)
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        msg = QLabel(message)
        msg.setWordWrap(True)
        msg.setStyleSheet("font-size:14px;")
        layout.addWidget(msg)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        cancel = QPushButton("Annuler")
        cancel.clicked.connect(self.reject)
        btn_row.addWidget(cancel)

        confirm = QPushButton(confirm_text)
        confirm.setProperty("class", "danger_btn" if danger else "primary_btn")
        confirm.clicked.connect(self.accept)
        btn_row.addWidget(confirm)
        layout.addLayout(btn_row)
