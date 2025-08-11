from db import get_connection
from mcp_app import mcp

@mcp.tool
def analyze_db_health() -> dict:
    """Basic health: table sizes (user tables)."""
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
