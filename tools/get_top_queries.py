from fastmcp.tools import tool
from db import get_connection

@tool()
def get_top_queries(limit: int = 5) -> list[dict]:
    """
    Gets top slow queries from pg_stat_statements (if enabled).
    """
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT query, calls, total_time, mean_time
            FROM pg_stat_statements
            ORDER BY total_time DESC
            LIMIT %s
        """, (limit,))
        results = cur.fetchall()
    except Exception as e:
        results = [{"error": str(e)}]
    cur.close()
    conn.close()
    return results
