from db import get_connection
from mcp_app import mcp

@mcp.tool
def get_top_queries(limit: int = 5) -> list[dict]:
    """Top queries by total_time from pg_stat_statements (if enabled)."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT query, calls, total_time, mean_time
            FROM pg_stat_statements
            ORDER BY total_time DESC
            LIMIT %s
        """, (limit,))
        rows = cur.fetchall()
    except Exception as e:
        rows = [{"error": str(e)}]
    finally:
        cur.close()
        conn.close()
    return rows
