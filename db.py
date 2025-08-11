import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return psycopg2.connect(
        dsn=os.getenv("DATABASE_URI"),
        cursor_factory=RealDictCursor,
    )
