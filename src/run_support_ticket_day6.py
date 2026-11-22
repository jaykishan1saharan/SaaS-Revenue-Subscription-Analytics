import sqlite3
from pathlib import Path
import pandas as pd

root = Path(__file__).resolve().parents[1]
csv_path = root / "data/interim/support_tickets_clean.csv"
sql_path = root / "sql/05_support_ticket_day6_analysis.sql"
db_path = root / "data/interim/support_tickets_day6.db"

df = pd.read_csv(csv_path)

# Remove full-line SQL comments before splitting into statements.
sql_lines = [
    line for line in sql_path.read_text().splitlines()
    if not line.strip().startswith("--")
]
sql_text = "\n".join(sql_lines)
statements = [statement.strip() for statement in sql_text.split(";")
              if statement.strip()]

with sqlite3.connect(db_path) as conn:
    df.to_sql("support_tickets", conn, if_exists="replace", index=False)

    print("DAY 6 SUPPORT TICKET ANALYSIS")
    print("=" * 60)

    for number, statement in enumerate(statements, start=1):
        cursor = conn.execute(statement)
        rows = cursor.fetchall()

        print(f"\nQUERY {number}")
        print("-" * 40)
        if cursor.description:
            print([column[0] for column in cursor.description])
            for row in rows:
                print(row)
        else:
            print("Executed successfully")

    count = conn.execute(
        "SELECT COUNT(*) FROM support_tickets"
    ).fetchone()[0]

    print("\nDATABASE VERIFICATION")
    print("Loaded records:", count)
    print("Database file:", db_path)
