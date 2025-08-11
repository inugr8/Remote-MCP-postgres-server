from db import get_connection
from mcp_app import mcp

@mcp.tool
def list_objects(schema: str = "public") -> dict:
    """List tables, views, and sequences in a schema."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT table_name, table_type
        FROM information_schema.tables
        WHERE table_schema = %s
        ORDER BY table_name
    """, (schema,))
    tables_and_views = cur.fetchall()

    cur.execute("""
        SELECT sequence_name
        FROM information_schema.sequences
        WHERE sequence_schema = %s
        ORDER BY sequence_name
    """, (schema,))
    sequences = cur.fetchall()

    cur.close()
    conn.close()

    return {
        "tables_and_views": tables_and_views,
        "sequences": [s["sequence_name"] for s in sequences],
    }
