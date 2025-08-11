from db import get_connection
from mcp_app import mcp

@mcp.tool
def analyze_query_indexes(sql: str) -> list[str]:
    """EXPLAIN a query to see index usage."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("EXPLAIN " + sql)
        plan = [row[0] for row in cur.fetchall()]
    except Exception as e:
        plan = [str(e)]
    finally:
        cur.close()
        conn.close()
    return plan
