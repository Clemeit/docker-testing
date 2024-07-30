import os

from psycopg2 import pool

# Load environment variables
DB_CONFIG = {
    "dbname": os.getenv("POSTGRES_DB"),
    "host": os.getenv("POSTGRES_HOST"),
    "port": int(os.getenv("POSTGRES_PORT")),
    "user": os.getenv("POSTGRES_USER"),
    "password": os.getenv("POSTGRES_PASSWORD"),
}
DB_MIN_CONN = int(os.getenv("POSTGRES_MIN_CONN"))
DB_MAX_CONN = int(os.getenv("POSTGRES_MAX_CONN"))


class PostgresSingleton:
    _instance = None
    client: pool.SimpleConnectionPool

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            print("Creating PostgreSQL connection pool...")
            cls._instance = super(PostgresSingleton, cls).__new__(cls, *args, **kwargs)
            cls._instance.client = pool.SimpleConnectionPool(
                minconn=DB_MIN_CONN,
                maxconn=DB_MAX_CONN,
                **DB_CONFIG,
            )
        return cls._instance

    def close(self):
        self.client.closeall()

    def get_client(self):
        return self.client


postgres_singleton = PostgresSingleton()


def get_postgres_client() -> pool.SimpleConnectionPool:
    return postgres_singleton.get_client()


def close_postgres_client() -> None:
    postgres_singleton.close()


def persist_characters_to_db() -> None:
    """
    Persists the character data to the PostgreSQL database.
    """
    with postgres_singleton.get_client().getconn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO players (id, name, gender)
                VALUES (%s, %s, %s)
                ON CONFLICT (id) DO UPDATE
                SET name = EXCLUDED
                """,
                (151433537470672790, "Clemeit", "Male"),
            )
    # with postgres_singleton.get_client().getconn() as conn:
    #     with conn.cursor() as cur:
    #         for player in players:
    #             cur.execute(
    #                 """
    #                 INSERT INTO players (id, name, gender)
    #                 VALUES (%s, %s, %s)
    #                 ON CONFLICT (id) DO UPDATE
    #                 SET name = EXCLUDED
    #                 """,
    #                 (151433537470672790, "Clemeit", "Male"),
    #             )
