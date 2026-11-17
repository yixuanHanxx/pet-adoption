# Volunteer roles upgrade (incremental patch)

This is a **patch**, not a complete runnable project. It uses the original project's `database.py`, `app.db`, and other templates/static files.

1. **Back up** your original `ca1` folder, especially `app.db`.
2. Copy `app.py`, `forms.py`, `migrate_roles.py`, `bootstrap_admin.py` and the three files in `templates/` into the matching locations in `ca1`.
3. From the `ca1` directory run `python migrate_roles.py` **once**. It is safe to rerun; it does not drop tables or reset records.
4. Run `python bootstrap_admin.py`, supplying an existing user's username and password to designate the initial admin. This is a local developer utility, not a public web route. Never deploy this script to an untrusted host.
5. Start Flask as before, log in as admin, and visit `/admin/volunteers`. A normal user can visit `/volunteer` to apply.

## What changed
- `users.role` is now authoritative (`user`, `volunteer`, `admin`). All old accounts default to `user` because previous `admin='T'` flags were self-assignable.
- A new `volunteer_applications` table records `Pending`, `Approved`, `Rejected` applications.
- The admin reviews applications and grants volunteer access; the applicant cannot grant themselves privileges.
- Existing `users.admin` is left intact for compatibility but is no longer consulted by authorization.
- Only admin may review volunteers; volunteers and admins may manage adoption applications.
- New approval/rejection routes use POST with CSRF protection.

## Important follow-ups
- `SECRET_KEY` is still hardcoded in this learning patch; fix it in the next security step before deployment.
- Some **existing** GET routes mutate data (`/accept_visit`, `/finish`, `/confirm_adoption`, etc.). Change them to POST + CSRF before deployment.
- This patch is syntax-checked, not fully integration-tested. Test with a backup database.
- SQLite does not enforce foreign keys unless PRAGMA foreign_keys=ON is set; update `database.py` in a later database hardening step.
