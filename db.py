# db.py
import os
import re
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

def _redact(uri: str) -> str:
    if not uri:
        return "<EMPTY>"
    # mask password-like parts
    return re.sub(r"://([^:/]+):([^@]+)@", r"://\1:*****@", uri)

def get_connection():
    uri = os.getenv("DATABASE_URI", "")
    if not uri:
        # Log clearly; callers will surface this in JSON
        raise RuntimeError("DATABASE_URI is not set")

    # Neon usually needs sslmode=require
    if "neon.tech" in uri and "sslmode=" not in uri:
        uri = uri + ("&sslmode=require" if "?" in uri else "?sslmode=require")

    try:
        conn = psycopg2.connect(uri, cursor_factory=RealDictCursor)
        return conn
    except Exception as e:
        # include a redacted uri in the error so we can spot bad hosts/params
        raise RuntimeError(f"DB connect failed for { _redact(os.getenv('DATABASE_URI','')) }: {e!r}")
