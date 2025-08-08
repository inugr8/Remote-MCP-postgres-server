from db import get_connection
def list_objects(schema: str = "public") -> dict:
    """
    Lists tables, views, and sequences in the given schema.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT table_name, table_type
        FROM information_schema.tables
        WHERE table_schema = %s
    """, (schema,))
    tables = cur.fetchall()

    cur.execute("""
        SELECT sequence_name
        FROM information_schema.sequences
        WHERE sequence_schema = %s
    """, (schema,))
    sequences = [row["sequence_name"] for row in cur.fetchall()]

    cur.close()
    conn.close()

    return {
        "tables_and_views": tables,
        "sequences": sequences
    }
