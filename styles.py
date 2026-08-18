"""
QSS Stylesheet for the French Task Tracker.
Modern dark theme with priority/urgency color coding.
"""

# Color palette
COLORS = {
    'bg_dark': '#0f0f1a',
    'bg_main': '#1a1b2e',
    'bg_surface': '#252642',
    'bg_card': '#2d2e4a',
    'bg_hover': '#35365a',
    'bg_input': '#1e1f36',
    'border': '#3a3b5c',
    'border_focus': '#6c63ff',
    'primary': '#6c63ff',
    'primary_hover': '#7f78ff',
    'primary_dark': '#5a52d9',
    'accent_coral': '#ff6b6b',
    'accent_teal': '#4ecdc4',
    'accent_gold': '#ffd93d',
    'accent_blue': '#45b7d1',
    'accent_pink': '#f06292',
    'text_primary': '#e8e8f0',
    'text_secondary': '#9a9ab8',
    'text_muted': '#6b6b88',
    'success': '#4ecdc4',
    'warning': '#ffd93d',
    'danger': '#ff6b6b',
    'info': '#45b7d1',
}

IMPORTANCE_COLORS = {
    1: '#5a9e6f',   # Faible - green
    2: '#45b7d1',   # Moyenne - blue
    3: '#ffa726',   # Haute - orange
    4: '#ff5252',   # Critique - red
}

URGENCY_COLORS = {
    1: '#5a9e6f',
    2: '#45b7d1',
    3: '#ffa726',
    4: '#ff5252',
}

STATUS_COLORS = {
    'todo': '#9a9ab8',
    'in_progress': '#45b7d1',
    'completed': '#4ecdc4',
    'abandoned': '#ff6b6b',
}

IMPORTANCE_LABELS = {1: 'Faible', 2: 'Moyenne', 3: 'Haute', 4: 'Critique'}
URGENCY_LABELS = {1: 'Faible', 2: 'Moyenne', 3: 'Haute', 4: 'Critique'}
STATUS_LABELS = {
    'todo': 'À faire',
    'in_progress': 'En cours',
    'completed': 'Terminée',
    'abandoned': 'Abandonnée',
}


def get_stylesheet():
    return f"""
    /* ── Global ───────────────────────────────────── */
    QMainWindow, QWidget {{
        background-color: {COLORS['bg_main']};
        color: {COLORS['text_primary']};
        font-family: 'Segoe UI', 'Roboto', sans-serif;
        font-size: 14px;
    }}

    /* ── Sidebar ──────────────────────────────────── */
    #sidebar {{
        background-color: {COLORS['bg_dark']};
        border-right: 1px solid {COLORS['border']};
        min-width: 220px;
        max-width: 220px;
    }}
    #sidebar_logo {{
        color: {COLORS['primary']};
        font-size: 22px;
        font-weight: bold;
        padding: 20px 16px 10px 16px;
    }}
    #sidebar_subtitle {{
        color: {COLORS['text_muted']};
        font-size: 13px;
        padding: 0 16px 20px 16px;
    }}
    QPushButton.nav_btn {{
        background: transparent;
        color: {COLORS['text_secondary']};
        border: none;
        border-radius: 8px;
        padding: 12px 16px;
        text-align: left;
        font-size: 14px;
        font-weight: 500;
        margin: 2px 8px;
    }}
    QPushButton.nav_btn:hover {{
        background-color: {COLORS['bg_hover']};
        color: {COLORS['text_primary']};
    }}
    QPushButton.nav_btn[active="true"] {{
        background-color: {COLORS['primary']};
        color: white;
        font-weight: 600;
    }}

    /* ── Cards ────────────────────────────────────── */
    QFrame.card {{
        background-color: {COLORS['bg_card']};
        border: 1px solid {COLORS['border']};
        border-radius: 12px;
        padding: 16px;
    }}
    QFrame.card:hover {{
        border-color: {COLORS['primary']};
    }}
    QFrame.stat_card {{
        background-color: {COLORS['bg_card']};
        border: 1px solid {COLORS['border']};
        border-radius: 12px;
        padding: 20px;
        min-width: 160px;
    }}

    /* ── Inputs ───────────────────────────────────── */
    QLineEdit, QTextEdit, QPlainTextEdit {{
        background-color: {COLORS['bg_input']};
        color: {COLORS['text_primary']};
        border: 1px solid {COLORS['border']};
        border-radius: 8px;
        padding: 8px 12px;
        font-size: 14px;
        selection-background-color: {COLORS['primary']};
    }}
    QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
        border-color: {COLORS['border_focus']};
    }}
    QComboBox {{
        background-color: {COLORS['bg_input']};
        color: {COLORS['text_primary']};
        border: 1px solid {COLORS['border']};
        border-radius: 8px;
        padding: 8px 12px;
        font-size: 14px;
        min-width: 120px;
    }}
    QComboBox::drop-down {{
        border: none;
        width: 24px;
    }}
    QComboBox::down-arrow {{
        image: none;
        border: none;
    }}
    QComboBox QAbstractItemView {{
        background-color: {COLORS['bg_card']};
        color: {COLORS['text_primary']};
        border: 1px solid {COLORS['border']};
        border-radius: 4px;
        padding: 4px;
        selection-background-color: {COLORS['primary']};
    }}
    QSpinBox, QDoubleSpinBox {{
        background-color: {COLORS['bg_input']};
        color: {COLORS['text_primary']};
        border: 1px solid {COLORS['border']};
        border-radius: 8px;
        padding: 8px 12px;
    }}
    QDateEdit, QTimeEdit {{
        background-color: {COLORS['bg_input']};
        color: {COLORS['text_primary']};
        border: 1px solid {COLORS['border']};
        border-radius: 8px;
        padding: 8px 12px;
    }}
    QDateEdit::drop-down, QTimeEdit::drop-down {{
        border: none;
        width: 24px;
    }}

    /* ── Buttons ──────────────────────────────────── */
    QPushButton {{
        background-color: {COLORS['bg_card']};
        color: {COLORS['text_primary']};
        border: 1px solid {COLORS['border']};
        border-radius: 8px;
        padding: 8px 16px;
        font-size: 14px;
        font-weight: 500;
    }}
    QPushButton:hover {{
        background-color: {COLORS['bg_hover']};
        border-color: {COLORS['primary']};
    }}
    QPushButton:pressed {{
        background-color: {COLORS['primary_dark']};
    }}
    QPushButton.primary_btn {{
        background-color: {COLORS['primary']};
        color: white;
        border: none;
        font-weight: 600;
    }}
    QPushButton.primary_btn:hover {{
        background-color: {COLORS['primary_hover']};
    }}
    QPushButton.danger_btn {{
        background-color: transparent;
        color: {COLORS['danger']};
        border: 1px solid {COLORS['danger']};
    }}
    QPushButton.danger_btn:hover {{
        background-color: {COLORS['danger']};
        color: white;
    }}
    QPushButton.success_btn {{
        background-color: transparent;
        color: {COLORS['success']};
        border: 1px solid {COLORS['success']};
    }}
    QPushButton.success_btn:hover {{
        background-color: {COLORS['success']};
        color: white;
    }}

    /* ── Scroll Area ──────────────────────────────── */
    QScrollArea {{
        border: none;
        background: transparent;
    }}
    QScrollArea > QWidget > QWidget {{
        background: transparent;
    }}
    QScrollBar:vertical {{
        background-color: {COLORS['bg_dark']};
        width: 8px;
        border-radius: 4px;
        margin: 0;
    }}
    QScrollBar::handle:vertical {{
        background-color: {COLORS['border']};
        min-height: 30px;
        border-radius: 4px;
    }}
    QScrollBar::handle:vertical:hover {{
        background-color: {COLORS['primary']};
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0;
    }}
    QScrollBar:horizontal {{
        background-color: {COLORS['bg_dark']};
        height: 8px;
        border-radius: 4px;
    }}
    QScrollBar::handle:horizontal {{
        background-color: {COLORS['border']};
        min-width: 30px;
        border-radius: 4px;
    }}
    QScrollBar::handle:horizontal:hover {{
        background-color: {COLORS['primary']};
    }}
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
        width: 0;
    }}

    /* ── Labels ───────────────────────────────────── */
    QLabel {{
        color: {COLORS['text_primary']};
        background: transparent;
    }}
    QLabel.section_title {{
        font-size: 26px;
        font-weight: 700;
        color: {COLORS['text_primary']};
        padding: 0;
    }}
    QLabel.section_subtitle {{
        font-size: 14px;
        color: {COLORS['text_secondary']};
    }}
    QLabel.stat_value {{
        font-size: 34px;
        font-weight: 700;
    }}
    QLabel.stat_label {{
        font-size: 14px;
        color: {COLORS['text_secondary']};
    }}
    QLabel.badge {{
        font-size: 13px;
        font-weight: 600;
        padding: 3px 10px;
        border-radius: 10px;
    }}

    /* ── Tab Widget ───────────────────────────────── */
    QTabWidget::pane {{
        border: 1px solid {COLORS['border']};
        border-radius: 8px;
        background: {COLORS['bg_surface']};
        top: -1px;
    }}
    QTabBar::tab {{
        background: {COLORS['bg_card']};
        color: {COLORS['text_secondary']};
        border: 1px solid {COLORS['border']};
        border-bottom: none;
        border-radius: 8px 8px 0 0;
        padding: 8px 20px;
        margin-right: 2px;
    }}
    QTabBar::tab:selected {{
        background: {COLORS['bg_surface']};
        color: {COLORS['primary']};
        font-weight: 600;
    }}

    /* ── CheckBox ─────────────────────────────────── */
    QCheckBox {{
        color: {COLORS['text_primary']};
        spacing: 8px;
    }}
    QCheckBox::indicator {{
        width: 18px;
        height: 18px;
        border-radius: 4px;
        border: 2px solid {COLORS['border']};
        background: {COLORS['bg_input']};
    }}
    QCheckBox::indicator:checked {{
        background: {COLORS['primary']};
        border-color: {COLORS['primary']};
    }}

    /* ── Progress Bar ─────────────────────────────── */
    QProgressBar {{
        background-color: {COLORS['bg_input']};
        border: none;
        border-radius: 6px;
        height: 12px;
        text-align: center;
        color: transparent;
    }}
    QProgressBar::chunk {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 {COLORS['primary']}, stop:1 {COLORS['accent_teal']});
        border-radius: 6px;
    }}

    /* ── Slider ───────────────────────────────────── */
    QSlider::groove:horizontal {{
        background: {COLORS['bg_input']};
        height: 6px;
        border-radius: 3px;
    }}
    QSlider::handle:horizontal {{
        background: {COLORS['primary']};
        width: 16px;
        height: 16px;
        margin: -5px 0;
        border-radius: 8px;
    }}
    QSlider::sub-page:horizontal {{
        background: {COLORS['primary']};
        border-radius: 3px;
    }}

    /* ── Dialog ───────────────────────────────────── */
    QDialog {{
        background-color: {COLORS['bg_surface']};
    }}

    /* ── ToolTip ──────────────────────────────────── */
    QToolTip {{
        background-color: {COLORS['bg_card']};
        color: {COLORS['text_primary']};
        border: 1px solid {COLORS['border']};
        border-radius: 6px;
        padding: 6px 10px;
        font-size: 13px;
    }}

    /* ── Calendar Day Cells ───────────────────────── */
    QPushButton.cal_day {{
        background: {COLORS['bg_card']};
        border: 1px solid {COLORS['border']};
        border-radius: 8px;
        padding: 4px;
        font-size: 14px;
        min-height: 70px;
    }}
    QPushButton.cal_day:hover {{
        border-color: {COLORS['primary']};
        background: {COLORS['bg_hover']};
    }}
    QPushButton.cal_day[today="true"] {{
        border-color: {COLORS['primary']};
        border-width: 2px;
    }}
    QPushButton.cal_day[selected="true"] {{
        background: {COLORS['primary_dark']};
    }}
    QPushButton.cal_day[outside="true"] {{
        background: {COLORS['bg_dark']};
        color: {COLORS['text_muted']};
    }}

    /* ── Menu ─────────────────────────────────────── */
    QMenu {{
        background-color: {COLORS['bg_card']};
        border: 1px solid {COLORS['border']};
        border-radius: 8px;
        padding: 4px;
    }}
    QMenu::item {{
        padding: 8px 24px;
        border-radius: 4px;
    }}
    QMenu::item:selected {{
        background-color: {COLORS['primary']};
        color: white;
    }}

    /* ── GroupBox ──────────────────────────────────── */
    QGroupBox {{
        border: 1px solid {COLORS['border']};
        border-radius: 8px;
        margin-top: 16px;
        padding-top: 16px;
        font-weight: 600;
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        left: 12px;
        padding: 0 6px;
        color: {COLORS['primary']};
    }}
    """
