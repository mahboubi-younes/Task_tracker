"""
Settings page – global reminder defaults, data management.
"""
from qt import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QPushButton, QSpinBox, QCheckBox, QGroupBox, QFormLayout,
    QMessageBox, QScrollArea, Qt
)

from styles import COLORS
import database as db
from dialogs import ConfirmDialog


class SettingsPage(QWidget):
    """Application settings."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        main = QVBoxLayout(self)
        main.setContentsMargins(24, 24, 24, 24)
        main.setSpacing(16)

        # Header
        title = QLabel("⚙️  Paramètres")
        title.setProperty("class", "section_title")
        main.addWidget(title)

        sub = QLabel("Configurez votre assistant de productivité")
        sub.setStyleSheet(f"color:{COLORS['text_muted']};font-size:13px;margin-top:-8px;")
        main.addWidget(sub)

        # Scrollable content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        content = QWidget()
        content_lay = QVBoxLayout(content)
        content_lay.setSpacing(20)
        content_lay.setContentsMargins(0, 0, 8, 0)

        # ── Reminders Group ──
        reminder_group = QGroupBox("🔔  Rappels")
        r_lay = QFormLayout(reminder_group)
        r_lay.setSpacing(12)
        r_lay.setContentsMargins(16, 24, 16, 16)

        self.reminder_enabled = QCheckBox("Activer les rappels")
        r_lay.addRow(self.reminder_enabled)

        self.reminder_minutes = QSpinBox()
        self.reminder_minutes.setRange(5, 1440)
        self.reminder_minutes.setSuffix(" minutes avant l'échéance")
        self.reminder_minutes.setMinimumWidth(250)
        r_lay.addRow("Délai par défaut :", self.reminder_minutes)

        self.notification_sound = QCheckBox("Son de notification")
        r_lay.addRow(self.notification_sound)

        reminder_info = QLabel(
            "💡  Le rappel par défaut s'applique à toutes les tâches, sauf celles "
            "avec un rappel personnalisé."
        )
        reminder_info.setWordWrap(True)
        reminder_info.setStyleSheet(f"color:{COLORS['text_muted']};font-size:12px;padding:4px 0;")
        r_lay.addRow(reminder_info)

        content_lay.addWidget(reminder_group)

        # ── Data Management Group ──
        data_group = QGroupBox("💾  Données")
        d_lay = QVBoxLayout(data_group)
        d_lay.setSpacing(12)
        d_lay.setContentsMargins(16, 24, 16, 16)

        db_path_lbl = QLabel(f"Base de données : {db.get_db_path()}")
        db_path_lbl.setStyleSheet(f"color:{COLORS['text_secondary']};font-size:12px;")
        db_path_lbl.setWordWrap(True)
        d_lay.addWidget(db_path_lbl)

        btn_row = QHBoxLayout()

        clear_history_btn = QPushButton("🧹  Purger l'historique")
        clear_history_btn.setProperty("class", "danger_btn")
        clear_history_btn.setCursor(Qt.PointingHandCursor)
        clear_history_btn.clicked.connect(self._clear_history)
        btn_row.addWidget(clear_history_btn)

        clear_all_btn = QPushButton("⚠️  Supprimer toutes les tâches")
        clear_all_btn.setProperty("class", "danger_btn")
        clear_all_btn.setCursor(Qt.PointingHandCursor)
        clear_all_btn.clicked.connect(self._clear_all)
        btn_row.addWidget(clear_all_btn)

        btn_row.addStretch()
        d_lay.addLayout(btn_row)

        content_lay.addWidget(data_group)

        # ── About ──
        about_group = QGroupBox("ℹ️  À propos")
        a_lay = QVBoxLayout(about_group)
        a_lay.setContentsMargins(16, 24, 16, 16)

        about_text = QLabel(
            "<b>Mon Assistant – Gestionnaire de Tâches</b><br>"
            "Version 1.1<br><br>"
            "Développé par <b>Younes M.</b> pour une productivité optimale.<br><br>"
            "Votre assistant personnel de productivité.<br>"
            "Toutes les données sont stockées localement sur votre ordinateur.<br>"
            "Aucune connexion internet requise."
        )
        about_text.setWordWrap(True)
        about_text.setStyleSheet(f"color:{COLORS['text_secondary']};font-size:13px;line-height:1.5;")
        a_lay.addWidget(about_text)
        content_lay.addWidget(about_group)

        content_lay.addStretch()

        # Save button
        save_row = QHBoxLayout()
        save_row.addStretch()
        save_btn = QPushButton("💾  Enregistrer les paramètres")
        save_btn.setProperty("class", "primary_btn")
        save_btn.setMinimumHeight(42)
        save_btn.setMinimumWidth(220)
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.clicked.connect(self._save_settings)
        save_row.addWidget(save_btn)
        content_lay.addLayout(save_row)

        scroll.setWidget(content)
        main.addWidget(scroll, 1)

    def refresh_data(self):
        self.reminder_enabled.setChecked(db.get_setting('reminder_enabled', '1') == '1')
        self.reminder_minutes.setValue(int(db.get_setting('reminder_minutes', '30')))
        self.notification_sound.setChecked(db.get_setting('notification_sound', '1') == '1')

    def _save_settings(self):
        db.set_setting('reminder_enabled', '1' if self.reminder_enabled.isChecked() else '0')
        db.set_setting('reminder_minutes', str(self.reminder_minutes.value()))
        db.set_setting('notification_sound', '1' if self.notification_sound.isChecked() else '0')
        QMessageBox.information(self, "Succès", "✅  Paramètres enregistrés avec succès !")

    def _clear_history(self):
        dlg = ConfirmDialog(
            self, "Purger l'historique",
            "Supprimer toutes les tâches terminées et abandonnées ?\n"
            "Cette action est irréversible.",
            "Purger", danger=True
        )
        if dlg.exec() == ConfirmDialog.Accepted:
            conn = db.get_connection()
            conn.execute("DELETE FROM tasks WHERE status IN ('completed','abandoned')")
            conn.commit()
            conn.close()
            QMessageBox.information(self, "Succès", "Historique purgé.")

    def _clear_all(self):
        dlg = ConfirmDialog(
            self, "Tout supprimer",
            "⚠️  Supprimer TOUTES les tâches, l'historique et les événements ?\n"
            "Cette action est IRRÉVERSIBLE !",
            "Tout supprimer", danger=True
        )
        if dlg.exec() == ConfirmDialog.Accepted:
            conn = db.get_connection()
            conn.execute("DELETE FROM task_events")
            conn.execute("DELETE FROM skipped_occurrences")
            conn.execute("DELETE FROM dismissed_reminders")
            conn.execute("DELETE FROM tasks")
            conn.commit()
            conn.close()
            QMessageBox.information(self, "Succès", "Toutes les données ont été supprimées.")
