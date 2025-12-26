import sqlite3

DB_NAME = "server_log.db"


def setup_database():
    print("-- Setting up Database --")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""CREATE TABLE IF NOT EXISTS incidents(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        severity TEXT,
        message TEXT,
        status TEXT DEFAULT 'OPEN'
        )""")

    conn.commit()
    conn.close()


def report_incident(severity: str, message: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO incidents(severity,message) VALUES(:severity,:message)",
        {"severity": severity, "message": message},
    )

    conn.commit()
    conn.close()


def get_pending_criticals():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM incidents WHERE severity='CRITICAL' AND status='OPEN' "
    )

    rows = cursor.fetchall()

    for row in rows:
        print(f"ID:{row[0]}-{row[2]}")

    conn.close()


def mark_resolved(id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("UPDATE incidents SET status='SOLVED' WHERE id=:id", {"id": id})

    conn.commit()
    conn.close()


def generate_stats():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT severity,COUNT(*) FROM incidents GROUP BY severity")

        rows = cursor.fetchall()

        for row in rows:
            print(f"{row[0]}:{row[1]}")


if __name__ == "__main__":
    setup_database()

    print("--Reporting Incidnets--")
    report_incident("CRITICAL", "Main Database on Fire")
    report_incident("LOW", "User 505 forgot password")
    report_incident("CRITICAL", "Payment Gateway Timeout")

    print("--PENDING CRITICALS--")
    get_pending_criticals()

    print("--FIXING ID 1--")
    mark_resolved(1)

    print("--PENDING CRITICALS (AFTER FIX)--")
    get_pending_criticals()

    print("-- INCIDENT REPORT --")
    generate_stats()
