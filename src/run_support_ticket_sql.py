
import sqlite3
from pathlib import Path
import pandas as pd

root = Path(__file__).resolve().parents[1]
csv_path = root / "data/interim/support_tickets_clean.csv"
sql_path = root / "sql/03_initial_exploration.sql"
db_path = root / "data/interim/support_tickets_day4.db"

df = pd.read_csv(csv_path)

with sqlite3.connect(db_path) as conn:
    df.to_sql("support_tickets", conn, if_exists="replace", index=False)

    sql_text = sql_path.read_text()
    statements = [
        statement.strip()
        for statement in sql_text.split(";")
        if statement.strip() and not all(
            line.strip().startswith("--") or not line.strip()
            for line in statement.splitlines()
        )
    ]

    print("DAY 4 SQL EXECUTION")
    print("=" * 50)

    for number, statement in enumerate(statements, start=1):
        # Remove SQL comment lines before execution
        executable = "\n".join(
            line for line in statement.splitlines()
            if not line.strip().startswith("--")
        ).strip()

        if not executable:
            continue

        cursor = conn.execute(executable)
        rows = cursor.fetchall()

        print(f"\nQUERY {number}")
        print("-" * 30)
        if cursor.description:
            print([column[0] for column in cursor.description])
            for row in rows[:10]:
                print(row)
        else:
            print("Executed successfully")

    count = conn.execute(
        "SELECT COUNT(*) FROM support_tickets"
    ).fetchone()[0]

    print("\nDATABASE VERIFICATION")
    print("Loaded records:", count)
    print("Database file:", db_path)
