import psycopg2
from psycopg2 import pool
import os

# Database configuration
DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://uthuman_fggz_user:bCABeBKNob2AIeKLW0slWQ5JA3gqzfIV@dpg-d5vfmf4oud1c738g6go0-a.oregon-postgres.render.com/uthuman_fggz')

# Create connection pool
try:
    connection_pool = psycopg2.pool.SimpleConnectionPool(
        1, 20, DATABASE_URL
    )
    print("Connection pool created successfully")
except Exception as e:
    print(f"Error creating connection pool: {e}")
    connection_pool = None

def get_connection():
    if connection_pool:
        return connection_pool.getconn()
    return None

def return_connection(connection):
    if connection_pool:
        connection_pool.putconn(connection)

def init_db():
    conn = get_connection()
    if conn:
        try:
            cur = conn.cursor()
            # Create contacts table if not exists
            cur.execute("""
                CREATE TABLE IF NOT EXISTS contacts (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    phone VARCHAR(50) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Create index on created_at
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_contacts_created_at 
                ON contacts(created_at)
            """)

            # Ensure phone is unique
            cur.execute("""
                DO $$
                BEGIN
                    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'uq_contacts_phone') THEN
                        CREATE UNIQUE INDEX uq_contacts_phone ON contacts(phone);
                    END IF;
                END
                $$;
            """)

            # Ensure name is unique case-insensitively
            cur.execute("""
                DO $$
                BEGIN
                    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'uq_contacts_name_lower') THEN
                        CREATE UNIQUE INDEX uq_contacts_name_lower ON contacts(LOWER(name));
                    END IF;
                END
                $$;
            """)

            conn.commit()
            cur.close()
            print("Database initialized successfully")
        except Exception as e:
            print(f"Error initializing database: {e}")
        finally:
            return_connection(conn)

# Initialize database on startup
init_db()