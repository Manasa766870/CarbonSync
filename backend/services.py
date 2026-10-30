from backend.database import connect

def get_user(user_id):
    with connect() as conn:
        row = conn.execute("SELECT id,name,email,hostel,department FROM users WHERE id=?", (user_id,)).fetchone()
    return dict(row) if row else None

def update_profile(user_id, name, hostel, department):
    with connect() as conn:
        conn.execute("UPDATE users SET name=?,hostel=?,department=? WHERE id=?",
                     (name.strip(), hostel.strip(), department.strip(), user_id))

def save_message(user_id, session_id, role, content):
    with connect() as conn:
        conn.execute("""INSERT INTO messages(user_id,session_id,role,content)
                        VALUES(?,?,?,?)""", (user_id, session_id, role, content))

def get_messages(user_id, session_id):
    with connect() as conn:
        rows = conn.execute("""SELECT role,content FROM messages
            WHERE user_id=? AND session_id=? ORDER BY id""", (user_id, session_id)).fetchall()
    return [dict(r) for r in rows]

def get_dashboard_stats(user_id):
    with connect() as conn:
        activities = conn.execute("""SELECT category,details,emissions_kg,created_at
            FROM activities WHERE user_id=? ORDER BY id DESC LIMIT 20""", (user_id,)).fetchall()
        totals = conn.execute("""SELECT COUNT(*) AS n, COALESCE(SUM(emissions_kg),0) AS total
            FROM activities WHERE user_id=?""", (user_id,)).fetchone()
        messages = conn.execute("SELECT COUNT(*) AS n FROM messages WHERE user_id=?", (user_id,)).fetchone()
    return {
        "activity_count": totals["n"],
        "total_kg": totals["total"],
        "message_count": messages["n"],
        "activities": [dict(r) for r in activities]
    }
