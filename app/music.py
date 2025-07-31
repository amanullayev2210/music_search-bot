import sqlite3

def init_admin_db():
    conn = sqlite3.connect("admin_added.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        doc_id TEXT NOT NULL
    )
    """)
    conn.commit()
    conn.close()

init_admin_db()


async def search_music(query: str, offset: int = 0, limit: int = 10) -> list:
    result = []
    for db in ("admin_added.db", "music.db"):
        try:
            conn = sqlite3.connect(db)
            conn.create_function("LOWER", 1, str.lower)
            cur = conn.cursor()
            cur.execute("""
                SELECT id, name, doc_id FROM data
                WHERE LOWER(name) LIKE LOWER(?)
            """, (f"%{query}%",))
            result += cur.fetchall()
            conn.close()
        except Exception as e:
            print("Xatolik:", e)


    return result[offset:offset + limit]



async def check_music():
    total = 0
    try:
        conn1 = sqlite3.connect("music.db")
        cur1 = conn1.cursor()
        cur1.execute("SELECT COUNT(*) FROM data")
        total = cur1.fetchone()[0]
        conn1.close()
    except Exception:
            pass

    return total

async def check_music_add():
    admin = 0
    try:
        conn2 = sqlite3.connect("admin_added.db")
        cur2 = conn2.cursor()
        cur2.execute("SELECT COUNT(*) FROM data")
        admin = cur2.fetchone()[0]
        conn2.close()
    except Exception:
        pass
    return admin

def random_music():
    all_tracks = []

    try:
        conn1 = sqlite3.connect("music.db")
        cur1 = conn1.cursor()
        cur1.execute("SELECT name, doc_id FROM data")
        all_tracks.extend(cur1.fetchall())
        conn1.close()
    except Exception:
        pass

    try:
        conn2 = sqlite3.connect("admin_added.db")
        cur2 = conn2.cursor()
        cur2.execute("SELECT name, doc_id FROM data")
        all_tracks.extend(cur2.fetchall())
        conn2.close()
    except sqlite3.OperationalError:
        pass  

    return all_tracks