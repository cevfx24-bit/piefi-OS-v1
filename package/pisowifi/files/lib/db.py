import sqlite3, os, time, threading
from contextlib import contextmanager

DB_PATH = "/var/lib/pisowifi/pisowifi.db"
_lock = threading.Lock()

SCHEMA = """
CREATE TABLE IF NOT EXISTS clients (
    mac TEXT PRIMARY KEY, ip TEXT, hostname TEXT,
    balance_seconds INTEGER DEFAULT 0, remaining_seconds INTEGER DEFAULT 0,
    authorized INTEGER DEFAULT 0, paused INTEGER DEFAULT 0,
    pending INTEGER DEFAULT 0, pending_since INTEGER DEFAULT 0,
    last_seen INTEGER DEFAULT 0, total_spent_php INTEGER DEFAULT 0,
    created_at INTEGER DEFAULT 0
);
CREATE TABLE IF NOT EXISTS coin_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT, mac TEXT, peso INTEGER, ts INTEGER
);
CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY, value TEXT
);
"""

def init():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with _conn() as c: c.executescript(SCHEMA)

@contextmanager
def _conn():
    with _lock:
        con = sqlite3.connect(DB_PATH)
        con.row_factory = sqlite3.Row
        try:
            yield con
            con.commit()
        finally:
            con.close()

def upsert_client(mac, ip=None, hostname=None):
    now = int(time.time())
    with _conn() as c:
        c.execute("""INSERT INTO clients (mac, ip, hostname, last_seen, created_at)
                     VALUES (?, ?, ?, ?, ?)
                     ON CONFLICT(mac) DO UPDATE SET
                       ip=COALESCE(?, ip), hostname=COALESCE(?, hostname), last_seen=?""",
                  (mac, ip, hostname, now, now, ip, hostname, now))

def get_client(mac):
    with _conn() as c:
        row = c.execute("SELECT * FROM clients WHERE mac=?", (mac,)).fetchone()
        return dict(row) if row else None

def set_pending(mac):
    now = int(time.time())
    with _conn() as c:
        c.execute("UPDATE clients SET pending=1, pending_since=? WHERE mac=?", (now, mac))

def oldest_pending(within_seconds=90):
    cutoff = int(time.time()) - within_seconds
    with _conn() as c:
        row = c.execute("SELECT * FROM clients WHERE pending=1 AND pending_since>=? ORDER BY pending_since ASC LIMIT 1", (cutoff,)).fetchone()
        return dict(row) if row else None

def credit_client(mac, seconds, peso):
    now = int(time.time())
    with _conn() as c:
        c.execute("""UPDATE clients SET
                       remaining_seconds = remaining_seconds + ?, balance_seconds = balance_seconds + ?,
                       total_spent_php = total_spent_php + ?, pending = 0, pending_since = 0,
                       authorized = 1, paused = 0 WHERE mac=?""", (seconds, seconds, peso, mac))
        c.execute("INSERT INTO coin_log (mac, peso, ts) VALUES (?, ?, ?)", (mac, peso, now))

def tick_clients():
    with _conn() as c:
        c.execute("UPDATE clients SET remaining_seconds = remaining_seconds - 1 WHERE authorized=1 AND paused=0 AND remaining_seconds > 0")
        expired = c.execute("SELECT mac FROM clients WHERE authorized=1 AND remaining_seconds <= 0").fetchall()
        for row in expired:
            c.execute("UPDATE clients SET authorized=0, remaining_seconds=0 WHERE mac=?", (row["mac"],))
        return [r["mac"] for r in expired]

def list_sessions(only_active=False):
    with _conn() as c:
        q = "SELECT * FROM clients"
        if only_active: q += " WHERE authorized=1 OR pending=1"
        q += " ORDER BY last_seen DESC"
        return [dict(r) for r in c.execute(q).fetchall()]

def set_paused(mac, paused):
    with _conn() as c:
        c.execute("UPDATE clients SET paused=? WHERE mac=?", (1 if paused else 0, mac))

def get_setting(key, default=None):
    with _conn() as c:
        r = c.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
        return r["value"] if r else default

def set_setting(key, value):
    with _conn() as c:
        c.execute("INSERT INTO settings (key,value) VALUES (?,?) ON CONFLICT(key) DO UPDATE SET value=?", (key, str(value), str(value)))

def recent_coins(limit=50):
    with _conn() as c:
        return [dict(r) for r in c.execute("SELECT * FROM coin_log ORDER BY id DESC LIMIT ?", (limit,)).fetchall()]
