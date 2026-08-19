# 🚀 Mon Assistant – Personal Desktop Task & Productivity Manager

[![Python Version](https://img.shields.io/badge/python-3.8%20%7C%203.13-blue.svg)](https://www.python.org/)
[![UI Framework](https://img.shields.io/badge/GUI-PyQt5%20%2F%20PySide6-green.svg)](https://www.qt.io/)
[![Platform](https://img.shields.io/badge/platform-Windows%207%20%2F%2010%20%2F%2011-lightgrey.svg)](https://www.microsoft.com/windows)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Mon Assistant** is a modern, high-performance, offline-first personal task manager and productivity desktop application built with Python and Qt. It features an intelligent background notification engine, interactive calendar view, automated assistant insights, and a dynamic Qt compatibility layer allowing native execution on both legacy Windows 7 and modern Windows 10/11 systems.

---

## 🌐 Interactive Web Landing Page

Check out the official Web Landing Page for live preview and one-click downloads:  
👉 **[https://mahboubi-younes.github.io/Mon_Assistant/](https://mahboubi-younes.github.io/Mon_Assistant/)**

---

## 🌟 Key Features

- **📊 KPI Dashboard & Insights**: Live tracking of completed, overdue, in-progress, and upcoming tasks with automated advice cards.
- **🔔 Background System Tray Engine**: Minimalist system tray integration with custom soundless/sound alerts before due dates.
- **📅 Interactive Calendar View**: Month-grid calendar displaying tasks color-coded by importance and urgency level.
- **🛡️ Universal Dual-Engine Compatibility**: Custom compatibility layer (`qt.py`) that dynamically switches between **PySide6 (Qt6)** on Windows 10/11 and **PyQt5 (Qt5)** on legacy Windows 7.
- **🔒 100% Offline & Private**: All data is stored locally in an optimized SQLite database. No cloud dependence or tracking.
- **🎨 Glassmorphic Dark UI**: Custom QSS theme, smooth visual feedback, keyboard shortcuts, and clean layout scaling.

---

## 📥 Direct Downloads

Download the standalone executable directly from the repository:

| OS Version | Technology | Download Link |
| :--- | :--- | :--- |
| **Windows 10 / 11** | Python 3.13 + PySide6 (Qt6) | [Download Mon_Assistant.exe](dist/Mon_Assistant.exe) |
| **Windows 7 (Legacy)** | Python 3.8 + PyQt5 (Qt5) | [Download Mon_Assistant_Win7.exe](dist/Mon_Assistant_Win7.exe) |

---

## 💻 Technical Architecture

```
task_tracker/
├── main.py              # Application entry point & High-DPI configuration
├── main_window.py       # Main window layout, sidebar, system tray & reminder timer
├── qt.py                # Dual-engine Qt compatibility wrapper (PySide6 / PyQt5)
├── database.py          # SQLite persistence layer, schema & stats calculation
├── styles.py            # Global QSS dark glassmorphism stylesheet & palette
├── dialogs.py           # Task creation/editing & detailed modal dialogs
├── pages/
│   ├── dashboard.py     # KPI metrics & automated assistant advice
│   ├── tasks.py         # Task management list with filter & search
│   ├── calendar_view.py # Interactive month grid calendar
│   ├── history.py       # Event log & completed task archive
│   └── settings.py      # Preference configurations & database cleanup
└── index.html           # Web Landing Page for GitHub Pages
```

---

## 🛠️ Building from Source

```bash
# Clone repository
git clone https://github.com/mahboubi-younes/Mon_Assistant.git
cd Mon_Assistant

# Install dependencies
pip install PySide6

# Run application
python main.py

# Build standalone executable (Windows 10/11)
pyinstaller --onefile --noconsole --name "Mon_Assistant" main.py
```

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.

Developed by **Younes Mahboubi**
