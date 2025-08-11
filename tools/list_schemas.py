from db import get_connection
from mcp_app import mcp

@mcp.tool
def list_schemas() -> list[str]:
    """List all schemas in the PostgreSQL database."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT schema_name FROM information_schema.schemata ORDER BY schema_name")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [r["schema_name"] for r in rows]
