import sys

try:
    # Try importing PySide6
    from PySide6 import QtCore, QtGui, QtWidgets
    from PySide6.QtCore import Signal, Slot, Property, Qt, QTimer, QSize, QDate, QTime
    from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor, QFont, QAction, QPen, QPainterPath
    from PySide6.QtWidgets import (
        QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
        QPushButton, QStackedWidget, QFrame, QSystemTrayIcon,
        QMenu, QApplication, QDialog, QFormLayout, QLineEdit,
        QTextEdit, QComboBox, QDateEdit, QTimeEdit, QCheckBox,
        QSpinBox, QSlider, QGroupBox, QMessageBox, QScrollArea,
        QSizePolicy, QGridLayout, QProgressBar
    )
    USING_PYSIDE6 = True
except ImportError:
    # Fallback to PyQt5 for Windows 7 support
    from PyQt5 import QtCore, QtGui, QtWidgets
    from PyQt5.QtCore import (
        pyqtSignal as Signal, pyqtSlot as Slot, pyqtProperty as Property,
        Qt, QTimer, QSize, QDate, QTime
    )
    from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor, QFont, QPen, QPainterPath
    from PyQt5.QtWidgets import (
        QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
        QPushButton, QStackedWidget, QFrame, QSystemTrayIcon,
        QMenu, QApplication, QDialog, QFormLayout, QLineEdit,
        QTextEdit, QComboBox, QDateEdit, QTimeEdit, QCheckBox,
        QSpinBox, QSlider, QGroupBox, QMessageBox, QScrollArea,
        QSizePolicy, QGridLayout, QProgressBar, QAction
    )
    USING_PYSIDE6 = False

# Safe exec compatibility alias for PyQt5
if not USING_PYSIDE6:
    if not hasattr(QDialog, 'exec'):
        try:
            setattr(QDialog, 'exec', QDialog.exec_)
        except (AttributeError, TypeError):
            pass
    if not hasattr(QMenu, 'exec'):
        try:
            setattr(QMenu, 'exec', QMenu.exec_)
        except (AttributeError, TypeError):
            pass

