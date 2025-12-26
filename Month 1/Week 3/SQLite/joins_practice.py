import sqlite3 as sql


DB_NAME = "server_log.db"


def setup_database() -> None:
    with sql.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")

        cursor.execute("""CREATE TABLE IF NOT EXISTS user(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT
            )""")

        cursor.execute("""CREATE TABLE IF NOT EXISTS incidents(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            severity TEXT,
            message TEXT,
            user_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES user(id)
            )""")


def insert_user(name: str, email: str) -> None:
    with sql.connect(DB_NAME) as conn:
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO user(name,email) VALUES(:name,:email)",
            {"name": name, "email": email},
        )


def insert_incident(severity: str, message: str, user_id: int) -> None:
    with sql.connect(DB_NAME) as conn:
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO incidents(severity,message,user_id) VALUES(:severity,:message,:user_id)",
            {"severity": severity, "message": message, "user_id": user_id},
        )


def get_stats() -> None:
    with sql.connect(DB_NAME) as conn:
        cursor = conn.cursor()

        cursor.execute("""SELECT i.message,u.name FROM incidents as i
                       JOIN user as u ON u.id=i.user_id 
                       """)

        rows = cursor.fetchall()

        for row in rows:
            print(f"Incident:{row[0]} | Reported by:{row[1]}")


if __name__ == "__main__":
    setup_database()

    print("--- Adding Users ---")
    insert_user("Alice", "alice@company.com")
    insert_user("Bob", "bob@intern.com")

    print("--- Adding Incidents ---")
    insert_incident("CRITICAL", "Server Fire", 1)
    insert_incident("LOW", "Lost Pencil", 2)

    print("\n--- THE BLAME GAME ---")
    get_stats()
