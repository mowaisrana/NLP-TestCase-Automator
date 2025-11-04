# import sqlite3

# DB_NAME = "testcases.db"

# def create_table():
#     conn = sqlite3.connect(DB_NAME)
#     cursor = conn.cursor()

#     cursor.execute("""
#     CREATE TABLE IF NOT EXISTS testcases (
#         id INTEGER PRIMARY KEY AUTOINCREMENT,
#         original_text TEXT,
#         actions TEXT,
#         objects TEXT,
#         created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#     )
#     """)

#     conn.commit()
#     conn.close()


# def save_testcase(original_text, actions, objects):
#     conn = sqlite3.connect(DB_NAME)
#     cursor = conn.cursor()

#     cursor.execute("""
#     INSERT INTO testcases (original_text, actions, objects)
#     VALUES (?, ?, ?)
#     """, (original_text, ", ".join(actions), ", ".join(objects)))

#     conn.commit()
#     conn.close()


# def fetch_all():
#     conn = sqlite3.connect(DB_NAME)
#     cursor = conn.cursor()

#     cursor.execute("SELECT * FROM testcases ORDER BY created_at DESC")
#     rows = cursor.fetchall()

#     conn.close()
#     return rows

import sqlite3

# Connect to DB
def get_connection():
    return sqlite3.connect("testcases.db")

# Create table if not exists (run once)
def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS testcases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        requirement TEXT,
        actions TEXT,
        objects TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()
    conn.close()

# Save test case record
def save_testcase(requirement, actions, objects):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO testcases (requirement, actions, objects) VALUES (?, ?, ?)",
              (requirement, str(actions), str(objects)))
    conn.commit()
    conn.close()

# ⬇️ Fetch all history for Streamlit UI
def get_all_testcases():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id, requirement, actions, objects, created_at FROM testcases")
    rows = c.fetchall()
    conn.close()

    # Convert result to list of dicts for pandas/streamlit
    history = []
    for r in rows:
        history.append({
            "id": r[0],
            "requirement": r[1],
            "actions": r[2],
            "objects": r[3],
            "created_at": r[4]
        })
    return history


# Initialize DB
init_db()
