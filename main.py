"""
Mon Assistant – Gestionnaire de Tâches
Entry point for the French task tracker application.
"""
import sys
import os

# Ensure the app directory is in the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from qt import QApplication, Qt, QFont

import database as db
from main_window import MainWindow


def main():
    # Initialize database
    db.init_db()

    # High DPI support – must be set BEFORE creating QApplication
    try:
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    except AttributeError:
        pass  # PySide6/Qt6 enables this by default

    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("Mon Assistant")
    app.setOrganizationName("TaskTrackerFR")
    app.setQuitOnLastWindowClosed(False)

    # Set default font – 12pt for readability on all screens
    font = QFont("Segoe UI", 12)
    app.setFont(font)

    # Fusion style for consistent cross-platform look
    app.setStyle("Fusion")

    # Create and show main window
    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
