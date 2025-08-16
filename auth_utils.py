import psycopg2
import bcrypt
from dotenv import load_dotenv
import os

# Load .env variables
load_dotenv()

# Get the full DB connection URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    """Create and return a PostgreSQL connection."""
    try:
        return psycopg2.connect(DATABASE_URL)
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return None

def get_user(username: str):
    """Fetch a user by username."""
    conn = get_db_connection()
    if not conn:
        return None

    try:
        cur = conn.cursor()
        cur.execute("SELECT id, name, username, password FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        cur.close()
        return user  # (id, name, username, password)
    except Exception as e:
        print(f"❌ Error fetching user: {e}")
        return None
    finally:
        conn.close()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Check if entered password matches the stored hash."""
    try:
        return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())
    except Exception as e:
        print(f"❌ Password verification error: {e}")
        return False

def register_user(name: str, username: str, password: str) -> bool:
    """Register a new user into the database."""
    conn = get_db_connection()
    if not conn:
        return False

    cur = conn.cursor()
    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    try:
        cur.execute(
            "INSERT INTO users (name, username, password) VALUES (%s, %s, %s)",
            (name, username, hashed_pw)
        )
        conn.commit()
        return True
    except psycopg2.IntegrityError:
        conn.rollback()
        print("⚠️ Username already exists.")
        return False
    except Exception as e:
        conn.rollback()
        print(f"❌ Error registering user: {e}")
        return False
    finally:
        cur.close()
        conn.close()
