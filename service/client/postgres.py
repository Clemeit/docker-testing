import os

from psycopg2 import pool

# Load environment variables
DB_CONFIG = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASS"),
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT")),
}
DB_MIN_CONN = int(os.getenv("DB_MIN_CONN"))
DB_MAX_CONN = int(os.getenv("DB_MAX_CONN"))


# Set up the PostgreSQL connection pool
async def create_db_pool(app) -> None:
    """Create a PostgreSQL connection pool and attach it to the app context."""
    app.ctx.db_pool = pool.SimpleConnectionPool(
        minconn=DB_MIN_CONN,
        maxconn=DB_MAX_CONN,
        **DB_CONFIG,
    )
    print("Created PostgreSQL connection pool")


# Close the PostgreSQL connection
async def close_db_pool(app) -> None:
    """Close the PostgreSQL connection pool."""
    app.ctx.db_pool.closeall()
    print("Closed PostgreSQL connection")
