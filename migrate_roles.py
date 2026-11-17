"""One-time, non-destructive migration. Run from project directory."""
import sqlite3
from pathlib import Path

path = Path(__file__).with_name('app.db')
if not path.exists():
    raise SystemExit('app.db not found. Copy migration beside existing app.db first.')
con = sqlite3.connect(path)
try:
    with con:
        columns = {row[1] for row in con.execute('PRAGMA table_info(users)')}
        if 'role' not in columns:
            con.execute("ALTER TABLE users ADD COLUMN role TEXT NOT NULL DEFAULT 'user' CHECK (role IN ('user','volunteer','admin'))")
            # Historical self-assigned admin='T' is NOT trusted; manually designate admin via bootstrap_admin.py.
        con.execute('''CREATE TABLE IF NOT EXISTS volunteer_applications (
            application_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL REFERENCES users(user_id),
            reason TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Pending' CHECK(status IN ('Pending','Approved','Rejected')),
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            reviewed_at TEXT,
            reviewed_by TEXT REFERENCES users(user_id)
        )''')
        con.execute("CREATE UNIQUE INDEX IF NOT EXISTS one_pending_volunteer_application ON volunteer_applications(user_id) WHERE status='Pending'")
    print('Migration successful. All existing users start with role=user unless previously migrated.')
finally:
    con.close()
