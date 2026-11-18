
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL not found in .env file")

# Create PostgreSQL connection
engine = create_engine(
    DATABASE_URL.replace(
        "postgresql://",
        "postgresql+psycopg2://",
        1
    ),
    connect_args={"sslmode": "require"},
    pool_pre_ping=True
)

def test_connection():
    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT version();")
        )

        print("Connected to Supabase successfully!")
        print(result.scalar())


if __name__ == "__main__":
    test_connection()
