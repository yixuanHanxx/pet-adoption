"""Run manually on trusted machine after migration. Promotes an existing account."""
from pathlib import Path
import sqlite3
import getpass
from werkzeug.security import check_password_hash

path = Path(__file__).with_name('app.db')
if not path.exists():
    raise SystemExit('app.db not found')
user_id = input('Existing account to promote: ').strip()
password = getpass.getpass('Confirm that account password: ')
con = sqlite3.connect(path)
con.row_factory = sqlite3.Row
try:
    with con:
        user = con.execute('SELECT password FROM users WHERE user_id = ?', (user_id,)).fetchone()
        if user is None or not check_password_hash(user['password'], password):
            raise SystemExit('Invalid credentials; no changes made.')
        con.execute("UPDATE users SET role='admin' WHERE user_id=?", (user_id,))
    print('Admin role granted.')
finally:
    con.close()
