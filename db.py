import psycopg2
import os
from dotenv import load_dotenv

from psycopg2.extras import RealDictCursor

load_dotenv()

def get_connection():
    return psycopg2.connect(
        dsn=os.getenv("DATABASE_URI"),cursor_factory=RealDictCursor
     
    )
