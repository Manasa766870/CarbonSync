import hashlib
import hmac
import secrets
from backend.database import connect

def _hash_password(password, salt):
    return hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 310_000).hex()

def register_user(name, email, password, hostel="", department=""):
    name, email = name.strip(), email.strip().lower()
    if not name or not email or not password:
        return False, "Please complete all required fields.", None
    if len(password) < 8:
        return False, "Use a password with at least 8 characters.", None
    salt = secrets.token_bytes(16)
    password_hash = _hash_password(password, salt)
    try:
        with connect() as conn:
            cur = conn.execute(
                """INSERT INTO users(name,email,password_hash,password_salt,hostel,department)
                   VALUES(?,?,?,?,?,?)""",
                (name, email, password_hash, salt.hex(), hostel.strip(), department.strip())
            )
            return True, "Account created.", cur.lastrowid
    except Exception as exc:
        if "UNIQUE" in str(exc).upper():
            return False, "An account with this email already exists.", None
        return False, "Could not create account. Please try again.", None

def authenticate_user(email, password):
    with connect() as conn:
        row = conn.execute("SELECT * FROM users WHERE email=?", (email.strip().lower(),)).fetchone()
    if not row:
        return None
    expected = _hash_password(password, bytes.fromhex(row["password_salt"]))
    if not hmac.compare_digest(expected, row["password_hash"]):
        return None
    return {"id": row["id"], "name": row["name"]}
