from db import get_connection
from mcp_app import mcp

def get_object_details(table_name: str, schema: str = "public") -> dict:
    """
    Returns column details and constraints for a table.
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_schema = %s AND table_name = %s
    """, (schema, table_name))
    columns = cur.fetchall()

    cur.execute("""
        SELECT constraint_type, constraint_name
        FROM information_schema.table_constraints
        WHERE table_schema = %s AND table_name = %s
    """, (schema, table_name))
    constraints = cur.fetchall()

    cur.close()
    conn.close()

    return {
        "columns": columns,
        "constraints": constraints
    }
