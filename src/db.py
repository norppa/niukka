import sqlite3


def get_conn():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS records (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            password TEXT
        )
    """
    )
    conn.commit()
    conn.close()


def get_record(key: str, password: str = None):
    conn = get_conn()
    row = conn.execute(
        "SELECT key, value, password FROM records WHERE key = ?", (key,)
    ).fetchone()
    conn.close()
    if row:
        if row["password"] != password:
            raise ValueError("Invalid password")
        return {"key": row["key"], "value": row["value"]}
    return None


def set_record(key: str, value: str, password: str = None):
    conn = get_conn()
    existing = conn.execute(
        "SELECT key, value, password FROM records WHERE key = ?", (key,)
    ).fetchone()
    if existing:
        if existing["password"] != password:
            raise ValueError("Invalid password")
        conn.execute(
            "UPDATE records SET value = ? WHERE key = ?",
            (value, key),
        )
    else:
        conn.execute(
            "INSERT INTO records (key, value, password) VALUES (?, ?, ?)",
            (key, value, password),
        )
    conn.commit()
    conn.close()


def del_record(key: str, password: str = None):
    conn = get_conn()
    existing = conn.execute(
        "SELECT key, password FROM records WHERE key = ?", (key,)
    ).fetchone()
    if existing:
        if existing["password"] != password:
            raise ValueError("Invalid password")
        conn.execute("DELETE FROM records WHERE key = ?", (key,))
        conn.commit()
    conn.close()
