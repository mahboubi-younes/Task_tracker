"""
Database layer for the French Task Tracker.
Uses SQLite for offline-first local storage.
"""
import sqlite3
import json
import os
from datetime import datetime, timedelta, date
from pathlib import Path

DB_DIR = Path(os.environ.get('APPDATA', '.')) / 'TaskTrackerFR'
DB_PATH = DB_DIR / 'tasks.db'


def get_db_path():
    DB_DIR.mkdir(parents=True, exist_ok=True)
    return str(DB_PATH)


def get_connection():
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.executescript("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT DEFAULT '',
        importance INTEGER DEFAULT 2,
        urgency INTEGER DEFAULT 2,
        status TEXT DEFAULT 'todo',
        progress INTEGER DEFAULT 0,
        due_date TEXT,
        due_time TEXT DEFAULT '09:00',
        category TEXT DEFAULT '',
        reminder_minutes INTEGER,
        is_recurring INTEGER DEFAULT 0,
        recurrence_pattern TEXT,
        recurrence_end_date TEXT,
        parent_task_id INTEGER,
        created_at TEXT NOT NULL,
        started_at TEXT,
        completed_at TEXT,
        abandoned_at TEXT,
        FOREIGN KEY (parent_task_id) REFERENCES tasks(id) ON DELETE SET NULL
    );

    CREATE TABLE IF NOT EXISTS task_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_id INTEGER NOT NULL,
        event_type TEXT NOT NULL,
        event_date TEXT NOT NULL,
        details TEXT DEFAULT '',
        FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT
    );

    CREATE TABLE IF NOT EXISTS skipped_occurrences (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_id INTEGER NOT NULL,
        skipped_date TEXT NOT NULL,
        FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS dismissed_reminders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_id INTEGER NOT NULL,
        reminder_key TEXT NOT NULL,
        FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
    );
    """)
    defaults = {
        'reminder_minutes': '30',
        'reminder_enabled': '1',
        'notification_sound': '1',
    }
    for key, value in defaults.items():
        c.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", (key, value))
    conn.commit()
    conn.close()


# ── Settings ────────────────────────────────────────────────────────

def get_setting(key, default=''):
    conn = get_connection()
    row = conn.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
    conn.close()
    return row['value'] if row else default


def set_setting(key, value):
    conn = get_connection()
    conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, str(value)))
    conn.commit()
    conn.close()


# ── Task CRUD ───────────────────────────────────────────────────────

def _row_to_dict(row):
    if row is None:
        return None
    return dict(row)


def create_task(data):
    conn = get_connection()
    now = datetime.now().isoformat()
    c = conn.cursor()
    c.execute("""
        INSERT INTO tasks (title, description, importance, urgency, status, progress,
            due_date, due_time, category, reminder_minutes, is_recurring,
            recurrence_pattern, recurrence_end_date, parent_task_id, created_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        data.get('title', ''),
        data.get('description', ''),
        data.get('importance', 2),
        data.get('urgency', 2),
        data.get('status', 'todo'),
        data.get('progress', 0),
        data.get('due_date'),
        data.get('due_time', '09:00'),
        data.get('category', ''),
        data.get('reminder_minutes'),
        data.get('is_recurring', 0),
        json.dumps(data['recurrence_pattern']) if data.get('recurrence_pattern') else None,
        data.get('recurrence_end_date'),
        data.get('parent_task_id'),
        now,
    ))
    task_id = c.lastrowid
    log_event(task_id, 'created', 'Tâche créée', conn=conn)
    conn.commit()
    conn.close()
    return task_id


def update_task(task_id, data):
    conn = get_connection()
    sets = []
    vals = []
    for key, val in data.items():
        if key == 'recurrence_pattern' and isinstance(val, dict):
            val = json.dumps(val)
        sets.append(f"{key}=?")
        vals.append(val)
    vals.append(task_id)
    conn.execute(f"UPDATE tasks SET {','.join(sets)} WHERE id=?", vals)
    log_event(task_id, 'edited', 'Tâche modifiée', conn=conn)
    conn.commit()
    conn.close()


def delete_task(task_id):
    conn = get_connection()
    conn.execute("DELETE FROM tasks WHERE id=?", (task_id,))
    conn.commit()
    conn.close()


def get_task(task_id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM tasks WHERE id=?", (task_id,)).fetchone()
    conn.close()
    return _row_to_dict(row)


def get_all_tasks(status_filter=None, importance_filter=None, urgency_filter=None,
                  category_filter=None, search_text=None, exclude_statuses=None):
    conn = get_connection()
    query = "SELECT * FROM tasks WHERE 1=1"
    params = []
    if status_filter:
        query += " AND status=?"
        params.append(status_filter)
    if exclude_statuses:
        placeholders = ','.join(['?'] * len(exclude_statuses))
        query += f" AND status NOT IN ({placeholders})"
        params.extend(exclude_statuses)
    if importance_filter is not None:
        query += " AND importance=?"
        params.append(importance_filter)
    if urgency_filter is not None:
        query += " AND urgency=?"
        params.append(urgency_filter)
    if category_filter:
        query += " AND category=?"
        params.append(category_filter)
    if search_text:
        query += " AND (title LIKE ? OR description LIKE ?)"
        params.extend([f'%{search_text}%', f'%{search_text}%'])
    query += " ORDER BY urgency DESC, importance DESC, due_date ASC"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [_row_to_dict(r) for r in rows]


def get_tasks_by_date(date_str):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM tasks WHERE due_date=? ORDER BY due_time ASC, urgency DESC",
        (date_str,)
    ).fetchall()
    conn.close()
    return [_row_to_dict(r) for r in rows]


def get_overdue_tasks():
    today = date.today().isoformat()
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM tasks WHERE due_date < ? AND status NOT IN ('completed','abandoned') ORDER BY due_date ASC",
        (today,)
    ).fetchall()
    conn.close()
    return [_row_to_dict(r) for r in rows]


def get_tasks_due_today():
    today = date.today().isoformat()
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM tasks WHERE due_date=? AND status NOT IN ('completed','abandoned') ORDER BY due_time ASC",
        (today,)
    ).fetchall()
    conn.close()
    return [_row_to_dict(r) for r in rows]


def get_tasks_due_soon(days=3):
    today = date.today()
    end = (today + timedelta(days=days)).isoformat()
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM tasks WHERE due_date BETWEEN ? AND ? AND status NOT IN ('completed','abandoned') ORDER BY due_date ASC, due_time ASC",
        (today.isoformat(), end)
    ).fetchall()
    conn.close()
    return [_row_to_dict(r) for r in rows]


def get_tasks_in_range(start_date, end_date):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM tasks WHERE due_date BETWEEN ? AND ? ORDER BY due_date ASC, due_time ASC",
        (start_date, end_date)
    ).fetchall()
    conn.close()
    return [_row_to_dict(r) for r in rows]


def start_task(task_id):
    now = datetime.now().isoformat()
    conn = get_connection()
    conn.execute("UPDATE tasks SET status='in_progress', started_at=? WHERE id=?", (now, task_id))
    log_event(task_id, 'started', 'Tâche démarrée', conn=conn)
    conn.commit()
    conn.close()


def complete_task(task_id):
    now = datetime.now().isoformat()
    conn = get_connection()
    conn.execute("UPDATE tasks SET status='completed', progress=100, completed_at=? WHERE id=?", (now, task_id))
    log_event(task_id, 'completed', 'Tâche terminée', conn=conn)
    conn.commit()
    conn.close()


def abandon_task(task_id):
    now = datetime.now().isoformat()
    conn = get_connection()
    conn.execute("UPDATE tasks SET status='abandoned', abandoned_at=? WHERE id=?", (now, task_id))
    log_event(task_id, 'abandoned', 'Tâche abandonnée', conn=conn)
    conn.commit()
    conn.close()


def pause_task(task_id):
    conn = get_connection()
    conn.execute("UPDATE tasks SET status='todo' WHERE id=?", (task_id,))
    log_event(task_id, 'paused', 'Tâche mise en pause', conn=conn)
    conn.commit()
    conn.close()


def update_progress(task_id, progress):
    conn = get_connection()
    status = 'in_progress' if 0 < progress < 100 else ('completed' if progress >= 100 else 'todo')
    updates = {'progress': progress, 'status': status}
    if progress >= 100:
        updates['completed_at'] = datetime.now().isoformat()
    sets = ','.join(f"{k}=?" for k in updates)
    vals = list(updates.values()) + [task_id]
    conn.execute(f"UPDATE tasks SET {sets} WHERE id=?", vals)
    log_event(task_id, 'progress', f'Progression: {progress}%', conn=conn)
    conn.commit()
    conn.close()


# ── Events ──────────────────────────────────────────────────────────

def log_event(task_id, event_type, details='', conn=None):
    own_conn = conn is None
    if own_conn:
        conn = get_connection()
    now = datetime.now().isoformat()
    conn.execute(
        "INSERT INTO task_events (task_id, event_type, event_date, details) VALUES (?,?,?,?)",
        (task_id, event_type, now, details)
    )
    if own_conn:
        conn.commit()
        conn.close()


def get_task_events(task_id):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM task_events WHERE task_id=? ORDER BY event_date DESC", (task_id,)
    ).fetchall()
    conn.close()
    return [_row_to_dict(r) for r in rows]


# ── Reminders ───────────────────────────────────────────────────────

def dismiss_reminder(task_id, key):
    conn = get_connection()
    conn.execute("INSERT INTO dismissed_reminders (task_id, reminder_key) VALUES (?,?)", (task_id, key))
    conn.commit()
    conn.close()


def is_reminder_dismissed(task_id, key):
    conn = get_connection()
    row = conn.execute(
        "SELECT id FROM dismissed_reminders WHERE task_id=? AND reminder_key=?", (task_id, key)
    ).fetchone()
    conn.close()
    return row is not None


# ── Recurring ───────────────────────────────────────────────────────

def skip_occurrence(task_id, date_str):
    conn = get_connection()
    conn.execute("INSERT INTO skipped_occurrences (task_id, skipped_date) VALUES (?,?)", (task_id, date_str))
    conn.commit()
    conn.close()


def get_skipped_occurrences(task_id):
    conn = get_connection()
    rows = conn.execute("SELECT skipped_date FROM skipped_occurrences WHERE task_id=?", (task_id,)).fetchall()
    conn.close()
    return [r['skipped_date'] for r in rows]


# ── Statistics ──────────────────────────────────────────────────────

def get_task_stats():
    conn = get_connection()
    total = conn.execute("SELECT COUNT(*) as c FROM tasks").fetchone()['c']
    today_count = len(get_tasks_due_today())
    overdue_count = len(get_overdue_tasks())
    in_progress = conn.execute("SELECT COUNT(*) as c FROM tasks WHERE status='in_progress'").fetchone()['c']
    completed = conn.execute("SELECT COUNT(*) as c FROM tasks WHERE status='completed'").fetchone()['c']
    todo = conn.execute("SELECT COUNT(*) as c FROM tasks WHERE status='todo'").fetchone()['c']
    conn.close()
    return {
        'total': total,
        'today': today_count,
        'overdue': overdue_count,
        'in_progress': in_progress,
        'completed': completed,
        'todo': todo,
    }


def get_categories():
    conn = get_connection()
    rows = conn.execute("SELECT DISTINCT category FROM tasks WHERE category != '' ORDER BY category").fetchall()
    conn.close()
    return [r['category'] for r in rows]


def get_history_tasks(search_text=None, status_filter=None, date_from=None, date_to=None):
    conn = get_connection()
    query = "SELECT * FROM tasks WHERE status IN ('completed','abandoned')"
    params = []
    if status_filter:
        query = f"SELECT * FROM tasks WHERE status=?"
        params.append(status_filter)
    if search_text:
        query += " AND (title LIKE ? OR description LIKE ?)"
        params.extend([f'%{search_text}%', f'%{search_text}%'])
    if date_from:
        query += " AND (completed_at >= ? OR abandoned_at >= ?)"
        params.extend([date_from, date_from])
    if date_to:
        query += " AND (completed_at <= ? OR abandoned_at <= ?)"
        params.extend([date_to, date_to])
    query += " ORDER BY COALESCE(completed_at, abandoned_at) DESC"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [_row_to_dict(r) for r in rows]


def get_task_density(year, month):
    """Returns dict of {date_str: count} for the given month."""
    start = f"{year:04d}-{month:02d}-01"
    if month == 12:
        end = f"{year + 1:04d}-01-01"
    else:
        end = f"{year:04d}-{month + 1:02d}-01"
    conn = get_connection()
    rows = conn.execute(
        "SELECT due_date, COUNT(*) as c FROM tasks WHERE due_date >= ? AND due_date < ? GROUP BY due_date",
        (start, end)
    ).fetchall()
    conn.close()
    return {r['due_date']: r['c'] for r in rows}
