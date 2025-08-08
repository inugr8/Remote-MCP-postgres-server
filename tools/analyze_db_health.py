from fastmcp import tool
from db import get_connection

@tool()
def analyze_db_health() -> dict:
    """
    Returns size of each table in the public schema.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT relname AS table_name,
               pg_size_pretty(pg_total_relation_size(relid)) AS total_size
        FROM pg_catalog.pg_statio_user_tables
        ORDER BY pg_total_relation_size(relid) DESC
    """)
    sizes = cur.fetchall()
    cur.close()
    conn.close()
    return {"table_sizes": sizes}
