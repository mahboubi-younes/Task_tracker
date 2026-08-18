"""
Dashboard page – personal assistant view with KPIs and insights.
"""
from datetime import date, datetime
from qt import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QScrollArea, QGridLayout, QPushButton, QSizePolicy,
    Qt, Signal
)

from styles import COLORS
import database as db


class StatCard(QFrame):
    """A single KPI stat card."""

    def __init__(self, icon, label, value, color, parent=None):
        super().__init__(parent)
        self.setProperty("class", "stat_card")
        self.setStyleSheet(f"""
            StatCard {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                    stop:0 {COLORS['bg_card']}, stop:1 {COLORS['bg_surface']});
                border-left: 4px solid {color};
                border-radius: 12px;
            }}
        """)
        lay = QVBoxLayout(self)
        lay.setSpacing(6)

        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet(f"font-size:24px;background:transparent;")
        lay.addWidget(icon_lbl)

        val_lbl = QLabel(str(value))
        val_lbl.setObjectName("stat_val")
        val_lbl.setStyleSheet(f"font-size:28px;font-weight:700;color:{color};background:transparent;")
        lay.addWidget(val_lbl)

        lbl = QLabel(label)
        lbl.setStyleSheet(f"font-size:12px;color:{COLORS['text_secondary']};background:transparent;")
        lay.addWidget(lbl)

        self.value_label = val_lbl

    def update_value(self, val):
        self.value_label.setText(str(val))


class InsightCard(QFrame):
    """Assistant insight/message card."""

    def __init__(self, icon, message, color=None, parent=None):
        super().__init__(parent)
        color = color or COLORS['primary']
        self.setProperty("class", "card")
        self.setStyleSheet(f"""
            InsightCard {{
                border-left: 4px solid {color};
                background: {COLORS['bg_card']};
                border-radius: 8px;
            }}
        """)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(12, 10, 12, 10)

        ic = QLabel(icon)
        ic.setStyleSheet("font-size:20px;background:transparent;")
        ic.setFixedWidth(32)
        lay.addWidget(ic)

        msg = QLabel(message)
        msg.setWordWrap(True)
        msg.setStyleSheet(f"color:{COLORS['text_primary']};font-size:13px;background:transparent;")
        lay.addWidget(msg, 1)


class DashboardPage(QWidget):
    """Main dashboard with KPIs and assistant insights."""
    navigate_to = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        main_lay = QVBoxLayout(self)
        main_lay.setContentsMargins(24, 24, 24, 24)
        main_lay.setSpacing(20)

        # Header
        header = QHBoxLayout()
        greeting = self._get_greeting()
        title = QLabel(f"👋  {greeting}")
        title.setStyleSheet(f"font-size:22px;font-weight:700;color:{COLORS['text_primary']};")
        header.addWidget(title)
        header.addStretch()

        DAYS_FR = {
            0: 'Lundi', 1: 'Mardi', 2: 'Mercredi', 3: 'Jeudi',
            4: 'Vendredi', 5: 'Samedi', 6: 'Dimanche'
        }
        MONTHS_FR = {
            1: 'janvier', 2: 'février', 3: 'mars', 4: 'avril', 5: 'mai', 6: 'juin',
            7: 'juillet', 8: 'août', 9: 'septembre', 10: 'octobre', 11: 'novembre', 12: 'décembre'
        }
        d = date.today()
        french_date = f"{DAYS_FR[d.weekday()]} {d.day} {MONTHS_FR[d.month]} {d.year}"

        today_lbl = QLabel(french_date)
        today_lbl.setStyleSheet(f"font-size:13px;color:{COLORS['text_secondary']};")
        header.addWidget(today_lbl)
        main_lay.addLayout(header)

        # Subtitle
        sub = QLabel("Votre assistant personnel de productivité")
        sub.setStyleSheet(f"font-size:13px;color:{COLORS['text_muted']};margin-top:-12px;")
        main_lay.addWidget(sub)

        # Scrollable content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        content = QWidget()
        content_lay = QVBoxLayout(content)
        content_lay.setSpacing(20)
        content_lay.setContentsMargins(0, 0, 8, 0)

        # ── KPI Cards ──
        self.cards_grid = QGridLayout()
        self.cards_grid.setSpacing(16)
        self.stat_cards = {}

        cards_data = [
            ('today', '📅', 'Tâches du jour', 0, COLORS['primary']),
            ('overdue', '⚠️', 'En retard', 0, COLORS['danger']),
            ('in_progress', '🔄', 'En cours', 0, COLORS['info']),
            ('todo', '📝', 'À faire', 0, COLORS['accent_gold']),
            ('completed', '✅', 'Terminées', 0, COLORS['success']),
            ('total', '📊', 'Total', 0, COLORS['text_secondary']),
        ]
        for i, (key, icon, label, val, color) in enumerate(cards_data):
            card = StatCard(icon, label, val, color)
            card.setCursor(Qt.PointingHandCursor)
            self.stat_cards[key] = card
            self.cards_grid.addWidget(card, i // 3, i % 3)

        content_lay.addLayout(self.cards_grid)

        # ── Assistant Insights ──
        insights_title = QLabel("💡  Conseils de votre assistant")
        insights_title.setStyleSheet(f"font-size:16px;font-weight:600;color:{COLORS['primary']};")
        content_lay.addWidget(insights_title)

        self.insights_container = QVBoxLayout()
        self.insights_container.setSpacing(8)
        content_lay.addLayout(self.insights_container)

        # ── Quick Actions ──
        actions_title = QLabel("⚡  Actions rapides")
        actions_title.setStyleSheet(f"font-size:16px;font-weight:600;color:{COLORS['primary']};margin-top:8px;")
        content_lay.addWidget(actions_title)

        actions_row = QHBoxLayout()
        actions_row.setSpacing(12)

        btn_new = QPushButton("➕  Nouvelle tâche")
        btn_new.setProperty("class", "primary_btn")
        btn_new.setCursor(Qt.PointingHandCursor)
        btn_new.setMinimumHeight(44)
        btn_new.clicked.connect(lambda: self.navigate_to.emit('new_task'))
        actions_row.addWidget(btn_new)

        btn_cal = QPushButton("📅  Calendrier")
        btn_cal.setCursor(Qt.PointingHandCursor)
        btn_cal.setMinimumHeight(44)
        btn_cal.clicked.connect(lambda: self.navigate_to.emit('calendar'))
        actions_row.addWidget(btn_cal)

        btn_hist = QPushButton("📜  Historique")
        btn_hist.setCursor(Qt.PointingHandCursor)
        btn_hist.setMinimumHeight(44)
        btn_hist.clicked.connect(lambda: self.navigate_to.emit('history'))
        actions_row.addWidget(btn_hist)

        content_lay.addLayout(actions_row)

        # ── Upcoming Tasks ──
        upcoming_title = QLabel("📌  Tâches à venir (3 jours)")
        upcoming_title.setStyleSheet(f"font-size:16px;font-weight:600;color:{COLORS['primary']};margin-top:8px;")
        content_lay.addWidget(upcoming_title)

        self.upcoming_container = QVBoxLayout()
        self.upcoming_container.setSpacing(6)
        content_lay.addLayout(self.upcoming_container)

        content_lay.addStretch()
        scroll.setWidget(content)
        main_lay.addWidget(scroll, 1)

    def _get_greeting(self):
        hour = datetime.now().hour
        if hour < 12:
            return "Bonjour !"
        elif hour < 18:
            return "Bon après-midi !"
        else:
            return "Bonsoir !"

    def refresh_data(self):
        stats = db.get_task_stats()

        # Update stat cards
        for key, card in self.stat_cards.items():
            card.update_value(stats.get(key, 0))

        # Update insights
        self._clear_layout(self.insights_container)
        insights = self._generate_insights(stats)
        for icon, msg, color in insights:
            self.insights_container.addWidget(InsightCard(icon, msg, color))

        if not insights:
            self.insights_container.addWidget(
                InsightCard("🎉", "Tout est sous contrôle ! Aucune alerte pour le moment.", COLORS['success'])
            )

        # Update upcoming tasks
        self._clear_layout(self.upcoming_container)
        upcoming = db.get_tasks_due_soon(3)
        if upcoming:
            for task in upcoming[:8]:
                self.upcoming_container.addWidget(self._make_task_mini_card(task))
        else:
            no_task = QLabel("  Aucune tâche prévue dans les 3 prochains jours.")
            no_task.setStyleSheet(f"color:{COLORS['text_muted']};font-size:13px;padding:8px;")
            self.upcoming_container.addWidget(no_task)

    def _generate_insights(self, stats):
        insights = []
        if stats['overdue'] > 0:
            insights.append((
                "🔴",
                f"Attention ! Vous avez {stats['overdue']} tâche(s) en retard. "
                f"Pensez à les traiter ou à les reporter.",
                COLORS['danger']
            ))
        if stats['today'] > 0:
            insights.append((
                "📅",
                f"Vous avez {stats['today']} tâche(s) prévue(s) aujourd'hui. Courage !",
                COLORS['primary']
            ))
        if stats['in_progress'] > 3:
            insights.append((
                "💡",
                f"Vous avez {stats['in_progress']} tâches en cours simultanément. "
                f"Concentrez-vous sur une ou deux pour être plus efficace.",
                COLORS['accent_gold']
            ))
        if stats['completed'] > 0 and stats['total'] > 0:
            pct = int(stats['completed'] / stats['total'] * 100)
            if pct >= 75:
                insights.append((
                    "🏆",
                    f"Excellent ! {pct}% de vos tâches sont terminées. Continuez ainsi !",
                    COLORS['success']
                ))
        if stats['todo'] > 10:
            insights.append((
                "📋",
                f"Vous avez {stats['todo']} tâches en attente. "
                f"Priorisez les plus urgentes pour avancer sereinement.",
                COLORS['info']
            ))
        return insights

    def _make_task_mini_card(self, task):
        from styles import IMPORTANCE_COLORS, URGENCY_COLORS, STATUS_LABELS
        frame = QFrame()
        frame.setProperty("class", "card")
        frame.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['bg_card']};
                border-left: 3px solid {IMPORTANCE_COLORS.get(task.get('importance', 2), COLORS['primary'])};
                padding: 8px 12px;
                border-radius: 8px;
            }}
        """)
        lay = QHBoxLayout(frame)
        lay.setContentsMargins(8, 6, 8, 6)
        lay.setSpacing(12)

        title = QLabel(task['title'])
        title.setStyleSheet(f"font-weight:500;color:{COLORS['text_primary']};font-size:13px;background:transparent;")
        lay.addWidget(title, 1)

        if task.get('due_date'):
            due = QLabel(f"📅 {task['due_date']}")
            due.setStyleSheet(f"color:{COLORS['text_secondary']};font-size:11px;background:transparent;")
            lay.addWidget(due)

        status = task.get('status', 'todo')
        s_color = {'todo': COLORS['text_secondary'], 'in_progress': COLORS['info'],
                   'completed': COLORS['success']}.get(status, COLORS['text_secondary'])
        s_lbl = QLabel(STATUS_LABELS.get(status, ''))
        s_lbl.setStyleSheet(f"color:{s_color};font-size:11px;font-weight:600;background:transparent;")
        lay.addWidget(s_lbl)

        return frame

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
