from db import get_connection
from mcp_app import mcp

@mcp.tool
def get_object_details(table_name: str, schema: str = "public") -> dict:
    """Return columns and constraints for a table."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT column_name, data_type, is_nullable, COALESCE(character_maximum_length, -1) AS char_len
        FROM information_schema.columns
        WHERE table_schema = %s AND table_name = %s
        ORDER BY ordinal_position
    """, (schema, table_name))
    columns = cur.fetchall()

    cur.execute("""
        SELECT constraint_type, constraint_name
        FROM information_schema.table_constraints
        WHERE table_schema = %s AND table_name = %s
        ORDER BY constraint_type, constraint_name
    """, (schema, table_name))
    constraints = cur.fetchall()

    cur.close()
    conn.close()

    return {"columns": columns, "constraints": constraints}
