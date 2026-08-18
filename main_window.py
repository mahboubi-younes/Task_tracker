"""
Main window with sidebar navigation, system tray, and reminder engine.
"""
import sys
from datetime import datetime, date, timedelta
from qt import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QStackedWidget, QFrame, QSystemTrayIcon,
    QMenu, QApplication, Qt, QTimer, QSize, QIcon, QPixmap,
    QPainter, QColor, QFont, QAction, QPen
)

from styles import COLORS, get_stylesheet
import database as db

from pages.dashboard import DashboardPage
from pages.tasks import TasksPage
from pages.calendar_view import CalendarPage
from pages.history import HistoryPage
from pages.settings import SettingsPage
from dialogs import TaskDialog


def _create_app_icon():
    """Create a stunning, minimalist checklist icon using QPainter."""
    pix = QPixmap(128, 128)
    pix.fill(Qt.transparent)
    p = QPainter(pix)
    p.setRenderHint(QPainter.Antialiasing)

    # Draw rounded rect background
    p.setPen(Qt.NoPen)
    p.setBrush(QColor('#131324'))
    p.drawRoundedRect(8, 8, 112, 112, 28, 28)

    # Draw modern border
    pen = QPen(QColor('#6c63ff'))
    pen.setWidth(4)
    p.setPen(pen)
    p.setBrush(Qt.NoBrush)
    p.drawRoundedRect(8, 8, 112, 112, 28, 28)

    # Draw top minimalist dots
    p.setPen(Qt.NoPen)
    p.setBrush(QColor('#3a3b5c'))
    p.drawEllipse(36, 28, 6, 6)
    p.drawEllipse(52, 28, 6, 6)
    p.drawEllipse(68, 28, 6, 6)

    # Draw modern checkmark
    pen = QPen(QColor('#4ecdc4'))
    pen.setWidth(8)
    pen.setCapStyle(Qt.RoundCap)
    pen.setJoinStyle(Qt.RoundJoin)
    p.setPen(pen)

    from qt import QPainterPath
    path = QPainterPath()
    path.moveTo(40, 68)
    path.lineTo(56, 84)
    path.lineTo(88, 48)
    p.drawPath(path)

    p.end()
    return QIcon(pix)


class SidebarButton(QPushButton):
    """Styled navigation button."""

    def __init__(self, icon_text, label, parent=None):
        super().__init__(f"  {icon_text}   {label}", parent)
        self.setProperty("class", "nav_btn")
        self.setCursor(Qt.PointingHandCursor)
        self.setCheckable(True)
        self.setMinimumHeight(44)

    def set_active(self, active):
        self.setProperty("active", "true" if active else "false")
        self.setChecked(active)
        self.style().unpolish(self)
        self.style().polish(self)


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mon Assistant – Gestionnaire de Tâches")
        self.setMinimumSize(1100, 700)
        self.resize(1280, 800)
        self.setWindowIcon(_create_app_icon())

        # Apply global stylesheet
        self.setStyleSheet(get_stylesheet())

        self._build_ui()
        self._setup_tray()
        self._setup_reminder_timer()

        # Initial page
        self._navigate(0)
        self._refresh_current_page()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Sidebar ──
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar_lay = QVBoxLayout(sidebar)
        sidebar_lay.setContentsMargins(0, 0, 0, 0)
        sidebar_lay.setSpacing(0)

        # Logo
        logo = QLabel("  ✓ Mon Assistant")
        logo.setObjectName("sidebar_logo")
        sidebar_lay.addWidget(logo)

        subtitle = QLabel("  Productivité personnelle")
        subtitle.setObjectName("sidebar_subtitle")
        sidebar_lay.addWidget(subtitle)

        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet(f"color:{COLORS['border']};margin:0 12px;")
        sidebar_lay.addWidget(sep)

        # Navigation buttons
        self.nav_buttons = []
        nav_items = [
            ("🏠", "Tableau de bord"),
            ("📋", "Mes tâches"),
            ("📅", "Calendrier"),
            ("📜", "Historique"),
            ("⚙️", "Paramètres"),
        ]

        for i, (icon, label) in enumerate(nav_items):
            btn = SidebarButton(icon, label)
            btn.clicked.connect(lambda checked, idx=i: self._navigate(idx))
            sidebar_lay.addWidget(btn)
            self.nav_buttons.append(btn)

        sidebar_lay.addStretch()

        # Overdue alert in sidebar
        self.sidebar_alert = QLabel("")
        self.sidebar_alert.setWordWrap(True)
        self.sidebar_alert.setStyleSheet(f"""
            color: {COLORS['danger']};
            font-size: 11px;
            padding: 12px 16px;
            background: rgba(255, 107, 107, 0.1);
            border-radius: 8px;
            margin: 8px;
        """)
        self.sidebar_alert.setVisible(False)
        sidebar_lay.addWidget(self.sidebar_alert)

        # Version & Watermark
        watermark = QLabel("  © Younes M.")
        watermark.setStyleSheet(f"color:{COLORS['text_muted']};font-size:11px;font-weight:600;padding:8px 16px 0 16px;")
        sidebar_lay.addWidget(watermark)

        ver = QLabel("  v1.1")
        ver.setStyleSheet(f"color:{COLORS['text_muted']};font-size:10px;padding:0 16px 8px 16px;")
        sidebar_lay.addWidget(ver)

        root.addWidget(sidebar)

        # ── Content area ──
        self.stack = QStackedWidget()

        self.dashboard_page = DashboardPage()
        self.dashboard_page.navigate_to.connect(self._handle_dashboard_nav)

        self.tasks_page = TasksPage()
        self.tasks_page.task_created.connect(self._on_task_changed)

        self.calendar_page = CalendarPage()
        self.history_page = HistoryPage()
        self.settings_page = SettingsPage()

        self.stack.addWidget(self.dashboard_page)
        self.stack.addWidget(self.tasks_page)
        self.stack.addWidget(self.calendar_page)
        self.stack.addWidget(self.history_page)
        self.stack.addWidget(self.settings_page)

        root.addWidget(self.stack, 1)

    def _navigate(self, idx):
        for i, btn in enumerate(self.nav_buttons):
            btn.set_active(i == idx)
        self.stack.setCurrentIndex(idx)
        self._refresh_current_page()

    def _refresh_current_page(self):
        page = self.stack.currentWidget()
        if hasattr(page, 'refresh_data'):
            page.refresh_data()
        self._update_sidebar_alert()

    def _update_sidebar_alert(self):
        overdue = db.get_overdue_tasks()
        today_tasks = db.get_tasks_due_today()

        parts = []
        if overdue:
            parts.append(f"⚠️ {len(overdue)} tâche(s) en retard")
        if today_tasks:
            parts.append(f"📅 {len(today_tasks)} tâche(s) aujourd'hui")

        if parts:
            self.sidebar_alert.setText("\n".join(parts))
            self.sidebar_alert.setVisible(True)
        else:
            self.sidebar_alert.setVisible(False)

    def _handle_dashboard_nav(self, target):
        if target == 'new_task':
            self._navigate(1)  # Go to tasks page
            self.tasks_page._create_task()
        elif target == 'calendar':
            self._navigate(2)
        elif target == 'history':
            self._navigate(3)

    def _on_task_changed(self):
        """When a task is created/modified, refresh relevant pages."""
        self._update_sidebar_alert()

    # ── System Tray ──

    def _setup_tray(self):
        self.tray = QSystemTrayIcon(_create_app_icon(), self)
        tray_menu = QMenu()

        show_action = QAction("Ouvrir Mon Assistant", self)
        show_action.triggered.connect(self._show_window)
        tray_menu.addAction(show_action)

        new_task_action = QAction("Nouvelle tâche", self)
        new_task_action.triggered.connect(self._quick_new_task)
        tray_menu.addAction(new_task_action)

        tray_menu.addSeparator()

        quit_action = QAction("Quitter", self)
        quit_action.triggered.connect(self._quit_app)
        tray_menu.addAction(quit_action)

        self.tray.setContextMenu(tray_menu)
        self.tray.activated.connect(self._on_tray_activated)
        self.tray.setToolTip("Mon Assistant – Gestionnaire de Tâches")
        self.tray.show()

    def _show_window(self):
        self.showNormal()
        self.activateWindow()
        self.raise_()

    def _on_tray_activated(self, reason):
        # Compatible with both PySide6 (enum class) and PyQt5 (flat enum)
        try:
            double_click = QSystemTrayIcon.ActivationReason.DoubleClick
        except AttributeError:
            double_click = QSystemTrayIcon.DoubleClick
        if reason == double_click:
            self._show_window()

    def _quick_new_task(self):
        self._show_window()
        self._navigate(1)
        self.tasks_page._create_task()

    def _quit_app(self):
        self.tray.hide()
        QApplication.quit()

    def closeEvent(self, event):
        # Minimize to tray instead of closing
        event.ignore()
        self.hide()
        try:
            info_icon = QSystemTrayIcon.MessageIcon.Information
        except AttributeError:
            info_icon = QSystemTrayIcon.Information
        self.tray.showMessage(
            "Mon Assistant",
            "L'application continue en arrière-plan. "
            "Double-cliquez sur l'icône pour la rouvrir.",
            info_icon,
            2000
        )

    # ── Reminder Engine ──

    def _setup_reminder_timer(self):
        self.reminder_timer = QTimer(self)
        self.reminder_timer.timeout.connect(self._check_reminders)
        self.reminder_timer.start(60000)  # Check every minute
        # Also check immediately on startup
        QTimer.singleShot(2000, self._check_reminders)

    def _check_reminders(self):
        if db.get_setting('reminder_enabled', '1') != '1':
            return

        default_minutes = int(db.get_setting('reminder_minutes', '30'))
        now = datetime.now()
        today_str = date.today().isoformat()

        # Get tasks due today that aren't completed/abandoned
        tasks = db.get_tasks_due_today()

        for task in tasks:
            if not task.get('due_date') or not task.get('due_time'):
                continue

            # Calculate reminder time
            reminder_min = task.get('reminder_minutes')
            if reminder_min is None:
                reminder_min = default_minutes

            try:
                due_dt = datetime.strptime(
                    f"{task['due_date']} {task['due_time']}", "%Y-%m-%d %H:%M"
                )
            except ValueError:
                continue

            reminder_dt = due_dt - timedelta(minutes=reminder_min)
            reminder_key = f"{task['id']}_{today_str}_{reminder_min}"

            # Check if we should trigger
            if reminder_dt <= now <= due_dt:
                if not db.is_reminder_dismissed(task['id'], reminder_key):
                    self._show_reminder(task, due_dt)
                    db.dismiss_reminder(task['id'], reminder_key)

            # Check overdue
            if now > due_dt:
                overdue_key = f"overdue_{task['id']}_{today_str}"
                if not db.is_reminder_dismissed(task['id'], overdue_key):
                    self._show_overdue_reminder(task)
                    db.dismiss_reminder(task['id'], overdue_key)

    def _show_reminder(self, task, due_dt):
        time_str = due_dt.strftime("%H:%M")
        try:
            info_icon = QSystemTrayIcon.MessageIcon.Information
        except AttributeError:
            info_icon = QSystemTrayIcon.Information
        self.tray.showMessage(
            "⏰  Rappel – Mon Assistant",
            f"La tâche « {task['title']} » est prévue à {time_str}.\n"
            f"N'oubliez pas de vous y mettre !",
            info_icon,
            5000
        )

    def _show_overdue_reminder(self, task):
        try:
            warn_icon = QSystemTrayIcon.MessageIcon.Warning
        except AttributeError:
            warn_icon = QSystemTrayIcon.Warning
        self.tray.showMessage(
            "⚠️  Tâche en retard",
            f"La tâche « {task['title']} » est en retard.\n"
            f"Pensez à la terminer ou à la reporter.",
            warn_icon,
            5000
        )
