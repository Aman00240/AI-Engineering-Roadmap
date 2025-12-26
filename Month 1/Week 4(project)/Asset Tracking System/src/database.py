import sqlite3 as sql
import datetime

DB_NAME = "data.db"


def setup_database() -> None:
    with sql.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")

        cursor.execute("""CREATE TABLE IF NOT EXISTS assets(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            category TEXT,
            status TEXT DEFAULT 'IN_STOCK'
            )""")

        cursor.execute("""CREATE TABLE IF NOT EXISTS employees(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            department TEXT,
            is_active INTEGER DEFAULT 1
            )""")

        cursor.execute("""CREATE TABLE IF NOT EXISTS assignments(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            asset_id INTEGER,
            employee_id INTEGER,
            assigned_date TEXT,
            return_date TEXT,
            FOREIGN KEY (asset_id) REFERENCES assets(id),
            FOREIGN KEY (employee_id) REFERENCES employees(id)
            )""")


class Database_manager:
    def __init__(self, db_name: str) -> None:
        self.db_name = db_name

    def add_assets(self, name: str, category: str, status: str = "IN_STOCK") -> None:
        with sql.connect(self.db_name) as conn:
            cursor = conn.cursor()

            cursor.execute(
                "INSERT INTO assets(name,category,status) VALUES(:name,:cat,:status)",
                {"name": name, "cat": category, "status": status},
            )

    def add_employees(self, name: str, department: str) -> None:
        with sql.connect(self.db_name) as conn:
            cursor = conn.cursor()

            cursor.execute(
                "INSERT INTO employees(name,department) VALUES(:name,:dept)",
                {"name": name, "dept": department},
            )

    def assign_asset(self, asset_id: int, employee_id: int) -> None:
        assign_date = datetime.date.today()

        with sql.connect(self.db_name) as conn:
            cursor = conn.cursor()

            cursor.execute(
                "INSERT INTO assignments(asset_id,employee_id,assigned_date) VALUES(:asset,:emp,:assig)",
                {"asset": asset_id, "emp": employee_id, "assig": assign_date},
            )

            cursor.execute(
                "UPDATE assets SET status='ASSIGNED' WHERE id=:asset_id",
                {"asset_id": asset_id},
            )

    def return_asset(self, asset_id: int) -> None:
        return_date = datetime.date.today()

        with sql.connect(self.db_name) as conn:
            cursor = conn.cursor()

            cursor.execute(
                """UPDATE assignments
                SET return_date=:re_dt 
                WHERE asset_id=:asset AND return_date IS NULL""",
                {"re_dt": return_date, "asset": asset_id},
            )

            cursor.execute(
                "UPDATE assets SET status='IN_STOCK' WHERE id=:asset_id ",
                {"asset_id": asset_id},
            )

    def offboard_employee(self, id: int) -> None:
        with sql.connect(self.db_name) as conn:
            cursor = conn.cursor()

            cursor.execute("UPDATE employees SET is_active=0 WHERE id=:id", {"id": id})

    def get_active_assignments(self) -> list[tuple[str, str, str]]:
        with sql.connect(self.db_name) as conn:
            cursor = conn.cursor()

            cursor.execute("""
                           SELECT e.name,ase.name,assign.assigned_date
                           FROM assignments AS assign
                           JOIN assets AS ase ON ase.id=assign.asset_id
                           JOIN employees AS e ON e.id=assign.employee_id
                           WHERE assign.return_date IS NULL
                           """)

            return  cursor.fetchall()
