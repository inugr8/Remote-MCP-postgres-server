from fastmcp.tools import tool
from db import get_connection

@tool()
def list_schemas() -> list[str]:
    """
    Lists all available schemas in the PostgreSQL database.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT schema_name FROM information_schema.schemata")
    schemas = [row["schema_name"] for row in cur.fetchall()]
    cur.close()
    conn.close()
    return schemas
